from apscheduler.schedulers.blocking import BlockingScheduler

from common.database import healthcheck
from common.log import log
from reset.job import job


def start_scheduler():
    log('# Starting generic cron service')
    healthcheck(influxdb=False)
    scheduler = BlockingScheduler(timezone="Europe/Vienna")

    schedule_time = 2  # start daily at 02:00
    log('# Adding job, resetting people readings to 0 at', schedule_time)
    scheduler.add_job(job, trigger='cron', hour=schedule_time, minute=0, misfire_grace_time=60)

    log('# Starting scheduler')
    scheduler.start()


if __name__ == '__main__':
    start_scheduler()
