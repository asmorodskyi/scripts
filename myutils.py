import logging
from logging.handlers import RotatingFileHandler
import smtplib
import socket
import traceback
import requests
import subprocess
from subprocess import CalledProcessError
import json


class TaskHelper:

    OPENQA_URL_BASE = 'https://openqa.suse.de/'
    OPENQA_EXE = '/usr/bin/openqa-client --json-output'

    def __init__(self, name, log_to_file=True):
        self.name = name
        logging.basicConfig(format='%(asctime)s -  %(levelname)s:%(message)s',
                            level=logging.INFO, datefmt='%m-%d %H:%M:%S')
        self.logger = logging.getLogger(__name__)
        if log_to_file:
            handler = logging.handlers.RotatingFileHandler(
                '/var/log/{0}/{0}.log'.format(self.name), maxBytes=100*1024*1024, backupCount=50)
            formatter = logging.Formatter(
                '%(asctime)s -  %(levelname)s:%(message)s', datefmt='%m-%d %H:%M:%S')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            smtp_host = 'relay.suse.de'
            smtp_port = 25
            s.connect((smtp_host, int(smtp_port)))
            s.shutdown(2)
            self.smtpObj = smtplib.SMTP(smtp_host, smtp_port)
        except:
            pass

    def run(self, params_dict):
        raise NotImplementedError

    def handle_error(self, error=''):
        if not error:
            error = traceback.format_exc()
        self.logger.error(error)
        if hasattr(self, 'smtpObj'):
            sender = 'asmorodskyi@suse.com'
            receivers = ['asmorodskyi@suse.com']
            email = '''\
        Subject: [{_name}] ERROR - {_host}
        From: {_from}
        To: {_to}
        {_error}
        '''.format(_from=sender, _to=receivers, _error=error, _name=self.name, _host=socket.gethostname())
            self.smtpObj.sendmail(sender, receivers, email)
        else:
            self.logger.warn(
                'SMTP object not initialized ! So not sending email')

    def get_latest_build(self):
        build = '1'
        try:
            group_json = requests.get(
                self.OPENQA_URL_BASE + 'group_overview/262.json', verify=False).json()
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
