import datetime as dt
import traceback

from common import database
from common.dbwrapper.influxdbwrapper import InfluxDBException, InfluxDBWrapper
from common.log import log, err, warn
from common.type_def import building_types, on_change_types


def write_sensor_to_influxdb(sensor, invocation_time, tsdb: InfluxDBWrapper):
    try:
        sensor_name = sensor['name']
        reading = sensor['reading']

    except KeyError:
        err('Cannot decode sensor name / reading:', sensor)
        return False

    date_modified_iso = sensor.get('dateModified', {}).get('value')
    if not date_modified_iso:
        warn(f'Sensor {sensor_name} does not have a `dateModified` field, skipping...')
        return False

    # Job is always executed +1 Minute, so take this into account
    # 10:01 - 10:16 -> 10:15
    # 10:16 - 10:31 -> 10:30
    # 10:31 - 10:46 -> 10:45
    # 10:46 - 11:01 -> 11:00
    date_modified = dt.datetime.fromisoformat(date_modified_iso)
    diff = (invocation_time - date_modified).total_seconds() / 60 + 1
    if diff > 15 or diff < 0:
        log(f'Sensor {sensor_name} did not get an update in the last 15 minutes (diff: {diff}), skipping...')
        return False

    log(f'Storing entry for Sensor {sensor_name} from {date_modified} - {float(reading)} (diff: {diff})')
    try:
        tags = {'sensor': sensor_name}
        add_conditionally('source', sensor, tags)

        fields = {'reading': float(reading)}
        add_conditionally('source_status', sensor, fields)

        tsdb.upsert(invocation_time, fields, tags)
        return True
    except InfluxDBException:
        err(f'Cannot upsert new reading for sensor {sensor_name} to influxdb')
    except Exception:
        err(f'Exception occurred for sensor {sensor_name}: ', traceback.format_exc())
    return False


def add_conditionally(key: str, _from: dict, _to: dict):
    if key in _from:
        _to[key] = _from[key]


def mongo_to_influx(db, tsdb):
    invocation_time = dt.datetime.utcnow()
    invocation_time = invocation_time.replace(
        minute=invocation_time.minute - invocation_time.minute % 15, second=0, microsecond=0)

    log('')
    log('#######################################')
    log('Writing mongodb sensor data to influxdb')
    log('#######################################')
    log('Invocation time:', invocation_time)

    # FIXME annotate sensors / buildings
    sensors = db.find({
        'type': {'$nin': building_types + on_change_types},
        'reading': {'$exists': True}
    })
    successful_updates = [sensor['name'] for sensor in sensors if
                          write_sensor_to_influxdb(sensor, invocation_time, tsdb)]

    log(f'Updated {len(successful_updates)} sensors:')
    [log(' ', update) for update in successful_updates]


def job():
    db = database.get_db()
    tsdb = database.get_tsdb()
    mongo_to_influx(db, tsdb)


if __name__ == '__main__':
    job()
