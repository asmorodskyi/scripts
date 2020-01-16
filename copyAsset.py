#!/usr/bin/python3

import argparse
import sys
import urllib.request
import ssl
import requests

def get_asset(source_url,asset_type,asset_name):
    ssl._create_default_https_context = ssl._create_unverified_context
    urllib.request.urlretrieve (source_url + '/assets/'+asset_type + asset_name, '/var/lib/openqa/factory/'+asset_type+asset_name)

parser = argparse.ArgumentParser()
parser.add_argument('--host')
parser.add_argument('--file')
parser.add_argument('--jobid')
parser.add_argument('--nossl', action='store_true')
args = parser.parse_args()

source_url=''
asset_type=''
if args.nossl:
    source_url = 'http://'
else:
    source_url = 'https://'
if args.host:
    source_url += args.host
else:
    source_url += 'openqa.suse.de'
if args.jobid:
    job_json = requests.get( source_url + '/api/v1/jobs/' + args.jobid + '.json').json()
    print("copying " + source_url + '/assets/hdd/' + job_json['job']['assets']['hdd'][0])
    get_asset(source_url,'hdd/',job_json['job']['assets']['hdd'][0])
    print("copying " + source_url + '/assets/iso/' + job_json['job']['assets']['iso'][0])
    get_asset(source_url,'iso/',job_json['job']['assets']['iso'][0])
else:
    if args.file[-3:] == 'iso':
        asset_type='iso/'
    elif args.file[-5:] == 'qcow2':
        asset_type='hdd/'
    else:
        print('Unsupported image type , exiting')
        sys.exit()
    get_asset(source_url,asset_type,args.file)