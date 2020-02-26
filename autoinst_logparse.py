#!/usr/bin/python3
import re
from decimal import Decimal
import jinja2
from myutils import TaskHelper
import argparse
import urllib.request
import webbrowser

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
    filtered = []
    next_line_re = re.compile(
        r'\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3,4} (CET|UTC)\].*')

    for line in lines:
        if need_to_keep(line):
            if last_skiped and next_line_re.match(line):
                last_skiped = False
            if not last_skiped:
                filtered.append(line)
        else:
            last_skiped = True
    return filtered


def collapse_nochange(lines):
    nochange_re = re.compile(r'no (change|match): (\d{1,3}\.\d)s')
    summary = {}
    collapsed = []

    for line in lines:
        m = nochange_re.match(line['msg'])
        if m:
            if summary:
                summary['end'] = m.group(2)
            else:
                summary['time'] = line['time']
                summary['start'] = m.group(2)
        else:
            if summary:
                delta = 0
                if summary.get('end'):
                    delta = Decimal(
                        summary.get('start')) - Decimal(summary.get('end'))
                else:
                    delta = 1
                collapsed.append({'time': summary.get(
                    'time'), 'msg': 'no match during {}s\n'.format(delta)})
                summary = {}
            collapsed.append(line)
    return collapsed


def remove_duplicates(lines):
    with_time = []
    bufr = None
    for line in lines:
        if 'time' in line:
            if bufr:
                with_time.append(bufr)
            bufr = line
        else:
            bufr['msg'] = '{}<br/>{}'.format(bufr['msg'], line['msg'])
    with_time.append(bufr)
    caller_re = re.compile(r'((tests|lib)\/.*\.pm:\d{1,4} called.*)')
    already_matched = set()
    nodup = []
    for line in with_time:
        m = caller_re.match(line['msg'])
        if m:
            if m.group(1) not in already_matched:
                already_matched.add(m.group(1))
                line['class'] = 'cC'
                nodup.append(line)
        else:
            nodup.append(line)
    return nodup


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


def set_css_class(lines_dict):
    wait_re = re.compile(r'.*testapi::wait_serial')
    type_string_re = re.compile(r'.*consoles::serial_screen::type_string')
    script_run_re = re.compile(
        r'.*(testapi::script_run|distribution::script_output)')
    starting_re = re.compile(r'.*\|\|\| (starting|finished)')

    for line in lines_dict:
        if 'class' not in line:
            if wait_re.match(line['msg']):
                line['class'] = 'wC'
            elif type_string_re.match(line['msg']):
                line['class'] = 'tyC'
            elif script_run_re.match(line['msg']):
                line['class'] = 'rC'
            elif starting_re.match(line['msg']):
                line['class'] = 'sC'
            else:
                line['class'] = 'mC'


def generate_dict(lines):
    lines_dict = []
    log_line_re = re.compile(
        r'\[\d{4}-\d{2}-\d{2}T(\d{2}:\d{2}:\d{2}\.\d{3,4}) (CET|UTC)\] \[(debug|info|warn|error)\] (>>>|<<<|:::)?(\[pid:\d{1,5}\])?(.*)')
    for line in lines:
        m = log_line_re.match(line)
        if m:
            lines_dict.append(
                {'time': m.group(1), 'msg': m.group(6)})
        else:
            lines_dict.append({'msg': line})
    return lines_dict


class LogParse(TaskHelper):

    def run(self, jobid, url_base):
        if jobid == '0':
            with open('/test', 'r') as f:
                str_lines = f.readlines()
                f.close()
        else:
            raw_log = urllib.request.urlopen(
                '{}/tests/{}/file/autoinst-log.txt'.format(url_base, jobid)).readlines()
            str_lines = [x.decode('UTF-8') for x in raw_log]
        filtered = remove_lines(str_lines)
        lines_dict = generate_dict(filtered)
        collapsed = collapse_nochange(lines_dict)
        nodup = remove_duplicates(collapsed)
        shrink_wait_serial(nodup)
        set_css_class(nodup)

        jinjaEnv = jinja2.Environment(
            loader=jinja2.FileSystemLoader(searchpath="./"))
        autoinst_template = jinjaEnv.get_template("autoinst_log_template.html")
        cool_log = autoinst_template.render(items=nodup)

        m = re.compile(r'http(s)://(.*)').match(url_base)
        resulting_file = '/tmp/{}_{}.html'.format(m.group(2), jobid)
        with open(resulting_file, 'w') as f:
            f.writelines(cool_log)
            f.close()
        webbrowser.get('firefox').open_new_tab(resulting_file)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--frm', default='https://openqa.suse.de')
    parser.add_argument('--jobid', required=True)
    args = parser.parse_args()

    runner = LogParse('logparse', log_to_file=False)
    runner.run(args.jobid, args.frm)


if __name__ == "__main__":
    main()
