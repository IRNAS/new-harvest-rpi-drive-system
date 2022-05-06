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
    LOW_PWM_RUNNING = "LOW_PWM_RUNNING"
    LOW_PWM_DONE = "LOW_PWM_DONE"
    HIGH_PWM_RUNNING = "HIGH_PWM_RUNNING"
    HIGH_PWM_DONE = "HIGH_PWM_DONE"
    ABORTED = "ABORTED"
    COMPLETED = "COMPLETED"

class NewHarvest():
    def __init__(self):
        """Init class with motor"""

        self.motor = None
        self.current_state = State.IDLE  # current global state

        self.current_calibration_step = CalibrationStep.IDLE

        self.direction = False
        self.action_in_progress = False

        # run all motor commands threaded so nothing is blocked
        self.thread = None
        self.stop_current_thread = False
        self.stop_moving_motor = False

        self.calibration = None
        self.speed_profile = None

        # functional variables
        self.current_set_flow = 0
        self.current_set_pwm = 0

        self.state = {
            "flow": [],
            "pwm": [],
            "temp": []
        }

        self.csv_logging = False
        self.csv_writer = CsvWriter()

        try:
            self.motor = Motor(DC_MODE)
            self.direction = self.motor.get_direction()
            log.info("Initialized motor")
        except Exception as e:
            log.error(f"Failed to initialize motor: {e}")

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
            log.warning(f"Failed to create profiles folder")

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

                pwm = self.get_current_mapped_pwm()
                # print(f"Current pwm: {pwm}")
                self.state["flow"].append(self.current_set_flow)
                self.state["pwm"].append(int(pwm))
                if self.csv_logging:
                    self.csv_writer.append_row([self.current_set_flow, int(pwm), current_temp])

                self.state["temp"] = self.state["temp"][-600:] 
                self.state["flow"] = self.state["flow"][-600:]
                self.state["pwm"] = self.state["pwm"][-600:]
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
        print(f"Stopping thread")
        # time.sleep(2)
        self.csv_logging = False
        self.thread = None

    def stop_manual_execution(self):
        self.stop_moving_motor = True
        if self.thread is not None:
            self.thread.join()
        print(f"Stopping thread")
        # time.sleep(2)
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

    def get_pwm(self):
        return self.current_set_pwm

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
        with open("/home/pi/last_calibration.json", "r") as f:
            file_obj = json.load(f)
            
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

    def set_flow(self, direction, flow, new_log=False, type="", pwm_per_sec=100):
        """convert flow to pwm and set speed"""
        if self.action_in_progress:
            return

        self.action_in_progress = True
        try:
            pwm = self.calibration.get_pwm(flow)
            ret = self.run_motor(direction, pwm, new_log=new_log, type=type, pwm_per_sec=pwm_per_sec)
            print(f"Ret in set flow: {ret}")
            if ret:
                max_flow = int(self.calibration.get_max_flow(flow))
                self.current_set_flow = min(flow, max_flow)
            self.action_in_progress = False
            return ret
        except Exception as e:
            logging.error(f"Failed to set flow: {e}")
            self.action_in_progress = False
            return None        

    def get_flow(self):
        """Get current set flow"""
        return self.current_set_flow

    def stop_motor(self, pwm_per_sec=100):
        """Stop motor"""
        print(F"STOPPING MOTOR")
        # self.csv_logging = False
        direction = self.motor.get_direction()
        # print(f"Current set direction: {direction}")
        ret = self.run_motor(direction, 0, pwm_per_sec=pwm_per_sec)  # set speed to 0
        if ret:
            ret = self.motor.stop_motor()
            if ret:
                self.current_set_flow = 0
                self.current_set_pwm = 0
        return ret

    def get_current_mapped_pwm(self):
        current_direction = self.motor.get_direction()
        # print(f"Current motor direction: {current_direction}")

        if current_direction == "cw":
            direction_factor = 1
        if current_direction == "acw":
            direction_factor = -1

        current_pwm = self.current_set_pwm * direction_factor  # map currently set pwm from [0, 100] to [-100, 100] based on direction

        return current_pwm

    def run_motor(self, set_dir, target_pwm, new_log=False, type="", pwm_per_sec=100):
        # dir_str = "cw"

        if new_log:
            self.csv_writer.start_new_log(type)
            self.csv_logging = True

        pwm_per_tick = pwm_per_sec * 0.1
        print(f"pwm per tick: {pwm_per_tick}")

        if target_pwm != "":
            target_pwm = int(min(target_pwm, 100))

        current_direction = self.motor.get_direction()
        self.motor.set_direction(current_direction)

        # speed = max(speed, 100)
        # if set_dir == current_direction:
        #     direction_factor = 1
        # else:
        if (set_dir == True or set_dir == "cw"):
            direction_factor = 1
            set_dir = "cw"
        if (set_dir == False or set_dir == "acw"):
            direction_factor = -1
            set_dir = "acw"

        target_pwm = direction_factor * target_pwm  # map from [0, 100] to [-100, 100] based on set direction
        # print(f"Trying to run motor with direction: {set_dir} speed: {target_pwm}")
        current_pwm = self.get_current_mapped_pwm()

        ret = self.motor.start_motor()

        if target_pwm == current_pwm:  # if speed is already set there is nothing to do
            return True

        dir_changed = False

        start_time = time.time()

        if ret:        
            start_pwm = self.current_set_pwm
            speed_diff = abs(current_pwm - target_pwm)  # the difference in speed we need to change for, [0, 200] - we decrease this variable, when 0 is hit we are done
            
            # speed_change = self.current_set_pwm
            current_set_pwm = self.current_set_pwm  # the currently set pwm, we periodically adjust this to reflect the change in speed

            # if current_pwm < target_pwm:
            #     current_pwm = current_pwm * -1
            slope = target_pwm - current_pwm  # the slope of pwm change

            while True:
                if self.stop_moving_motor:
                    print(f"Stopping motor in run_motor")
                    return None
                current_pwm = self.get_current_mapped_pwm()
                speed_diff = abs(current_pwm - target_pwm)  # the difference in speed we need to change for, [0, 200] - we decrease this variable, when 0 is hit we are done

                slope = target_pwm - current_pwm  # the slope of pwm change
                # print(f"Speed diff: {speed_diff}")
                # print(f"Target pwm: {target_pwm}, current_pwm: {current_pwm}")

                tick_multiplier = 1.0
                if pwm_per_tick >= 2 * speed_diff:
                    tick_multiplier = 0.1

        
                if slope == target_pwm and current_direction != set_dir and not dir_changed:
                    self.motor.set_direction(set_dir)
                    time.sleep(0.01)
                    dir_changed = True
                    continue

                if slope < 0:
                    if set_dir == "cw":
                        current_set_pwm -= pwm_per_tick * tick_multiplier
                    else:
                        current_set_pwm += pwm_per_tick * tick_multiplier  # decrease current_set_pwm if slope is negative
                if slope > 0:
                    if set_dir == "cw":
                        current_set_pwm += pwm_per_tick * tick_multiplier
                    # if not dir_changed:
                    else:
                        current_set_pwm -= pwm_per_tick * tick_multiplier
                    # print(F"Positive slope, current speed: {current_set_pwm}")

                current_set_pwm = min(abs(current_set_pwm), 100)  # cap to 100
                ret = self.motor.set_speed(current_set_pwm)
                if ret:
                    self.current_set_pwm = current_set_pwm
                
                time.sleep(0.1)  # sleep for predefined duration - acceleration is based on this duration
                # print(f"Duration: {time.time() - start_time}")
                if speed_diff <= 1:  # once speed diff is 0 exit out
                    print("Speed set. Exiting")
                    break
        

        return ret

    def run_low_pwm_calibration(self, speed, duration):
        if self.current_state == State.IDLE:
            self.current_state = State.CALIBRATION
        
        if self.current_calibration_step == CalibrationStep.IDLE or self.current_calibration_step == CalibrationStep.COMPLETED:
            self.current_calibration_step = CalibrationStep.LOW_PWM_RUNNING

            print(f"Starting low pwm calibration")
            ret = self.run_motor(Direction.CW, speed)

            start_time = time.time()
            while not self.stop_current_thread and time.time() - start_time < duration:
                time.sleep(0.01)
            
            if self.current_calibration_step == CalibrationStep.LOW_PWM_RUNNING:
                ret = self.stop_motor()
                if self.stop_current_thread:
                    self.current_calibration_step = CalibrationStep.IDLE
                else:
                    self.current_calibration_step = CalibrationStep.LOW_PWM_DONE

    def run_high_pwm_calibration(self, speed, duration):
        """Run selected calibration step"""

        print(f"Current calibration step: {self.current_calibration_step}, current state: {self.current_state}")
        if self.current_calibration_step == CalibrationStep.LOW_PWM_DONE and self.current_state == State.CALIBRATION:

            print(f"Starting high pwm calibration")
            self.current_calibration_step = CalibrationStep.HIGH_PWM_RUNNING

            ret = self.run_motor(Direction.CW, speed)

            start_time = time.time()
            while not self.stop_current_thread and time.time() - start_time < duration:
                time.sleep(0.01)
            
            if self.current_calibration_step == CalibrationStep.HIGH_PWM_RUNNING:
                ret = self.stop_motor()
                if self.stop_current_thread:
                    self.current_calibration_step = CalibrationStep.IDLE
                else:
                    self.current_calibration_step = CalibrationStep.HIGH_PWM_DONE

    def abort_calibration(self):
        """Abort calibration"""
        if self.current_state == State.CALIBRATION:
            self.stop_thread()  # stop currently running thread
            self.current_calibration_step = CalibrationStep.IDLE

    def save_calibration_data(self, filename, low_pwm, high_pwm, low_pwm_vol, high_pwm_vol, duration):
        """Save data to calibration file"""

        print(f"Current calibration step: {self.current_calibration_step}")
        calib_json = {}
        calib_json["low_pwm"] = low_pwm
        calib_json["high_pwm"] = high_pwm
        calib_json["low_pwm_vol"] = low_pwm_vol
        calib_json["high_pwm_vol"] = high_pwm_vol
        calib_json["duration"] = duration

        if self.current_calibration_step == CalibrationStep.HIGH_PWM_DONE or self.current_calibration_step == CalibrationStep.COMPLETED:
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
                    pwm_per_second = speed_setting.get("pwm_per_second", 100)
                    ret = self.set_flow(direction, flow, pwm_per_sec=pwm_per_second)
                    print(f"Ret in run_speed_profile: {ret}")
                    if ret:
                        start_time = time.time()
                        # print(f"Running flow: {flow} for duration: {duration}")
                        while not self.stop_current_thread and time.time() - start_time < duration:
                            time.sleep(0.01)

            ret = self.stop_motor()

        # stop csv logging
        self.csv_logging = False

    def get_slope(self):
        try:
            # print("Getting slope")
            return self.calibration.get_slope()
        except Exception as e:
            return 0
