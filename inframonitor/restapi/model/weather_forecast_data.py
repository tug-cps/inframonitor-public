from dataclasses import dataclass
from typing import List, Dict

from dateutil import parser, tz

from restapi.model.time_values_pair import TimeValuesPair

# Weather data is retrived in CEST
cest = tz.gettz('Europe/Berlin')


@dataclass
class WeatherForecastData:
    created: int
    ids: List[str]
    values: List[TimeValuesPair]

    @staticmethod
    def from_db(entry: Dict, from_: int = None, to: int = None):
        data: Dict = entry['data']
        data_1h: Dict = data['data_1h']
        ids = list(filter(lambda k: k not in ['time', 'rainspot'], data_1h.keys()))

        values = []
        for idx, timestamp in enumerate(data_1h['time']):
            timestamp = parser.isoparse(timestamp).replace(tzinfo=cest)
            timestamp = int(timestamp.timestamp())

            if from_ and timestamp < from_:
                continue
            if to and timestamp > to:
                continue

            values.append(TimeValuesPair(timestamp, [data_1h[_id][idx] or 0 for _id in ids]))

        return WeatherForecastData(
            created=int(entry['timestamp'].timestamp()),
            ids=ids,
            values=values
        )
