import time
import json
import logging
import datetime

from threading import Thread

from src.calibration import Calibration
from src.stepper_usb import Stepper, Direction
from src.csv_writer import CsvWriter

log = logging.getLogger()

class State():
    ERROR = -1
    IDLE = 0
    RUNNING = 1
    CALIBRATION = 2

class CalibrationStep():
    IDLE = "IDLE"
    LOW_RPM_RUNNING = "LOW_RPM_RUNNING"
    LOW_RPM_DONE = "LOW_RPM_DONE"
    HIGH_RPM_RUNNING = "HIGH_RPM_RUNNING"
    HIGH_RPM_DONE = "HIGH_RPM_DONE"
    ABORTED = "ABORTED"
    COMPLETED = "COMPLETED"

class NewHarvest():
    def __init__(self):
        """Init class with stepper motor"""

        self.stepper = None
        self.current_state = State.IDLE  # current global state

        self.current_calibration_step = CalibrationStep.IDLE

        # run all motor commands threaded so nothing is blocked
        self.thread = None
        self.stop_current_thread = False

        self.calibration = None
        self.speed_profile = None

        # functional variables
        self.current_set_flow = 0
        self.current_set_rpm = 0

        self.acceleration = 50

        self.state = {
            "flow": [],
            "rpm": [],
            "temp": []
        }

        self.csv_logging = False
        self.csv_writer = CsvWriter()

        try:
            self.stepper = Stepper()
            log.info("Initialized Stepper motor")
        except Exception as e:
            log.error(f"Failed to initialize stepper motor: {e}")

        self.state_loop_running = True

        self.state_loop = Thread(target=self.state_update_loop, daemon=True)
        self.state_loop.start()

    def __del__(self):
        self.state_loop_running = False
        if self.state_loop.is_alive():
            self.state_loop.join()

    def state_update_loop(self):
        """Periodically update state"""
        while True:
            if self.state_loop_running:
                self.state["flow"].append(self.current_set_flow)
                self.state["rpm"].append(self.current_set_rpm)
                if self.csv_logging:
                    self.csv_writer.append_row([self.current_set_flow, self.current_set_rpm])
                # current_temp = self.get_temperature()  TODO: implement when sensor is known
                # self.state["temp"].append(current_temp)[-600:] 
                self.state["flow"] = self.state["flow"][-600:]
                self.state["rpm"] = self.state["rpm"][-600:]
            else:
                break
            time.sleep(1)

    def run_thread(self, target, args):
        self.stop_current_thread = False
        self.thread = Thread(target=target, args=args)
        self.thread.start()

    def stop_thread(self):
        self.stop_current_thread = True
        if self.thread is not None:
            self.thread.join()
        print(f"Stopping thread")
        self.thread = None

    def get_postep_config(self):
        """Return current postep config in json format"""
        settings_json = self.stepper.get_driver_settings()
        return settings_json
        # microstepping = config[36]

    def set_acceleration(self, acc):
        """Set acceleration"""
        self.acceleration = acc

    def get_acceleration(self):
        return self.acceleration

    def set_postep_config(self, fsc=None, idlec=None, overheatc=None, step_mode=None):
        self.stepper.set_driver_settings(fsc, idlec, overheatc, step_mode)

    def get_state(self):
        return self.state

    def get_calibration_step(self):
        return self.current_calibration_step

    def get_direction(self):
        return self.stepper.get_direction()

    def get_rpm(self):
        return self.current_set_rpm

    def set_calibration(self, calibration_obj):
        """Set json objs contents to calibration"""
        print(f"Setting calibration: {calibration_obj}")
        self.calibration = calibration_obj

    def get_calibration_filename(self):
        """Return calibration filename"""
        if self.calibration:
            return self.calibration.get_filename()
        else:
            return "No Calibration Loaded"

    def load_speed_profile(self, speed_profile_json):
        """Load speed profile from json"""
        self.speed_profile = speed_profile_json

    def set_flow(self, direction, flow, new_log=False, type="", accel=False):
        """convert flow to rpm and set speed"""
        rpm = self.calibration.get_rpm(flow)
        ret = self.run_motor(direction, rpm, accel=accel)
        print(f"Ret in set flow: {ret}")
        if ret:
            self.current_set_flow = flow
        return ret

    def get_flow(self):
        """Get current set flow"""
        return self.current_set_flow

    def stop_motor(self):
        """Stop stepper motor"""
        self.csv_logging = False
        ret = self.stepper.stop_motor()
        if ret:
            self.current_set_flow = 0
            self.current_set_rpm = 0
        return ret

    def run_motor(self, direction, speed, new_log=False, type="", accel=False):
        # dir_str = "cw"
        print(f"Trying to run motor with direction: {direction} speed: {speed}")
        if direction == True:
            dir_str = "cw"
        if direction == False:
            dir_str = "acw"
        ret = self.stepper.set_direction(dir_str)
        if ret:
            if accel:
                accel_speed = self.acceleration
                while accel_speed < speed:
                    print(f"Slowly accelerating")
                    ret = self.stepper.set_speed(accel_speed)
                    accel_speed += self.acceleration
                    accel_speed = min(accel_speed, speed)
                    if ret:
                        self.stepper.start_motor()
                        self.current_set_rpm = speed
                    time.sleep(0.5)
            else:
                ret = self.stepper.set_speed(speed)
                if ret:
                    self.stepper.start_motor()
                    self.current_set_rpm = speed
        if new_log:
            self.csv_writer.start_new_log(type)
            self.csv_logging = True
        return ret

    def run_low_rpm_calibration(self, speed, duration):
        if self.current_state == State.IDLE:
            self.current_state = State.CALIBRATION
        
        if self.current_calibration_step == CalibrationStep.IDLE or self.current_calibration_step == CalibrationStep.COMPLETED:
            self.current_calibration_step = CalibrationStep.LOW_RPM_RUNNING

            print(f"Starting low rpm calibration")
            ret = self.run_motor(Direction.CW, speed)

            start_time = time.time()
            while not self.stop_current_thread and time.time() - start_time < duration:
                time.sleep(0.01)
            
            if self.current_calibration_step == CalibrationStep.LOW_RPM_RUNNING:
                ret = self.stop_motor()
                if self.stop_current_thread:
                    self.current_calibration_step = CalibrationStep.IDLE
                else:
                    self.current_calibration_step = CalibrationStep.LOW_RPM_DONE

    def run_high_rpm_calibration(self, speed, duration):
        """Run selected calibration step"""

        print(f"Current calibration step: {self.current_calibration_step}, current state: {self.current_state}")
        if self.current_calibration_step == CalibrationStep.LOW_RPM_DONE and self.current_state == State.CALIBRATION:

            print(f"Starting high rpm calibration")
            self.current_calibration_step = CalibrationStep.HIGH_RPM_RUNNING

            ret = self.run_motor(Direction.CW, speed)

            start_time = time.time()
            while not self.stop_current_thread and time.time() - start_time < duration:
                time.sleep(0.01)
            
            if self.current_calibration_step == CalibrationStep.HIGH_RPM_RUNNING:
                ret = self.stop_motor()
                if self.stop_current_thread:
                    self.current_calibration_step = CalibrationStep.IDLE
                else:
                    self.current_calibration_step = CalibrationStep.HIGH_RPM_DONE

    def abort_calibration(self):
        """Abort calibration"""
        if self.current_state == State.CALIBRATION:
            self.stop_thread()  # stop currently running thread
            self.current_calibration_step = CalibrationStep.IDLE

    def save_calibration_data(self, filename, low_rpm, high_rpm, low_rpm_vol, high_rpm_vol, duration):
        """Save data to calibration file"""

        print(f"Current calibration step: {self.current_calibration_step}")
        calib_json = {}
        calib_json["low_rpm"] = low_rpm
        calib_json["high_rpm"] = high_rpm
        calib_json["low_rpm_vol"] = low_rpm_vol
        calib_json["high_rpm_vol"] = high_rpm_vol
        calib_json["duration"] = duration

        if self.current_calibration_step == CalibrationStep.HIGH_RPM_DONE or self.current_calibration_step == CalibrationStep.COMPLETED:
            with open(filename, "w") as calib_file:
                json.dump(calib_json, calib_file)
            
            self.current_calibration_step = CalibrationStep.COMPLETED
            self.current_state = State.IDLE

    def run_speed_profile(self, direction):
        if self.speed_profile is None:
            print("No speed profile set! Returning!")
            return

        print(f"running profile: {self.speed_profile['profile']}")

        if len(self.speed_profile["profile"]) < 1:
            print(f"Speed profile set incorrectly. Returning!")

        self.csv_writer.start_new_log("speed_profile")
        self.csv_logging = True

        for speed_setting in self.speed_profile["profile"]:
            print(f"Running speed setting: {speed_setting} with direction: {direction}")
            duration = speed_setting.get("duration", 0)
            flow = speed_setting.get("flow", 0)
            ret = self.set_flow(direction, flow)
            print(f"Ret in run_speed_profile: {ret}")
            if ret:
                start_time = time.time()
                # print(f"Running flow: {flow} for duration: {duration}")
                while not self.stop_current_thread and time.time() - start_time < duration:
                    time.sleep(0.01)

        ret = self.stop_motor()
