#!/usr/bin/python3
import re
from sys import argv
from decimal import Decimal

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


def collapse_nochange(lines):
    nochange_re = re.compile(
        '\[(\d{2}:\d{2}:\d{2}\.\d{3,4})\] no (change|match): (\d{1,3}\.\d)s')
    nochange_dict = {}
    i = 0

    while i < len(lines):
        matched = nochange_re.match(lines[i])
        if matched:
            if nochange_dict:
                nochange_dict['end'] = matched.group(3)
            else:
                nochange_dict['time'] = matched.group(1)
                nochange_dict['start'] = matched.group(3)
            del lines[i]
        else:
            if nochange_dict:
                delta = 0
                if nochange_dict.get('end'):
                    delta = Decimal(
                        nochange_dict.get('start')) - Decimal(nochange_dict.get('end'))
                else:
                    delta = 1
                lines.insert(
                    i, '[{}] no match during {}s\n'.format(nochange_dict.get('time'), delta))
                nochange_dict = {}
            i += 1


def remove_duplicates(lines):
    caller_re = re.compile(
        '\[\d{2}:\d{2}:\d{2}\.\d{3,4}\] (.*\/tests\/.*\.pm:\d{1,4} called.*)')
    already_matched = set()
    i = 0

    while i < len(lines):
        matched = caller_re.match(lines[i])
        if matched:
            if matched.group(1) in already_matched:
                del lines[i]
            else:
                already_matched.add(matched.group(1))
                i += 1
        else:
            i += 1


def shrink_wait_serial(lines):
    ws_begin_re = re.compile('.*testapi::wait_serial\(')
    ws_end_re = re.compile('.*testapi::wait_serial:.*: ok')

    i = 0
    ws_begin = False

    while i < len(lines):
        if ws_begin:
            if ws_end_re.match(lines[i]):
                del lines[i]
                tmp = lines[i-1][:-1] + ': ok\n'
                del lines[i-1]
                lines.insert(i-1, tmp)
                ws_begin = False
            else:
                i += 1
        else:
            ws_begin = ws_begin_re.match(lines[i])
            i += 1


def main():
    lines = []
    if len(argv) != 2:
            print("Missing source file")
            exit(1)
    with open(argv[1], "r") as f:
        lines = f.readlines()
        f.close()

    remove_lines(lines)

    log_line_re = re.compile(
        "\[\d{4}-\d{2}-\d{2}T(\d{2}:\d{2}:\d{2}\.\d{3,4}) CET\] \[(debug|info|warn|error)\] (\[pid:\d{1,5}\])?(.*)")
    for i in range(len(lines)):
        matched = log_line_re.match(lines[i])
        if matched:
            lines[i] = '[{}] {}\n'.format(matched.group(1), matched.group(4))

    collapse_nochange(lines)
    remove_duplicates(lines)
    shrink_wait_serial(lines)

    with open('/auto_formated.txt', 'w') as f:
        f.writelines(lines)
        f.close()


if __name__ == "__main__":
    main()
