#!/usr/bin/python3
import re
from decimal import Decimal

skip_regex = [re.compile('.*Download of .* processed:'),
              re.compile('.*Output of rsync:'),
              re.compile('.*Waiting for \d{1,2} attempts'),
              re.compile('.*WARNING: check_asserted_screen took'),
              re.compile(
                  '.*WARNING: There is some problem with your environment'),
              re.compile('.*Migrating (total|remaining) bytes:')]


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


def main():
    lines = []
    with open('/scripts/auto.txt', "r") as f:
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

    with open('/scripts/auto_formated.txt', 'w') as f:
        f.writelines(lines)
        f.close()


if __name__ == "__main__":
    main()
