from apscheduler.schedulers.blocking import BlockingScheduler

from common.database import healthcheck
from common.log import log
from monitor.job import job


def start_scheduler():
    log('# Starting status interpretation service')
    healthcheck()
    scheduler = BlockingScheduler(timezone="Europe/Vienna")
    scheduler.add_job(job, trigger='cron', minute=3, misfire_grace_time=60)
    log('# Starting job, adding diagnosis for all sensors every hour.')
    scheduler.start()


if __name__ == '__main__':
    start_scheduler()
