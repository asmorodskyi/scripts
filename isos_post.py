#!/usr/bin/python3

import subprocess
import argparse
import sys
import requests
import json


def get_job_name(host, job_id):
    cmd = '/usr/bin/openqa-client --json-output --host {} jobs/{}'.format(host, job_id)
    print('getting job name : {} \n'.format(cmd))
    o_json = json.loads(subprocess.check_output(cmd, shell=True))
    return o_json['job']['name']


parser = argparse.ArgumentParser()
parser.add_argument('--host', default='https://openqa.suse.de')
parser.add_argument('--distri', default='SLE')
parser.add_argument('--version', default='12-SP5')
parser.add_argument('--flavor', default='Server-DVD')
parser.add_argument('--arch', default='x86_64')
parser.add_argument('--iso')
parser.add_argument('--noiso', action='store_true')
parser.add_argument('--build')
parser.add_argument('--test')
parser.add_argument('--alias')
parser.add_argument('--params')
parser.add_argument('--nostartafter', action='store_true')
parser.add_argument('--branch')
parser.add_argument('--github-user', default='asmorodskyi')
parser.add_argument('--force', action='store_true')
args = parser.parse_args()
allargs = '/usr/bin/openqa-client --json-output isos post _NOOBSOLETEBUILD=1 '
allargs += '--host ' + args.host
distri = args.distri
version = args.version
flavor = args.flavor
arch = args.arch

if args.build:
    build = args.build
else:
    group_json = requests.get(
        "https://openqa.suse.de/group_overview/170.json").json()
    build = group_json['build_results'][0]['build']

if args.iso:
    iso = args.iso
else:
    build_label = "Build"
    if "openqa.opensuse.org" in allargs:
        build_label = "Snapshot"
    iso = '{0}-{1}-{2}-{3}-{5}{4}-Media1.iso'.format(
        distri, version, flavor, arch, build, build_label)

if args.test:
    if args.alias:
        sys.exit("You can't use test and alias at the same time")
    allargs += ' TEST=' + args.test

if args.alias:
    available_testsuites = {'mrsh': 'hpc_mrsh_master,hpc_mrsh_slave,hpc_mrsh_supportserver',
                            'munge': 'hpc_munge_master,hpc_munge_slave,hpc_munge_supportserver',
                            'pdsh': 'hpc_pdsh_master,hpc_pdsh_slave,hpc_pdsh_supportserver',
                            'slurm': 'hpc_slurm_master,hpc_slurm_slave,hpc_slurm_supportserver',
                            'ganglia': 'hpc_ganglia_server,hpc_ganglia_client,hpc_ganglia_supportserver',
                            'pdsh_genders': 'hpc_pdsh_genders_master,hpc_pdsh_genders_slave,hpc_pdsh_genders_supportserver',
                            'network': 'wicked_advanced_ref,wicked_advanced_sut,wicked_basic_sut,wicked_basic_ref,wicked_startandstop_ref,wicked_startandstop_sut',
                            'wicked_advanced': 'wicked_advanced_ref,wicked_advanced_sut',
                            'wicked_2nics': 'wicked_2nics_ref,wicked_2nics_sut',
                            'wicked_basic': 'wicked_basic_ref,wicked_basic_sut',
                            'wicked_startandstop': 'wicked_startandstop_ref,wicked_startandstop_sut',
                            'wicked_aggregate': 'wicked_aggregate_ref,wicked_aggregate_sut'}
    if (args.alias == 'list'):
        print('Aliases:')
        for key, value in available_testsuites.items():
            print("  {:20s} => {}".format(key, value))
        sys.exit(0);

    testsuites = []
    testsuites = args.alias.split(',')
    result_string = ''
    for item in testsuites:
        if item in available_testsuites.keys():
            result_string += available_testsuites.get(item) + ','
    if result_string:
        allargs += ' TEST=' + result_string[:-1]

if args.params:
    allargs += ' ' + args.params

allargs += ' BUILD={0} DISTRI={1} VERSION={2} FLAVOR={3} ARCH={4}'.format(
    build, distri, version, flavor, arch)
if "openqa.opensuse.org" not in allargs:
    allargs += ' BUILD_SLE={0}'.format(build)
if not args.noiso:
    allargs += ' ISO={0}'.format(iso)

if args.nostartafter:
    allargs += ' START_AFTER_TEST=\' \''

if args.branch:
    allargs += ' CASEDIR=https://github.com/{0}/os-autoinst-distri-opensuse.git#{1}'.format(args.github_user, args.branch)

print('Command to execute: \n' + allargs)
if not args.force:
    answer = ""
    while answer not in ["y", "n"]:
        answer = input("Execute [Y/N]? ").lower()
    if answer == 'n':
        sys.exit()
o_json = json.loads(subprocess.check_output(allargs, shell=True))

print(o_json)

if len(o_json['failed']) > 0:
    print("Failed Jobs:")
    for job in o_json['failed']:
        print("  %s/t%d - Name:%s MSG:%s" % (args.host, job['job_id'], get_job_name(args.host, job['job_id']), job['error_messages']))

if len(o_json['ids']) > 0:
    print("Jobs:")
    for job_id in o_json['ids']:
        print("  %s/t%d - Name:%s" % (args.host, job_id, get_job_name(args.host, job_id)))
