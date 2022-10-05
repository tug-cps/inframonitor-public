from typing import List, Dict

from flask import abort
from influxdb.exceptions import InfluxDBClientError
from influxdb.resultset import ResultSet
from pymongo.collection import Collection

from restapi.db import database


def find_sensor(sensor_id: str):
    db = database.get_db()
    coll: Collection = db.entities
    return coll.find_one({'_id': sensor_id, 'type': {'$nin': ['Building', 'Site']}}) or abort(404)


def create_query(field, from_, limit, offset, order, to, sample_time, aggregation, fill):
    metric = f'{aggregation}("{field}") as {field}' if sample_time else f'"{field}"'
    query = f'SELECT {metric} FROM "sensor-readings" WHERE sensor = $sensor'
    if from_:
        query += f' AND time >= {from_}s'
    if to:
        query += f' AND time <= {to}s'
    if sample_time:
        query += f' GROUP BY time({sample_time}s) fill({fill})'
    query += f' ORDER BY time {order}'
    if limit:
        query += f' LIMIT {limit}'
    if offset:
        query += f' OFFSET {offset}'
    query += ";"
    return query


def query_tsdb(query: str, sensor_name: str):
    try:
        tsdb = database.get_tsdb()
        result: ResultSet = tsdb.query(query, bind_params={'sensor': sensor_name}, epoch='s')
        return list(result.get_points())

    except InfluxDBClientError:
        abort(500)


def write_tsdb(points):
    try:
        client = database.get_tsdb()
        client.write_points(points, time_precision='s') or abort(500)
    except InfluxDBClientError:
        abort(500)


def create_points(sensor_name: str, field: str, values: List[Dict], created: int):
    return [{
        'measurement': 'sensor-readings',
        'time': value['timestamp'],
        'fields': {field: value['value']},
        'tags': {'sensor': sensor_name, 'created': created}
    } for value in values]


def field_search(field: str, data_item_id: str, from_: int = None, to: int = None, limit: int = None,
                 order: str = 'ASC', offset: int = None, sample_time: int = None, aggregation: str = None,
                 fill: str = 'null'):
    sensor = find_sensor(data_item_id)
    sensor_name = sensor.get('name') or abort(404)
    query = create_query(field, from_, limit, offset, order, to, sample_time, aggregation, fill)
    return query_tsdb(query, sensor_name)
