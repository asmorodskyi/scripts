#!/usr/bin/python3

import subprocess
from subprocess import CalledProcessError
from myutils import TaskHelper
import argparse


class SmartClone(TaskHelper):

    def solve(self, params_dict):
        try:
            parser = argparse.ArgumentParser()
            parser.add_argument('--frm', default='openqa.suse.de')
            parser.add_argument('--params')
            parser.add_argument('--tolocal', action='store_true')
            parser.add_argument('--jobid', required=True)
            parser.add_argument('--branch')
            parser.add_argument('--github-user', default='asmorodskyi')

            args = parser.parse_args()
            cmd = '/usr/share/openqa/script/clone_job.pl --skip-chained-deps --from {}'.format(
                args.frm)
            if args.sameinst:
                cmd += ' --within-instance'
            cmd += ' {}'.format(args.jobid)
            if args.params:
                cmd += args.params.replace(',', ' ')
            if args.branch:
                cmd += ' CASEDIR=https://github.com/{0}/os-autoinst-distri-opensuse.git#{1}'.format(
                    args.github_user, args.branch)
            self.logger.info(cmd)
            self.logger.info(subprocess.check_output(cmd, shell=True))
        except subprocess.CalledProcessError:
            self.handle_error('Clone died')
        except Exception:
            self.handle_error()


def main():
    solver = SmartClone('smartclone')
    solver.run({})


if __name__ == "__main__":
    main()
