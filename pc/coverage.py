import logging
import re

from typing import Self
from myutils import openQAHelper
import yaml

logger = logging.getLogger("coverage")


class openQATest:

    def __init__(self, version, flavor, test, arch, testname_regex):
        self.version = version
        if "-Updates" in flavor:
            self.flavor = flavor.removesuffix("-Updates")
        else:
            self.flavor = flavor
        self.test = test.split(testname_regex, 1)[1]
        self.arch = arch

    def get_key(self):
        return f"{self.flavor}-{self.version}-{self.arch}"

    def __str__(self):
        return f"|{self.flavor}| {self.version} | {self.test} | {self.arch}"


class Coverage(openQAHelper):

    def extract_openqatests(self, group_id: int, testname_regex) -> list[openQATest]:
        contents = self.jobgroups[group_id]
        cnt = 0

        for arch in contents["scenarios"].keys():
            for flavor in contents["scenarios"][arch].keys():
                flavor_match_group = re.search(
                    r"sle-(\d{2}-SP\d)-([\w\-]+)-(aarch64|x86_64|s390x)", flavor
                )
                if flavor_match_group is None:
                    raise Exception(f"{flavor} does not match regex")
                for test in contents["scenarios"][arch][flavor]:
                    if isinstance(test, dict):
                        testname = "".join(test.keys())
                    else:
                        testname = test
                    if testname_regex in testname:
                        cnt += 1
                        self.all_tests.append(
                            openQATest(
                                flavor_match_group[1],
                                flavor_match_group[2],
                                testname,
                                flavor_match_group[3],
                                testname_regex,
                            )
                        )

        logger.info(f"{cnt} openQATest object generated for job group {group_id}")

    def __init__(self, group_ids: list[int], name: str, testname_regex) -> None:
        super(Coverage, self).__init__(name, load_cache=False)
        logger.info(f"Create coverage for openQA job groups {group_ids}")
        self.jobgroups = {}
        self.all_tests = list()
        for group_id in group_ids:
            yaml_content = self.osd_get(f"api/v1/job_groups/{group_id}")[0]["template"]
            self.jobgroups[group_id] = yaml.safe_load(yaml_content)

        for group_id in group_ids:
            self.extract_openqatests(group_id, testname_regex)

        self.unique_flavors = set()
        self.unique_tests = set()
        for test in self.all_tests:
            self.unique_flavors.add(test.flavor)
            self.unique_tests.add(test.test)
        logger.info(f"{self.name} unique flavors: {self.unique_flavors}")
        logger.info(f"{self.name} unique test names: {self.unique_tests}")

    def exists_in(self, flavor: str, testname: str) -> bool:

        for test in self.all_tests:
            if test.test == testname and test.flavor == flavor:
                return True
        return False

    def self_analyze(self):
        grouped = dict()
        for test in self.all_tests:
            k1 = test.get_key()
            if k1 in grouped.keys():
                grouped[k1] += test.test
            else:
                grouped[k1] = test.test
        for k1, v1 in grouped.items():
            logger.info(f"{k1} - {v1}")

    def compare_flavors(self, other_coverage: Self):
        logger.error(
            f"Flavors not in {self.name} : {other_coverage.unique_flavors.difference(self.unique_flavors)}"
        )
        logger.error(
            f"Flavors not in {other_coverage.name} : {self.unique_flavors.difference(other_coverage.unique_flavors)}"
        )

    def compare_tests(self, other_coverage: Self):
        logger.error(
            f"Tests not in {self.name} : {other_coverage.unique_tests.difference(self.unique_tests)}"
        )
        logger.error(
            f"Tests not in {other_coverage.name} : {self.unique_tests.difference(other_coverage.unique_tests)}"
        )

    def flavors_by_tests(self, other_coverage: Self):
        logger.error(
            f"Output flavors which covering test in {self.name} and {other_coverage.name}"
        )
        all_unique_tests = self.unique_tests.union(other_coverage.unique_tests)
        same_flavors = self.unique_flavors.intersection(other_coverage.unique_flavors)
        no_common_flavors = set()
        for test in all_unique_tests:
            flavors_for_test = set()
            for flavor in same_flavors:
                if self.exists_in(flavor, test) and other_coverage.exists_in(
                    flavor, test
                ):
                    flavors_for_test.add(flavor)
            if len(flavors_for_test) > 0:
                logger.error(f"{test} : {flavors_for_test}")
            else:
                no_common_flavors.add(test)
        logger.error(
            f"Tests which does not have common flavors in {self.name} and {other_coverage.name}\n {no_common_flavors}"
        )
