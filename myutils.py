from email.mime.text import MIMEText

import logzero
import smtplib
import socket
import os
import traceback
import requests
import subprocess
import json
from git import Repo


class TaskHelper:

    def __init__(self, name, log_to_file=True):
        self.name = name
        if log_to_file:
            self.logger = logzero.setup_logger(
                name=name, logfile='/var/log/{0}/{0}.log'.format(self.name), formatter=logzero.LogFormatter(
                    fmt='%(color)s[%(asctime)s %(module)s:%(lineno)d]%(end_color)s %(message)s',
                    datefmt='%d-%m %H:%M:%S'))
        else:
            self.logger = logzero.setup_logger(
                name=name, formatter=logzero.LogFormatter(
                    fmt='%(color)s%(module)s:%(lineno)d|%(end_color)s %(message)s'))

    def send_mail(self, subject, message, to_list):
        try:
            mimetext = MIMEText(message)
            mimetext['Subject'] = subject
            mimetext['From'] = 'asmorodskyi@suse.com'
            mimetext['To'] = to_list
            server = smtplib.SMTP('relay.suse.de', 25)
            server.ehlo()
            server.sendmail('asmorodskyi@suse.com', to_list.split(','), mimetext.as_string())
        except Exception:
            self.logger.error("Fail to send email - {}".format(traceback.format_exc()))

    def handle_error(self, error=''):
        if not error:
            error = traceback.format_exc()
        self.logger.error(error)
        self.send_mail('[{}] ERROR - {}'.format(self.name, socket.gethostname()), error, 'asmorodskyi@suse.com')

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


class GitHelper(TaskHelper):

    def __init__(self):
        super().__init__("GitHelper", log_to_file=False)
        self.repo = Repo(os.getcwd())
        self.remote = None
        try:
            if self.repo.remotes.asmorodskyi.exists():
                self.remote = self.repo.remotes.asmorodskyi
        except Exception:
            self.remote = self.repo.remotes.origin


class openQAHelper(TaskHelper):

    def __init__(self, name, for_o3, log_to_file=False):
        super(openQAHelper, self).__init__(name, log_to_file=log_to_file)
        self.for_o3 = for_o3
        if self.for_o3:
            self.OPENQA_URL_BASE = 'https://openqa.opensuse.org/'
        else:
            self.OPENQA_URL_BASE = 'https://openqa.suse.de/'
        self.OPENQA_API_BASE = self.OPENQA_URL_BASE + 'api/v1/'

    def get_previous_builds(self, job_group_id: int, deep: int = 3):
        builds = []
        group_json = requests.get('{}group_overview/{}.json'.format(self.OPENQA_URL_BASE, job_group_id),
                                  verify=False).json()
        if len(group_json['build_results']) < deep:
            raise IndexError
        for i in range(0, deep):
            builds.append(group_json['build_results'][i + 1]['build'])
        return builds

    def groupID_to_name(self, id):
        if id == 170 or id == 262:
            return "Network"
        elif id == 219:
            return  "Azure"
        elif id == 274:
            return "EC2"
        elif id == 275:
            return "GCE"
        else:
            return str(id)
