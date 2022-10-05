from dataclasses import dataclass
from typing import List


@dataclass
class TimeValuesPair:
    timestamp: int
    values: List[float]
