#!/usr/bin/python3

import requests

from myutils import openQAHelper
import argparse
import urllib3
import json
from models import JobSQL

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Review(openQAHelper):
    known_json = '/scripts/known.json'

    def __init__(self, dry_run: bool = False):
        super(Review, self).__init__('review', False, load_cache=True)
        self.dry_run = dry_run

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
                if len(existing_bugrefs) == 0 and not self.apply_known_refs(job):
                    bugrefs = set()
                    previous_jobs = self.osd_query("{} build in ({}) and test='{}' and flavor='{}' and group_id={} and result in ('failed', 'timeout_exceeded', 'incomplete')".format(
                        JobSQL.SELECT_QUERY, previous_builds, job.name, job.flavor, groupid))
                    failed_modules = self.get_failed_modules(job.id)
                    for previous_job in previous_jobs:
                        previous_job_sql = JobSQL(previous_job)
                        previous_job_failed_modules = self.get_failed_modules(previous_job_sql.id)
                        if previous_job_failed_modules == failed_modules:
                            bugrefs = bugrefs | self.get_bugrefs(previous_job.id)
                    if len(bugrefs) == 0:
                        self.logger.info(
                            '{} on {} {}t{} [{}]'.format(job.name, job.flavor, self.OPENQA_URL_BASE, job.id,
                                                         failed_modules))
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
        with open(Review.known_json) as f:
            known = json.load(f)
            failed_modules = self.get_failed_modules(job.id)
            comment_applied = False
            for item in known:
                if item['test'] == job.name and failed_modules == item["failed_modules"]:
                    self.add_comment(job, item['label'])
                    comment_applied = True
            return comment_applied


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dry_run', action='store_true')
    args = parser.parse_args()

    review = Review(args.dry_run)
    review.run()


if __name__ == "__main__":
    main()
