#!/usr/bin/env python3

import os
import logging
from pathlib import Path
from osctiny import Osc
from osctiny.extensions.packages import Package
import configparser
from specfile.specfile import Specfile
from specfile.macros import Macros; Macros.dump()

logger = logging.getLogger("osc")
logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)


class Updater:

    def __init__(self, project: str, package: str) -> None:
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
        self.osc_package = Package(self.osc)
        self.package_path = f"{home_dir}/obs_updater/{self.package}"

    def create_package_branch(self):
        self.osc_package.cmd(self.project, self.package, "branch")

    def checkout_package(self):
        Path(self.package_path).mkdir()
        self.osc_package.checkout(self.project, self.package, self.package_path)

    def get_new_version(self):
        PYTHON_MODULE_MACRO = ('%python_module', 'python3-')

        # 2. Add the tuple to a list for the 'macros' parameter
        MACRO_TUPLES = [PYTHON_MODULE_MACRO]
        specfile = Specfile(f"{self.package_path}/{self.package}.spec", macros=MACRO_TUPLES, force_parse=True)
        logger.info(specfile.URL)


def main():
    updater = Updater("openSUSE:Factory", "python-BTrees")
    #updater.create_package_branch()
    #updater.checkout_package()
    updater.get_new_version()


if __name__ == "__main__":
    main()
