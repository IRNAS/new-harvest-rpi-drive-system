#!/bin/bash
sleep 1
xset s noblank
xset s off
xset -dpms
/usr/bin/chromium-browser --kiosk http://localhost:1234/calibration --no-sandbox --disable-pinch --overscroll-history-navigation=0 --test-type
