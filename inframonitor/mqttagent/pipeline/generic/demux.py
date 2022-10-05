from dataclasses import dataclass
from typing import List

from common.log import warn
from mqttagent.pipeline import Operation


@dataclass
class DemuxSink:
    api_key: str
    operation: Operation


class Demux(Operation):
    def __init__(self, rules: List[DemuxSink]):
        self.rules = {rule.api_key: rule for rule in rules}

    def process(self, timestamp, topic, payload):
        rule = self.rules.get(topic.api_key)
        if rule:
            return rule.operation.process(timestamp, topic, payload)
        warn('Message received, but no rule to handle message')
        return False
