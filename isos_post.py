#!/usr/bin/python3

import argparse
import sys
import json
from myutils import TaskHelper


class IsosPost(TaskHelper):

    available_testsuites = {'network': 'wicked_advanced_ref,wicked_advanced_sut,wicked_basic_sut,wicked_basic_ref,wicked_startandstop_ref,wicked_startandstop_sut,wicked_ipv6_ref,wicked_ipv6_sut',
                            'advanced': 'wicked_advanced_ref,wicked_advanced_sut',
                            '2nics': 'wicked_2nics_ref,wicked_2nics_sut',
                            'basic': 'wicked_basic_ref,wicked_basic_sut',
                            'startandstop': 'wicked_startandstop_ref,wicked_startandstop_sut',
                            'aggregate': 'wicked_aggregate_ref,wicked_aggregate_sut',
                            'ipv6': 'wicked_ipv6_ref,wicked_ipv6_sut'}

    def get_job_name(self, host, job_id):
        cmd = self.OPENQA_EXE + ' --host {} jobs/{}'.format(host, job_id)
        return self.shell_exec(cmd, is_json=True)['job']['name']

    def set_job_priority(self, host, job_id, priority):
        cmd = 'openqa-client --host {} jobs/{} put --json-data \'{{"priority": {} }}\''.format(
            host, job_id, priority)
        self.logger.info('setting job priority : %s', cmd)
        self.shell_exec(cmd)

    def build_exec_string(self, args):
        exec_str = "{} isos post --host {} ".format(self.OPENQA_EXE, args.host)
        if args.test:
            if args.alias:
                sys.exit("You can't use test and alias at the same time")
            exec_str += ' TEST=' + args.test

        if args.alias:
            tests_list = ''
            for item in args.alias.split(','):
                if item in self.available_testsuites.keys():
                    tests_list += self.available_testsuites.get(item) + ','
            if tests_list:
                exec_str += ' TEST=' + tests_list[:-1]

        if args.build:
            build = args.build
        else:
            build = self.get_latest_build()

        exec_str += ' BUILD={0} DISTRI={1} VERSION={2} FLAVOR={3} ARCH={4}'.format(
            build, args.distri, args.version, args.flavor, args.arch)

        if "openqa.opensuse.org" not in exec_str:
            exec_str += ' BUILD_SLE={0}'.format(build)

        if not args.noiso:
            if args.iso:
                exec_str += ' ISO={0}'.format(args.iso)
            else:
                build_label = "Build"
                if "openqa.opensuse.org" in args.host:
                    build_label = "Snapshot"
                exec_str += ' ISO={0}-{1}-{2}-{3}-{5}{4}-Media1.iso '.format(
                    args.distri, args.version, args.flavor, args.arch, build, build_label)

        if args.nostartafter:
            exec_str += ' START_AFTER_TEST=\' \''

        if args.branch:
            exec_str += ' CASEDIR=https://github.com/{0}/os-autoinst-distri-opensuse.git#{1}'.format(
                args.github_user, args.branch)

        if args.params:
            exec_str += ' ' + args.params.replace(',', ' ')
        return exec_str

    def run(self, params_dict):
        try:
            parser = argparse.ArgumentParser()
            parser.add_argument('--host', default=self.OPENQA_URL_BASE)
            parser.add_argument('--distri', default='SLE')
            parser.add_argument('--version', default='15-SP2')
            parser.add_argument('--flavor', default='Online')
            parser.add_argument('--arch', default='x86_64')
            parser.add_argument('--iso')
            parser.add_argument('--noiso', action='store_true')
            parser.add_argument('--build')
            parser.add_argument('--test')
            parser.add_argument('--alias', help=",".join(("{}={}".format(*i)
                                                          for i in self.available_testsuites.items())))
            parser.add_argument('--debug', action='store_true')
            parser.add_argument('--params')
            parser.add_argument('--nostartafter', action='store_true')
            parser.add_argument('--branch')
            parser.add_argument('--priority', default=None)
            parser.add_argument('--github-user', default='asmorodskyi')
            parser.add_argument('--force', action='store_true')
            args = parser.parse_args()

            cmd = self.build_exec_string(args)
            self.logger.info(cmd)

            if not args.force:
                answer = ""
                while answer not in ["y", "n"]:
                    answer = input("Execute [Y/N]? ").lower()
                if answer == 'n':
                    sys.exit()

            o_json = self.shell_exec(cmd, log=True, is_json=True)

            if o_json:
                for job in o_json['failed']:
                    self.logger.error("{}/{} - Name:{} MSG:{}".format(
                        args.host, job['job_id'], self.get_job_name(args.host, job['job_id']), job['error_messages']))
                for job_id in o_json['ids']:
                    self.logger.info(
                        "{}/{} - Name:{}".format(args.host, job_id, self.get_job_name(args.host, job_id)))
                    if (args.priority is not None):
                        self.set_job_priority(args.host, job_id, args.priority)
        except Exception:
            self.handle_error()


def main():
    solver = IsosPost('isospost')
    solver.run({})


if __name__ == "__main__":
    main()
