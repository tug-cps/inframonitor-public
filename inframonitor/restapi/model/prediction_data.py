from dataclasses import dataclass
from typing import List

from restapi.model.time_values_pair import TimeValuesPair


@dataclass
class PredictionData:
    created: int
    from_: int
    ids: List[str]
    to: int
    values: List[TimeValuesPair]

    @staticmethod
    def from_db(entry):
        # TODO
        return PredictionData(
            created=-1,
            from_=-1,
            ids=[],
            to=-1,
            values=[]
        )
