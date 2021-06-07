from sqlalchemy import Column, Integer, String, Boolean, PickleType, DateTime, Interval
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import UniqueConstraint
from datetime import datetime, timedelta

Base = declarative_base()

class JobSQL:

    SELECT_QUERY = 'select id, test, result, state, flavor from jobs where '

    def __init__(self, raw_job):
        self.id = raw_job[0]
        self.name = raw_job[1]
        self.result = raw_job[2]
        self.state = raw_job[3]
        self.flavor = raw_job[4]

    def __str__(self):
        pattern = 'Job(id: {}, name: {}, result: {}, state: {}, flavor: {})'
        return pattern.format(self.id, self.name, self.result, self.state, self.flavor)

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




