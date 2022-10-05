import datetime as dt
from typing import List, Dict

from alert.event import ReportEvent
from alert.mail import sendmail
from alert.report import build_report
from alert.sensorevent import SensorEvent
from common import database
from common.debug import measure_time
from common.log import log, warn
from common.type_def import building_types


def create_events(sensor: Dict, data: List[Dict],
                  new_events: List[ReportEvent],
                  persistent_events: List[ReportEvent],
                  fixed_events: List[ReportEvent]):
    previous = data[-2]['status']
    now = data[-1]['status']
    persist = now & previous
    changed = now ^ previous

    if persist != 0:
        for flag in [1, 2, 4, 1024]:
            if persist & flag:
                persistent_events.append(SensorEvent(sensor, flag))

    if changed != 0:
        for flag in [1, 2, 4, 1024]:
            if changed & flag:
                if now & flag:
                    new_events.append(SensorEvent(sensor, flag))
                else:
                    fixed_events.append(SensorEvent(sensor, flag))


@measure_time
def job():
    invocation_time = dt.datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    log(f'Start alert service {invocation_time.isoformat()}')

    tsdb = database.get_tsdb()
    db = database.get_db()
    sensors = db.find({
        'type': {'$nin': building_types},
        'refBuilding.object': 'urn:ngsi-ld:Building:Inffeldgasse33'
    })

    log('# Scanning for changes in sensors')

    new_events = []
    persistent_events = []
    fixed_events = []

    for sensor in sensors:
        sensor_name = sensor['name']

        # get last two entries for sensor
        data = tsdb.get(sensor_name, '2h')
        # check if values exist
        if len(data) < 2:
            warn('Less than 2 entries in the last 2 hours for sensor', sensor_name)
            continue

        # check if status fields are not none
        if any(d.get('status') is None for d in data):
            log('No status evaluation for sensor', sensor_name)
            continue

        if all(d['status'] == 0 for d in data):
            log(f'Status for sensor {sensor_name}: OK in the last 2 hours, skipping')
            continue

        # Get building data from mongodb
        sensor['building'] = db.find({'_id': sensor['refBuilding']['object']})[0]
        log('Status changed for sensor', sensor_name)

        create_events(sensor, data, new_events, persistent_events, fixed_events)

    if len(new_events) or len(fixed_events):
        log("New changes, generating report...")

        report = build_report(new_events, persistent_events, fixed_events)
        log("Generated report:", report.header)
        log("Sending mail....")
        result = sendmail(report)
        log("Email sent :", result)
    else:
        log("No changes, report discarded.")


if __name__ == '__main__':
    job()
