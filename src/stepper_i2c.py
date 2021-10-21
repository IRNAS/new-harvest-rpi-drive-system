import logging
from hardware.postep256 import PoStep256, DRIVER_RUN, DRIVER_SLEEP, MODE_DEFAULT

log = logging.getLogger()

POSTEP_ADDRESS = 0x46

class Direction():
    ACW = 0
    CW = 1

class Stepper():
    def __init__(self):
        """Init stepper motor control"""

        self.postep = None
        self.current_speed = 0
        
        try:
            self.postep = PoStep256(POSTEP_ADDRESS)
            self.postep.set_run_sleep_mode(DRIVER_SLEEP)

            ret = self.postep.read_driver_mode()
            if not ret:
                # print(f"Failed to init postep driver!")
                self.postep = None

            if ret != MODE_DEFAULT:
                ret_val = self.postep.set_driver_mode(MODE_DEFAULT)
                if not ret_val:
                    logging.error("set_driver_mode failed")
                else:
                    logging.info("set_driver_mode success: {}".format(ret_val))

            ret = self.postep.set_requested_speed(self.current_speed)  # set speed to 0
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
        self.current_speed = speed
        try:
            ret = self.postep.set_requested_speed(self.current_speed)  # set speed
            if not ret:
                read_speed = self.postep.read_requested_speed()
                if self.current_speed == read_speed:
                    return True
                else:
                    return False
            return False
        except Exception as e:
            log.error(f"An exception occured when trying to set stepper speed: {e}")
            return None

    def get_speed(self):
        """Return last successfuly set speed"""
        try:
            ret = self.postep.read_current_speed()
            return ret
        except Exception as e:
            log.error(f"An exception occured when trying to get stepper speed: {e}")
            return None

    def set_direction(self, direction):
        """Set direction"""
        try:
            self.current_direction = direction
            ret = self.postep.set_invert_direction(self.current_direction)
            if not ret:
                read_direction = self.postep.read_auto_run_invert_direction_status()
                if self.current_direction == read_direction:
                    return True
                else:
                    return False
            return False
        except Exception as e:
            log.error(f"An exception occured when trying to set stepper direction: {e}")
            return None

    def get_direction(self):
        """Read set direction"""
        try:
            ret = self.postep.read_auto_run_invert_direction_status()
            return ret
        except Exception as e:
            log.error(f"An exception occured when trying to get stepper direction: {e}")
            return None

    def set_acceleration(self, accel):
        """Set acceleration in steps/s^2"""
        self.acceleration = accel
        try:
            ret = self.postep.set_acceleration(self.acceleration)
            if not ret:
                read_accel = self.postep.read_acceleration()
                if self.acceleration == read_accel:
                    return True
                else:
                    return False
            return False
        except Exception as e:
            log.error(f"An exception occured when trying to set stepper acceleration: {e}")
            return None

    def get_acceleration(self):
        """Read acceleration setting from driver in steps/s^2"""
        try:
            ret = self.postep.read_acceleration()
            return ret
        except Exception as e:
            log.error(f"An exception occured when trying to get stepper acceleration: {e}")
            return None

    def start_motor(self):
        """Start motor"""
        try:
            ret = self.postep.set_run_sleep_mode(DRIVER_RUN)
            return ret
        except Exception as e:
            log.error(f"An exception occured when trying to start stepper motor: {e}")
            return None

    def stop_motor(self):
        """Stop motor"""
        try:
            ret = self.postep.set_run_sleep_mode(DRIVER_SLEEP)
            return ret
        except Exception as e:
            log.error(f"An exception occured when trying to stop stepper motor: {e}")
            return None