import sys
import logging
from hardware.postep256usb import PoStep256USB, DRIVER_RUN, DRIVER_SLEEP

log = logging.getLogger()
log.setLevel(logging.ERROR)

POSTEP_ADDRESS = 0x46

DC_MODE = 0
STEPPER_MODE = 1

class Direction():
    ACW = 0
    CW = 1

class Motor():
    def __init__(self, mode=STEPPER_MODE):
        """Init stepper motor control"""

        self.postep = None
        self.current_speed = 0
        self.current_direction = "cw"

        self.current_settings = []
        self.is_gain = 0

        self.mode = mode
        
        try:
            self.postep = PoStep256USB(logging.INFO)
            if self.postep.device is None:
                print("Driver not found, exiting.")
                sys.exit(0)

            self.postep.read_configuration()
            self.postep.set_run_sleep_mode(DRIVER_SLEEP)

            ret = self.set_speed(self.current_speed)

        except Exception as e:
            self.postep = None
            print(f"Failed to init postep driver with error: {e}")

    def set_speed(self, speed):
        """Set speed to stepper motor"""
        print(f"Setting motor speed: {speed}")
        self.current_speed = speed
        try:
            if self.mode == DC_MODE:
                duty1_acw = 0
                duty1_ccw = 0
                duty2_acw = 0
                duty2_ccw = 0

                if self.current_direction == "cw":
                    direction = 1
                    duty1_ccw = 0
                    duty2_ccw = speed
                if self.current_direction == "acw":
                    duty1_acw = 0
                    duty2_acw = speed


                
                ret = self.postep.set_pwm(duty1_ccw, duty2_ccw, duty1_acw, duty2_acw)
                return ret
                
            if self.mode == STEPPER_MODE:        
                ret = self.postep.set_requested_speed(self.current_speed, self.current_direction)  # set speed
                return ret
        
        except Exception as e:
            log.error(f"An exception occured when trying to set stepper speed: {e}")
            return None
      

    def map_gain(self, gain):
        if gain == 0:
            return 5
        if gain == 1:
            return 10
        if gain == 2:
            return 20
        if gain == 3:
            return 40

    def fullscale_current_to_torque(self, fsc, is_gain):
        """Convert fullscale current to torque value"""
        torque = min(int(fsc * (256 * self.map_gain(is_gain) * 0.033) / 2.75), 255)
        print(f"Calculated torque: {torque}")
        return torque

    def current_to_reg_val(self, curr):
        """Convert current to register value"""
        reg_val = int(curr * 123)
        return reg_val

    def get_driver_settings(self):
        received = self.postep.read_driver_settings()
        settings = {}

        ctrl_reg = received[40:42]
        print(f"Control register:{ctrl_reg}")

        microstepping = (ctrl_reg[0] & 0x78) >> 3  # this is good
        print(f"Microstep setting: {microstepping}")
        settings["microstepping"] = microstepping

        is_gain = ctrl_reg[1] & 0x03
        print(f"Read is_gain: {is_gain}")
        settings["isgain"] = is_gain
        self.is_gain = is_gain

        torque = received[42:44]  # actually torque setting - convert to fs current
        print(f"Read torque: {torque[0]}")
        settings["torque"] = torque[0]

        fsc = (2.75 * torque[0]) / (256 * self.map_gain(is_gain) * 0.033)
        print(f"Calculated full scale current: {fsc}")
        settings["fullscale_current"] = round(fsc, 2)

        idle_current_reg = received[57:59]
        print(f"Set idle current: {idle_current_reg}")

        idle_current = idle_current_reg[0] / 123
        print(f"Calculated current: {idle_current}")
        settings["idle_current"] = round(idle_current, 2)

        overheat_current_reg = received[59:61]
        print(f"overheat current: {overheat_current_reg}")  # works

        overheat_current = overheat_current_reg[0] / 123
        print(f"Calculated current: {overheat_current}")  # works
        settings["overheat_current"] = round(overheat_current, 2)

        self.current_settings = received

        return settings

    def set_driver_settings(self, fsc=None, idlec=None, overheatc=None, step_mode=None):

        print(f"fsc: {fsc}, idlec: {idlec}, overheatc: {overheatc}, step_mode: {step_mode}")
        if fsc is not None:
            torque = self.fullscale_current_to_torque(float(fsc), self.is_gain)
            self.current_settings[42] = torque
        if idlec is not None:
            idle_current = self.current_to_reg_val(float(idlec))
            self.current_settings[57] = idle_current
        if overheatc is not None:
            overheat_current = self.current_to_reg_val(float(overheatc))
            self.current_settings[59] = overheat_current
        if step_mode is not None:
            current_ctrl_reg = self.current_settings[40]
            current_ctrl_reg &= 0x87
            new_ctrl_reg = current_ctrl_reg | (int(step_mode) << 3)
            self.current_settings[40] = new_ctrl_reg

        self.postep.write_driver_settings(self.current_settings)

    def get_speed(self):
        return self.current_speed

    def set_direction(self, direction):
        """Set direction"""
        try:
            self.current_direction = direction
            print(f"Current set direction: {self.current_direction}")
            ret = self.set_speed(self.current_speed)
            return ret
        except Exception as e:
            log.error(f"An exception occured when trying to set stepper direction: {e}")
            return None

    def get_direction(self):
        return self.current_direction

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