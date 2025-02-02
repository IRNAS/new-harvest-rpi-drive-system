#!/bin/bash

for i in {1..5}; do
    if ping -c 1 google.com &> /dev/null; then
        echo "Internet connection is available."
        break
    else
        echo "No internet connection. Retrying..."
        sleep 1
    fi
done

cd /home/pi/new-harvest-rpi-drive-system
git config --global --add safe.directory /home/pi/new-harvest-rpi-drive-system
git pull

sudo python3 -m gui.index