from apscheduler.schedulers.blocking import BlockingScheduler

from common.database import healthcheck
from common.log import log
from httpagent.job import job


def start_scheduler():
    log('# Starting HTTP Agent')
    healthcheck(influxdb=False)
    scheduler = BlockingScheduler(timezone="Europe/Vienna")

    log('# Adding job, polling HTTP API every hour')
    scheduler.add_job(job, trigger='cron', minute=15, misfire_grace_time=60)

    log('# Starting scheduler')
    scheduler.start()


if __name__ == '__main__':
    start_scheduler()
