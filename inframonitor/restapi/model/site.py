from dataclasses import dataclass
from typing import List

from restapi.db.database import unpack_id


@dataclass
class Site:
    id: str
    buildingIds: List[str]

    @staticmethod
    def from_db(entry):
        return Site(
            id=unpack_id(entry['_id']),
            buildingIds=[unpack_id(e['_id']) for e in entry['buildingIds']]
        )
