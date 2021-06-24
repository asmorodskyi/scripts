#!/usr/bin/python3

import requests

from myutils import openQAHelper
import argparse
import urllib3
import json
import webbrowser
from models import JobSQL, Base, ReviewCache, KnownIssues
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import re


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Review(openQAHelper):

    def __init__(self, dry_run: bool = False, browser: bool = False):
        super(Review, self).__init__('review', False, load_cache=True)
        self.dry_run = dry_run
        self.browser = browser
        engine = create_engine('sqlite:////scripts/review.db')
        Base.metadata.create_all(engine, Base.metadata.tables.values(), checkfirst=True)
        Session = sessionmaker(bind=engine)
        self.session = Session()
        self.reviewcache_query = self.session.query(ReviewCache)
        self.known_issues_query = self.session.query(KnownIssues)

    def run(self):
        for groupid in self.my_osd_groups:
            latest_build = self.get_latest_build(groupid)
            previous_builds = self.get_previous_builds(groupid)
            self.logger.info('{} is latest build for {}'.format(
                latest_build, self.config.get(str(groupid), 'name', fallback=groupid)))
            jobs = self.osd_get_jobs_where(
                latest_build, groupid, " and result in ('failed', 'timeout_exceeded', 'incomplete')")
            unique_jobs = self.filter_latest(jobs)
            for job in unique_jobs:
                existing_bugrefs = self.get_bugrefs(job.id)
                if len(existing_bugrefs) == 0 and not self.apply_known_refs(job) and previous_builds:
                    bugrefs = set()
                    previous_jobs = self.osd_query("{} build in ({}) and test='{}' and flavor='{}' and group_id={} and result in ('failed', 'timeout_exceeded', 'incomplete')".format(
                        JobSQL.SELECT_QUERY, previous_builds, job.name, job.flavor, groupid))
                    failed_modules = self.get_failed_modules(job.id)
                    for previous_job in previous_jobs:
                        previous_job_sql = JobSQL(previous_job)
                        previous_job_failed_modules = self.get_failed_modules(previous_job_sql.id)
                        if previous_job_failed_modules == failed_modules:
                            bugrefs = bugrefs | self.get_bugrefs(previous_job_sql.id)
                    if len(bugrefs) == 0:
                        self.logger.info(
                            '{} on {} {}t{} [{}]'.format(job.name, job.flavor, self.OPENQA_URL_BASE, job.id,
                                                         failed_modules))
                        if self.browser:
                            webbrowser.open("{}t{}".format(self.OPENQA_URL_BASE, job.id))
                        self.session.add(ReviewCache(job.name, failed_modules))
                        self.session.commit()
                    else:
                        for ref in bugrefs:
                            self.add_comment(job, ref)

    def add_comment(self, job, comment):
        self.logger.info('Add a comment to {} with reference {}'.format(job, comment))
        cmd = 'openqa-cli api --host {} -X POST jobs/{}/comments text=\'{}\''.format(self.OPENQA_URL_BASE, job.id,
                                                                                     comment)
        if self.dry_run:
            self.logger.info('"{}" not executed due to dry_run=True'.format(cmd))
        else:
            self.shell_exec(cmd, log=True)

    def get_failed_modules(self, job_id):
        rezult = self.osd_query(
            "select name from job_modules where job_id={} and result='failed'".format(job_id))
        failed_modules = ""
        for rez in rezult:
            if not failed_modules:
                failed_modules = "{}".format(rez[0])
            else:
                failed_modules = "{},{}".format(failed_modules, rez[0])
        return failed_modules

    def apply_known_refs(self, job):
        failed_modules = self.get_failed_modules(job.id)
        comment_applied = False
        for item in self.known_issues_query.filter(KnownIssues.job_name == job.name).filter(KnownIssues.failed_modules == failed_modules):
            self.add_comment(job, item.label)
            comment_applied = True
        return comment_applied

    def clean_cache(self):
        self.session.query(ReviewCache).delete()

    def move_cache(self, query):
        m = re.match(r"([fn]=[a-z_,]*)\|([a-z#0-9]*)", query)
        if m:
            cache_filter = m.group(1).split('=')
            if cache_filter[0] == 'f':
                for review in self.reviewcache_query.filter(ReviewCache.failed_modules == cache_filter[1]).all():
                    self.logger.info("Moving {} to known_issues with label={}".format(review, m.group(2)))
                    self.session.add(KnownIssues(review.job_name, review.failed_modules, m.group(2)))
                    self.reviewcache_query.filter(ReviewCache.id == review.id).delete()
                self.session.commit()
        else:
            raise ValueError("Unkown key")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dry_run', action='store_true')
    parser.add_argument('-b', '--browser', action='store_true')
    parser.add_argument('-c', '--cleancache', action='store_true')
    parser.add_argument('-m', '--movecache')
    args = parser.parse_args()

    review = Review(args.dry_run, args.browser)
    if args.cleancache:
        review.clean_cache()
    if args.movecache:
        review.move_cache(args.movecache)
    else:
        review.run()


if __name__ == "__main__":
    main()
