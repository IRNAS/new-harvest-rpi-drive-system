#!/bin/bash
sleep 10
xset s noblank
xset s off
xset -dpms
/usr/bin/chromium-browser --kiosk http://localhost:1234/calibration --no-sandbox