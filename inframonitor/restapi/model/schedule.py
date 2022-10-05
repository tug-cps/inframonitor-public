from dataclasses import dataclass
from typing import List


@dataclass
class Info:
    status: str
    timestamp: str


@dataclass
class ScheduleItem:
    id: str
    description: str
    unit: str
    values: List[float]
    timestamps: str


@dataclass
class Schedule:
    info: Info
    schedules: List[ScheduleItem]

    @staticmethod
    def from_db(entry):
        return Schedule(info=entry['info'], schedules=entry['schedules'])
