from apscheduler.schedulers.blocking import BlockingScheduler

from common.database import healthcheck
from common.log import log
from prediction.job import job


def start_scheduler():
    log('# Starting prediction service')
    healthcheck()
    scheduler = BlockingScheduler(timezone="Europe/Vienna")
    scheduler.add_job(job, trigger='cron', minute=0, misfire_grace_time=60)
    log('# Starting job, adding predictions every hour.')
    scheduler.start()


if __name__ == '__main__':
    start_scheduler()
