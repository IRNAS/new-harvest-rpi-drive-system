#!/bin/bash

cd /home/pi/new-harvest-rpi-drive-system
git config --global --add safe.directory /home/pi/new-harvest-rpi-drive-system
git pull

sudo python3 -m gui.index