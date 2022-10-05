import datetime as dt
import traceback
from typing import Any

from paho.mqtt.client import MQTTMessage, Client

from common.log import log, err, print_status
from mqttagent.pipeline import Operation, Topic, Skip


def print_mqtt(message: MQTTMessage):
    return {
        'retain': message.retain,
        'qos': message.qos,
        'payload': message.payload,
        'state': message.state,
        'topic': message.topic,
        'dup': message.dup,
    }


class MQTTSource:
    def __init__(self, operation: Operation, skip_retain=True):
        self.skip_retain = skip_retain
        self.operation = operation

    def on_message(self, client: Client, user_data: Any, message: MQTTMessage):
        timestamp = dt.datetime.utcnow()

        if not message.payload:
            log(f'MQTT message {print_mqtt(message)} with empty payload received, skipping...')
            return
        if message.retain and self.skip_retain:
            log(f'MQTT message {print_mqtt(message)} has retain set, skipping...')
            return

        topic = Topic.from_str(message.topic)
        self.operation.process(timestamp, topic, message)


class MQTTProcessor(Operation):
    def __init__(self, operation: Operation):
        self.operation = operation

    def process(self, timestamp, topic, payload):
        _payload = payload.payload.decode('utf-8')

        try:
            status = self.operation.process(timestamp, topic, _payload)
            log(topic.raw, _payload, print_status(status))
            return status
        except Skip:
            log(topic.raw, _payload, 'SKIPPED')
        except Exception:
            err(traceback.format_exc())
            err(f'MQTT message {print_mqtt(payload)} received - error during processing')
        return False
