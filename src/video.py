import os
from subprocess import Popen, PIPE, STDOUT, TimeoutExpired
from threading import Thread
from .config import LOG

class VideoSubprocess():
    def __init__(self):
        root = os.path.join(os.path.dirname(__file__), "..")
        self.bin = os.path.join(root, "bin", "go2rtc_linux_armv6")
        self.config = os.path.join(root, "config", "go2rtc.yaml")
        self.proc = None
    
    def _log_output(self):
        for line in iter(self.proc.stdout.readline, b''):
            LOG.info(f"go2rtc: {line.decode('CP437').strip()}")
        self.proc.stdout.close()
    
    def start(self):
        self.proc = Popen([self.bin, "-config", self.config], stdout=PIPE, stderr=STDOUT)
        t = Thread(target=self._log_output)
        t.daemon = True # thread dies with the program
        t.start()
    
    def stop(self):
        self.proc.terminate()
        try:
            self.proc.wait(timeout=2)
        except TimeoutExpired:
            self.proc.kill()
            self.proc.wait(timeout=2)


if __name__ == "__main__":
    print(f"Starting video stream.")
    video = VideoSubprocess()
    try:
        video.start()
        video.proc.wait()
    except KeyboardInterrupt:
        video.stop()