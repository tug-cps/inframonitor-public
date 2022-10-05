from dataclasses import dataclass


@dataclass
class Topic:
    api_key: str
    sensor_name: str
    detail: str
    raw: str

    @staticmethod
    def from_str(topic):
        offset = 1 if topic.startswith('/') else 0
        split = topic.split('/')

        return Topic(api_key=split[0 + offset], sensor_name=split[1 + offset], detail=split[2 + offset], raw=topic)
