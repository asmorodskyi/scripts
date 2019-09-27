#!/usr/bin/python3
from git import Repo
import logging
from logging.handlers import RotatingFileHandler
import traceback
import smtplib

logging.basicConfig(format='%(asctime)s -  %(levelname)s:%(message)s',
                    level=logging.INFO, datefmt='%m-%d %H:%M:%S')
handler = logging.handlers.RotatingFileHandler(
    '/var/log/smartpull/smartpull.log', maxBytes=100*1024*1024, backupCount=50)
formatter = logging.Formatter(
    '%(asctime)s -  %(levelname)s:%(message)s', datefmt='%m-%d %H:%M:%S')
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)


def send_email(msg):
    sender = 'asmorodskyi@suse.com'
    receivers = ['asmorodskyi@suse.com']
    smtpObj = smtplib.SMTP('relay.suse.de', 25)
    email = '''\
Subject: [GIT] ERROR
From: {_from}
To: {_to}
{error}
'''.format(_from=sender, _to=receivers, error=msg)
    smtpObj.sendmail(sender, receivers, email)


def pull_repo(repo_path):
    try:
        logger.info("#### START processing repo %s", repo_path)
        repo = Repo(repo_path)
        logger.info("Current branch is %s with commit %s",
                    repo.active_branch, repo.commit())
        was_dirty = False
        if repo.is_dirty():
            logger.info("HEAD is dirty, trying to stash changes")
            repo.git.stash('save')
            was_dirty = True
        old_branch = 'master'
        if str(repo.active_branch) != "master":
            logger.info(
                "HEAD pointing to %s,trying switch to master", repo.active_branch)
            old_branch = repo.active_branch
            repo.git.checkout('master')
        repo.remote().pull('master')
        logger.info("After pulling changes head pointing to %s", repo.commit())
        if old_branch != "master":
            logger.info("HEAD was at %s, switching it back", old_branch)
            repo.git.checkout(old_branch)
        if was_dirty:
            logger.info("master was dirty, so reapplying changes")
            repo.git.stash('apply')
    except Exception:
        error = traceback.format_exc()
        logger.error(error)
        send_email(error)
    finally:
        logger.info("#### End processing repo %s", repo_path)


def main():
    file = open('/smart_pull_repos', 'r')
    lines = file.readlines()
    for line in lines:
        pull_repo(line.strip())


if __name__ == "__main__":
    main()
