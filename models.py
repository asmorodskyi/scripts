from sqlalchemy import Column, Integer, String, Boolean, PickleType, DateTime, Interval, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import UniqueConstraint
from datetime import datetime, timedelta

Base = declarative_base()

class JobSQL:

    SELECT_QUERY = 'select id, test, result, state, flavor, arch from jobs where '

    def __init__(self, raw_job):
        self.id = raw_job[0]
        self.name = raw_job[1]
        self.result = raw_job[2]
        self.state = raw_job[3]
        self.flavor = raw_job[4]
        self.arch = raw_job[5]

    def __str__(self):
        pattern = 'Job(id: {}, name: {}, result: {}, state: {}, flavor: {}, arch: {})'
        return pattern.format(self.id, self.name, self.result, self.state, self.flavor, self.arch)

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


class ReviewCache(Base):

    __tablename__ = "reviewcache"

    def __init__(self, job_name, failed_modules, job_result, errors_text):
        self.job_name = job_name
        self.failed_modules = failed_modules
        self.job_result = job_result
        self.errors_text = errors_text

    id = Column(Integer, primary_key=True)
    job_name = Column(String)
    failed_modules = Column(String)
    job_result = Column(String)
    errors_text = Column(Text)

    def __str__(self):
        return 'ReviewCache(job_name: {}, job_result: {}, failed_modules: {})'\
               .format(self.job_name, self.job_result, self.failed_modules)

class KnownIssues(Base):

    __tablename__ = "knownissues"

    def __init__(self, job_name, job_result, errors_text, failed_modules, label):
        self.job_name = job_name
        self.failed_modules = failed_modules
        self.label = label
        self.job_result = job_result
        self.errors_text = errors_text

    id = Column(Integer, primary_key=True)
    job_name = Column(String)
    failed_modules = Column(String)
    job_result = Column(String)
    errors_text = Column(Text)
    label = Column(String)

    def errors_text_match(self, errors_text):
        # KnownIssues.errors_text is string build from list with ',' delimeter
        # KnownIssues.errors_text suppose to contain only generic parts of errors
        for known_issue_error in self.errors_text.split(','):
            match_found = False
            # with each error from KnownIssues we will loop over errors of certain job
            for error in errors_text:
                if known_issue_error in error:
                    match_found = True
                    break
            if not match_found:
                # if we failed to found match at least for one error from KnownIssues we consider that they do NOT match
                return False
        return True






