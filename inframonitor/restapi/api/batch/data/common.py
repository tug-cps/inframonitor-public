from typing import List

from influxdb.resultset import ResultSet
from pymongo.collection import Collection
from werkzeug.exceptions import abort

from restapi.db import database
from restapi.model.historic_data import HistoricData


def split_data_items(data_item_ids) -> List[str]:
    return [v.strip() for v in data_item_ids.split(',')]


def get_query_string(data_items: List[dict]) -> str:
    return '(' + ' OR '.join([f'"sensor" = \'{d}\'' for d in data_items]) + ')'


def create_query(sensors, field, from_, to, limit, offset, order, sample_time, aggregation, fill):
    metric = f'{aggregation}("{field}") as {field}' if sample_time else f'"{field}"'
    query = f'SELECT {metric} FROM "sensor-readings" WHERE ' + get_query_string(sensors)
    if from_:
        query += f' AND time >= {from_}s'
    if to:
        query += f' AND time <= {to}s'
    if sample_time:
        query += f' GROUP BY time({sample_time}s), "sensor" fill({fill})'
    else:
        query += ' GROUP BY *'
    query += f' ORDER BY {order}'
    if limit:
        query += f' LIMIT {int(limit)}'
    if offset:
        query += f' OFFSET {offset}'
    query += ";"
    return query


def query_field(data_item_ids, field, from_, to, limit, offset, order, sample_time=None, aggregation=None, fill='null'):
    if not from_ and not to and not limit:
        abort(400, "Either a 'from'- and 'to'- or a 'limit'-parameter must be provided!")
    data_items = split_data_items(data_item_ids)
    if not len(data_items):
        abort(404, 'No data items provided')
    if len(data_items) != len(set(data_items)):
        abort(400, 'Duplicate ids found in request')

    sensor_lookup = get_sensor_lookup(data_items)
    sensors = [sensor_lookup[sensor] for sensor in data_items]
    query = create_query(sensors, field, from_, to, limit, offset, order, sample_time, aggregation, fill)

    tsdb = database.get_tsdb()
    result: ResultSet = tsdb.query(query, epoch='s')
    values = HistoricData.values_from_resultset(sensors, result, field)
    return data_items, values


def get_sensor_lookup(data_items):
    db = database.get_db()
    coll: Collection = db.entities
    sensor_list = list(coll.aggregate([
        {'$match': {
            '_id': {'$in': data_items},
            'type': {'$nin': ['Building', 'Site']}
        }}
    ]))
    sensor_lookup = {sensor['_id']: sensor['name'] for sensor in sensor_list}
    if len(sensor_list) != len(data_items):
        [abort(404, f'Sensor {item} not found') for item in data_items if item not in sensor_lookup]

    return sensor_lookup
