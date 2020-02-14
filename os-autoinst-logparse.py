#!/usr/bin/python3
import re
from sys import argv
from decimal import Decimal
import jinja2

skip_regex = [re.compile('.*Download of .* processed:'),
              re.compile('.*Output of rsync:'),
              re.compile('.*Waiting for \d{1,2} attempts'),
              re.compile('.*WARNING: check_asserted_screen took'),
              re.compile(
                  '.*WARNING: There is some problem with your environment'),
              re.compile('.*Migrating (total|remaining) bytes:'),
              re.compile('.*pointer type \d'),
              re.compile('.*consoles::serial_screen::read_until'),
              re.compile('.*testapi::type_string')]


def need_to_rm(str):
    for regex in skip_regex:
        if regex.match(str):
            return True
    return False


def remove_lines(lines):
    last_matched = False
    i = 0
    next_line_re = re.compile(
        "\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3,4} CET\].*")

    while i < len(lines):
        if need_to_rm(lines[i]):
            del lines[i]
            last_matched = True
        else:
            if last_matched:
                if next_line_re.match(lines[i]):
                    last_matched = False
                    i += 1
                else:
                    del lines[i]
            else:
                i += 1


def collapse_nochange(lines_dict):
    nochange_re = re.compile('no (change|match): (\d{1,3}\.\d)s')
    nochange_dict = {}
    i = 0

    while i < len(lines_dict):
        matched = nochange_re.match(lines_dict[i]['msg'])
        if matched:
            if nochange_dict:
                nochange_dict['end'] = matched.group(2)
            else:
                nochange_dict['time'] = lines_dict[i]['time']
                nochange_dict['start'] = matched.group(2)
            del lines_dict[i]
        else:
            if nochange_dict:
                delta = 0
                if nochange_dict.get('end'):
                    delta = Decimal(
                        nochange_dict.get('start')) - Decimal(nochange_dict.get('end'))
                else:
                    delta = 1
                lines_dict.insert(i, {'time': nochange_dict.get(
                    'time'), 'msg': 'no match during {}s\n'.format(delta)})
                nochange_dict = {}
            i += 1


def remove_duplicates(lines_dict):
    caller_re = re.compile('(.*\/tests\/.*\.pm:\d{1,4} called.*)')
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
    ws_begin_re = re.compile('.*testapi::wait_serial\(')
    ws_end_re = re.compile('.*testapi::wait_serial:.*: ok')

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
    wait_re = re.compile('.*testapi::wait_serial')
    type_string_re = re.compile('.*consoles::serial_screen::type_string')
    script_run_re = re.compile(
        '.*(testapi::script_run|distribution::script_output)')
    starting_re = re.compile('.*\|\|\| (starting|finished)')

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


def main():
    lines = []
    if len(argv) != 2:
        print("Missing source file")
        exit(1)
    with open(argv[1], "r") as f:
        lines = f.readlines()
        f.close()

    remove_lines(lines)

    lines_dict = []
    log_line_re = re.compile(
        "\[\d{4}-\d{2}-\d{2}T(\d{2}:\d{2}:\d{2}\.\d{3,4}) CET\] \[(debug|info|warn|error)\] (>>>|<<<|:::)?(\[pid:\d{1,5}\])?(.*)")
    for i in range(len(lines)):
        matched = log_line_re.match(lines[i])
        if matched:
            lines_dict.append(
                {'time': matched.group(1), 'msg': matched.group(5)})
        else:
            lines_dict.append({'msg': lines[i]})

    del lines[:]

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


if __name__ == "__main__":
    main()
