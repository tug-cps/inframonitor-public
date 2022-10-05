import datetime as dt
import traceback

from common import database
from common.dbwrapper.influxdbwrapper import InfluxDBException
from common.debug import measure_time
from common.log import log, err
from monitor.helpers import time_from_string
from monitor.strategy import (value_exceeds_prediction, value_continuously_exceeds_prediction,
                              value_is_not_zero_over_night, value_does_not_change)


@measure_time
def job():
    invocation_time = dt.datetime.utcnow().replace(minute=0, second=0, microsecond=0)

    tsdb = database.get_tsdb()
    db = database.get_db()
    run_status_updates(invocation_time, db, tsdb)


def run_sensor_update(invocation_time, sensor, db, tsdb):
    sensor_name = sensor['name']
    # get latest values for prediction and actual value
    data = tsdb.get(sensor_name, '24h')
    if not data or len(data) < 2:
        return False

    latest_entry = data[-1]
    if time_from_string(latest_entry.get('time')) != invocation_time:
        log('No new entry found for sensor', sensor_name)
        return False
    if not latest_entry.get('reading'):
        log('No reading available for entry, skipping further checks', sensor_name)
        return False

    log(f'Valid sensor: {sensor["_id"]}')

    # sensor status
    status = 0

    # Calculate differences from absolute values
    if sensor['type'] != 'People':
        for i in range(len(data) - 1, 0, -1):
            data[i]['reading'] -= data[i - 1]['reading']
        data = data[1:]

    if latest_entry.get('prediction'):
        status += value_exceeds_prediction(data, sensor, sensor_name, db, tsdb) * 1
        status += value_continuously_exceeds_prediction(data) * 2
        status += value_is_not_zero_over_night(data, sensor, sensor_name, db, tsdb) * 4
    else:
        log('No prediction available for entry, skipping further checks', sensor_name)

    status += value_does_not_change(data) * 1024

    log("Verdict of", sensor_name, ":", status)

    tsdb.upsert(invocation_time, {'status': status}, {'sensor': sensor_name})
    return True


def run_status_updates(invocation_time, db, tsdb):
    log(f'Updating diagnosis at {invocation_time.isoformat()}')

    sensors = db.find({
        'type': {'$ne': 'Building'},
        'refBuilding.object': 'urn:ngsi-ld:Building:Inffeldgasse33'
    })

    successful_updates = []

    for sensor in sensors:
        sensor_name = sensor['name']
        try:
            success = run_sensor_update(invocation_time, sensor, db, tsdb)
            if success:
                successful_updates.append(sensor_name)
        except InfluxDBException:
            err(f'Cannot upsert prediction for sensor {sensor_name} to influxdb.')
        except Exception:
            err(f'Error while handling update for sensor {sensor_name}: {traceback.format_exc()}')

    log(f'Updated {len(successful_updates)} sensors:')
    [log(' ', update) for update in successful_updates]
    return successful_updates


if __name__ == '__main__':
    job()
