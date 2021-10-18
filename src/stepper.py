import logging
from hardware.postep256 import Postep256, DRIVER_RUN, DRIVER_SLEEP, MODE_DEFAULT

POSTEP_ADDRESS = 0x46

class Stepper():
    def __init__(self):
        """Init stepper motor control"""

        self.postep = None
        self.set_speed = 0
        
        try:
            self.postep = Postep256(POSTEP_ADDRESS)
            self.postep.set_run_sleep_mode(DRIVER_SLEEP)

            ret = self.postep.read_driver_mode()
            if not ret:
                print(f"Failed to init postep driver!")
                self.postep = None

            if ret != MODE_DEFAULT:
                ret_val = self.postep.set_driver_mode(MODE_DEFAULT)
                if not ret_val:
                    logging.error("set_driver_mode failed")
                else:
                    logging.info("set_driver_mode success: {}".format(ret_val))

            ret = self.postep.set_requested_speed(self.set_speed)  # set speed to 0
            if not ret:
                logging.error(f"Failed to set speed to 0")
            else:
                ret = self.postep.read_requested_speed()
                if ret is None:
                    print(f"Failed to read requested speed")
                else:
                    if ret == 0:
                        logging.info("Successfully set speed to 0")
                    else:
                        logging.info(f"Set speed of 0 differs from read speed: {ret}")

        except Exception as e:
            self.postep = None
            print(f"Failed to init postep driver with error: {e}")

    def set_speed(self, speed):
        """Set speed to stepper motor"""
        self.set_speed = speed
        ret = self.postep.set_requested_speed(self.set_speed)  # set speed
        if not ret:
            read_speed = self.postet.read_requested_speed()
            if self.set_speed == read_speed:
                return True
            else:
                return False
        return False

    def get_speed(self):
        """Return last successfuly set speed"""
        ret = self.postep.read_current_speed()
        return ret

    def set_acceleration(self, accel):
        """Set acceleration in steps/s^2"""
        ret = self.postep.set_acceleration(accel)
        return ret

    def get_acceleration(self):
        """Read acceleration setting from driver in steps/s^2"""
        ret = self.postep.read_acceleration()
        return ret

    def start_motor(self):
        """Start motor"""
        ret = self.postep.set_run_sleep_mode(DRIVER_RUN)
        return ret

    def stop_motor(self):
        """Stop motor"""
        ret = self.postep.set_run_sleep_mode(DRIVER_SLEEP)
        return ret