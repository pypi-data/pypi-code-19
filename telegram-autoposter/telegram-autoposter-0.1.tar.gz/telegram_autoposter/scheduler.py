from telegram.ext import JobQueue, Job


class Scheduler(object):
    def __init__(self, job_queue: JobQueue):
        self.job_queue = job_queue
        self.jobs = []

    def add_job(self, callback, interval):
        job: Job = self.job_queue.run_repeating(callback=lambda bot, _job: callback(),
                                                first=0, interval=interval)
        self.jobs.append(job)

    def stop(self):
        for job in self.jobs:
            job.schedule_removal()
        self.jobs = []
