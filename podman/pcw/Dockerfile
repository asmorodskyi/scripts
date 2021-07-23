FROM python:3.8
RUN apt-get update; \
     apt-get install -y git
RUN cd /; \
    git clone https://github.com/SUSE/pcw.git
WORKDIR /pcw
RUN pip install -r requirements_test.txt
