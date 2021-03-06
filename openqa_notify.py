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
from models import JobORM

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
        for gr_id in self.my_osd_groups:
            self.refresh_cache(gr_id)
        jinjaEnv = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath="/scripts/"))
        self.notify_template_html = jinjaEnv.get_template("notify_template.html")
        self.notify_template_txt = jinjaEnv.get_template("notify_template.txt")
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

    def generate_report(self, jobs):
        group_name = self.config.get(str(jobs[0].groupid), 'name', fallback=jobs[0].groupid)
        pc = bool(jobs[0].instance_type != 'N/A')
        build = jobs[0].build
        txt_report = self.notify_template_txt.render(items=jobs, build=build, group=group_name, pc=pc)
        html_report = self.notify_template_html.render(
            items=jobs, build=build, group=group_name, baseurl=self.OPENQA_URL_BASE + "t", pc=pc)
        self.send_mail('[Openqa-Notify] New build in {}'.format(group_name), txt_report,
                       html_report, self.config.get(str(jobs[0].groupid), 'to_list', fallback=None))

    def handle_job_done(self, groupid):
        self.refresh_cache(groupid)
        latest_build = self.get_latest_build(groupid)
        if self.job_query.filter(JobORM.build == latest_build).filter(JobORM.groupid == groupid).\
           filter(JobORM.needs_update.is_(True)).count():
            self.logger.info("Some jobs are still not done in {} group for {} build".format(
                self.config.get(str(groupid), 'name', fallback=groupid), latest_build))
            return
        jobs = self.job_query.filter(JobORM.build == latest_build).filter(JobORM.groupid == groupid).all()
        for job in jobs:
            if job.result == 'failed':
                job.bugrefs = self.get_bugrefs(job.id)
                formated_bugrefs = []
                for bug in job.bugrefs:
                    rez = re.search('(poo|bsc)\#(\d+)', bug)
                    if rez.group(1) == 'poo':
                        formated_bugrefs.append(
                            {'href': 'https://progress.opensuse.org/issues/{}'.format(rez.group(2)), 'name': bug})
                    elif rez.group(1) == 'bsc':
                        formated_bugrefs.append(
                            {'href': 'https://bugzilla.suse.com/show_bug.cgi?id={}'.format(rez.group(2)), 'name': bug})
                    else:
                        formated_bugrefs.append({'href': '', 'name': bug})
                job.bugrefs = formated_bugrefs
            else:
                job.bugrefs = ''
        self.generate_report(jobs)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--generate_report', action='store_true')
    args = parser.parse_args()
    global notifier
    notifier = openQANotify()
    if args.generate_report:
        for group in notifier.my_osd_groups:
            notifier.handle_job_done(group)
    else:
        notifier.run()


if __name__ == "__main__":
    main()
