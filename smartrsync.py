#!/usr/bin/python3

import os
import urllib.request
from myutils import TaskSolver


class SmartRSync(TaskSolver):

    def solve(self, params_dict):
        try:
            filetype = params_dict['filetype']
            filename = params_dict['filename']
            full_path = '/var/lib/openqa/factory/{0}/{1}'.format(
                filetype, filename)
            self.logger.info("#### START Looking for file - %s", full_path)
            if os.path.isfile(full_path):
                self.logger.info('File found')
            else:
                target_url = '{0}assets/{1}/{2}'.format(self.OPENQA_URL_BASE,
                                                        filetype, filename)
                self.logger.info(
                    'File not found. Will try to download it from %s', target_url)
                if urllib.request.urlopen(target_url).code == 200:
                    urllib.request.urlretrieve(target_url, full_path)
                else:
                    self.logger.warn(
                        'Not %s available at source yet', filename)
        except Exception:
            self.handle_error()
        finally:
            self.logger.info("#### Done processing file %s", filename)


def main():
    solver = SmartRSync('smartrsync')
    latest_build = solver.get_latest_build()
    hdd_dict = {'filetype': 'hdd', 'filename': 'SLES-12-SP5-x86_64-Build{0}-wicked.qcow2'.format(
        latest_build)}
    iso_dict = {'filetype': 'iso', 'filename': 'SLE-12-SP5-Server-DVD-x86_64-Build{0}-Media1.iso'.format(
        latest_build)}
    solver.solve(hdd_dict)
    solver.solve(iso_dict)


if __name__ == "__main__":
    main()
