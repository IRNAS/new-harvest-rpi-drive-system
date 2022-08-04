import os
import sys
import platform
import usb.core
import usb.util
import usb.backend.libusb1
import time
import struct
import logging
os.environ['PYUSB_DEBUG'] = 'debug' #for extra debugging of USB

VENDOR_ID = 0x1dc3
PRODUCT_ID = 0x0641
OUT_ENPOINT = 0x01
IN_ENPOINT = 0x81

DRIVER_RUN = True
DRIVER_SLEEP = False

class PoStep256USB(object):
    """PoStep256USB class"""
    def __init__(self,log_level=logging.INFO):
        self.was_kernel_driver_active = False
        self.device = None

        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S', level=log_level)
        
        logging.info("Detected platform {} with arch {}".format(platform.system(),platform.architecture()[0]))
        if platform.system() == 'Windows':
            # required for Windows only
            # libusb DLLs from: https://sourcefore.net/projects/libusb/
            
            arch = platform.architecture()
            if arch[0] == '32bit':
                backend = usb.backend.libusb1.get_backend(find_library=lambda x: "libusb/x86/libusb-1.0.dll") # 32-bit DLL, select the appropriate one based on your Python installation
                
            elif arch[0] == '64bit':
                backend = usb.backend.libusb1.get_backend(find_library=lambda x: "libusb/x64/libusb-1.0.dll") # 64-bit DLL

            self.device = usb.core.find(backend=backend, idVendor=VENDOR_ID, idProduct=PRODUCT_ID)
            
            
        elif platform.system() == 'Linux':
            self.device = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)


            # if the OS kernel already claimed the device
            if self.device is not None and self.device.is_kernel_driver_active(0) is True:
                # tell the kernel to detach
                self.device.detach_kernel_driver(0)
                self.was_kernel_driver_active = True
        else:
            self.device = usb.core.find(idVendor=VENDOR_ID, idProduct=PRODUCT_ID)

        if self.device is None:
            logging.error("Driver not found, make sure it is attached.")
            return

        # print(self.device)
        self.device.reset()

        # Set the active configuration. With no arguments, the first configuration will be the active one
        self.device.set_configuration()

        # Claim interface 0
        usb.util.claim_interface(self.device, 0)

        self.configuration = self.read_configuration()

        # initialize motor parameter
        self.max_speed = 1000
        self.max_accel = 1000
        self.max_decel = 1000
        self.endsw = None
    
    def __del__(self):
        if self.device is not None:
            usb.util.release_interface(self.device, 0)

        # This applies to Linux only - reattach the kernel driver if we previously detached it
        if self.was_kernel_driver_active == True:
            self.device.attach_kernel_driver(0)
            logging.info("Kernel driver reattached.")


    def get_device_info(self):
        data_list = [0] * 64

        data_list[0] = 0x00
        data_list[1] = 0x01
        data_list[63] = 0x00

        self.write_to_postep(data_list)
        # request data with 500ms tuimeout
        received = self.read_from_postep(500)
        print(list(received))

        received = list(received)

        bl_fw_version = (received[1] << 8) | received[2]
        print(f"Bootloader fw version: {bl_fw_version}")

        app_fw_version = (received[3] << 8) | received[4]
        print(f"App fw version: {app_fw_version}")

        supply_voltage = (received[8] * 256 + received[9]) * 0.072
        print(f"Supply voltage: {supply_voltage}")

        temperature = (received[44] * 256 + received[45]) * 0.125
        print(f"Device temperature: {temperature}")

        status = received[46]  # 0x01 - sleep, 0x02 - active, 0x03 - idle, 0x04 - overheated, 0x05 - pwm mode
        print(f"Device status: {status}")
        # check if response is valid
        # if(received[0]!=0x02):
        #     logging.error("Bad response: {}".format(received[0]))
        #     return False
        # return True

    def enable_rt_stream(self):

        data_list = [0] * 64
        # request data streaming
        data_list[1] = 0xA0
        # write to driver
        logging.info("postep_enable_rt_stream")
        self.write_to_postep(data_list)
        # request data with 500ms tuimeout
        received = self.read_from_postep(500)
        # check if response is valid
        if(received[0]!=0x02):
            logging.error("Bad response: {}".format(received[0]))
            return False
        return True

    def read_stream(self):
        received = self.read_from_postep(500)
        #parse data
        status = {}
        status["pos"], status["speed"], status["final"] = struct.unpack('>iii', received[20:32])
        status["endswitch"]= bool((received[6]>>6)&0x01)
        logging.debug("Status: {}".format(status))
        return status

    def set_run_sleep_mode(self,run):

        data_list = [0] * 64
        # request data streaming
        data_list[1] = 0xA1
        if run is True:
            data_list[20] = 0x01
        # write to driver
        logging.info("postep_run_sleep {}".format(run))
        self.write_to_postep(data_list)
        # self.write_to_postep(data_list)
        # request data
        received = self.read_from_postep(500)
        # check if response is valid
        if received is None:
            return False
            logging.error("No response.")
        if(received[0]!=0x02):
            logging.error("Bad response: {}".format(received[0]))
            return False
        return True

    def set_requested_speed(self,speed,direction="cw"):

        # print(f"Setting requested speed: {speed} with direction {direction}")
        data_list = [0] * 64
        # request data streaming
        data_list[1] = 0x90
        #480000 kHz/step_value = speed
        if speed != 0:
            step_values=480000/speed
        else:
            step_values=480000
        data_list[20:24]=struct.pack('<I', int(step_values))
        # print(data_list[20:24])
        if direction == "acw":
            data_list[24]=0x01
        # write to driver
        logging.info("postep_move_speed {} dir {}".format(speed, direction))
        self.write_to_postep(data_list)
        # write again - TODO this is an unknown bug
        self.write_to_postep(data_list)
        # request data
        received = self.read_from_postep(500)
        # print(received)
        # check if response is valid
        if(received[15]!=0x90):
            logging.error("Bad response: {}".format(received[15]))
            return False
        return True

    def set_run(self, run):

        data_list = [0] * 64
        data_list[1] = 0xA1
        data_list[20] = 0x01 if run else 0x00

        self.write_to_postep(data_list)

        received = self.read_from_postep(500)
        print(list(received))
        print(f"Byte at 15: {received[15]}")

    def read_configuration(self):
        data_list = [0] * 64
        data_list[1] = 0x88

        self.write_to_postep(data_list)
        received = self.read_from_postep(500)
        print(list(received))

        received = list(received)

        velocity_max = int.from_bytes(received[24:28], byteorder="little")
        print(f"raw bytes velocity: {received[24:28]}")
        print(f"Velocity max: {velocity_max}")

        acceleration = int.from_bytes(received[28:32], byteorder="little")
        print(f"Raw bytes acceleration: {received[28:32]}")
        print(f"Acceleration: {acceleration}")

        deceleration = int.from_bytes(received[32:36], byteorder="little")
        print(f"Raw bytes deceleration: {received[32:36]}")
        print(f"Deceleration: {deceleration}")

        settings_byte = received[36]
        print(f"Settings byte: {settings_byte}")

        return received
    def write_driver_settings(self, settings_list):
        data_list = [0] * 64
        data_list[1] = 0x80
        data_list[20:36] = settings_list[40:56]
        data_list[37] = settings_list[62]
        data_list[38:44] = settings_list[56:62]
        data_list[44] = settings_list[63]

        print(f"Writing data list: {data_list}")
        self.write_to_postep(data_list)
        self.write_to_postep(data_list)
        time.sleep(1)
        received = self.read_from_postep(500)
        print(list(received))

    def read_driver_settings(self):
        data_list = [0] * 64
        data_list[1] = 0x81

        self.write_to_postep(data_list)
        received = self.read_from_postep(500)
        print(list(received))

        received = list(received)

        return received

    def change_configuration(self, velocity=10000, acceleration=2000, deceleration=2000, settings=0):
        data_list = [0] * 64
        data_list[1] = 0x87

        # set velocity
        data_list[24:28] = list(velocity.to_bytes(4, "little"))

        # set acceleration
        data_list[28:32] = list(acceleration.to_bytes(4, "little"))

        # set deceleration
        data_list[32:36] = list(deceleration.to_bytes(4, "little"))

        # set settings
        data_list[36] = settings

        self.write_to_postep(data_list)

        received = self.read_from_postep(500)
        print(list(received))
        print(f"Byte at 15: {received[15]}")

    def set_pwm(self, duty1_ccw, duty2_ccw, duty1_acw, duty2_acw, frequency=20000):

        data_list = [0] * 64
        data_list[1] = 0xB0
        data_list[20] = 0
        data_list[21] = 0
        data_list[22] = 0
        data_list[23] = int(480000 / frequency)  # 480000 / 24 = 20000 -> 20kHz when the setting is 24

        data_list[24] = duty1_ccw
        data_list[25] = duty1_acw
        data_list[26] = duty2_ccw
        data_list[27] = duty2_acw

        print(f"Writing list: {data_list}")
        self.write_to_postep(data_list)

        received = self.read_from_postep(500)
        # print(list(received))
        # print(f"Byte at 15: {received[15]}")

        return received[15] == 0xB0

    def move_config(self,max_speed,max_accel,max_decel,endsw=None):
        '''
        Configure motion parameters

        :param int max_speed: Maximal speed
        :param int max_accel: Maximal acceleration
        :param int max_decel: Maximal deceleration
        :param str endsw: Define if endswitch is to be used in no or nc configuration, default is None
        '''
        self.max_speed=max_speed
        self.max_accel=max_accel
        self.max_decel=max_decel
        self.endws=endsw
    
    def move_to(self,position):
        self.move_trajectory(position,self.max_speed,self.max_accel,self.max_decel,self.endsw)


    def move_trajectory(self,final_position,max_speed,max_accel,max_decel,endsw=None):
        '''
        Move with drivers position tracking system by specifiying the desired position

        :param int final_position: The position where we want to move to
        :param int max_speed: Maximal speed
        :param int max_decel: Maximal deceleration
        :param bool endsw: Define if endswitch is to be used in no or nc configuration, default is None
        :return: success
        :rtype: bool
        '''
        data_list = [0] * 64
        data_list[1] = 0xb1
        #do not enable autorun
        data_list[2]= 0b00000000
        # Set trajectory final position
        data_list[20:24]=struct.pack('<i', final_position)
        # Set trajectory max speed
        data_list[24:28]=struct.pack('<I', max_speed)
        # Set traject. max acceleration
        data_list[28:32]=struct.pack('<I', max_accel)
        # Set traject. max deceleration
        data_list[32:36]=struct.pack('<I', max_decel)
        # Set InvDir<<2|NCSw<<1| SwEn
        if endsw is not None:
            data_list[36]=data_list[36]|0b00000001
            if endsw == "nc":
                data_list[36]=data_list[36]|0b00000010
        # write to driver
        error = False
        for x in range(3):
            error = True
            try:
                logging.info("postep_move_trajectory to {} speed {} accel {} decel {} endsw {}".format(final_position,max_speed,max_accel,max_decel,endsw))
                self.write_to_postep(data_list)
                # request data
                received = self.read_from_postep(500)
                # check if response is valid
                if(received[15]!=0xb1):
                    logging.error("Bad response: {}".format(received[15]))
                    
                else:
                    error = False
                    break
            except:
                logging.error("Bad response")
        return error

    def move_to_stop(self):
        #stop trajectory
        data_list = [0] * 64
        data_list[1] = 0xb2
        
        # write to driver
        self.write_to_postep(data_list)
        # request data
        logging.info("move_to_stop")
        received = self.read_from_postep(500)
        # check if response is valid
        if(received[0]!=0x02):
            logging.error("Bad response: {}".format(received[0]))
            return False
        return True

    def move_reset_to_zero(self):
        # zero trajectory
        data_list = [0] * 64
        data_list[1] = 0xb3
        
        # write to driver
        logging.info("move_reset_to_zero")
        self.write_to_postep(data_list)
        # request data
        received = self.read_from_postep(500)
        # check if response is valid
        if(received[0]!=0x02):
            logging.error("Bad response: {}".format(received[0]))
            return False
        return True

    def system_reset(self):
        # note driver will disconnect from USB
        data_list = [0] * 64
        data_list[1] = 0x02
        
        # write to driver
        logging.info("postep_system_reset")
        self.write_to_postep(data_list)

    def write_to_postep(self,data_list):

        #data_list = [0] * 64
        #for run/sleep send data[1] = 0xA1
        #data_list[0] = 0x01
        #data_list[1] = 0x90

        data = bytearray(data_list)
        logging.debug("Writing command: {}".format(bytes(data).hex()))

        num_bytes_written = 0
        try:
            num_bytes_written = self.device.write(OUT_ENPOINT, data,500)
        except usb.core.USBError as e:
            print (e.args)

        return num_bytes_written

    def read_from_postep(self, timeout):
        data = None
        for x in range(3):
            try:
                data = self.device.read(IN_ENPOINT, 64, timeout)
            except usb.core.USBError as e:
                print ("Error reading response: {}".format(e.args))
                continue
            logging.debug("Receive command: {}".format(bytes(data).hex()))
            if len(data) == 0:
                logging.error("No data received")
                data = None
                continue
            else:
                break
        return data