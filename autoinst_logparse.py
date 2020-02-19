#!/usr/bin/python3
import re
from decimal import Decimal
import jinja2
from myutils import TaskHelper
import argparse
import urllib.request

skip_regex = [re.compile(r'.*Download of .* processed:'),
              re.compile(r'.*Output of rsync:'),
              re.compile(r'.*Waiting for \d{1,2} attempts'),
              re.compile(r'.*WARNING: check_asserted_screen took'),
              re.compile(
                  r'.*WARNING: There is some problem with your environment'),
              re.compile(r'.*Migrating (total|remaining) bytes:'),
              re.compile(r'.*pointer type \d'),
              re.compile(r'.*consoles::serial_screen::read_until'),
              re.compile(r'.*testapi::type_string')]


def remove_lines(lines):
    def need_to_keep(str):
        for regex in skip_regex:
            if regex.match(str):
                return False
        return True
    last_skiped = False
    filtered_lines = []
    next_line_re = re.compile(
        r'\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3,4} CET\].*')

    for line in lines:
        if need_to_keep(line):
            if last_skiped and next_line_re.match(line):
                last_skiped = False
            if not last_skiped:
                filtered_lines.append(line)
        else:
            last_skiped = True
    return filtered_lines


def collapse_nochange(lines_dict):
    nochange_re = re.compile(r'no (change|match): (\d{1,3}\.\d)s')
    nochange_dict = {}
    collapsed_dict = []

    for line in lines_dict:
        matched = nochange_re.match(line['msg'])
        if matched:
            if nochange_dict:
                nochange_dict['end'] = matched.group(2)
            else:
                nochange_dict['time'] = line['time']
                nochange_dict['start'] = matched.group(2)
        else:
            if nochange_dict:
                delta = 0
                if nochange_dict.get('end'):
                    delta = Decimal(
                        nochange_dict.get('start')) - Decimal(nochange_dict.get('end'))
                else:
                    delta = 1
                collapsed_dict.append({'time': nochange_dict.get(
                    'time'), 'msg': 'no match during {}s\n'.format(delta)})
                nochange_dict = {}
            collapsed_dict.append(line)
    return collapsed_dict


def remove_duplicates(lines_dict):
    caller_re = re.compile(r'(.*\/tests\/.*\.pm:\d{1,4} called.*)')
    already_matched = set()
    i = 0

    while i < len(lines_dict):
        if 'time' not in lines_dict[i]:
            lines_dict[i-1]['msg'] = '{}<br/>{}'.format(
                lines_dict[i-1]['msg'], lines_dict[i]['msg'])
            del lines_dict[i]
        else:
            matched = caller_re.match(lines_dict[i]['msg'])
            if matched:
                if matched.group(1) in already_matched:
                    del lines_dict[i]
                else:
                    already_matched.add(matched.group(1))
                    lines_dict[i]['class'] = 'cC'
                    i += 1
            else:
                i += 1


def shrink_wait_serial(lines_dict):
    ws_begin_re = re.compile(r'.*testapi::wait_serial\(')
    ws_end_re = re.compile(r'.*testapi::wait_serial:.*: ok')

    i = 0
    ws_begin = False

    while i < len(lines_dict):
        if ws_begin:
            if ws_end_re.match(lines_dict[i]['msg']):
                del lines_dict[i]
                lines_dict[i-1]['msg'] = lines_dict[i-1]['msg'][:-1] + ': ok'
                ws_begin = False
            else:
                i += 1
        else:
            ws_begin = ws_begin_re.match(lines_dict[i]['msg'])
            i += 1


def apply_attributes(lines_dict):
    wait_re = re.compile(r'.*testapi::wait_serial')
    type_string_re = re.compile(r'.*consoles::serial_screen::type_string')
    script_run_re = re.compile(
        r'.*(testapi::script_run|distribution::script_output)')
    starting_re = re.compile(r'.*\|\|\| (starting|finished)')

    for line in lines_dict:
        if wait_re.match(line['msg']):
            line['class'] = 'wC'
        elif type_string_re.match(line['msg']):
            line['class'] = 'tyC'
        elif script_run_re.match(line['msg']):
            line['class'] = 'rC'
        elif starting_re.match(line['msg']):
            line['class'] = 'sC'
        elif 'class' not in line:
            line['class'] = 'mC'


def generate_dict(lines):
    lines_dict = []
    log_line_re = re.compile(
        r'\[\d{4}-\d{2}-\d{2}T(\d{2}:\d{2}:\d{2}\.\d{3,4}) CET\] \[(debug|info|warn|error)\] (>>>|<<<|:::)?(\[pid:\d{1,5}\])?(.*)')
    for line in lines:
        matched = log_line_re.match(line)
        if matched:
            lines_dict.append(
                {'time': matched.group(1), 'msg': matched.group(5)})
        else:
            lines_dict.append({'msg': line})
    return lines_dict


class LogParse(TaskHelper):

    def run(self, jobid):
        bytes_lines = urllib.request.urlopen(
            'https://openqa.suse.de/tests/{}/file/autoinst-log.txt'.format(jobid)).readlines()
        lines = [x.decode('UTF-8') for x in bytes_lines]
        filtered_lines = remove_lines(lines)
        lines_dict = generate_dict(filtered_lines)
        collapse_nochange(lines_dict)
        remove_duplicates(lines_dict)
        shrink_wait_serial(lines_dict)
        apply_attributes(lines_dict)

        templateEnv = jinja2.Environment(
            loader=jinja2.FileSystemLoader(searchpath="./"))
        template = templateEnv.get_template("template.html")
        outputText = template.render(items=lines_dict)

        with open('/auto.html', 'w') as f:
            f.writelines(outputText)
            f.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--frm', default='openqa.suse.de')
    parser.add_argument('--jobid', required=True)
    args = parser.parse_args()

    runner = LogParse('logparse', log_to_file=False)
    runner.run(args.jobid)


if __name__ == "__main__":
    main()
