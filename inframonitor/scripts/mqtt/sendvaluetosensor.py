import random
import time

import paho.mqtt.publish as publish

from common.config.mqtt import mqtt

sensor_names = ['10_123456', 'In1In11K1_S123_S94_P01_Vol', 'IN_IN160_LORA__TEIS123__B01_1_Temp']
sensor_attribute = 'r'


def send_value(value):
    sensor_name = random.choice(sensor_names)
    topic = '/{0}/{1}/attrs'.format(mqtt.api_key, sensor_name)
    payload = '{0}|{1}'.format(sensor_attribute, "{:.5f}".format(value))

    print('posting payload: \"{0}\" to {1}'.format(payload, topic))
    publish.single(topic, payload, hostname=mqtt.host)


if __name__ == "__main__":
    current_value = random.random() * 64000.0
    while True:
        current_value += random.random() * 10.0
        send_value(current_value)
        time.sleep(2)
