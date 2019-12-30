#!/usr/bin/python3

import subprocess
from subprocess import CalledProcessError
import argparse
import logging

cmd = '/usr/share/openqa/script/clone_job.pl --skip-chained-deps --{0} {1} {2} {3}'

parser = argparse.ArgumentParser()
parser.add_argument('--frm', default='openqa.suse.de')
parser.add_argument('--params')
parser.add_argument('--tolocal', action='store_true')
parser.add_argument('--jobid', required=True)
parser.add_argument('--branch')
parser.add_argument('--github-user', default='asmorodskyi')

args = parser.parse_args()

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

params = ''
if args.params:
    params = args.params.replace(',', ' ')

first_param = 'within-instance'
if args.tolocal:
    first_param = 'from'

cmd = cmd.format(first_param, args.frm, args.jobid, params)

if args.branch:
    cmd += ' CASEDIR=https://github.com/{0}/os-autoinst-distri-opensuse.git#{1}'.format(
        args.github_user, args.branch)

logger.info(cmd)

logger.info(subprocess.check_output(cmd, shell=True))
