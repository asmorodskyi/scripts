#!/usr/bin/python3
import fcntl
import json
import re
import sys
import time
import urllib3
import jinja2
import argparse

import pika

from myutils import openQAHelper, is_matched
from models import JobSQL

global notifier

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def msg_cb(ch, method, properties, body):
    topic = method.routing_key
    global notifier
    try:
        body = body.decode("UTF-8")
        msg = json.loads(body)
        if is_matched(notifier.rules_compiled, topic, msg):
            notifier.logger.info("{}: {}".format(topic, msg))
            notifier.handle_job_done(msg['group_id'])
    except ValueError:
        notifier.logger.warn("Invalid msg: {} -> {}".format(topic, body))


class openQANotify(openQAHelper):

    def __init__(self):
        super(openQANotify, self).__init__("openqanotify", False, load_cache=True)
        self.rules_compiled = []
        self.binding_key = "suse.openqa.job.done"
        rules_defined = [(self.binding_key, lambda t, m: m.get('group_id', "") in self.my_osd_groups)]
        self.amqp_server = "amqps://suse:suse@rabbit.suse.de"
        pid_file = '/tmp/suse_notify.lock'
        self.fp = open(pid_file, 'w')
        try:
            fcntl.lockf(self.fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            sys.exit(0)
        jinjaEnv = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath="/scripts/"))
        self.notify_template_html = jinjaEnv.get_template("notify_template.html")
        self.notify_template_txt = jinjaEnv.get_template("notify_template.txt")
        self.latest_report_template_html = jinjaEnv.get_template("latest_report_template.html")
        self.latest_report_template_txt = jinjaEnv.get_template("latest_report_template.txt")
        for rule in rules_defined:
            self.rules_compiled.append(
                (re.compile(rule[0].replace('.', '\.').replace('*', '[^.]*').replace('#', '.*')), rule[1]))

    def run(self):
        while True:
            try:
                self.logger.info("Connecting to {}".format(self.amqp_server))
                connection = pika.BlockingConnection(pika.URLParameters(self.amqp_server))
                channel = connection.channel()
                channel.exchange_declare(exchange="pubsub", exchange_type='topic', passive=True)
                result = channel.queue_declare('', exclusive=True)
                queue_name = result.method.queue
                channel.queue_bind(exchange="pubsub", queue=queue_name, routing_key=self.binding_key)
                channel.basic_consume(queue=queue_name, on_message_callback=msg_cb, auto_ack=True)
                self.logger.info("Connected")
                channel.start_consuming()
            except Exception:
                self.handle_error()
                if 'channel' in locals():
                    channel.stop_consuming()
                time.sleep(5)

    def generate_report(self, jobs, group_id, build):
        group_name = self.get_group_name(group_id)
        txt_report = self.notify_template_txt.render(items=jobs, build=build, group=group_name)
        html_report = self.notify_template_html.render(
            items=jobs, build=build, group=group_name, baseurl=self.OPENQA_URL_BASE + "t")
        self.send_mail('[Openqa-Notify] New build in {}'.format(group_name), txt_report,
                       html_report, self.config.get(str(group_id), 'to_list', fallback=None))

    def generate_latest_report(self, jobs, hours_depth):
        txt_report = self.latest_report_template_txt.render(items=jobs)
        html_report = self.latest_report_template_html.render(items=jobs, baseurl=self.OPENQA_URL_BASE + "t")
        self.send_mail('[Openqa-Notify] Failures within latest {} hours'.format(hours_depth), txt_report,
                       html_report, self.config.get('DEFAULT', 'to_list', fallback=None))

    def status(self):
        jobs = self.osd_get_latest_failures(3, ','.join([str(i) for i in notifier.my_osd_groups]))
        self.generate_latest_report(jobs, 3)

    def handle_job_done(self, groupid):
        latest_build = self.get_latest_build(groupid)
        rezult = self.osd_query(
            "select count(*) from jobs where group_id='{}' and build='{}' and state not in ('done','cancelled')".
            format(groupid, latest_build))
        if rezult[0][0] > 0:
            self.logger.info("Some jobs are still not done in {} group for {} build".format(
                self.get_group_name(groupid), latest_build))
        else:
            jobs = self.osd_get_jobs_where(latest_build, groupid)
            for job in jobs:
                if job.result == 'failed':
                    bugrefs = self.get_bugrefs(job.id)
                    formated_bugrefs = []
                    for bug in bugrefs:
                        rez = re.search('(poo|bsc)\#(\d+)', bug)
                        if rez.group(1) == 'poo':
                            formated_bugrefs.append(
                                {'href': 'https://progress.opensuse.org/issues/{}'.format(rez.group(2)), 'name': bug})
                        elif rez.group(1) == 'bsc':
                            formated_bugrefs.append(
                                {'href': 'https://bugzilla.suse.com/show_bug.cgi?id={}'.format(rez.group(2)), 'name': bug})
                        else:
                            formated_bugrefs.append({'href': '', 'name': bug})
                    if len(formated_bugrefs):
                        job.bugrefs = formated_bugrefs
                    else:
                        job.bugrefs = ''
                    failed_modules_rez = self.osd_query(
                        "select name from job_modules where job_id={} and result='failed'".format(job.id))
                    job.failed_modules = ''
                    for mod_name in failed_modules_rez:
                        job.failed_modules = "{},{}".format(mod_name[0], job.failed_modules)
                else:
                    job.bugrefs = ''
            self.generate_report(jobs, groupid, latest_build)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--generate_report', action='store_true')
    parser.add_argument('--status', action='store_true')
    args = parser.parse_args()
    global notifier
    notifier = openQANotify()
    if args.generate_report:
        if args.status:
            notifier.status()
        else:
            for group in notifier.my_osd_groups:
                notifier.handle_job_done(group)
    else:
        notifier.run()


if __name__ == "__main__":
    main()
