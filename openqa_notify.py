#!/usr/bin/python3
import fcntl
import json
import re
import sys
import time
import urllib3
import jinja2

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
            # notifier.handle_job_done(msg)
    except ValueError:
        notifier.logger.warn("Invalid msg: {} -> {}".format(topic, body))


class openQANotify(openQAHelper):

    def __init__(self):
        super(openQANotify, self).__init__("openqanotify", False, log_to_file=True, load_cache=True)
        self.rules_compiled = []
        self.binding_key = "suse.openqa.job.done"
        rules_defined = [(self.binding_key, lambda t, m: m.get('group_id', "") in self.my_osd_groups)]
        self.amqp_server = "amqps://suse:suse@rabbit.suse.de"
        pid_file = '/tmp/suse_notify.lock'
        self.fp = open(pid_file, 'w')
        try:
            self.logger.info("Check if another instance is running ....")
            fcntl.lockf(self.fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            sys.exit(0)
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

    def generate_report(self, groupid):
        self.refresh_cache(groupid)
        latest_build = self.get_latest_build(groupid)
        jobs = self.job_query.filter(JobORM.build == latest_build).filter(JobORM.groupid == groupid).all()
        jinjaEnv = jinja2.Environment(loader=jinja2.FileSystemLoader(searchpath="/scripts/"))
        notify_template = jinjaEnv.get_template("notify_template.html")
        report = notify_template.render(
            items=jobs, build=jobs[0].build, flavor=jobs[0].flavor, group=jobs[0].groupid)
        with open('/tmp/11111.html', 'w') as f:
            f.writelines(report)
            f.close()

    # def handle_job_done(self, msg):
     #   self.refresh_cache(msg['group_id'])
     #   job = self.get


def main():
    global notifier
    notifier = openQANotify()
    notifier.generate_report(275)
    # notifier.run()


if __name__ == "__main__":
    main()
