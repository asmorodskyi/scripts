#!/usr/bin/env python3

import os
import re
import argparse
import logging
import urllib.request
from urllib.parse import urlparse
import ssl
from pathlib import Path
from osctiny import Osc
from osctiny.extensions.packages import Package
import configparser
import subprocess

logger = logging.getLogger("osc")
logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)


class Updater:

    HOME_PROJECT = "home:asmorodskyi:branches:devel:languages:python"

    def __init__(self, project: str, package: str, new_version: str) -> None:
        logger.info(f"init OSC object for {project}-{package}")
        config = configparser.ConfigParser()
        home_dir = os.getenv("HOME")
        config.read(f"{home_dir}/.config/osc/oscrc")
        self.api_url = "https://api.opensuse.org"
        self.osc = Osc(
            url=self.api_url,
            username=config[self.api_url]["user"],
            password=config[self.api_url]["pass"],
        )
        self.project = project
        self.package = package
        self.new_version = new_version
        self.osc_package = Package(self.osc)
        self.package_path = f"{home_dir}/obs_updater/{self.package}"
        self.specfile = f"{self.package_path}/{self.package}.spec"

    def create_package_branch(self):
        logger.info("## Step 1 ##: Branch package in OBS")
        self.osc_package.cmd(self.project, self.package, "branch")

    def checkout_package(self):
        logger.info("## Step 2 ##: Checkout branched package")
        Path(self.package_path).mkdir()
        self.osc_package.checkout(Updater.HOME_PROJECT, self.package, self.package_path)

    def _get_spec_file_content(self):
        with open(self.specfile, 'r') as file:
            return file.read()

    def _get_from_spec(self, regex):
        pattern = re.compile(regex, re.MULTILINE)
        match = pattern.search(self._get_spec_file_content())
        if match:
            return match.group(1).strip()
        raise ValueError(f"{regex} was not found")

    def get_new_version(self):
        logger.info("## Step 3 ##: Download new version and delete old one")
        old_version = self._get_from_spec(r"^\s*Version:\s*(.*)")
        source_url = self._get_from_spec(r"^\s*Source:\s*(.*)")
        new_source_url = source_url.replace('%{version}', self.new_version)
        logger.info("Downloading new package from %s", new_source_url)
        parsed_new_source = urlparse(new_source_url)
        new_filename = os.path.basename(parsed_new_source.path)
        ssl._create_default_https_context = ssl._create_unverified_context
        urllib.request.urlretrieve (new_source_url, f"{self.package_path}/{new_filename}")
        old_filename = new_filename.replace(self.new_version, old_version)
        logger.info("Deleting old version of the package %s", new_filename.replace(self.new_version, old_version))
        self._execute_cmd(f"osc rm {old_filename}")

    def tweak_specfile(self):
        logger.info("## Step 4 ##: Tweak specfile")
        updated_content = re.sub(r'(Version:\s+)(\S+)', rf'\g<1>{self.new_version}', self._get_spec_file_content())
        with open(self.specfile, 'w') as f:
            f.write(updated_content)

    def _execute_cmd(self, cmd):
        logger.info(f"Executing {cmd}")
        output = subprocess.check_output(cmd, shell=True, cwd=self.package_path)
        output_str = output.decode('utf-8')
        logger.info(output_str)
        return output_str

    def commit(self):
        logger.info("## Step 5 ## - add/commit changed files")
        output_str = self._execute_cmd("osc status")
        changed_files = [
            line.split(maxsplit=1)[1]
            for line in output_str.splitlines()
            if line.strip() and not line.startswith('D')
        ]
        for file in changed_files:
            self._execute_cmd(f"osc add {file}")




def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--package", help="Name of the package to update", required=True)
    parser.add_argument("-n", "--new_version", help="Desired package version to update", required=True)
    parser.add_argument("-s", "--step", help=""" what steps needs to be executed.\n
        currently available steps\n
        1 - create package branch\n
        2 - checkout package\n
        3 - get new version
        4 - tweak version in specfile
        5 - add/commit changed files
        6 - MANUAL STEP - 'osc ci' ( because requires inserting commit message)
        NOTE: selecting previous steps automatically means execution of following steps
        """, default=1)
    args = parser.parse_args()
    updater = Updater("openSUSE:Factory", args.package, args.new_version)
    step = int(args.step)
    if step == 1:
        updater.create_package_branch()
    if step <= 2:
        updater.checkout_package()
    if step <= 3:
        updater.get_new_version()
    if step <= 4:
        updater.tweak_specfile()
    if step <= 5:
        updater.commit()


if __name__ == "__main__":
    main()
