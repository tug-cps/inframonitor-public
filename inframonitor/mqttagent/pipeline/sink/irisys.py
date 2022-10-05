from typing import List, Dict

from common import database
from common.dbwrapper import MongoDBWrapper, InfluxDBWrapper
from common.log import log
from mqttagent.pipeline import Operation, Skip, Provider


def unpack(d: Dict, keys: List):
    return [d[v] for v in keys]


def aggregate_readings(message: List) -> int:
    if not message:
        return 0

    delta = 0
    for entry in message:
        register, value = unpack(entry, ['register', 'value'])
        if register == 'Line 1':
            delta += value
        elif register == 'Line 2':
            delta -= value
    return delta


class IrisysSink(Operation):
    """
    Sink object for data from Irisys Vector 4D People Counter System
    """

    def __init__(self, provider: Provider, db: MongoDBWrapper = None, tsdb: InfluxDBWrapper = None):
        self.provider = provider
        self.db = db or database.get_db()
        self.tsdb = tsdb or database.get_tsdb()

    def process(self, timestamp, topic, payload):
        if not topic.raw.endswith('/counts'):
            raise Skip

        delta = aggregate_readings(payload)

        _type = 'People'
        building = topic.sensor_name.split('_')[0]
        _id = f'urn:ngsi-ld:{_type}:{building}'
        sensor = self.db.find_one({'_id': _id})

        reading = delta
        update_query = {'source': self.provider.name}
        if not sensor:
            self.create_sensor(timestamp, _id, building, _type)
        else:
            reading += sensor.get('reading', 0)

            if 'dateCreated' not in sensor:
                log(f'Sensor {building} has no dateCreated field, estimating one from influxdb')
                date_created = self.tsdb.find_first(building)
                update_query['dateCreated'] = {
                    'type': 'DateTime',
                    'value': date_created.replace(microsecond=0).isoformat()
                }

        update_query['reading'] = reading

        # per sensor value
        self.tsdb.upsert(timestamp, {'reading': float(delta)}, {'sensor': topic.sensor_name})
        # aggregate
        self.tsdb.upsert(timestamp, {'reading': float(reading)}, {'sensor': building})
        return self.db.update(_id, update_query)

    def create_sensor(self, timestamp, _id, building, _type):
        self.db.insert({
            '_id': _id,
            'type': _type,
            'name': building,
            'dateCreated': {
                'type': 'DateTime',
                'value': timestamp.isoformat()
            }
        })
