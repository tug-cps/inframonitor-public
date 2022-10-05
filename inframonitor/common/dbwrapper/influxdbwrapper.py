import datetime as dt
from dataclasses import dataclass
from typing import List

from influxdb import InfluxDBClient


@dataclass
class MeasurementPoint:
    timestamp: dt.datetime
    fields: dict


class InfluxDBException(Exception):
    pass


class InfluxDBWrapper:
    def __init__(self, host, database, measurement, username, password, ssl=True):
        self.database = database
        self.__host = host
        self.__measurement = measurement
        self.__username = username
        self.__password = password
        self.__ssl = ssl
        self.client = InfluxDBClient(host=self.__host, database=self.database, username=self.__username,
                                     password=self.__password, ssl=self.__ssl, timeout=5)

    def find_first(self, sensor: str) -> dt.datetime:
        """
        Find date of first entry for sensor
        :param sensor: Sensor name to look up
        :return: datetime of first entry or utcnow
        """
        bind_params = {'sensor': sensor}
        query = f'SELECT first(reading) FROM \"{self.__measurement}\" WHERE sensor = $sensor;'
        points = list(self.client.query(query, bind_params=bind_params, epoch='s').get_points())
        return dt.datetime.fromtimestamp(points[0]['time']) if points else dt.datetime.utcnow()

    @staticmethod
    def __remove_prefix(points: List[dict]):
        keys = [('field_prediction', 'prediction'), ('field_reading', 'reading'), ('field_status', 'status')]
        for point in points:
            for key in keys:
                value = point.pop(key[0], None)
                if value is not None:
                    point[key[1]] = value
        return points

    def get(self, sensor: str, look_back: str) -> list:
        """
        :param sensor: Sensor designation
        :param look_back: has to be a valid identifier, e.g. 3h for three hours
        """
        bind_params = {'sensor': sensor}
        query = f'SELECT first(*) AS "field" FROM "{self.__measurement}" WHERE ' \
                f'sensor = $sensor AND time >= now() - {look_back} AND time <= now()' \
                f'GROUP BY time(1h);'

        points = list(self.client.query(query, bind_params=bind_params).get_points())

        # remove field prefix
        points = self.__remove_prefix(points)

        # remove 'empty' measurements
        points = [p for p in points if len(p) > 1]
        return points

    def upsert(self, timestamp: dt.datetime, fields: dict, tags: dict) -> None:
        influx_point = {
            'measurement': self.__measurement,
            'time': timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'fields': fields,
            'tags': tags
        }
        if not self.client.write_points(points=[influx_point]):
            raise InfluxDBException()

    def upsert_many(self, points: List[MeasurementPoint], tags: dict) -> None:
        influx_points = [{
            'measurement': self.__measurement,
            'time': point.timestamp.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'fields': point.fields
        } for point in points]
        if not self.client.write_points(points=influx_points, tags=tags):
            raise InfluxDBException()

    def add_tags(self, sensor, tags: dict):
        client = self.client
        db_data = list(client.query(query=f'select * from "{self.__measurement}" WHERE ("sensor"=\'{sensor}\');',
                                    bind_params={"sensor": sensor}).get_points())

        tags = {**tags, **{"sensor": sensor}}

        data_to_write = [{
            "tags": tags,
            "measurement": self.__measurement,
            "time": d['time'],
            "fields": {k: d[k] for k in (d.keys()) if k not in ("time", "measurement", "sensor")}
        } for d in db_data]

        client.write_points(points=data_to_write)
        query = f'delete from "{self.__measurement}" where ("sensor"=$sensor) and "type" =\'\' and "description"=\'\''
        client.query(query=query, bind_params={"sensor": sensor})
