from sqlalchemy import Column, Integer, String, DateTime, Interval
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import UniqueConstraint
from datetime import datetime, timedelta

Base = declarative_base()


class JobSQL:

    # group_id is queried but not serialized because in most cases we don't need it
    # but we have one case where we do ( openQAHelper.osd_get_latest_failures)
    SELECT_QUERY = 'select id, test, result, state, flavor, arch, build, group_id from jobs where '

    def __init__(self, raw_job):
        self.id = raw_job[0]
        self.name = raw_job[1]
        self.result = raw_job[2]
        self.state = raw_job[3]
        self.flavor = raw_job[4]
        self.arch = raw_job[5]
        self.build = raw_job[6]

    def __str__(self):
        pattern = 'Job(id: {}, name: {}, result: {}, state: {}, flavor: {}, arch: {}, build: {})'
        return pattern.format(self.id, self.name, self.result, self.state, self.flavor, self.arch, self.build)


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
