#!/usr/bin/python3

import argparse
import sys
import time
import fcntl

import pika
import json
import re

from myutils import openQAHelper, is_matched

global bot


def msg_cb(ch, method, properties, body):
    topic = method.routing_key
    global bot
    try:
        body = body.decode("UTF-8")
        msg = json.loads(body)
        if is_matched(bot.rules_compiled, topic, msg):
            bot.logger.info("{}: {}".format(topic, msg))
            bot.send_email(topic, msg)
    except ValueError:
        bot.logger.warn("Invalid msg: {} -> {}".format(topic, body))


class openQABot(openQAHelper):

    def __init__(self, for_o3):
        super(openQABot, self).__init__('openqabot', for_o3, log_to_file=True)
        self.rules_compiled = []
        if self.for_o3:
            self.binding_key = "opensuse.openqa.job.done"
            rules_defined = [
                (
                    self.binding_key,
                    lambda t, m: m.get('result', "") == "failed" and m.get('TEST').startswith("wicked_"))]
            self.amqp_server = "amqps://opensuse:opensuse@rabbit.opensuse.org"
            pid_file = '/tmp/suse_msg_o3.lock'
        else:
            my_osd_groups = [262, 219, 274, 275, 276]
            self.binding_key = "suse.openqa.job.done"
            rules_defined = [
                (self.binding_key,
                 lambda t, m: m.get('result', "") == "failed" and m.get('group_id', "") in my_osd_groups)]
            self.amqp_server = "amqps://suse:suse@rabbit.suse.de"
            pid_file = '/tmp/suse_msg_osd.lock'
        self.fp = open(pid_file, 'w')
        try:
            self.logger.info("Check if another instance is running ....")
            fcntl.lockf(self.fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            sys.exit(0)
        for rule in rules_defined:
            self.rules_compiled.append(
                (re.compile(rule[0].replace('.', '\.').replace('*', '[^.]*').replace('#', '.*')), rule[1]))

    def send_email(self, topic, msg):
        if self.for_o3:
            subj_text = 'openSUSE.ORG - '
        else:
            subj_text = 'SUSE.DE - '
        subj_text += "{}-{}-{}".format(msg['TEST'], msg['ARCH'], self.groupID_to_name(msg['group_id']))
        job_url = '{}t{}'.format(self.OPENQA_URL_BASE, msg['id'])
        hdd = 'None'
        if 'HDD_1' in msg:
            hdd = msg['HDD_1']
        message = '''  
        Build={build}
        Flavor={flavor}
        Disk={disk}
        JobID={jobURL}
    '''.format(build=msg['BUILD'], flavor=msg['FLAVOR'], disk=hdd, jobURL=job_url)
        super().send_mail('[Openqa-Notify] {}'.format(subj_text), message,
                          'asmorodskyi@suse.com, cfamullaconrad@suse.de')

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
            except Exception as e:
                self.handle_error()
                if 'channel' in locals():
                    channel.stop_consuming()
                time.sleep(5)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--o3', action='store_true')
    args = parser.parse_args()
    global bot
    bot = openQABot(args.o3)
    bot.run()


if __name__ == "__main__":
    main()
