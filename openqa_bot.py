#!/usr/bin/python3.11

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
        super(openQABot, self).__init__('openqabot', load_cache=False)
        self.rules_compiled = []
        if for_o3:
            self.OPENQA_URL_BASE = 'https://openqa.opensuse.org'
            self.binding_key = "opensuse.openqa.job.done"
            rules_defined = [
                (
                    self.binding_key,
                    lambda t, m: m.get('result', "") == "failed" and m.get('TEST').startswith("wicked_"))]
            self.amqp_server = "amqps://opensuse:opensuse@rabbit.opensuse.org"
            pid_file = '/tmp/suse_msg_o3.lock'
        else:
            self.binding_key = "suse.openqa.job.done"
            rules_defined = [
                (self.binding_key,
                 lambda t, m: m.get('result', "") == "failed" and m.get('group_id', "") in self.my_osd_groups)]
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
        subj_text += "{}-{}-{}".format(msg['TEST'], msg['ARCH'], self.get_group_name(msg['group_id']))
        job_url = '{}t{}'.format(self.OPENQA_URL_BASE, msg['id'])
        hdd = 'None'
        if 'HDD_1' in msg:
            hdd = msg['HDD_1']
        message = f'''
        Build={msg['BUILD']}
        Flavor={msg['FLAVOR']}
        Disk={hdd}
        JobID={job_url}
    '''
        super().send_mail(f'[Openqa-Notify] {subj_text}', message)

    def run(self):
        while True:
            try:
                self.logger.info(f"Connecting to {self.amqp_server}")
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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--o3', action='store_true')
    args = parser.parse_args()
    global bot
    bot = openQABot(args.o3)
    bot.run()


if __name__ == "__main__":
    main()
