#!/usr/bin/python3

from urllib.request import urlopen, urlretrieve
from bs4 import BeautifulSoup
import re

url = "https://download.suse.de/ibs/Devel:/PubCloud:/Stable:/CrossCloud:/SLE15-SP3:/ModifiedTestImages/images/"

with urlopen(url) as response:
    soup = BeautifulSoup(response.read(), 'html.parser')
    for a in soup.findAll('a', href=True):
        m = re.match(r"\.\/(SLES15-SP3-Lasso-BYOS.x86_64-[\d\.]+-EC2-HVM-Build1.22.raw.xz)$", a['href'])
        if m:
            full_url = "{}{}".format(url, m.group(1))
            print("Will download {} \n".format(full_url))
            urlretrieve(full_url, m.group(1))
