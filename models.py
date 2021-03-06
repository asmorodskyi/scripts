from sqlalchemy import Column, Integer, String, Boolean, PickleType, DateTime, Interval
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import UniqueConstraint
from datetime import datetime, timedelta

Base = declarative_base()


class JobORM(Base):
    __tablename__ = "job"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    instance_type = Column(String)
    result = Column(String)
    state = Column(String)
    build = Column(String)
    flavor = Column(String)
    hdd = Column(String)
    groupid = Column(String)
    needs_update = Column(Boolean)
    failed_modules = Column(String)

    def update_from_json(self, openqa_json):
        self.id = openqa_json['job']['id']
        self.name = openqa_json['job']['settings']['TEST']
        if 'PUBLIC_CLOUD_INSTANCE_TYPE' in openqa_json['job']['settings']:
            self.instance_type = openqa_json['job']['settings']['PUBLIC_CLOUD_INSTANCE_TYPE']
        else:
            self.instance_type = 'N/A'
        self.result = openqa_json['job']['result']
        self.state = openqa_json['job']['state']
        self.build = openqa_json['job']['settings']['BUILD']
        self.flavor = openqa_json['job']['settings']['FLAVOR']
        if 'HDD_1' in openqa_json['job']['settings']:
            self.hdd = openqa_json['job']['settings']['HDD_1']
        else:
            self.hdd = 'N/A'
        self.failed_modules = ""
        self.groupid = openqa_json['job']['group_id']
        self.needs_update = bool(self.state not in ['done', 'cancelled'])
        for module in openqa_json['job']['testresults']:
            if module['result'] == 'failed':
                if self.failed_modules:
                    self.failed_modules = "{},{}".format(self.failed_modules, module['name'])
                else:
                    self.failed_modules = module['name']

    def __str__(self):
        pattern = 'Job(id: {}, name: {}, instance_type: {}, result: {}, state: {}, build: {}, flavor: {},' \
                  ' failed_modules: {})'
        return pattern.format(self.id, self.name, self.instance_type, self.result, self.state, self.build, self.flavor,
                              self.failed_modules)


class MessageLatency(Base):

    __tablename__ = "msglatency"

    def __init__(self, topic, subject):
        self.topic = topic
        self.subject = subject
        self.cnt = 1
        self.locked_till = datetime.now()
        self.time_delta = timedelta(hours=1)

    id = Column(Integer, primary_key=True)
    topic = Column(String)
    subject = Column(String)
    cnt = Column(Integer)
    locked_till = Column(DateTime)
    time_delta = Column(Interval)
    UniqueConstraint('topic', 'subject')

    def __str__(self):
        return 'MessageLatency(id: {}, topic: {}, subject: {}, cnt: {},time_delta: {}, locked_till: {})'.format(
            self.id, self.topic, self.subject, self.cnt, self.time_delta, self.locked_till)

    def inc_cnt(self):
        self.cnt = self.cnt + 1

    def lock(self):
        self.locked_till = self.locked_till + self.time_delta




