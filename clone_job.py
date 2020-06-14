#!/usr/bin/python3

from myutils import TaskHelper
import argparse


class SmartClone(TaskHelper):

    def generate_params_string(self, params, reset_worker, branch, github_user):
        self.params_str = ''
        if params:
            self.params_str = ' {}'.format(params.replace(',', ' '))
        if reset_worker:
            self.params_str += ' WORKER_CLASS=qemu_x86_64 '
        if branch:
            self.params_str += ' CASEDIR=https://github.com/{0}/os-autoinst-distri-opensuse.git#{1}'.format(
                github_user, branch)

    def run(self):
        try:
            parser = argparse.ArgumentParser()
            parser.add_argument('--frm', default='openqa.suse.de')
            parser.add_argument('--params')
            parser.add_argument('--winst', action='store_true')
            parser.add_argument('--jobid', required=True)
            parser.add_argument('--branch')
            parser.add_argument('--resetworker', action='store_true')
            parser.add_argument('--github-user', default='asmorodskyi')
            args = parser.parse_args()
            self.generate_params_string()
            cmd = '/usr/share/openqa/script/clone_job.pl --skip-chained-deps --parental-inheritance'
            if args.winst:
                cmd += ' --within-instance {}'.format(args.frm)
            else:
                cmd += ' --from {}'.format(args.frm)
            ids = args.jobid.split(',')
            for one_id in ids:
                self.shell_exec('{} {} {}'.format(
                    cmd, one_id, self.params_str), log=True)
        except Exception:
            self.handle_error()


def main():
    solver = SmartClone('smartclone')
    solver.run()


if __name__ == "__main__":
    main()
