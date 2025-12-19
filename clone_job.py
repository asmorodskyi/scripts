#!/usr/bin/python3.11

import argparse
import re
import urllib3
from datetime import datetime
from myutils import TaskHelper, shell_exec

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class JobSQL:

    # group_id is queried but not serialized because in most cases we don't need it
    # but we have one case where we do ( openQAHelper.osd_get_latest_failures)
    SELECT_QUERY = 'select id, test, result, state, flavor, arch, build, group_id from jobs where '

    def __init__(self, raw_job):
        self.id = raw_job[0]
        self.name = raw_job[1]
        self.result = raw_job[2]
        self.state = raw_job[3]
        self.flavor = raw_job[4]
        self.arch = raw_job[5]
        self.build = raw_job[6]

    def __str__(self):
        pattern = 'Job(id: {}, name: {}, result: {}, state: {}, flavor: {}, arch: {}, build: {})'
        return pattern.format(self.id, self.name, self.result, self.state, self.flavor, self.arch, self.build)

class SmartClone(TaskHelper):

    FIND_LATEST = "select max(id) from jobs where  build='{}' and group_id='{}'  and test='{}' and arch='{}' \
        and flavor='{}';"
    CLONED_JOBS_LOG = "/var/log/cloned_urls.log"

    def __init__(self, args):
        super(SmartClone, self).__init__("SmartClone")
        self.cmd = "/usr/share/openqa/script/clone_job.pl --skip-chained-deps --parental-inheritance"
        self.params_str = ""
        if args.masktestissues:
            job_json = self.osd_get(f'tests/{args.jobid}/file/vars.json')
            for var1 in job_json:
                if 'TEST_ISSUES' in var1 or 'TEST_REPOS' in var1:
                    self.params_str += f" {var1}=''"
        if args.params:
            self.params_str += " ".join(args.params)
        if args.branch:
            self.params_str += f" CASEDIR=https://github.com/{args.github_user}/os-autoinst-distri-opensuse.git#{args.branch} BUILD={args.branch} _GROUP=0"
        if args.winst:
            self.cmd += f" --within-instance {args.frm}"
        else:
            self.cmd += f" --from {args.frm}"
        if args.skipmaintenance:
            self.params_str += " SKIP_MAINTENANCE_UPDATES=1 PUBLIC_CLOUD_IGNORE_EMPTY_REPO=1 PUBLIC_CLOUD_SKIP_MU=1"
            if '_GROUP=0' not in self.params_str:
                self.params_str += " _GROUP=0"

    def run(self, jobid, dryrun: bool = False):
        ids = jobid.split(",")
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for one_id in ids:
            ret1 = shell_exec(f"{self.cmd} {one_id} {self.params_str}", self.logger, dryrun=dryrun)
            if ret1 is not None:
                match = re.search(r"->\s+(https?://[^\s\\']+)", ret1)
                if match:
                    url = match.group(1).rstrip("\\n'")
                    with open(SmartClone.CLONED_JOBS_LOG, "a") as f:
                        f.write(f"{current_time} : {url}\n")

    def osd_get_jobs_where(self, build, group_id, extra_conditions=''):
        rezult = self.osd_query(f"{JobSQL.SELECT_QUERY} build='{build}' and group_id='{group_id}' {extra_conditions}")
        jobs = []
        for raw_job in rezult:
            sql_job = JobSQL(raw_job)
            rez = self.osd_query(self.FIND_LATEST.format(
                build, group_id, sql_job.name, sql_job.arch, sql_job.flavor))
            if rez[0][0] == sql_job.id:
                jobs.append(sql_job)
        return jobs

    def query(self, query: str, dryrun: bool = False):
        m = re.match(r"(\w+)=(\w+)", query)
        groupid = m.group(2)
        latest_build = self.get_latest_build(groupid)
        if query.startswith("allpc"):
            unique_jobs = self.osd_get_jobs_where(
                latest_build, groupid, " and test = 'publiccloud_download_testrepos'"
            )
            for job in unique_jobs:
                shell_exec(
                    f"{self.cmd} {job.id} {self.params_str}", self.logger, dryrun=dryrun
                )
        else:
            raise AttributeError(
                "Unexpected query %s, excpected : allpc=<groupid>,fixworker=<groupid>"
            )


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-q", "--query")
    group.add_argument("-j", "--jobid")
    parser.add_argument("-f", "--frm", default="openqa.suse.de")
    parser.add_argument("params", help="List of variables passed to openQA", nargs="*", default=[])
    parser.add_argument("-w", "--winst", action="store_true")
    parser.add_argument("-d", "--dryrun", action="store_true")
    parser.add_argument("-b", "--branch")
    parser.add_argument(
        "-s",
        "--skipmaintenance",
        action="store_true",
        help="Add variables causing job to skip maint. updates",
    )
    parser.add_argument("-m", "--masktestissues", action="store_true", help="Cloning job with all *_TEST_ISSUES vars set to empty")
    parser.add_argument("-g", "--github-user", default="asmorodskyi")

    args = parser.parse_args()
    solver = SmartClone(args)
    if args.query:
        solver.query(args.query, args.dryrun)
    elif args.jobid:
        solver.run(args.jobid, args.dryrun)
    else:
        raise AttributeError("Need to specify --jobid or --query")


if __name__ == "__main__":
    main()
