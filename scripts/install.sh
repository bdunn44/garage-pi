#!/bin/bash
# Get script dir
SCRIPTS_PATH=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
chmod +x "$SCRIPTS_PATH/install.sh"
chmod +x "$SCRIPTS_PATH/run.sh"
chmod +x "$SCRIPTS_PATH/test.sh"

# Install python libraries
echo "Installing Python libraries..."
sudo apt-get install -y python3-pip
pip3 install -r "$SCRIPTS_PATH/../requirements.txt"

# Enable bluepy to run without root
BPH_LOC=`find /usr/local/lib -name bluepy-helper`
sudo setcap cap_net_raw+e "$BPH_LOC"
sudo setcap cap_net_admin+eip "$BPH_LOC"

# Configure go2rtc
echo "Configuring go2rtc video streaming..."
chmod +x "$SCRIPTS_PATH/../bin/go2rtc_linux_armv6"
CAM_CMD="libcamera-vid"
if ! command -v $CAM_CMD &> /dev/null
then
    CAM_CMD="raspivid"
fi
cat << EOF > "$SCRIPTS_PATH/../config/go2rtc.yaml"
streams:
  cam: exec:${CAM_CMD} --width 1280 --height 720 --framerate 15 -t 0 --inline -o -
EOF

# Create service, run at boot
echo "Configuring garage-pi as a service to run at boot..."
cat << EOF > /etc/systemd/system/garage-pi.service
[Unit]
Description=Service that keeps running the echo-server from startup.
After=network.target

[Install]
WantedBy=multi-user.target

[Service]
Type=simple
WorkingDirectory=$SCRIPTS_PATH
ExecStart=$SCRIPTS_PATH/run.sh
Restart=always
RestartSec=5
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=%n
EOF
sudo systemctl daemon-reload
sudo systemctl enable garage-pi.service

# Run blinka install script
echo "Installing libraries for SI7021 climate sensor..."
sudo python3 "$SCRIPTS_PATH/raspi-blinka.py"