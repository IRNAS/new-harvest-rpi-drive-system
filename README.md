# new-harvest-rpi-drive-system

## PoStep60-256-pyusb-driver
To install required driver for the PoStep60-256-pyusb module follow installation instructions found [here](https://github.com/IRNAS/postep256-pyusb-driver).

## Installation
1. Clone this repo with `git clone https://github.com/IRNAS/new-harvest-rpi-drive-system.git`.
2. Install required Python modules with `sudo pip3 install -r requirements.txt`.
3. Enable the One Wire interface with the set pin (GPIO 8) by adding `dtoverlay=w1-gpio,gpiopin=8` to `/boot/config.txt`.
4. Install vnc virtual screen following [these steps](https://medium.com/coinmonks/run-raspberry-pi-in-a-true-headless-state-cfb3431667de).
5. Download Anydesk with `wget https://download.anydesk.com/rpi/anydesk_6.1.1-1_armhf.deb`
6. Run `sudo apt --fix-broken install ./anydesk_6.1.1-1_armhf.deb`
7. Configure realvnc-vnc-server https://help.realvnc.com/hc/en-us/articles/360002249917-VNC-Connect-and-Raspberry-Pi#setting-up-your-raspberry-pi-0-0. This will enable function of AnyDesk as well.
8. Add `X11Forwarding yes` to the end of `/etc/ssh/sshd_config`
9. Set a non-default value for Screen resolution in `sudo raspi-config`

## Usage
Run the program from the main directory with `sudo python3 -m gui.index`.

Available controls:
* Set Speed - text input in interval [0, 10000], to set speed click the `Set` button
* Direction Setting - slider with "ACW" and "CW" values, `on change` of slider value the motor changes direction
* Motor Control - Start, Stop, Set - buttons, appropriate action is triggered on the `click` of a button
