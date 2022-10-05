import os
from time import sleep

from pymongo import MongoClient
from pymongo.database import Database

from common.config import mqtt
from common.dbwrapper import (InfluxDBWrapper, MongoDBWrapper)
from common.log import log


def get_protected_db() -> Database:
    host = os.environ.get('MONGODB_HOST', 'localhost')
    port = int(os.environ.get('MONGODB_PORT', 27017))
    database = 'protected'

    username = os.environ.get('MONGODB_PROTECTED_USER', None)
    if not username:
        return MongoClient(host, port, serverSelectionTimeoutMS=5000)[database]

    password = os.environ.get('MONGODB_PROTECTED_PASSWORD')
    return MongoClient(host, port, username=username, password=password, authSource=database,
                       serverSelectionTimeoutMS=5000)[database]


def get_db(entities: str = None) -> MongoDBWrapper:
    host = os.environ.get('MONGODB_HOST', 'localhost')
    port = int(os.environ.get('MONGODB_PORT', 27017))
    database = 'ontology'
    username = os.environ.get('MONGODB_USER', 'grafana')
    password = os.environ.get('MONGODB_PASSWORD', 'grafana')

    return MongoDBWrapper(host, port, database, username, password, entities=entities)


def get_tsdb(measurement: str = None) -> InfluxDBWrapper:
    host = os.environ.get('INFLUXDB_HOST', 'localhost')
    database = 'mqtt'
    measurement = measurement or 'sensor-readings'
    username = os.environ.get('INFLUXDB_USER', 'grafana')
    password = os.environ.get('INFLUXDB_PASSWORD', 'grafana')
    ssl = os.environ.get('INFLUXDB_SSL', 'False').lower() in ['true', '1', 'yes']

    return InfluxDBWrapper(host, database, measurement, username, password, ssl=ssl)


def log_config():
    def filter_pw(d):
        if 'password' in d:
            d['password'] = '*****'
        return d

    db = get_db()
    log(db.__class__.__name__, filter_pw(db.__dict__))
    tsdb = get_tsdb()
    log(tsdb.__class__.__name__, filter_pw(tsdb.__dict__))
    log(mqtt.__class__.__name__, mqtt.__dict__)


def healthcheck(mongodb=True, influxdb=True):
    log_config()
    if mongodb:
        log('Connecting to MongoDB...')
        log(get_db().client.server_info())
        log('Done.')
    if influxdb:
        log('Connecting to InfluxDB...')
        error = None

        for i in range(5):
            try:
                error = None
                log(get_tsdb().client.ping())
                break
            except OSError as os_error:
                error = os_error
                log('Failed. Retrying...')
                sleep(1)

        if error:
            raise error
        log('Done.')


if __name__ == '__main__':
    healthcheck()
