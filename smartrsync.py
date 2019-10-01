#!/usr/bin/python3

import logging
from logging.handlers import RotatingFileHandler
import smtplib
import requests
import os
import urllib.request
import shutil
import traceback
import socket

logging.basicConfig(format='%(asctime)s -  %(levelname)s:%(message)s',
                    level=logging.INFO, datefmt='%m-%d %H:%M:%S')
handler = logging.handlers.RotatingFileHandler(
    '/var/log/smartrsync/smartrsync.log', maxBytes=100*1024*1024, backupCount=50)
formatter = logging.Formatter(
    '%(asctime)s -  %(levelname)s:%(message)s', datefmt='%m-%d %H:%M:%S')
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)

OPENQA_URL_BASE = 'https://openqa.suse.de/'


def send_email(msg):
    sender = 'asmorodskyi@suse.com'
    receivers = ['asmorodskyi@suse.com']
    smtpObj = smtplib.SMTP('relay.suse.de', 25)
    email = '''\
Subject: [RSYNC] ERROR - {host}
From: {_from}
To: {_to}
{error}
'''.format(_from=sender, _to=receivers, error=msg, host=socket.gethostname())
    smtpObj.sendmail(sender, receivers, email)


def sync_file(filename, filetype):
    try:
        full_path = '/var/lib/openqa/factory/{0}/{1}'.format(
            filetype, filename)
        logger.info("#### START Looking for file - %s", full_path)
        if os.path.isfile(full_path):
            logger.info('File found')
        else:
            target_url = '{0}assets/{1}/{2}'.format(OPENQA_URL_BASE,
                                                    filetype, filename)
            logger.info(
                'File not found. Will try to download it from %s', target_url)
            urllib.request.urlretrieve(target_url, full_path)
    except Exception:
        error = traceback.format_exc()
        logger.error(error)
        send_email(error)
    finally:
        logger.info("#### Done processing file %s", filename)


def main():
    group_json = requests.get(
        OPENQA_URL_BASE + 'group_overview/170.json').json()
    latest_build = group_json['build_results'][0]['build']
    sync_file('SLES-12-SP5-x86_64-Build{0}-wicked.qcow2'.format(
        latest_build), 'hdd')
    sync_file('SLE-12-SP5-Server-DVD-x86_64-Build{0}-Media1.iso'.format(
        latest_build), 'iso')


if __name__ == "__main__":
    main()
