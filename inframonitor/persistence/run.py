from apscheduler.schedulers.blocking import BlockingScheduler

from common.database import healthcheck
from common.log import log
from persistence.job import job

if __name__ == '__main__':
    log('# Starting mongo/influx connector')
    healthcheck()
    scheduler = BlockingScheduler(timezone="Europe/Vienna")
    log('# Adding job, pulling updates every 15 minutes.')
    scheduler.add_job(job, trigger='cron', minute="1,16,31,46", misfire_grace_time=60)
    log('# Starting scheduler')
    scheduler.start()
