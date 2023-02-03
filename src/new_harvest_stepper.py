import time
import json
import logging
import pathlib
import datetime

from threading import Thread

from src.csv_writer import CsvWriter
# from w1thermsensor import W1ThermSensor
from src.calibration import Calibration
from src.motor_usb import Motor, Direction, DC_MODE, STEPPER_MODE

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

        self.motor = None
        self.current_state = State.IDLE  # current global state

        self.current_calibration_step = CalibrationStep.IDLE

        self.direction = False
        self.action_in_progress = False

        # run all motor commands threaded so nothing is blocked
        self.thread = None
        self.stop_current_thread = False

        self.calibration = None
        self.speed_profile = None

        # functional variables
        self.current_set_flow = 0
        self.current_set_rpm = 0
        self.target_rpm = 0
        self.converted_rpm = 0

        self.state = {
            "flow": [],
            "rpm": [],
            "temp": []
        }

        self.csv_logging = False
        self.csv_writer = CsvWriter()

        try:
            self.motor = Motor(STEPPER_MODE)
            self.direction = self.motor.get_direction()
            # self.motor.stop_motor()
            # time.sleep(1)
            # self.motor.set_speed(0)
            # time.sleep(1)
            # self.motor.start_motor()
            log.info("Initialized Stepper motor")
        except Exception as e:
            log.error(f"Failed to initialize stepper motor: {e}")

        self.temp_sensor = None
        # try:
        #     self.temp_sensor = W1ThermSensor()
        # except Exception as e:
        #     log.error(f"Failed to initialize DS1820: {e}")

        # create folders where calibrations and flow profiles are saved
        try:
            pathlib.Path("/mnt/storage/calibrations").mkdir(parents=True, exist_ok=True)
        except Exception as e:
            log.warning(f"Failed to create calibrations folder")

        try:
            pathlib.Path("/mnt/storage/profiles").mkdir(parents=True, exist_ok=True)
        except Exception as e:
            log.warning(f"Failed to create profiles folder")

        # create folder with measurements
        try:
            pathlib.Path("/mnt/storage/measurements").mkdir(parents=True, exist_ok=True)
        except Exception as e:
            log.warning(f"Failed to create measurements folder")

        # Create another folder for local storage measurements
        try:
            pathlib.Path("/home/pi/new-harvest-storage/measurements").mkdir(parents=True, exist_ok=True)
        except Exception as e:
            log.warning(f"Failed to create local measurements folder")

        # load last saved calibration
        try:
            temp_c = Calibration()
            with open("/home/pi/last_calibration.json", "r") as f:
                calib_obj = json.load(f)
            filepath = calib_obj["calib_filename"]
            if filepath != "":
                temp_c.load_calibration(filepath)
                self.set_calibration(temp_c)
        except Exception as e:
            print(f"Failed to load calibration: {e}")


        self.state_loop_running = True
        self.stop_moving_motor = False
        self.stopping_motor = False

        self.state_loop = None

        self.profile_filename = None
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
                if self.temp_sensor is not None:
                    current_temp = round(self.temp_sensor.get_temperature(), 1)
                    try:
                        self.state["temp"].append(current_temp)
                    except Exception as e:
                        pass
                else:
                    current_temp = None
                self.state["flow"].append(self.current_set_flow)
                actual_rpm = int(self.converted_rpm)
                self.state["rpm"].append(actual_rpm)
                if self.csv_logging:
                    self.csv_writer.append_row([self.current_set_flow, actual_rpm, current_temp])

                self.state["temp"] = self.state["temp"][-600:] 
                self.state["flow"] = self.state["flow"][-600:]
                self.state["rpm"] = self.state["rpm"][-600:]
            else:
                break
            time.sleep(1)

    def run_thread(self, target, args):
        self.stop_current_thread = False
        self.stop_moving_motor = False
        self.thread = Thread(target=target, args=args)
        self.thread.start()

    def stop_thread(self):
        self.stop_current_thread = True
        if self.thread is not None:
            self.thread.join()
            time.sleep(1)
        print(f"Stopping thread")
        self.csv_logging = False
        self.thread = None

    def stop_manual_execution(self):
        self.stop_moving_motor = True
        if self.thread is not None:
            self.thread.join()
            time.sleep(1)
        print(f"Stopping thread")
        self.csv_logging = False
        self.thread = None

    def get_postep_config(self):
        """Return current postep config in json format"""
        settings_json = self.motor.get_driver_settings()
        return settings_json
        # microstepping = config[36]


    def set_postep_config(self, fsc=None, idlec=None, overheatc=None, step_mode=None):
        self.motor.set_driver_settings(fsc, idlec, overheatc, step_mode)

    def get_state(self):
        return self.state

    def get_calibration_step(self):
        return self.current_calibration_step

    def get_direction(self):
        return self.direction

    def get_rpm(self):
        return self.current_set_rpm

    def set_direction(self, direction):
        if direction == True or direction == "cw":
            dir_str = "cw"
        if direction == False or direction == "acw":
            dir_str = "acw"
        ret = self.motor.set_direction(dir_str)

        self.direction = self.motor.get_direction()

    def set_calibration(self, calibration_obj):
        """Set json objs contents to calibration"""
        print(f"Setting calibration: {calibration_obj}")
        self.calibration = calibration_obj

        """Update last used calibration filename to file"""
        # write last used calibration filename to json file
        filename = self.calibration.get_filename()
        file_obj = {}
        try:
            with open("/home/pi/last_calibration.json", "r") as f:
                file_obj = json.load(f)
        except Exception as e:
            print(e)
            
        file_obj["calib_filename"] = f"/mnt/storage/calibrations/{filename}"
        with open("/home/pi/last_calibration.json", "w") as f:
            json.dump(file_obj, f)

    def get_calibration_filename(self):
        """Return calibration filename"""
        if self.calibration:
            return self.calibration.get_filename()
        else:
            return "No Calibration Loaded"

    def get_profile_filename(self):
        return self.profile_filename

    def load_speed_profile(self, speed_profile_json=None, profile_filename=None):
        """Load speed profile from json"""
        if speed_profile_json is not None and profile_filename is not None:
            self.speed_profile = speed_profile_json
            self.profile_filename = profile_filename
            return self.speed_profile

        if profile_filename is not None:
            with open(profile_filename, "r") as f:
                speed_profile_json = json.load(f)
                self.speed_profile = speed_profile_json
                self.profile_filename = profile_filename

        return self.speed_profile

    def set_flow(self, direction, flow, new_log=False, type="", rpm_per_sec=10000):
        """convert flow to rpm and set speed"""
        if self.action_in_progress:
            return

        try:
            rpm = self.calibration.get_rpm(flow)
            ret = self.run_motor(direction, rpm, new_log=new_log, type=type, rpm_per_sec=rpm_per_sec)
            # print(f"Ret in set flow: {ret}")
            if ret:
                # max_flow = int(self.calibration.get_max_flow(flow))
                # print(f"Max flow: {max_flow}")
                self.current_set_flow = flow
            self.action_in_progress = False
            return ret
        except Exception as e:
            logging.error(f"Failed to set flow: {e}")
            self.action_in_progress = False
            return None        

    def get_flow(self):
        """Get current set flow"""
        return self.current_set_flow

    def stop_motor(self, rpm_per_sec=1000):
        """Stop stepper motor"""
        # self.action_in_progress = True

        self.stopping_motor = True
        # self.csv_logging = False
        if self.target_rpm != 0:
            ret = self.run_motor(self.direction, 0, rpm_per_sec=rpm_per_sec)  # set speed to 0
            # time.sleep(0.2)
        
        # if ret:
        ret = self.motor.stop_motor()
        if ret:
            self.current_set_flow = 0
            self.current_set_rpm = 0

        self.stopping_motor = False
        self.action_in_progress = False

        return ret

    def run_motor(self, direction, speed, new_log=False, type="", rpm_per_sec=10000):
        # dir_str = "cw"
        if self.action_in_progress:
            return

        self.target_rpm = speed

        self.action_in_progress = True
        print(f"Trying to run motor with direction: {direction} speed: {speed}")
        self.set_direction(direction)
        tick_interval = 0.1  # 100 ms is a tick
        rpm_per_tick = rpm_per_sec / (1 / tick_interval)

        start_speed = self.current_set_rpm
        accel_speed = self.current_set_rpm

        ret = self.motor.set_speed(accel_speed)
        ret = self.motor.start_motor()
        
        start_time = time.time()
        if ret:
            print(f"Start speed: {start_speed} Accel speed: {accel_speed}")
            ret = self.motor.set_speed(accel_speed)
            while accel_speed - speed != 0:
                # print(f"While loop")
                print(f"Set speed: {accel_speed}")
                if speed > start_speed:
                    accel_speed += rpm_per_tick
                    accel_speed = min(accel_speed, speed)
                else: 
                    accel_speed -= rpm_per_tick
                    accel_speed = max(accel_speed, speed)
                ret = self.motor.set_speed(accel_speed)
                
                self.direction = self.motor.get_direction()
                if self.direction == "cw":
                    mult = 1
                else:
                    mult = -1
                self.converted_rpm = mult * accel_speed
                self.current_set_rpm = accel_speed
                time.sleep(tick_interval)

                if self.stop_moving_motor:
                    break

        print(f"Duration to speed change: {time.time() - start_time}")
        # if ret and not self.stop_moving_motor:
        #     self.current_set_rpm = speed

        if new_log:
            self.csv_writer.start_new_log(type)
            self.csv_logging = True

        self.stop_moving_motor = False
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
            self.action_in_progress = False
            ret = self.stop_motor()
            if self.current_calibration_step == CalibrationStep.LOW_RPM_RUNNING:
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
            self.action_in_progress = False
            ret = self.stop_motor()
            if self.current_calibration_step == CalibrationStep.HIGH_RPM_RUNNING:
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

    def run_speed_profile(self, direction, num_repeat):
        if self.speed_profile is None:
            print("No speed profile set! Returning!")
            return

        print(f"running profile: {self.speed_profile['profile']}")

        if len(self.speed_profile["profile"]) < 1:
            print(f"Speed profile set incorrectly. Returning!")

        self.csv_writer.start_new_log("profile")
        self.csv_logging = True

        if num_repeat is None:
            num_repeat = 1
        
        print(f"Running speed profile {num_repeat} times")
        for _ in range(0, num_repeat):
            for speed_setting in self.speed_profile["profile"]:
                if not self.stop_current_thread:
                    print(f"Running speed setting: {speed_setting} with direction: {direction}")
                    duration = speed_setting.get("duration", 0)
                    flow = speed_setting.get("flow", 0)
                    rpm_per_sec = speed_setting.get("rpm_per_second", 1000)
                    print(f"Read rpm per second: {rpm_per_sec}")
                    ret = self.set_flow(direction, flow, rpm_per_sec=rpm_per_sec)
                    # print(f"Ret in run_speed_profile: {ret}")
                    if ret:
                        start_time = time.time()
                        # print(f"Running flow: {flow} for duration: {duration}")
                        while not self.stop_current_thread and time.time() - start_time < duration:
                            time.sleep(0.01)

            if self.target_rpm != 0:
                ret = self.stop_motor(rpm_per_sec=rpm_per_sec)
                time.sleep(1)  # wait a second for motor to completely stop

        self.csv_logging = False

    def get_slope(self):
        try:
            # print("Getting slope")
            return self.calibration.get_slope()
        except Exception as e:
            return 0
