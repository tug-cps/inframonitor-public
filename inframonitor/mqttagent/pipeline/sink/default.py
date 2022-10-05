import datetime as dt
import re

from common import database
from common.dbwrapper import MongoDBWrapper, InfluxDBWrapper
from common.log import warn
from common.type_def import on_change_types
from mqttagent.pipeline import Operation, Skip, Topic, Provider


def guess_sensor_type(sensor_name: str) -> str:
    patterns = [
        # EAM / BAC Net naming
        ('^In.*_Vol$', 'Water'),
        ('^In.*_Nrg$', 'Energy'),
        ('^IN.*_Temp$', 'Temperature'),
        ('^IN.*_Hum$', 'Humidity'),
        ('^IN.*_Co2$', 'Co2'),

        ('.*_LORA__TETBDW.*Temp.$', 'Temperature'),
        ('.*_LORA__TETBDW.*Stat.$', 'OpenClose'),
        ('.*_LORA__TETBDW.*Bat.$', 'Battery'),
        ('.*_LORA__TETBDW.*BatV.$', 'BatteryVoltage'),

        # Room CO2/Temperature/Humidity sensor
        ('.*_LORA__TEIS.*Temp$', 'Temperature'),
        ('.*_LORA__TEIS.*Hum$', 'Humidity'),
        ('.*_LORA__TEIS.*Bat$', 'Battery'),
        ('.*_LORA__TEIS.*Co2$', 'CO2'),

        # Contact sensor
        ('.*_LORA__TEIB.*Bat$', 'Battery'),
        ('.*_LORA__TEIB.*Status_Sensor$', 'ContactStatus'),
        ('.*_LORA__TEIB.*Counter_Total_A$', 'Contact'),
        ('.*_LORA__TEIB.*Counter_Total_B$', 'Contact'),

        # Weather station
        ('.*_WETT_.*_DewPoint$', 'DewPoint'),
        ('.*_WETT_.*_Enth$', 'Enthalpy'),
        ('.*_WETT_.*_GlobIrradInDiffuse_Disc$', 'GlobalIrradianceDiffuse'),
        ('.*_WETT_.*_GlobIrradTotal_Disc$', 'GlobalIrradianceTotal'),
        ('.*_WETT_.*_AbsHum$', 'HumidityAbsolute'),
        ('.*_WETT_.*_RelHum', 'HumidityRelative'),
        ('.*_WETT_.*_SunshineDetect_Disc', 'SunshineDetect'),
        ('.*_WETT_.*_Temp', 'Temperature'),

        # Wildpacher
        ('^\\d{2}_\\d{6}$', 'Energy')
    ]
    for pattern in patterns:
        if re.match(pattern[0], sensor_name):
            return pattern[1]
    return 'UnknownSensor'


def convert_to_float(value):
    if type(value) is str:
        if value.lower() in ['true', 'false']:
            return 1.0 if value.lower() == 'true' else 0.0
    return float(value)


class DefaultSink(Operation):
    """
    Decoder object for data from generic sources
    """

    def __init__(self, provider: Provider, db: MongoDBWrapper = None, tsdb: InfluxDBWrapper = None):
        self.provider = provider
        self.operation = DefaultDatabaseSink(provider, db, tsdb)

    def process(self, timestamp, topic, payload):
        if not topic.raw.endswith('/attrs'):
            raise Skip

        if 'r' not in payload:
            raise Skip

        reading = convert_to_float(payload['r'])

        db_update = {
            'reading': reading,
            'source': self.provider.name
        }

        if 's' in payload:
            db_update['source_status'] = payload['s']

        return self.operation.process(timestamp, topic, db_update)


METER_TYPE_SENSORS = [
    'Water',
    'Energy'
]


class DefaultDatabaseSink(Operation):
    def __init__(self, provider: Provider, db: MongoDBWrapper, tsdb: InfluxDBWrapper):
        self.provider = provider
        self.db = db or database.get_db()
        self.tsdb = tsdb or database.get_tsdb()

    def create_sensor(self, timestamp: dt.datetime, provider: Provider, topic: Topic):
        _type = guess_sensor_type(topic.sensor_name)
        _id = f'urn:ngsi-ld:{_type}:{topic.sensor_name}'

        sensor = {
            '_id': _id,
            'type': _type,
            'name': topic.sensor_name,
            'source': provider.name,
            'dateCreated': {
                'type': 'DateTime',
                'value': timestamp.isoformat()
            }
        }
        self.db.insert(sensor)

        return sensor

    def process(self, timestamp, topic, payload):
        sensor = self.db.find_one({'name': topic.sensor_name})

        # Create missing sensors / dateCreated fields
        if not sensor:
            warn(f'Sensor {topic.sensor_name} is unknown, creating in MongoDB...')
            sensor = self.create_sensor(timestamp, self.provider, topic)
        elif 'dateCreated' not in sensor:
            warn(f'Sensor {topic.sensor_name} has no dateCreated field, estimating one from influxdb')
            date_created = self.tsdb.find_first(topic.sensor_name)
            payload['dateCreated'] = {
                'type': 'DateTime',
                'value': date_created.replace(microsecond=0).isoformat()
            }

        # Sanity checks
        if sensor['source'] != payload['source']:
            warn(f'Provider ID conflict: {sensor["source"]} <> {payload["source"]} are writing to {topic.sensor_name}')
        if sensor['type'] in METER_TYPE_SENSORS and sensor.get('reading', 0) > payload['reading']:
            warn(f'{sensor["type"]} meter reporting a lower value - possible sensor collision?')

        if sensor['type'] in on_change_types:
            fields = {'reading': payload['reading']}
            tags = {'sensor': topic.sensor_name, 'source': self.provider.name}
            if 'source_status' in payload:
                fields['source_status'] = payload['source_status']
            self.tsdb.upsert(timestamp, fields=fields, tags=tags)

        return self.db.update(sensor['_id'], payload)
