import traceback

from common import database, type_def
from common.dbwrapper import MongoDBWrapper, InfluxDBWrapper, InfluxDBException
from common.log import err


def update_from_mongodb(influxdb_wrapper: InfluxDBWrapper, mongodb_wrapper: MongoDBWrapper):
    ignored_entity_types = type_def.building_types

    sensors = mongodb_wrapper.find({'type': {'$nin': ignored_entity_types}})
    successful_updates = []
    for sensor in sensors:
        try:
            sensor_name = sensor['name']
            tags = {'id': sensor['_id']}
            if 'type' in sensor:
                tags['type'] = sensor['type']
            print(tags)

        except Exception:
            err('Cannot decode sensor name / reading')
            continue

        try:
            influxdb_wrapper.add_tags(sensor_name, tags)
            successful_updates.append(sensor_name)

        except InfluxDBException:
            err(f'Cannot add new tags for sensor {sensor_name} to influxdb')
        except Exception:
            err(f'Exception occured for sensor {sensor_name}: ', traceback.format_exc())

    print(f'Updated {len(successful_updates)} sensors:')
    [print(' ', update) for update in successful_updates]
    return len(successful_updates)


def main():
    influxdb_wrapper = database.get_tsdb()
    mongodb_wrapper = database.get_db()

    update_from_mongodb(influxdb_wrapper, mongodb_wrapper)


if __name__ == "__main__":
    main()
