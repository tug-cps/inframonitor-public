import json

from mqttagent.pipeline import Operation


class JsonDecoder(Operation):
    """
    Pipeline object for JSON data
    """

    def __init__(self, operation: Operation) -> None:
        self.operation = operation

    def process(self, timestamp, topic, payload):
        payload = json.loads(payload)

        return self.operation.process(timestamp, topic, payload)
