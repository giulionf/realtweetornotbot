from enum import Enum


class Job:

    class JobType(Enum):
        POST = 1,
        COMMENT = 2

    def __init__(self, job_type, instance):
        self.job_type = job_type
        self.instance = instance

    def get_post(self):
        if self.job_type == self.JobType.POST:
            return self.instance
        elif self.job_type == self.JobType.COMMENT:
            return self.instance.submission
        return None
