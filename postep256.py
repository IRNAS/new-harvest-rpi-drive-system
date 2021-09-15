""" Follow installation instructions on https://github.com/IRNAS/postep256-pyusb-driver to install usb drivers"""

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

        #print(self.device)
        self.device.reset()

        # Set the active configuration. With no arguments, the first configuration will be the active one
        self.device.set_configuration()

        # Claim interface 0
        usb.util.claim_interface(self.device, 0)

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

    def run_sleep(self,run):

        data_list = [0] * 64
        # request data streaming
        data_list[1] = 0xA1
        if run is True:
            data_list[20] = 0x01
        # write to driver
        logging.info("postep_run_sleep {}".format(run))
        self.write_to_postep(data_list)
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

    def move_speed(self,speed,direction="cw"):

        data_list = [0] * 64
        # request data streaming
        data_list[1] = 0x90
        #480000 kHz/step_value = speed
        if speed is not 0:
            step_values=480000/speed
        else:
            step_values=480000
        data_list[20:24]=struct.pack('<I', int(step_values))
        if direction == "acw":
            data_list[24]=0x01
        # write to driver
        logging.info("postep_move_speed {} dir {}".format(speed, direction))
        self.write_to_postep(data_list)
        # write again - TODO this is an unknown bug
        self.write_to_postep(data_list)
        # request data
        received = self.read_from_postep(500)
        # check if response is valid
        if(received[15]!=0x90):
            logging.error("Bad response: {}".format(received[15]))
            return False
        return True

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
        logging.info("postep_move_trajectory to {} speed {} accel {} decel {} endsw {}".format(final_position,max_speed,max_accel,max_decel,endsw))
        self.write_to_postep(data_list)
        # request data
        received = self.read_from_postep(500)
        # check if response is valid
        if(received[15]!=0xb1):
            logging.error("Bad response: {}".format(received[15]))
            return False
        return True

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
        try:
            data = self.device.read(IN_ENPOINT, 64, timeout)
        except usb.core.USBError as e:
            print ("Error reading response: {}".format(e.args))
            return None
        logging.debug("Receive command: {}".format(bytes(data).hex()))
        if len(data) == 0:
            logging.error("No data received")
            return None

        return data
