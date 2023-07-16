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
        'payload': json.dumps(payload),
        'retain': True
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
            for addr, info in bscanner.scan(SCAN_INTERVAL).items():
                if info.publish:
                    msgs.append(_create_msg(f'ble/{addr}', {"detected": info.detected, "rssi": info.rssi}))
            # Scan climate
            reading = cscanner.scan()
            if reading.publish:
                msgs.append(_create_msg('temperature', reading.temperature))
                msgs.append(_create_msg('humidity', reading.humidity))
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