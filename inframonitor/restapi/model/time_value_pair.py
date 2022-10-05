from dataclasses import dataclass


@dataclass
class TimeValuePair:
    timestamp: int
    value: float

    @staticmethod
    def from_db(entry, field_name):
        return TimeValuePair(
            timestamp=entry['time'],
            value=entry[field_name]
        )
