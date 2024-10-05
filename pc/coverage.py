
import logging
import re

from typing import Self
from myutils import openQAHelper
import yaml

logger = logging.getLogger("coverage")

class openQATest:

    def __init__(self, version, flavor, test, arch):
        self.version = version
        if '-Updates' in flavor:
            self.flavor = flavor.removesuffix('-Updates')
        else:
            self.flavor = flavor
        self.test = ''.join(test.keys()).split('publiccloud_',1)[1]
        self.arch = arch


class Coverage(openQAHelper):

 
    def extract_openqatests(self, group_id: int) -> list[openQATest]:
        yaml_content = self.osd_get(f"api/v1/job_groups/{group_id}")[0]['template']
        contents = yaml.safe_load(yaml_content)
        openqatests = []

        for arch in contents['scenarios'].keys():
            for flavor in contents['scenarios'][arch].keys():
                flavor_match_group = re.search(r'sle-(\d{2}-SP\d)-([\w\-]+)-(aarch64|x86_64|s390x)', flavor)
                if flavor_match_group is None:
                    raise Exception(f"{flavor} does not match regex")
                for test in contents['scenarios'][arch][flavor]:
                    openqatests.append(openQATest(flavor_match_group[1],flavor_match_group[2],test,flavor_match_group[3]))
                    
        logger.debug(f"{len(openqatests)} openQATest object generated for job group {group_id}")

        return openqatests

    def __init__(self, group_ids: list[int], name: str) -> None:
        super(Coverage, self).__init__(name, load_cache=False)
        logger.info(f"Create coverage for openQA job groups {group_ids}")
        self.all_tests = list()
        for group_id in group_ids:
            self.all_tests.extend(self.extract_openqatests(group_id))
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


    def compare_flavors(self, other_coverage: Self):
        logger.error(f"Flavors not in {self.name} : {other_coverage.unique_flavors.difference(self.unique_flavors)}")
        logger.error(f"Flavors not in {other_coverage.name} : {self.unique_flavors.difference(other_coverage.unique_flavors)}")

    def compare_tests(self, other_coverage: Self):
        logger.error(f"Tests not in {self.name} : {other_coverage.unique_tests.difference(self.unique_tests)}")
        logger.error(f"Tests not in {other_coverage.name} : {self.unique_tests.difference(other_coverage.unique_tests)}")

    def flavors_by_tests(self, other_coverage: Self):
        logger.error(f"Output flavors which covering test in {self.name} and {other_coverage.name}")
        all_unique_tests = self.unique_tests.union(other_coverage.unique_tests)
        same_flavors = self.unique_flavors.intersection(other_coverage.unique_flavors)
        no_common_flavors = set()
        for test in all_unique_tests:
            flavors_for_test = set()
            for flavor in same_flavors:
                if self.exists_in(flavor, test) and other_coverage.exists_in(flavor, test):
                    flavors_for_test.add(flavor)
            if len(flavors_for_test) > 0:
                logger.error(f"{test} : {flavors_for_test}")
            else:
                no_common_flavors.add(test)
        logger.error(f"Tests which does not have common flavors in {self.name} and {other_coverage.name}\n {no_common_flavors}")