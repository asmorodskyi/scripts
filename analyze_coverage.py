#!/usr/bin/python3.11

import logging
from pc.coverage import Coverage
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger("coverage")


def main():

    all_publiccloud = [
        Coverage([219], "Latest - Azure", "publiccloud_"),
        Coverage([463], "Staging - Azure", "publiccloud_"),
        Coverage([464], "Staging - EC2", "publiccloud_"),
        Coverage([465], "Staging - GCE", "publiccloud_"),
        Coverage([274], "Latest - EC2", "publiccloud_"),
        Coverage([275], "Latest - GCE", "publiccloud_"),
        Coverage([545], "SLEM Latest", "publiccloud_"),
        Coverage([427], "Aggregates", "publiccloud_"),
        Coverage([532], "SLEM Aggregates", "publiccloud_"),
        Coverage([613], "SLEM PI", "publiccloud_"),
        Coverage([430], "Incidents", "publiccloud_"),
    ]

    all_azure = set()
    all_ec2 = set()
    all_gce = set()

    for cov1 in all_publiccloud:
        all_azure.update([k for k in cov1.unique_flavors if "Azure" in k])
        all_ec2.update([k for k in cov1.unique_flavors if "EC2" in k])
        all_gce.update([k for k in cov1.unique_flavors if "GCE" in k])

    logger.info(all_azure)
    logger.info(all_ec2)
    logger.info(all_gce)


if __name__ == "__main__":
    main()
