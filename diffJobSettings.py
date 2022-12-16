#!/usr/bin/python3

import subprocess
import argparse
import sys
import requests
import json

parser = argparse.ArgumentParser(description='openqa test data:display the  differences of Settings betwen 2 given tests IDs Or display the full data set of a single test ID')
parser.add_argument('--host', default='openqa.suse.de',help='default openqa.suse.de')
parser.add_argument('--jobids','-j', help='jobid1[,jobid2] # Enter 1[Full data] or 2[Differences] IDs')
parser.add_argument('--nossl','-n', action='store_true', help='http urls; default https')
parser.add_argument('--comments','-c', action='store_true', help='print job comments too')
args = parser.parse_args()

source_url=''

if not (args.jobids):
    parser.print_help()
    exit(1) 

ids=args.jobids.split(",")

if args.nossl:
    source_url = 'http://'
else:
    source_url = 'https://'

# default OSD in parser
source_url += args.host + '/api/v1/jobs/'
# Parameter list, to skip from diff.check
obvious_differs=()

print(f'Result url:{source_url} - jobids:{ids}')

if len(ids) < 1:
    exit(1)
else:
    group_json1   = requests.get(source_url+ids[0]).json()
    if args.comments:
        group_json1_c = requests.get(source_url+ids[0]+'/comments').json()

if len(ids) == 1:
    print('\n',json.dumps(group_json1,indent=2))
    if args.comments:
        print('\n',json.dumps(group_json1_c,indent=2))
else:
    group_json2   = requests.get(source_url+ids[1]).json()
    if args.comments:
        group_json2_c = requests.get(source_url+ids[1]+'/comments').json()

    diff_data1 = dict()
    diff_data2 = dict()
    common_data = dict()
    extra_first = dict()
    extra_second = dict()

    for key, value in group_json1['job']['settings'].items():
        if key in obvious_differs:
            continue
 
        # JOB 1+2 COMMON KEYS
        if key in group_json2['job']['settings']:
            value2 = group_json2['job']['settings'][key]
            if value != value2: 
                # SAME KEY DIFFERENT VALUES
                diff_data1.update({key:value})
                diff_data2.update({key:value2})
            else: 
                # SAME KEY SAME VALUE
                common_data.update({key:value})

    # job 1 only KEYS
    for key in group_json1['job']['settings'].keys():
        if key not in group_json2['job']['settings']:
            value=group_json1['job']['settings'][key]
            extra_first.update({key:value})

    # job 2 only KEYS
    for key in group_json2['job']['settings'].keys():
        if key not in group_json1['job']['settings']:
            value=group_json2['job']['settings'][key]
            extra_second.update({key:value})

    # Results:

    # All common key\val
    print(f'\n*** All common keys & values ')
    print(ids,json.dumps(common_data,indent=2))

    # Common keys, different values
    # job 1
    print(f'\n*** Common keys, different values:')
    print(ids[0],json.dumps(diff_data1,indent=2))
    # job 2
    #print(f'*** JOB:{ids[1]} - Common keys, different values')
    print(ids[1],json.dumps(diff_data2,indent=2))

    # Different Keys 
    # job 1
    print(f'\n*** Extra keys:')
    print(ids[0],json.dumps(extra_first,indent=2))

    # job 2
    #print(f'*** JOB {ids[1]} - Extra keys')
    print(ids[1],json.dumps(extra_second,indent=2))

    # Comments
    if args.comments:
        print(f'\n*** Comments:')
        print(ids[0], json.dumps(group_json1_c,indent=2))
        print(ids[1], json.dumps(group_json2_c,indent=2))
