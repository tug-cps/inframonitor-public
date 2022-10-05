from dataclasses import dataclass
from typing import List

from restapi.db.database import unpack_id


@dataclass
class GeoLocation:
    lat: float
    long: float
    alt: float

    @staticmethod
    def from_db(entry):
        try:
            if not entry:
                return None

            coordinates = entry.get('value', {}).get('coordinates')
            if not coordinates or len(coordinates) != 2:
                return None

            coordinates = [float(x) for x in coordinates]
        except ValueError:
            return None
        return GeoLocation(lat=coordinates[0], long=coordinates[1], alt=353)


@dataclass
class Building:
    id: str
    dataItemIds: List[str]
    geoLocation: GeoLocation

    @staticmethod
    def from_db(entry):
        return Building(
            id=unpack_id(entry['_id']),
            dataItemIds=[unpack_id(e['_id']) for e in entry['dataItemIds']],
            geoLocation=GeoLocation.from_db(entry.get('location'))
        )
