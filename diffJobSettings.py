#!/usr/bin/python3.11

import argparse
import requests

parser = argparse.ArgumentParser()
parser.add_argument('--host')
parser.add_argument('--jobids')
parser.add_argument('--nossl', action='store_true')
args = parser.parse_args()

source_url=''
obvious_differs=("NAME")

ids=args.jobids.split(",")

if args.nossl:
    source_url = 'http://'
else:
    source_url = 'https://'
if args.host:
    source_url += args.host + '/api/v1/jobs/'
else:
    source_url += 'openqa.suse.de/api/v1/jobs/'
print('Result url - ' + source_url)
group_json1 = requests.get(source_url+ids[0]).json()
group_json2 = requests.get(source_url+ids[1]).json()

diff_data = dict()
extra_second = dict()

for key, value in group_json1['job']['settings'].items():
    if key in obvious_differs:
        continue
    if key in group_json2['job']['settings']:
        if value != group_json2['job']['settings'][key]:
            diff_data.update({key:value})
    else:
        diff_data.update({key:value})

for key in group_json2['job']['settings'].keys():
    if key not in group_json1['job']['settings']:
        extra_second.update({key:group_json2['job']['settings'][key]})

print('All extra keys in first job AND diff between first and second ')
print(diff_data)
print('Extra keys in second job')
print(extra_second)
