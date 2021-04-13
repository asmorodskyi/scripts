#!/usr/bin/python3

from myutils import openQAHelper
import argparse


class SmartClone(openQAHelper):

    def __init__(self, args):
        super(SmartClone, self).__init__('SmartClone', False, load_cache=args.loadcache)
        self.cmd = '/usr/share/openqa/script/clone_job.pl --skip-chained-deps --parental-inheritance'
        self.params_str = ''
        if args.params:
            self.params_str = ' {}'.format(args.params.replace(',', ' '))
        if args.resetworker:
            self.params_str += ' WORKER_CLASS=qemu_x86_64 '
        if args.branch:
            self.params_str += ' CASEDIR=https://github.com/{0}/os-autoinst-distri-opensuse.git#{1}'.format(
                args.github_user, args.branch)
        if args.winst:
            self.cmd += ' --within-instance {}'.format(args.frm)
        else:
            self.cmd += ' --from {}'.format(args.frm)

    def run(self, jobid):
        try:
            ids = jobid.split(',')
            for one_id in ids:
                self.shell_exec('{} {} {}'.format(
                    self.cmd, one_id, self.params_str), log=True)
        except Exception:
            self.handle_error()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--frm', default='openqa.suse.de')
    parser.add_argument('--params')
    parser.add_argument('--winst', action='store_true')
    parser.add_argument('--jobid', required=True)
    parser.add_argument('--branch')
    parser.add_argument('--resetworker', action='store_true')
    parser.add_argument('--loadcache', action='store_true', default=False)
    parser.add_argument('--github-user', default='asmorodskyi')
    args = parser.parse_args()
    solver = SmartClone(args)
    solver.run(args.jobid)


if __name__ == "__main__":
    main()
