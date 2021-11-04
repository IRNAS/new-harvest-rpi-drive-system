# new-harvest-rpi-drive-system

## PoStep60-256-pyusb-driver
To install required driver for the PoStep60-256-pyusb module follow installation instructions found [here](https://github.com/IRNAS/postep256-pyusb-driver).

## Installation
1. Clone this repo with `git clone https://github.com/IRNAS/new-harvest-rpi-drive-system.git`.
2. Install required Python modules with `sudo pip3 install -r requirements.txt`.
3. Enable the One Wire interface with the set pin (GPIO 8) by adding `dtoverlay=w1-gpio,gpiopin=8` to `/boot/config.txt`.

## Usage
Run the program from the main directory with `sudo python3 -m gui.index`.

Available controls:
* Set Speed - text input in interval [0, 10000], to set speed click the `Set` button
* Direction Setting - slider with "ACW" and "CW" values, `on change` of slider value the motor changes direction
* Motor Control - Start, Stop, Set - buttons, appropriate action is triggered on the `click` of a button