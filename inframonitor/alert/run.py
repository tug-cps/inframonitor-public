from apscheduler.schedulers.blocking import BlockingScheduler

from alert.job import job
from common.database import healthcheck
from common.log import log


def start_scheduler():
    log('# Starting alert container')
    healthcheck()
    scheduler = BlockingScheduler()
    # start this job hourly at 5 minutes past every hour to give the monitor enough time
    scheduler.add_job(job, trigger='cron', minute=5, misfire_grace_time=60)
    log('# Starting job, pulling updates every hour + 5 minutes.')
    scheduler.start()


if __name__ == '__main__':
    start_scheduler()
