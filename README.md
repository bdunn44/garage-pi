# garage-pi
Raspberry Pi setup for a very low latency WebRTC camera stream (via go2rtc) plus Bluetooth Low Energy sensor (via BluePy) and humidity sensor (Adafruit SI7021) for home automation.

I wanted a good presence detection solution for the cars in my garage to drive automations in Home Assistant (for example, opening and closing garage doors). This accomplished that via object detection applied to the camera stream (I use Frigate) and by sensing a BLE beacon (my Tesla has a one built in, but you could potentially keep a third party beacon in the glovebox - I haven't tested this). The temp and humidity sensor is an added bonus.

BLE and climate readings are published via MQTT.

No extra hardware is needed for video and BLE functionality but you'll need an [Adafruit SI7021](https://www.adafruit.com/product/3251) to enable the climate sensor . The code could be easily modified for another sensor if you have one handy.

## Download & Configure
To download, simply `git clone https://github.com/bdunn44/garage-pi`. To configure, modify `garage-pi/config/config.yaml` in the following format:
```yaml
scan-interval: 5 #<-- scan every 5 seconds 
mqtt:
  hostname: my-mqtt.my-domain.com #<-- MQTT server host/IP
  port: 1883 #<-- MQTT server port
  auth:
    username: mqtt_client #<-- MQTT client username
    password: my_password #<-- MQTT client password
  topic: garage-pi #<-- MQTT topic to post to
climate:
  enabled: true #<-- Enable/disable the climate sensor
  publish-threshold-pct: 1 #<-- Only publish changes in temp/humidity that are +/- 1% of the previous reading
ble:
  enabled: true #<-- Enable/disable the BLE sensor
  mac-watch-list: #<-- List of BLE beacon MAC addresses to scan for
    - 'eb:8e:ef:d3:e7:98' 
  publish-threshold-pct: 10 #<-- Only publish changes in signal strength (RSSI) that are +/- 10% of the previous reading
video:
  enabled: true #<-- Enable/disable video streaming
```

The video stream configuration is generated during installation and can be found in `config/go2rtc.yaml`. See the [go2rtc documentation](https://github.com/AlexxIT/go2rtc/tree/v1.6.0) for more details on configuration.

Logs will be found in `garage-pi.log` the project's root directory. You can modify `config/logging.conf` to modify log levels and output. See documentation on the [Python logging module](https://docs.python.org/3/library/logging.html) for details.

## Install
To install:
```
cd garage-pi
chmod +x scripts/install.sh
./install.sh
```

Once installed it will automatically start upon boot. You can check the service's status and start/stop with standard systemd commands:
```
service garage-pi status
sudo service garage-pi stop
sudo service garage-pi start
sudo service garage-pi restart
```

## Test
You can easily test functionality with `scripts/test.sh`. Available commands are:
  - `./test.sh ble` - continuously scans for BLE beacons and prints details.
  - `./test.sh climate` - continuously takes climate readings and prints details.
  - `./test.sh ble` - starts the go2rtc server and video stream. You can view the go2rtc UI at `your-pi-address:1984`.

## MQTT Messages
MQTT messages are published to the `garage-pi/ble/[MAC address]`, `garage-pi/temperature`, and `garage-pi/humidity` topics by default (the `garage-pi` piece is configurable). The log entries below provide good example messages:

```
2023-07-16 11:01:49,951 - garage-pi - INFO - Published: {'topic': 'garage-pi/ble/eb:8e:ef:d3:e7:98', 'payload': '{"detected": true, "rssi": -81}', 'retain': True}
2023-07-16 11:01:49,954 - garage-pi - INFO - Published: {'topic': 'garage-pi/temperature', 'payload': '80.49', 'retain': True}
2023-07-16 11:01:49,960 - garage-pi - INFO - Published: {'topic': 'garage-pi/humidity', 'payload': '33.07', 'retain': True}
```

## Integration with Home Assistant
You can configure MQTT sensors to read the MQTT messages and create a sensor to capture the current state. For example:
```yaml
mqtt:
  sensor: 
    - name: garage_car_ble
      state_topic: "garage-pi/ble/eb:8e:ef:d3:e7:98"
      value_template: "{{ value_json.detected }}"
      json_attributes_topic: "garage-pi/ble/eb:8e:ef:d3:e7:98"
      icon: mdi:bluetooth-connect

    - name: garage_temperature
      state_topic: "garage-pi/temperature"
      icon: mdi:thermometer

    - name: garage_humidity
      state_topic: "garage-pi/humidity"
      icon: mdi:water-percent
```

A basic automation could simply check for the BLE sensor to flip between `True` (detected) and `False` (not detected). The example below leverages a 30-second timer to ensure any rapid changes between detected and not detected while the car is at the boundary of signal range won't cause the garage door to go up and down. 
```yaml
alias: Control Garage Door
description: ""
trigger:
  - platform: state
    entity_id:
      - sensor.garage_car_ble
    from: "False"
    to: "True"
    id: arrived
  - platform: state
    entity_id:
      - sensor.garage_car_ble
    from: "True"
    to: "False"
    id: departed
condition:
  - condition: not
    conditions:
      - condition: state
        entity_id: timer.garage_automation_active
        state: active
action:
  - choose:
      - conditions:
          - condition: trigger
            id: arrived
        sequence:
          - service: cover.open_cover
            data: {}
            target:
              entity_id: cover.garage_door
      - conditions:
          - condition: trigger
            id: departed
        sequence:
          - service: cover.close_cover
            data: {}
            target:
              entity_id: cover.garage_door
  - service: timer.start
    data: {}
    target:
      entity_id: timer.garage_automation_active
mode: single
```
