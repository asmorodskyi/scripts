#!/usr/bin/python3.11

from pc.coverage import Coverage
import urllib3 

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main():

    latest_coverage = Coverage([219,274,275], "Latest")

    aggregates_coverage = Coverage([427], "Aggregates")

    latest_coverage.compare_flavors(aggregates_coverage)
    latest_coverage.compare_tests(aggregates_coverage)
    latest_coverage.flavors_by_tests(aggregates_coverage)


if __name__ == "__main__":
    main()