from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import logzero
import smtplib
import socket
import os
import traceback
import requests
import subprocess
import json
from git import Repo
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, MessageLatency, JobSQL
import configparser
from datetime import datetime
import psycopg2


class TaskHelper:

    def __init__(self, name):
        self.name = name
        self.config = configparser.ConfigParser()
        self.config.read('/etc/{}.ini'.format(self.name))
        self.to_list = self.config.get('DEFAULT', 'to_list', fallback='asmorodskyi@suse.com')
        if self.config['DEFAULT'].getboolean('log_to_file', fallback=True):
            self.logger = logzero.setup_logger(
                name=name, logfile='/var/log/{0}/{0}.log'.format(self.name), formatter=logzero.LogFormatter(
                    fmt='%(color)s[%(asctime)s %(module)s:%(lineno)d]%(end_color)s %(message)s',
                    datefmt='%d-%m %H:%M:%S'))
        else:
            self.logger = logzero.setup_logger(
                name=name, formatter=logzero.LogFormatter(
                    fmt='%(color)s%(module)s:%(lineno)d|%(end_color)s %(message)s'))
        if self.config.has_section('OSD'):
            self.osd_username = self.config.get('OSD', 'username')
            self.osd_password = self.config.get('OSD', 'password')
            self.osd_host = self.config.get('OSD', 'host')

    def send_mail(self, subject, message, html_message: str = None, custom_to_list: str = None):
        try:
            if html_message:
                mimetext = MIMEMultipart('alternative')
                part1 = MIMEText(message, 'plain')
                part2 = MIMEText(html_message, 'html')
                mimetext.attach(part1)
                mimetext.attach(part2)
            else:
                mimetext = MIMEText(message)
            mimetext['Subject'] = subject
            mimetext['From'] = 'asmorodskyi@suse.com'
            if not custom_to_list:
                custom_to_list = self.to_list
            mimetext['To'] = custom_to_list
            server = smtplib.SMTP('relay.suse.de', 25)
            server.ehlo()
            server.sendmail('asmorodskyi@suse.com', custom_to_list.split(','), mimetext.as_string())
        except Exception:
            self.logger.error("Fail to send email - {}".format(traceback.format_exc()))

    def handle_error(self, error=''):
        if not error:
            error = traceback.format_exc()
        self.logger.error(error)
        self.send_mail('[{}] ERROR - {}'.format(self.name, socket.gethostname()), error)

    def get_latest_build(self, job_group_id=262):
        build = '1'
        try:
            group_json = requests.get('https://openqa.suse.de/group_overview/{}.json'.format(job_group_id),
                                      verify=False).json()
            build = group_json['build_results'][0]['build']
        except Exception as e:
            self.logger.error("Failed to get build from openQA - %s", e)
        finally:
            return build

    def shell_exec(self, cmd, log=False, is_json=False):
        try:
            if log:
                self.logger.info(cmd)
            output = subprocess.check_output(cmd, shell=True)
            if is_json:
                o_json = json.loads(output)
                if log:
                    self.logger.info("%s", o_json)
                return o_json
            else:
                if log:
                    self.logger.info("%s", output)
                return output
        except subprocess.CalledProcessError:
            self.handle_error('Command died')

    def osd_query(self, query):
        if hasattr(self, 'osd_username') and hasattr(self, 'osd_password') and hasattr(self, 'osd_host'):
            try:
                connection = psycopg2.connect(user=self.osd_username, password=self.osd_password,
                                              host=self.osd_host, port="5432", database="openqa")
                cursor = connection.cursor()
                cursor.execute(query)
                return cursor.fetchall()
            except (Exception, psycopg2.Error) as error:
                self.logger.error(error)
            finally:
                if connection is not None:
                    cursor.close()
                    connection.close()
        else:
            raise AttributeError("Connection to osd is not defined ")


class GitHelper(TaskHelper):

    def __init__(self):
        super().__init__("GitHelper")
        self.repo = Repo(os.getcwd())
        self.remote = None
        try:
            if self.repo.remotes.asmorodskyi.exists():
                self.remote = self.repo.remotes.asmorodskyi
        except Exception:
            self.remote = self.repo.remotes.origin


class openQAHelper(TaskHelper):

    def __init__(self, name, for_o3, load_cache=False):
        super(openQAHelper, self).__init__(name)
        self.for_o3 = for_o3
        self.my_osd_groups = [int(num_str) for num_str in str(self.config.get(
            'DEFAULT', 'groups', fallback='262,219,274,275')).split(',')]
        if self.for_o3:
            self.OPENQA_URL_BASE = 'https://openqa.opensuse.org/'
        else:
            self.OPENQA_URL_BASE = 'https://openqa.suse.de/'
        self.OPENQA_API_BASE = self.OPENQA_URL_BASE + 'api/v1/'
        if load_cache:
            engine = create_engine('sqlite:////scripts/openqa_cache.db')
            Base.metadata.create_all(engine, Base.metadata.tables.values(), checkfirst=True)
            Session = sessionmaker(bind=engine)
            self.session = Session()
            self.msg_query = self.session.query(MessageLatency)

    def get_previous_builds(self, job_group_id: int, deep: int = 3):
        builds = []
        group_json = requests.get('{}group_overview/{}.json'.format(self.OPENQA_URL_BASE, job_group_id),
                                  verify=False).json()
        if len(group_json['build_results']) > deep:
            for i in range(0, deep):
                builds.append(group_json['build_results'][i + 1]['build'])
        return builds

    def filter_latest(self, all_jobs):
        unique_jobs = {}
        for job in all_jobs:
            job_key = '{}-{}'.format(job.name, job.flavor)
            if job_key in unique_jobs:
                if job.id > unique_jobs[job_key].id:
                    unique_jobs[job_key] = job
            else:
                unique_jobs[job_key] = job
        return unique_jobs.values()

    def get_bugrefs(self, job_id):
        bugrefs = set()
        comments = requests.get('{}jobs/{}/comments'.format(self.OPENQA_API_BASE, job_id), verify=False).json()
        if 'error' in comments:
            raise RuntimeError(comments)
        for comment in comments:
            for bug in comment['bugrefs']:
                bugrefs.add(bug)
        return bugrefs

    def check_latency(self, topic, subject):
        msg = self.msg_query.filter(MessageLatency.topic == topic).filter(
            MessageLatency.subject == subject).one_or_none()
        rez = 0
        if msg:
            if datetime.now() < msg.locked_till:
                self.logger.info('still locked {}'.format(msg))
                rez = 3
            else:
                msg.lock()
                self.logger.info('Got locked {}'.format(msg))
                rez = 2
            msg.inc_cnt()
        else:
            new_msg = MessageLatency(topic, subject)
            self.session.add(new_msg)
            rez = 1
        self.session.commit()
        return rez

    def osd_get_jobs_where(self, build, group_id, extra_conditions=''):
        rezult = self.osd_query("{} build='{}' and group_id='{}' {}".format(
            JobSQL.SELECT_QUERY, build, group_id, extra_conditions))
        jobs = []
        for raw_job in rezult:
            jobs.append(JobSQL(raw_job))
        return jobs


def is_matched(rules, topic, msg):
    for rule in rules:
        rkey, filter_matches = rule
        if rkey.match(topic) and filter_matches(topic, msg):
            return True
