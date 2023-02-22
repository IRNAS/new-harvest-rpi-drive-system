sudo pip3 install -r requirements.txt

wget https://download.anydesk.com/rpi/anydesk_6.2.1-1_armhf.deb
sudo dpkg -i anydesk_6.2.1-1_armhf.deb
sudo apt-get -f install
rm anydesk_6.2.1-1_armhf.deb
sudo systemctl daemon-reload
sudo systemctl restart anydesk

# Configure hdmi output
sudo sh -c "echo 'hdmi_force_hotplug=1' >> /boot/config.txt"
sudo raspi-config nonint do_vnc 0
sudo raspi-config nonint do_vnc_resolution "1280x1024"
# Disable screen blanking
sudo raspi-config nonint do_blanking 1

# Configure anydesk unattened access
echo "axzn42b632c" | sudo anydesk --set-password
# Save anydesk ID to file system and print it
ID=$(anydesk --get-id)
echo "================================================ 
ANYDESK ID: $ID 
================================================"
echo "$ID" > anydesk_id.txt

echo "Adding $USER to input"
sudo usermod -a -G input $USER
echo "Creating startup script"
sudo cp new_harvest.service /etc/systemd/system/new_harvest.service
sudo cp new_harvest_chromium.service /etc/systemd/system/new_harvest_chromium.service
sudo cp mount_usb.service /etc/systemd/system/mount_usb.service

sudo systemctl daemon-reload
sudo systemctl enable new_harvest.service new_harvest_chromium.service mount_usb.service
sudo systemctl start new_harvest.service new_harvest_chromium.service mount_usb.service

# Disable the executable pop up
sed -i 's/quick_exec=0/quick_exec=1/' "/home/pi/.config/libfm/libfm.conf"
# Copy the desktop entry to Dekstop
sudo cp "new_harvest.desktop" "/home/pi/Desktop/new_harvest.desktop"
# Disable the ssh warning
sudo rm /etc/xdg/lxsession/LXDE-pi/sshpwd.sh
# Remove the startup wizard
sudo rm /etc/xdg/autostart/piwiz.desktop
