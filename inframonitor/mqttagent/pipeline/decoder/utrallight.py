from mqttagent.pipeline import Operation


class UltraLightDecoder(Operation):
    """
    Pipeline object for data in ultralight format
    """

    def __init__(self, operation: Operation):
        self.operation = operation

    def process(self, timestamp, topic, payload):
        payload_split = payload.split('|')
        payload = dict(zip(payload_split[::2], payload_split[1::2]))

        return self.operation.process(timestamp, topic, payload)
