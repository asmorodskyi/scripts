#!/usr/bin/python3.11

import os
import urllib.request
from myutils import TaskHelper


class SmartRSync(TaskHelper):

    def run(self, filetype, filename):
        try:
            full_path = '/var/lib/openqa/factory/{0}/{1}'.format(
                filetype, filename)
            self.logger.info("#### START Looking for file - %s", full_path)
            if os.path.isfile(full_path):
                self.logger.info('File found')
            else:
                target_url = 'https://openqa.suse.de/assets/{0}/{1}'.format(filetype, filename)
                self.logger.info(
                    'File not found. Will try to download it from %s', target_url)
                try:
                    # checking if asset already there
                    urllib.request.urlopen(target_url)
                except urllib.error.HTTPError as e:
                    if e.code == 404:
                        # in case not just write down warning
                        self.logger.warn(
                            'Not %s available at source yet', filename)
                    else:
                        # in case any other HTTP errors ( 5xx , 4xx but not 404 raising further)
                        raise e
                else:
                    # in case no exceptions happened during urlopen trying to download
                    urllib.request.urlretrieve(target_url, full_path)
        except Exception:
            self.handle_error()
        finally:
            self.logger.info("#### Done processing file %s", filename)


def main():
    solver = SmartRSync('smartrsync')
    latest_build = solver.get_latest_build()
    sle_version = '15-SP2'
    solver.run(
        'hdd', 'SLES-{0}-x86_64-Build{1}-wicked.qcow2'.format(sle_version, latest_build))
    solver.run(
        'iso', 'SLE-{0}-Online-x86_64-Build{1}-Media1.iso'.format(sle_version, latest_build))


if __name__ == "__main__":
    main()
