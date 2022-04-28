#!/usr/bin/python3

from myutils import openQAHelper
import argparse
import re
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class SmartClone(openQAHelper):

    def __init__(self, args):
        super(SmartClone, self).__init__('SmartClone', False, load_cache=True)
        self.cmd = '/usr/share/openqa/script/clone_job.pl --skip-chained-deps --parental-inheritance'
        self.params_str = ''
        if args.params:
            self.params_str = ' {}'.format(args.params.replace(',', ' '))
        if args.resetworker:
            self.params_str += ' WORKER_CLASS=qemu_x86_64 '
        if args.branch:
            self.params_str += ' CASEDIR=https://github.com/{0}/os-autoinst-distri-opensuse.git#{1} BUILD={1}'.format(
                args.github_user, args.branch)
        if args.winst:
            self.cmd += ' --within-instance {}'.format(args.frm)
        else:
            self.cmd += ' --from {}'.format(args.frm)

    def run(self, jobid, dryrun: bool = False):
        try:
            ids = jobid.split(',')
            for one_id in ids:
                self.shell_exec('{} {} {}'.format(self.cmd, one_id, self.params_str), log=True, dryrun=dryrun)
        except Exception:
            self.handle_error()

    def query(self, query: str, dryrun: bool = False):
        m = re.match(r"(\w+)=(\w+)", query)
        groupid = m.group(2)
        latest_build = self.get_latest_build(groupid)
        if query.startswith('allpc'):
            unique_jobs = self.osd_get_jobs_where(
                latest_build, groupid, " and test = 'publiccloud_download_testrepos'")
            for job in unique_jobs:
                self.shell_exec('{} {} {}'.format(self.cmd, job.id, self.params_str), log=True, dryrun=dryrun)
        elif query.startswith('fixworker'):
            if not latest_build:
                raise ValueError("No jobs was found in {}".format(groupid))
            unique_jobs = self.osd_get_jobs_where(
                latest_build, groupid, " and test != 'publiccloud_download_testrepos'")
            for job in unique_jobs:
                if job.flavor.startswith('EC2'):
                    new_params = "{} {} ".format(self.params_str, 'WORKER_CLASS=pc_ec2')
                elif job.flavor.startswith('AZURE'):
                    new_params = "{} {}".format(self.params_str, 'WORKER_CLASS=pc_azure')
                elif job.flavor.startswith('GCE'):
                    new_params = "{} {}".format(self.params_str, 'WORKER_CLASS=pc_gce')
                else:
                    raise AttributeError('Unexpected job flavor {}'.format(job))
                self.shell_exec('{} {} {}'.format(self.cmd, job.id, new_params), log=True, dryrun=dryrun)
        else:
            raise AttributeError('Unexpected query %s, excpected : allpc=<groupid>,fixworker=<groupid>')


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-q', '--query')
    group.add_argument('-j', '--jobid')
    parser.add_argument('-f', '--frm', default='openqa.suse.de')
    parser.add_argument('-p', '--params')
    parser.add_argument('-w', '--winst', action='store_true')
    parser.add_argument('-d', '--dryrun', action='store_true')
    parser.add_argument('-b', '--branch')
    parser.add_argument('-r', '--resetworker', action='store_true')
    parser.add_argument('-g', '--github-user', default='asmorodskyi')

    args = parser.parse_args()
    solver = SmartClone(args)
    if args.query:
        solver.query(args.query, args.dryrun)
    elif args.jobid:
        solver.run(args.jobid, args.dryrun)
    else:
        raise AttributeError('Need to specify --jobid or --query')


if __name__ == "__main__":
    main()
