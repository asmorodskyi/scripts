#!/usr/bin/python2

import subprocess
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--host')
parser.add_argument('--distri')
parser.add_argument('--version')
parser.add_argument('--flavor')
parser.add_argument('--arch')
parser.add_argument('--iso')
parser.add_argument('--build')
parser.add_argument('--test')
parser.add_argument('--alias')
parser.add_argument('--dryrun', action='store_true')
args = parser.parse_args()
allargs = '/usr/bin/openqa-client isos post _NOOBSOLETEBUILD=1 '
if args.host:
    allargs += '--host ' + args.host
else:
    allargs += '--host https://openqa.suse.de'
if args.distri:
    distri = args.distri
else:
    distri = 'SLE'
if args.version:
    version = args.version
else:
    version = '15'
if args.flavor:
    flavor = args.flavor
else:
    flavor = 'Installer-DVD'
if args.arch:
    arch = args.arch
else:
    arch = 'x86_64'
if args.build:
    build = args.build
else:
    build = '489.1'
if args.iso:
    iso = args.iso
else:
    iso = '{0}-{1}-{2}-{3}-Build{4}-Media1.iso'.format(
        distri, version, flavor, arch, build)

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
                            'pdsh_genders': 'hpc_pdsh_genders_master,hpc_pdsh_genders_slave,hpc_pdsh_genders_supportserver'}
    testsuites = []
    testsuites = args.alias.split(',')
    result_string = ''
    for item in testsuites:
        if item in available_testsuites.keys():
            result_string += available_testsuites.get(item) + ','
    if result_string:
        allargs += ' TEST=' + result_string[:-1]


allargs += ' BUILD={0} DISTRI={1} VERSION={2} FLAVOR={3} ARCH={4} ISO={5}'.format(
    build, distri, version, flavor, arch, iso)


print 'Command to execute: \n' + allargs
answer = ""
while answer not in ["y", "n"]:
    answer = raw_input("Execute [Y/N]? ").lower()
if answer == 'n':
    sys.exit()
if not args.dryrun:
    print subprocess.check_output(allargs, shell=True)
