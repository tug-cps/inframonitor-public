from dataclasses import dataclass
from typing import List

from influxdb.resultset import ResultSet

from restapi.model.time_values_pair import TimeValuesPair


@dataclass
class HistoricData:
    values: List[TimeValuesPair]

    @staticmethod
    def values_from_db(ids: List[str], points):
        idx = {v: i for i, v in enumerate(ids)}

        values = []
        timestamp = 0
        t = []

        for point in points:
            if timestamp != point['time']:
                if t:
                    values.append(TimeValuesPair(timestamp=timestamp, values=t))
                timestamp = point['time']
                t = [None] * len(ids)

            t[idx[point['sensor']]] = point['reading']

        values.append(TimeValuesPair(timestamp=timestamp, values=t))
        return values

    @staticmethod
    def values_from_resultset(sensors, result_set: ResultSet, field: str):
        merged = {}

        items = {item[0][1]['sensor']: item[1] for item in result_set.items()}
        for idx, item in enumerate(sensors):
            for point in items.get(item, []):
                v = merged.get(point['time'])
                if not v:
                    v = [None] * len(sensors)
                v[idx] = point[field]
                merged[point['time']] = v
        return [TimeValuesPair(timestamp=m[0], values=m[1]) for m in merged.items()]
