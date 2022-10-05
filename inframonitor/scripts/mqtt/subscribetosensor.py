import paho.mqtt.subscribe as subscribe
from paho.mqtt.client import MQTTMessage

from common.config.mqtt import mqtt


def on_message(client, user_data, message: MQTTMessage):
    print(client)
    print(user_data)
    print(message.mid)
    print("new message: {0} to topic: {1}".format(message.payload, message.topic))


if __name__ == "__main__":
    topic = f'/{mqtt.api_key}/+/attrs'
    print('# connecting to {0}'.format(mqtt.host))
    print('# subscribing to {0}'.format(topic))
    print('# listening ...')
    subscribe.callback(on_message, topic, hostname=mqtt.host)
