import board
import adafruit_si7021
from .config import LOG, CLIMATE_PUBLISH_THRESHOLD

class ClimateReading:
    def __init__(self, temperature=None, humidity=None, publish=False):
        self.temperature = temperature
        self.humidity = humidity
        self.publish = publish


class ClimateScanner:
    def __init__(self):
        self.sensor = adafruit_si7021.SI7021(board.I2C())
        self.last_published = None
    
    def scan(self):
        LOG.debug("Reading climate sensor...")
        reading = ClimateReading(
            round(self.sensor.temperature*1.8+32, 2),
            round(self.sensor.relative_humidity, 2)
        )
        if (
            self.last_published is None
            or abs((reading.temperature - self.last_published.temperature) / self.last_published.temperature) > CLIMATE_PUBLISH_THRESHOLD 
            or abs((reading.humidity - self.last_published.humidity) / self.last_published.humidity) > CLIMATE_PUBLISH_THRESHOLD 
        ):
            reading.publish = True
            self.last_published = reading
        LOG.debug(f"Climate reading is: {vars(reading)}")
        return reading


if __name__ == "__main__":
    import time
    from .config import SCAN_INTERVAL
    print(f"Starting climate sensor.")
    scanner = ClimateScanner()
    while True:
        reading = scanner.scan()
        print(f"Temp: {reading.temperature}{chr(176)}, Humidity: {reading.humidity}% {'[PUBLISH]' if reading.publish else ''}")
        time.sleep(SCAN_INTERVAL)