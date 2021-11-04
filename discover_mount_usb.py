import subprocess
import os
import time

while True:

    # find all block devices
    proc = subprocess.Popen(["sudo", "blkid"], stdout=subprocess.PIPE)
    (output, err) = proc.communicate()
    p_status = proc.wait()
    devices = filter(lambda x: "/dev/sd" in x, output.decode("utf-8").split("\n"))  # find all devices with /dev/sd*
    # print(list(devices))

    proc = subprocess.Popen(["cat", "/etc/fstab"], stdout=subprocess.PIPE)
    (output, err) = proc.communicate()
    p_status = proc.wait()
    fstab_file = output.decode("utf-8").split("\n")
    # print(fstab_file)
    device_line_exists = False
    device_UUID = None
    
    # if len(list(devices)) == 0:
    #     print("No storage devices found")

    for storage_dev in list(devices):
        print(storage_dev)
        dev_UUID = [x for x in storage_dev.split(" ")  if "UUID" in x][0]
        print(f"Dev_UUID: {dev_UUID}")
        dev_UUID = dev_UUID[6:-1]
        device_UUID = dev_UUID  #
        for dev in fstab_file:
            #print(dev)
            if dev_UUID in dev:
                device_line_exists = True

    # add line to /etc/fstab if device is not mounted
    if not device_line_exists and device_UUID is not None:
        device_mount_line = f"UUID={device_UUID} /mnt/storage vfat defaults,auto,users,rw,nofail,umask=000 0 0"
        print(device_mount_line)
        os.system(f'echo "{device_mount_line}" >> /etc/fstab')
        # proc = subprocess.Popen(["cat", device_mount_line, ">>", "/etc/fstab"], stdout=subprocess.PIPE)
        # (output, err) = proc.communicate()
        # p_status = proc.wait()

    # try to remount device
    if device_line_exists:
        print("Trying to remount device")
        os.system(f"mount -U {device_UUID}")

    time.sleep(0.1)