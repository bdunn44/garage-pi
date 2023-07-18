import yaml
import os
import logging
import logging.config

ROOT_PATH = os.path.join(os.path.dirname(__file__), os.pardir, "config")
CONFIG_PATH = os.path.join(ROOT_PATH, 'config.yaml')
LOG_CONFIG_PATH = os.path.join(ROOT_PATH, 'logging.conf')

logging.config.fileConfig(LOG_CONFIG_PATH)
LOG = logging.getLogger("garage-pi")

_CONFIG = {
    "scan-interval": 5,
    "mqtt": {
        "hostname": None,
        "port": 1883,
        "auth": {
            "username": None,
            "password": None
        },
        "topic": "garage-pi"
    },
    "climate": {
        "enabled": True,
        "publish-threshold_pct": 0
    },
    "ble": {
        "enabled": True,
        "mac-watch-list": [],
        "publish-threshold-pct": 0
    },
    "video": {
        "enabled": True
    }
}
SCAN_INTERVAL = None
MQTT_HOST = None
MQTT_PORT = None
MQTT_AUTH = None
MQTT_TOPIC = None
CLIMATE_ENABLED = None
CLIMATE_PUBLISH_THRESHOLD = None
BLE_ENABLED = None
BLE_MAC_WATCH_LIST = None
BLE_PUBLISH_THRESHOLD = None
VIDEO_ENABLED = None

def _merge(source, destination):
    """
    run me with nosetests --with-doctest file.py

    >>> a = { 'first' : { 'all_rows' : { 'pass' : 'dog', 'number' : '1' } } }
    >>> b = { 'first' : { 'all_rows' : { 'fail' : 'cat', 'number' : '5' } } }
    >>> merge(b, a) == { 'first' : { 'all_rows' : { 'pass' : 'dog', 'fail' : 'cat', 'number' : '5' } } }
    True
    """
    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            _merge(value, node)
        else:
            destination[key] = value
    return destination

with open(CONFIG_PATH, "r") as stream:
    _CONFIG = _merge(yaml.safe_load(stream), _CONFIG)
    LOG.debug(f"Using config: {_CONFIG}")
    SCAN_INTERVAL = _CONFIG["scan-interval"]
    MQTT_HOST = _CONFIG["mqtt"]["hostname"]
    MQTT_PORT = _CONFIG["mqtt"]["port"]
    MQTT_AUTH = _CONFIG["mqtt"]["auth"] if _CONFIG["mqtt"]["auth"]["username"] else None
    MQTT_TOPIC = _CONFIG["mqtt"]["topic"]
    CLIMATE_ENABLED = _CONFIG["climate"]["enabled"]
    CLIMATE_PUBLISH_THRESHOLD = _CONFIG["climate"]["publish-threshold-pct"] / 100
    BLE_ENABLED = _CONFIG["ble"]["enabled"]
    BLE_MAC_WATCH_LIST = _CONFIG["ble"]["mac-watch-list"]
    BLE_PUBLISH_THRESHOLD = _CONFIG["ble"]["publish-threshold-pct"] / 100
    VIDEO_ENABLED = _CONFIG["video"]["enabled"]