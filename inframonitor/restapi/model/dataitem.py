import datetime as dt
from dataclasses import dataclass
from typing import Optional

from dateutil import parser, tz

from restapi.db.database import unpack_id


def to_epoch(date) -> int:
    default = dt.datetime.now(tz=tz.gettz('Europe/Vienna'))
    return int(parser.parse(date, default=default).timestamp()) if date else date


@dataclass
class DataItem:
    id: str
    unit: str
    description: str
    updateInterval: int
    source: str
    timeCreated: int
    energoId: Optional[str]

    @staticmethod
    def from_db(entry):
        return DataItem(
            id=unpack_id(entry['_id']),
            unit=entry.get('unit', 'Unknown'),
            description=entry.get('description', ''),
            updateInterval=entry.get('updateInterval', 60 * 15),
            source=entry.get('source', 'Unknown'),
            timeCreated=to_epoch(entry.get('dateCreated', {}).get('value', 0)),
            energoId=entry.get('nameEnergo') or None
        )
