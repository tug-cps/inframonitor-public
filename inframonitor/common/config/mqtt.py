import os


class mqtt:
    host = os.environ.get('MQTT_HOST', 'localhost')
