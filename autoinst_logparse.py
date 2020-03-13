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


def remove_lines(lines, verbose):
    if not verbose:
        skip_regex.append(re.compile(r'.*testapi::wait_serial'))
        skip_regex.append(re.compile(
            r'.*consoles::serial_screen::type_string'))

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


def shrink_wait_serial(lines):
    ws_begin_re = re.compile(r'.*testapi::wait_serial\(')
    ws_end_re = re.compile(r'.*testapi::wait_serial:.*: ok')

    shrinked = []
    bufr = None

    for line in lines:
        if bufr:
            if ws_end_re.match(line['msg']):
                line['msg'] = bufr
                bufr = None
            shrinked.append(line)
        else:
            if ws_begin_re.match(line['msg']):
                bufr = line['msg'][:-1] + ': ok'
            else:
                shrinked.append(line)
    return shrinked


def set_css_class(lines_dict, verbose):
    wait_re = re.compile(r'.*testapi::wait_serial')
    type_string_re = re.compile(r'.*consoles::serial_screen::type_string')
    script_run_re = re.compile(
        r'.*(testapi::script_run|distribution::script_output)')
    starting_re = re.compile(r'.*\|\|\| (starting|finished)')

    for line in lines_dict:
        if 'class' not in line:
            if verbose and wait_re.match(line['msg']):
                line['class'] = 'wC'
            elif verbose and type_string_re.match(line['msg']):
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

    def run(self, jobid, url_base, verbose):
        if jobid == '0':
            with open('/test', 'r') as f:
                str_lines = f.readlines()
                f.close()
        else:
            url_full = '{}/tests/{}/file/autoinst-log.txt'.format(
                url_base, jobid)
            self.logger.info('String with url- {}'.format(url_full))
            raw_log = urllib.request.urlopen(url_full).readlines()
            str_lines = [x.decode('UTF-8') for x in raw_log]
            self.logger.info('%d lines read', len(str_lines))
        filtered = remove_lines(str_lines, verbose)
        self.logger.info('%d after remove_lines', len(filtered))
        lines_dict = generate_dict(filtered)
        self.logger.info('%d after generate_dict', len(lines_dict))
        collapsed = collapse_nochange(lines_dict)
        self.logger.info('%d after collapse_nochange', len(collapsed))
        nodup = remove_duplicates(collapsed)
        self.logger.info('%d after remove_duplicates', len(nodup))
        shrinked = shrink_wait_serial(nodup)
        self.logger.info('%d after shrink_wait_serial', len(shrinked))
        set_css_class(shrinked, verbose)
        self.logger.info('%d after set_css_class', len(shrinked))

        jinjaEnv = jinja2.Environment(
            loader=jinja2.FileSystemLoader(searchpath="/scripts/"))
        autoinst_template = jinjaEnv.get_template("autoinst_log_template.html")
        cool_log = autoinst_template.render(items=shrinked)

        m = re.compile(r'^http(s)?://(.*)').match(url_base)
        resulting_file = '/tmp/{}_{}.html'.format(m.group(2), jobid)
        self.logger.info('Write results into %s', resulting_file)
        with open(resulting_file, 'w') as f:
            f.writelines(cool_log)
            f.close()
        webbrowser.get('firefox').open_new_tab(resulting_file)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--frm', default='https://openqa.suse.de')
    parser.add_argument('--jobid', required=True)
    parser.add_argument('--verbose', action='store_true', default=False)
    args = parser.parse_args()

    runner = LogParse('logparse', log_to_file=False)
    runner.run(args.jobid, args.frm, args.verbose)


if __name__ == "__main__":
    main()
