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

logger = logging.getLogger("osc")
logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)


class Updater:

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

    def create_package_branch(self):
        logger.info("## Step 1 ##: Branch package in OBS")
        self.osc_package.cmd(self.project, self.package, "branch")

    def checkout_package(self):
        logger.info("## Step 2 ##: Checkout branched package")
        Path(self.package_path).mkdir()
        self.osc_package.checkout(self.project, self.package, self.package_path)

    def _get_from_spec(self, regex):
        pattern = re.compile(regex)
        with open(f"{self.package_path}/{self.package}.spec", 'r') as file:
            for line in file:
                match = pattern.match(line)
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
        os.remove(f"{self.package_path}/{old_filename}")




def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--package", help="Name of the package to update", required=True)
    parser.add_argument("-n", "--new_version", help="Desired package version to update", required=True)
    parser.add_argument("-s", "--step", help=""" what steps needs to be executed.\n
        currently available steps\n
        1 - create package branch\n
        2 - checkout package\n
        3 - get new version
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


if __name__ == "__main__":
    main()
