#!/usr/bin/python3

import requests

from myutils import openQAHelper
import argparse
import urllib3
import json
from models import JobORM

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Review(openQAHelper):
    known_json = '/scripts/known.json'

    def __init__(self, dry_run: bool = False, apply_known: bool = False):
        super(Review, self).__init__('review', False, log_to_file=False, load_cache=True)
        self.dry_run = dry_run
        self.apply_known = apply_known

    def run(self):
        for groupid in self.my_osd_groups:
            latest_build = self.get_latest_build(groupid)
            previous_builds = self.get_previous_builds(groupid)
            self.logger.info('{} is latest build for {}'.format(latest_build, self.groupID_to_name(groupid)))
            self.logger.info("{} needs to process".format(self.job_query.filter(
                JobORM.build == latest_build, JobORM.result not in ['passed', 'skipped'], JobORM.needs_update == False).count()))
            for job in self.job_query.filter(JobORM.build == latest_build, JobORM.result not in ['passed', 'skipped'], JobORM.needs_update == False):
                if self.apply_known:
                    self.apply_known_refs(job)
                need_review_bugrefs = self.get_bugrefs(job.id)
                if len(need_review_bugrefs) == 0:
                    bugrefs = set()
                    for id in self.job_query.filter(JobORM.build in previous_builds, JobORM.name == job.name, JobORM.instance_type == job.instance_type, JobORM.flavor == job.flavor, sorted(JobORM.failed_modules) == sorted(job.failed_modules), JobORM.result == 'failed'):
                        bugrefs = bugrefs | self.get_bugrefs(id)
                    if len(bugrefs) == 0:
                        self.logger.info(
                            '{}t{} [{}, {}, {}]'.format(self.OPENQA_URL_BASE, job.id, job.name, job.flavor,
                                                        job.failed_modules))
                    for ref in bugrefs:
                        self.add_comment(job.id, ref)

    def get_bugrefs(self, job_id):
        bugrefs = set()
        comments = requests.get('{}jobs/{}/comments'.format(self.OPENQA_API_BASE, job_id), verify=False).json()
        for comment in comments:
            for bug in comment['bugrefs']:
                bugrefs.add(bug)
        return bugrefs

    def add_comment(self, job, comment):
        self.logger.info('Add a comment to {} with reference {}'.format(job, comment))
        cmd = 'openqa-cli api --host {} -X POST jobs/{}/comments text=\'{}\''.format(self.OPENQA_URL_BASE, job.id,
                                                                                     comment)
        if self.dry_run:
            self.logger.info('"{}" not executed due to dry_run=True'.format(cmd))
        else:
            self.shell_exec(cmd, log=True)
            job.needs_update = False
            self.session.commit()

    def apply_known_refs(self, job):
        with open(Review.known_json) as f:
            known = json.load(f)
            for item in known:
                if item['test'] == job.name and item['failed_modules'] == job.failed_modules and len(
                        self.get_bugrefs(job.id)) == 0:
                    self.add_comment(job, item['label'])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry_run', action='store_true')
    parser.add_argument('--apply_known', action='store_true')
    args = parser.parse_args()

    review = Review(args.dry_run, args.apply_known)
    review.run()


if __name__ == "__main__":
    main()
