#!/usr/bin/python3
import sys
import json
import paho.mqtt.publish as publish
from .ble import BLEScanner
from .climate import ClimateScanner
from .video import VideoSubprocess
from .config import LOG, SCAN_INTERVAL, BLE_MAC_WATCH_LIST, MQTT_HOST, MQTT_PORT, MQTT_AUTH, MQTT_TOPIC

def _create_msg(sub_topic, payload):
    return {
        'topic': f'{MQTT_TOPIC}/{sub_topic}',
        'payload': json.dumps(payload)
    }

if __name__ == '__main__':
    LOG.info("Starting up...")
    video = VideoSubprocess()
    video.start()
    bscanner = BLEScanner(BLE_MAC_WATCH_LIST)
    cscanner = ClimateScanner()
    while True:
        try:
            msgs = []
            # Scan BLE
            ble_data = bscanner.scan(SCAN_INTERVAL)
            ble_pubs = {addr: vars(ble_data[addr]) for addr in ble_data.keys() if ble_data[addr].publish}
            if ble_pubs:
                msgs.append(_create_msg('ble', ble_pubs))
            # Scan climate
            reading = cscanner.scan()
            if reading.publish:
                msgs.append(_create_msg('climate', vars(reading)))
            # Publish via MQTT
            if msgs:
                publish.multiple(msgs, hostname=MQTT_HOST, port=MQTT_PORT, auth=MQTT_AUTH)
                for msg in msgs:
                    LOG.info(f"Published: {msg}")
        except KeyboardInterrupt:
            LOG.info("Shutting down...")
            video.stop()
            sys.exit()
        except:
            LOG.exception("Encountered unexpected error")