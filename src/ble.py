from bluepy.btle import Scanner
from .config import LOG, BLE_PUBLISH_THRESHOLD

class DeviceInfo():
    def __init__(self, name=None, rssi=None, detected=False, publish=False):
        self.name = name
        self.rssi = rssi
        self.detected = detected
        self.publish = publish


class BLEScanner(Scanner):
    def __init__(self, filter=[]):
        Scanner.__init__(self)
        self.filter = [addr.lower() for addr in filter]
        self.last_published = {addr: DeviceInfo() for addr in self.filter}
    
    def scan(self, timeout=10):
        LOG.debug("Scanning for BLE devices...")
        devices = super().scan(timeout)
        device_ct = len(devices)
        if self.filter:
            devices = [d for d in devices if d.addr.lower() in self.filter]
        LOG.debug(f"Detected {device_ct} BLE device(s) ({len(devices)} after applying filter)")
        result = {}
        # Find previously detected devices that are now out of range
        for addr, info in self.last_published.items():
            if addr not in [d.addr for d in devices]:
                info.publish = info.detected # was previously detected
                info.detected = False
                info.rssi = None
                result[addr] = info
                LOG.debug(f"Device {addr} ({info.name}) is no longer in range")
        # Update in-range devices
        for device in devices:
            old_info = self.last_published.get(device.addr)
            new_info = DeviceInfo(device.getValueText(9), device.rssi, True)
            result[device.addr] = new_info
            if (
                not old_info
                or old_info.detected != new_info.detected
                or abs((new_info.rssi - old_info.rssi) / old_info.rssi) > BLE_PUBLISH_THRESHOLD
            ):
                new_info.publish = True
                self.last_published[device.addr] = new_info
            LOG.debug(f"BLE data for {device.addr}: {vars(new_info)}")
        return result


if __name__ == '__main__':
    import datetime
    from .config import BLE_MAC_WATCH_LIST, SCAN_INTERVAL
    
    print(f"Starting BLE scanner. Looking for: {BLE_MAC_WATCH_LIST}")
    scanner = BLEScanner(BLE_MAC_WATCH_LIST)
    while True:
        t = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for addr, info in scanner.scan(SCAN_INTERVAL).items():
            print(f"{t} {addr} {info.name} {str(info.rssi) + ' dBm' if info.detected else 'Not Detected'} {'[PUBLISH]' if info.publish else ''}")