#!/usr/bin/python3
import sys
import json
import time
import paho.mqtt.publish as publish
from .ble import BLEScanner
from .climate import ClimateScanner
from .video import VideoSubprocess
from .config import (
    LOG, 
    SCAN_INTERVAL,
    MQTT_HOST, 
    MQTT_PORT, 
    MQTT_AUTH, 
    MQTT_TOPIC,
    CLIMATE_ENABLED,
    BLE_ENABLED,
    BLE_MAC_WATCH_LIST, 
    VIDEO_ENABLED
)

def _create_msg(sub_topic, payload):
    return {
        'topic': f'{MQTT_TOPIC}/{sub_topic}',
        'payload': json.dumps(payload),
        'retain': True
    }

def _start_video():
    video = VideoSubprocess()
    video.start()
    return video

def _scan_ble(msgs):
    for addr, info in bscanner.scan(SCAN_INTERVAL).items():
        if info.publish:
            msgs.append(_create_msg(f'ble/{addr}', {"detected": info.detected, "rssi": info.rssi}))

def _scan_climate(msgs):
    reading = cscanner.scan()
    if reading.publish:
        msgs.append(_create_msg('temperature', reading.temperature))
        msgs.append(_create_msg('humidity', reading.humidity))

def _mqtt_publish(msgs):
    if msgs:
        publish.multiple(msgs, hostname=MQTT_HOST, port=MQTT_PORT, auth=MQTT_AUTH)
        for msg in msgs:
            LOG.info(f"Published: {msg}")

if __name__ == '__main__':
    LOG.info("Starting up...")
    bscanner = BLEScanner(BLE_MAC_WATCH_LIST)
    cscanner = ClimateScanner()
    video = _start_video() if VIDEO_ENABLED else None
    while True:
        try:
            start = time.time()
            msgs = []
            if BLE_ENABLED:
                _scan_ble(msgs)
            if CLIMATE_ENABLED:
                _scan_climate(msgs)
            _mqtt_publish(msgs)
            duration = time.time() - start
            if duration < SCAN_INTERVAL:
                time.sleep(SCAN_INTERVAL - duration)
        except KeyboardInterrupt:
            LOG.info("Shutting down...")
            if video:
                video.stop()
            sys.exit()
        except:
            LOG.exception("Encountered unexpected error")