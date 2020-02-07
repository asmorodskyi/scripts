#!/usr/bin/python3

from myutils import TaskHelper
import argparse


class SmartClone(TaskHelper):

    def run(self):
        try:
            parser = argparse.ArgumentParser()
            parser.add_argument('--frm', default='openqa.suse.de')
            parser.add_argument('--params')
            parser.add_argument('--winst', action='store_true')
            parser.add_argument('--jobid', required=True)
            parser.add_argument('--branch')
            parser.add_argument('--github-user', default='asmorodskyi')
            args = parser.parse_args()
            cmd = '/usr/share/openqa/script/clone_job.pl --skip-chained-deps '
            if args.winst:
                cmd += ' --within-instance {}'.format(args.frm)
            else:
                cmd += ' --from {}'.format(args.frm)
            cmd += ' {}'.format(args.jobid)
            if args.params:
                cmd += ' {}'.format(args.params.replace(',', ' '))
            if args.branch:
                cmd += ' CASEDIR=https://github.com/{0}/os-autoinst-distri-opensuse.git#{1}'.format(
                    args.github_user, args.branch)
            self.shell_exec(cmd, log=True)
        except Exception:
            self.handle_error()


def main():
    solver = SmartClone('smartclone')
    solver.run()


if __name__ == "__main__":
    main()
