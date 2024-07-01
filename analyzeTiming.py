#!/usr/bin/python3.11
import re
from datetime import datetime
import urllib.request
import argparse
import random
import string

all_functiontime = []


class FunctionTime:
    def __init__(self, name, starttime_string):
        self.name = name
        self.starttime = datetime.strptime(starttime_string, '%H:%M:%S')

    def set_endtime(self, endtime_str):
        self.endtime = datetime.strptime(endtime_str, '%H:%M:%S')

    def get_duration(self):
        duration = self.endtime - self.starttime
        return duration.total_seconds()


def get_function_pos_by_name(name):
    for i in range(len(all_functiontime)):
        if all_functiontime[i].name == name:
            return i
    print("Expected function - {} was not found ".format(name))
    exit(42)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--jobid', required=True)
    args = parser.parse_args()
    local_file = '/tmp/' + random.choice(string.ascii_lowercase)
    urllib.request.urlretrieve(
        'https://openqa.suse.de/tests/{}/file/autoinst-log.txt'.format(args.jobid), local_file)
    f = open(local_file, "r")
    all_lines = f.readlines()
    current_test = ''
    for line in all_lines:
        rez = re.search(
            '\[\d{4}-\d{2}-\d{2}T(\d{2}:\d{2}:\d{2}).*\|\|\| [finished|starting]* ([\w]*)', line)
        if rez is not None:
            if current_test == rez.group(2):
                all_functiontime[get_function_pos_by_name(
                    rez.group(2))].set_endtime(rez.group(1))
            else:
                current_test = rez.group(2)
                all_functiontime.append(
                    FunctionTime(current_test, rez.group(1)))
    all_functiontime.sort(key=lambda x: x.get_duration())
    overall_pure_time = 0
    for i in range(len(all_functiontime)):
        overall_pure_time += all_functiontime[i].get_duration()
        print('test - {0} , took - {1}'.format(all_functiontime[i].name, all_functiontime[i].get_duration()))
    print('overall time {} minutes'.format(overall_pure_time / 60))


if __name__ == "__main__":
    main()
