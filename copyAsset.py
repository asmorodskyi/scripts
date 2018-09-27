#!/usr/bin/python

import subprocess
import argparse
import sys
import urllib.request
import ssl

parser = argparse.ArgumentParser()
parser.add_argument('--host')
parser.add_argument('--file')
parser.add_argument('--nossl', action='store_true')
args = parser.parse_args()

source_url=''
asset_type=''
target_path='/var/lib/openqa/factory/'

if args.nossl:
    source_url = 'http://'
else:
    source_url = 'https://'
if args.host:
    source_url += args.host + '/assets/'
else:
    source_url += 'openqa.suse.de/assets/'
if args.file[-3:] == 'iso':
    asset_type='iso/'
    source_url += asset_type + args.file
elif args.file[-5:] == 'qcow2':
    asset_type='hdd/'
    source_url += asset_type + args.file
else:
    print('Unsupported image type , exiting')
    sys.exit()
ssl._create_default_https_context = ssl._create_unverified_context
urllib.request.urlretrieve (source_url, target_path+asset_type+args.file)