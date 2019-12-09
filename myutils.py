import logging
from logging.handlers import RotatingFileHandler
import smtplib
import socket
import traceback
import requests


class TaskSolver:

    OPENQA_URL_BASE = 'https://openqa.suse.de/'

    def __init__(self, name):
        self.name = name
        logging.basicConfig(format='%(asctime)s -  %(levelname)s:%(message)s',
                            level=logging.INFO, datefmt='%m-%d %H:%M:%S')
        handler = logging.handlers.RotatingFileHandler(
            '/var/log/{0}/{0}.log'.format(self.name), maxBytes=100*1024*1024, backupCount=50)
        formatter = logging.Formatter(
            '%(asctime)s -  %(levelname)s:%(message)s', datefmt='%m-%d %H:%M:%S')
        handler.setFormatter(formatter)
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(handler)
        self.smtpObj = smtplib.SMTP('relay.suse.de', 25)

    def solve(self, params_dict):
        raise NotImplementedError

    def handle_error(self):
        error = traceback.format_exc()
        self.logger.error(error)
        sender = 'asmorodskyi@suse.com'
        receivers = ['asmorodskyi@suse.com']
        email = '''\
    Subject: [{_name}] ERROR - {host}
    From: {_from}
    To: {_to}
    {_error}
    '''.format(_from=sender, _to=receivers, _error=error, _name=self.name, host=socket.gethostname())
        self.smtpObj.sendmail(sender, receivers, email)

    def get_latest_build(self):
        group_json = requests.get(
            self.OPENQA_URL_BASE + 'group_overview/262.json', verify=False).json()
        return group_json['build_results'][0]['build']
