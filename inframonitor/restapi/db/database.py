import os

import rdflib
from influxdb import InfluxDBClient
from pymongo import MongoClient
from pymongo.database import Database

MONGO_URI = os.environ.get('MONGO_URI', "mongodb://localhost:27017")
MONGODB_USER = os.environ.get('MONGODB_USER', 'grafana')
MONGODB_PASSWORD = os.environ.get('MONGODB_PASSWORD', 'grafana')
MONGODB_DB = "ontology"

INFLUXDB_HOST = os.environ.get('INFLUXDB_HOST', "localhost")
INFLUXDB_DATABASE = os.environ.get('INFLUXDB_DATABASE', "mqtt")
INFLUXDB_USER = os.environ.get('INFLUXDB_USER', 'grafana')
INFLUXDB_PASSWORD = os.environ.get('INFLUXDB_PASSWORD', 'grafana')
INFLUXDB_USE_SSL = os.environ.get('INFLUXDB_SSL', 'False').lower() in ['true', '1', 'yes']


def get_db() -> Database:
    client = MongoClient(MONGO_URI, username=MONGODB_USER, password=MONGODB_PASSWORD, authSource="ontology")
    return client.get_database("ontology")


def get_tsdb() -> InfluxDBClient:
    return InfluxDBClient(host=INFLUXDB_HOST, database=INFLUXDB_DATABASE,
                          username=INFLUXDB_USER, password=INFLUXDB_PASSWORD, ssl=INFLUXDB_USE_SSL)


def get_ontology():
    graph = rdflib.Graph()
    graph.parse("restapi/db/inffeldgasse.ttl", format="ttl")  # TODO Replace with hoddb
    return graph


def unpack_id(id) -> str:
    return id if type(id) == str else str(id)
