import os
import subprocess
import configparser
import requests
import logging
import psycopg2
from git import Repo, Git




def shell_exec(cmd, logger,dryrun: bool = False):
    if dryrun:
        logger.info(f"NOT EXECUTING - {cmd}")
        return
    logger.info(cmd)
    output = subprocess.check_output(cmd, shell=True)
    logger.info("%s", output)
    return output


class TaskHelper:

    def __init__(self, name):
        self.name = name
        self.OPENQA_URL_BASE = 'https://openqa.suse.de/'
        self.config = configparser.ConfigParser()
        self.config.read(f'/etc/{self.name}.ini')
        self.to_list = self.config.get('DEFAULT', 'to_list', fallback='asmorodskyi@suse.com')
        self.logger = logging.getLogger(name)
        logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)
        if self.config.has_section('OSD'):
            self.osd_username = self.config.get('OSD', 'username')
            self.osd_password = self.config.get('OSD', 'password')
            self.osd_host = self.config.get('OSD', 'host')

    def osd_get(self, suffix):
        response = requests.get(f'{self.OPENQA_URL_BASE}{suffix}', timeout=100, verify=False)
        response.raise_for_status()
        return response.json()

    def get_latest_build(self, job_group_id=262):
        build = '1'
        try:
            group_json = self.osd_get(f'/group_overview/{job_group_id}.json')
            if len(group_json['build_results']) == 0:
                self.logger.warning(f"No jobs found in {job_group_id}")
                return None
            build = group_json['build_results'][0]['build']
        except Exception as e:
            self.logger.error("Failed to get build from openQA - %s", e)
        return build

    def osd_query(self, query):
        if hasattr(self, 'osd_username') and hasattr(self, 'osd_password') and hasattr(self, 'osd_host'):
            connection = None
            try:
                connection = psycopg2.connect(user=self.osd_username, password=self.osd_password,
                                              host=self.osd_host, port="5432", database="openqa")
                cursor = connection.cursor()
                # self.logger.debug(query)
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


class GitHelper:

    def __init__(self):
        self.logger = logging.getLogger('GitHelper')
        logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)
        self.repo = Repo(os.getcwd())
        remotes = Git().remote().split()
        branches = Git().branch("--all").split()
        self.remote = None
        self.master = "master"
        if "asmorodskyi" in remotes:
            self.remote = self.repo.remotes.asmorodskyi
        else:
            self.remote = self.repo.remotes.origin
        if "master" not in branches:
            self.master = "main"
