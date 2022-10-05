import os

from paho.mqtt import subscribe

from common.config import mqtt
from common.database import healthcheck, get_db, get_tsdb
from common.log import log
from mqttagent.pipeline import Provider
from mqttagent.pipeline.decoder import UltraLightDecoder, JsonDecoder
from mqttagent.pipeline.generic import Demux, DemuxSink
from mqttagent.pipeline.sink import DefaultSink, IrisysSink
from mqttagent.pipeline.source import MQTTSource, MQTTProcessor

if __name__ == '__main__':
    log('# Starting mqtt agent')
    healthcheck()

    provider = Provider('XXXXXXXXXXXXXXXXXX', 'DEFAULT')

    demux = Demux([
        DemuxSink(proivder.api_key, UltraLightDecoder(DefaultSink(provider)))
    ])

    source = MQTTSource(MQTTProcessor(demux))

    log("# Subscribing on broker", mqtt.host)
    client_id = os.environ.get("MQTT_AGENT_CLIENT_ID", None)
    subscribe.callback(callback=source.on_message, topics='#', hostname=mqtt.host, client_id=client_id)
