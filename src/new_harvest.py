import time
import json
import logging

from threading import Thread

from src.calibration import Calibration
from src.stepper import Stepper, Direction

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

        # functional variables
        self.current_set_flow = 0
        self.current_set_speed = 0

        self.state = {
            "flow": [],
            "rpm": [],
            "temp": []
        }

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
                self.state["rpm"].append(self.current_set_speed)
                # current_temp = self.get_temperature()  TODO: implement when sensor is known
                # self.state["temp"].append(current_temp)[-600:] 
                self.state["flow"] = self.state["flow"][-600:]
                self.state["rpm"] = self.state["rpm"][-600:]
            else:
                break
            time.sleep(1)

    def run_thread(self, method, args):
        self.stop_current_thread = False
        self.thread = Thread(target=method, args=args)
        self.thread.start()

    def stop_thread(self):
        self.stop_current_thread = True
        self.thread.join()
        self.thread = None

    def get_state(self):
        return self.state

    def get_calibration_step(self):
        return self.current_calibration_step

    def get_direction(self):
        return self.stepper.get_direction()

    def load_calibration(self, filename):
        """Load calibration"""
        self.calibration = Calibration(filename)

    def set_flow(self, flow, direction):
        """convert flow to rpm and set speed"""
        rpm = self.calibration.get_rpm(flow)
        ret = self.run_motor(direction, rpm)
        if ret:
            self.current_set_flow = flow

    def stop_motor(self):
        """Stop stepper motor"""
        ret = self.stepper.stop_motor()
        return ret

    def run_motor(self, direction, speed):
        ret = self.stepper.set_direction(direction)
        if ret:
            ret = self.stepper.set_speed(speed)
        if ret:
            self.stepper.start_motor()
            self.current_set_speed = speed
        return ret

    def run_low_rpm_calibration(self, speed, duration):
        if self.current_state == State.IDLE:
            self.current_state = State.CALIBRATION
        
        if self.current_calibration_step == CalibrationStep.IDLE or self.current_calibration_step == CalibrationStep.COMPLETED:
            self.current_calibration_step = CalibrationStep.LOW_RPM_RUNNING

            print(f"Starting low rpm calibration")
            ret = self.run_motor(Direction.ACW, speed)

            start_time = time.time()
            while not self.stop_current_thread and time.time() - start_time < duration:
                time.sleep(0.1)
            
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

            ret = self.run_motor(Direction.ACW, speed)

            start_time = time.time()
            while not self.stop_current_thread and time.time() - start_time < duration:
                time.sleep(0.1)
            
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