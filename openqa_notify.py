#!/usr/bin/python3
import argparse

from myutils import openQAHelper


class openQANotify(openQAHelper):

    def __init__(self, for_o3):
        super(openQANotify, self).__init__("openqanotify", for_o3, log_to_file=True)

    def run(self):
        pass



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--o3', action='store_true')
    args = parser.parse_args()
    notifier = openQANotify(args.o3)
    notifier.run()


if __name__ == "__main__":
    main()
