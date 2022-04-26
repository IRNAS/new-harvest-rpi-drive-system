import time
import dash
import json
import logging
import datetime

from gui.app import app
from dash.dependencies import Input, Output, State
from src.new_harvest import CalibrationStep
from src.calibration import Calibration
from .components.functions import map_calibration_step, generate_figure_data, map_title, map_color, parse_json_contents
from .components.speed_profile_plot import generate_speed_profile

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

ACW = 0
CW = 1

class NewHarvestCallbacks():
    """Wrapper class"""
    def __init__(self, new_harvest):
        self.new_harvest = new_harvest

        self.direction = self.new_harvest.get_direction()

        self.prev_state = self.new_harvest.get_state()
        self.current_state = self.new_harvest.get_state()

        self.prev_calibration_step = self.new_harvest.get_calibration_step()
        self.current_calibration_step = self.new_harvest.get_calibration_step()

        self.calibration_start_time = None
        self.calibration_percent_done = 0

        self.set_speed_profile_plot = {}

        self.motor_running = None

        self.abort = False
        self.btn_click = None

        self.prev_direction = self.direction

    def calibration_callbacks(self):

        # stop motor when loading new layout
        self.new_harvest.stop_motor()

        @app.callback(
            [
                Output("current-step-span", "children"),
                Output("calib-dialog", "message"),
                Output("calib-dialog", "displayed"),
                Output("confirm-dialog", "message"),
                Output("confirm-dialog", "displayed"),
                Output("calib-progress", "value")
            ],
            [
                Input("check-state-interval", "n_intervals"),
                Input("btn-start-calib", "n_clicks"),
                Input("btn-stop-calib", "n_clicks"),
                Input("btn-continue-calib", "n_clicks"),
                Input("btn-save-calib", "n_clicks"),
                Input("confirm-dialog", "submit_n_clicks"),
            ],
            [
                State("low-pwm-input", "value"),
                State("low-pwm-volume-input", "value"),
                State("high-pwm-input", "value"),
                State("high-pwm-volume-input", "value"),
                State("set-time-input", "value"),
                State("filename-input", "value"),
                State("current-step-span", "children"),
                # State("calib-progress", "value")
            ]
        )
        def update_calib_status(n, btn_start, btn_stop, btn_cont, btn_save, confirm, low_pwm_in, low_pwm_vol, high_pwm_in, high_pwm_vol, set_time, filename, current_step):
            """Update calib status and display dialogs"""

            display_calib_dialog = False
            calib_dialog_message = ""

            display_confirm_dialog = False
            confirm_dialog_message = ""

            current_step_text = current_step

            filename = f"/mnt/storage/calibrations/{filename}.json"

            calib_progress = self.calibration_percent_done

            ctx = dash.callback_context
            if ctx.triggered and ctx.triggered[0]['value'] > 0:
                split = ctx.triggered[0]["prop_id"].split(".")
                prop_id = split[0]
                # print(split)

                if prop_id == "check-state-interval":

                    self.prev_calibration_step = self.current_calibration_step
                    self.current_calibration_step = self.new_harvest.get_calibration_step()

                    if self.prev_calibration_step != self.current_calibration_step:
                        if self.current_calibration_step == CalibrationStep.LOW_PWM_DONE:
                            display_calib_dialog = True
                            calib_dialog_message = "Enter low pwm calibration volume (mL) and press continue"
                    
                        if self.current_calibration_step == CalibrationStep.HIGH_PWM_DONE:
                            display_calib_dialog = True
                            calib_dialog_message = "Calibration done. Enter high pwm calibration volume (mL) and press save"

                        if self.current_calibration_step == CalibrationStep.COMPLETED:

                            calib = Calibration()
                            calib.load_calibration(filename)
                            slope = calib.get_slope()
                            self.new_harvest.set_calibration(calib)

                            display_calib_dialog = True
                            calib_dialog_message = f"Calibration saved to {filename}.\nCalculated (mL/min)/pwm: {round(slope, 2)}"

                    if self.current_calibration_step == CalibrationStep.LOW_PWM_RUNNING:
                        self.calibration_percent_done = min((((time.time() - self.calibration_start_time) / set_time) * 49), 49)
                    if self.current_calibration_step == CalibrationStep.LOW_PWM_DONE:
                        self.calibration_percent_done = 49
                    if self.current_calibration_step == CalibrationStep.HIGH_PWM_RUNNING:
                        self.calibration_percent_done = 49 + min((((time.time() - self.calibration_start_time) / set_time) * 49), 49)
                    if self.current_calibration_step == CalibrationStep.HIGH_PWM_DONE:
                        self.calibration_percent_done = 98
                    if self.current_calibration_step == CalibrationStep.COMPLETED:
                        self.calibration_percent_done = 100
                    if self.current_calibration_step == CalibrationStep.IDLE:
                        self.calibration_percent_done = 0

                    current_step_text = map_calibration_step(self.current_calibration_step)

                if prop_id == "btn-start-calib":
                    if self.current_calibration_step == CalibrationStep.IDLE or self.current_calibration_step == CalibrationStep.COMPLETED:
                        self.btn_click = "START"
                        self.calibration_start_time = time.time()
                        display_confirm_dialog = True
                        confirm_dialog_message = "Press OK to start calibration process with low pwm"

                if prop_id == "btn-stop-calib":
                    if self.current_calibration_step != CalibrationStep.IDLE and self.current_calibration_step != CalibrationStep.COMPLETED:
                        self.abort = True
                        self.btn_click = "STOP"
                        self.calibration_percent_done = 0
                        display_confirm_dialog = True
                        confirm_dialog_message = "Press OK to abort calibration"

                if prop_id == "btn-continue-calib":
                    if self.current_calibration_step == CalibrationStep.LOW_PWM_DONE:
                        self.btn_click = "CNT"
                        self.calibration_start_time = time.time()
                        display_confirm_dialog = True
                        confirm_dialog_message = "Press OK to start calibration process with high pwm"

                if prop_id == "confirm-dialog" and confirm:
                    if self.abort:
                        self.new_harvest.abort_calibration()
                        self.abort = False
                    if self.btn_click == "START":
                        self.new_harvest.run_thread(target=self.new_harvest.run_low_pwm_calibration, args=(low_pwm_in, set_time, ))
                        self.btn_click = None
                    if self.btn_click == "CNT":
                        self.new_harvest.run_thread(target=self.new_harvest.run_high_pwm_calibration, args=(high_pwm_in, set_time, ))
                        self.btn_click = None
                    if self.btn_click == "SAVE":
                        self.new_harvest.save_calibration_data(filename, low_pwm_in, high_pwm_in, low_pwm_vol, high_pwm_vol, set_time)
                        self.btn_click = None

                if prop_id == "btn-save-calib":
                    if self.current_calibration_step == CalibrationStep.HIGH_PWM_DONE or self.current_calibration_step == CalibrationStep.COMPLETED:
                        self.btn_click = "SAVE"
                        display_confirm_dialog = True
                        confirm_dialog_message = "Press OK to confirm saving to file"

            return current_step_text, calib_dialog_message, display_calib_dialog, confirm_dialog_message, display_confirm_dialog, calib_progress
                    
    def single_speed_callbacks(self):

        # stop motor when loading new layout
        self.new_harvest.stop_motor()

        @app.callback(
            [
                Output("hidden-div", "children"),
                Output("calibration-filename", "children"),
                # Output("direction-toggle", "checked"),
                Output("slope", "children"),
                Output("set-pwm", "children"),
                Output("confirm-dialog-pwm-alert", "message"),
                Output("confirm-dialog-pwm-alert", "displayed")
            ],
            [
                Input("btn-start", "n_clicks"),
                Input("btn-set", "n_clicks"),
                Input("btn-stop", "n_clicks"),
                Input("select-direction-dropdown", "value"),
                Input("upload-calibration", "contents"),
                # Input("check-dir-interval", "n_intervals"),
                Input("select-calibration-dropdown", "value")
            ],
            [
                State("select-direction-dropdown", "value"),
                State("flow-speed-input", "value"),
                State("accel-pwm-input", "value"),
                State("upload-calibration", "filename")
            ]
        )
        def update_single_speed_status(btn_start, btn_set, btn_stop, dir, calib_contents, selected_calib, dir_state, speed, pwm_per_sec, calibration_filename):
            """Update single speed layout"""

            dir_toggle = self.new_harvest.get_direction()
            MAX_PWM = 100
            display_pwm_warning = False
            pwm_dialog_message = f"Set pwm exceeds the maximum allowed pwm of {MAX_PWM}!"
            
            ctx = dash.callback_context
            # print(ctx)
            if ctx.triggered:
                split = ctx.triggered[0]["prop_id"].split(".")
                prop_id = split[0]
                # print(split)

                if prop_id == "btn-start":
                    self.motor_running = True
                    self.new_harvest.stop_manual_execution()
                    self.new_harvest.stop_moving_motor = False
                    time.sleep(0.25)  # wait for motor to stop moving
                    self.new_harvest.stop_motor(pwm_per_sec=pwm_per_sec)
                    self.new_harvest.run_thread(target=self.new_harvest.set_flow, args=(dir_state, speed, True, "single_speed", pwm_per_sec, ))
                    print(f"Pwm per sec: {pwm_per_sec}")
                    self.prev_direction = dir_state
                    
                if prop_id == "btn-stop":
                    self.motor_running = False
                    self.new_harvest.stop_manual_execution()
                    self.new_harvest.stop_moving_motor = False
                    time.sleep(0.25)  # wait for motor to stop moving
                    self.new_harvest.stop_motor(pwm_per_sec=pwm_per_sec)
                    self.prev_direction = dir_state
                    
                if prop_id == "btn-set":
                    if self.motor_running:
                        print(f"Current direction setting: {dir_state}")
                        print(f"Prev direction: {self.prev_direction}")
                        self.new_harvest.stop_manual_execution()
                        self.new_harvest.stop_moving_motor = False
                        time.sleep(0.25)  # wait for motor to stop moving
                        if dir_state != self.prev_direction:
                            self.new_harvest.stop_motor(pwm_per_sec=pwm_per_sec)
                            self.prev_direction = dir_state
                        self.new_harvest.run_thread(target=self.new_harvest.set_flow, args=(dir_state, speed, False, "none", pwm_per_sec, ))
                        print(f"Pwm per sec: {pwm_per_sec}")

                if prop_id == "upload-calibration":
                    if calib_contents is not None and ".json" in calibration_filename:
                        calib = Calibration()
                        calib.set_calibration(parse_json_contents(calib_contents), calibration_filename)
                        self.new_harvest.set_calibration(calib)

                if prop_id == "select-calibration-dropdown":
                    # print(selected_calib)
                    if ".json" in selected_calib:
                        calib = Calibration()
                        calib.load_calibration(selected_calib)
                        self.new_harvest.set_calibration(calib)

                # if prop_id == "check-dir-interval":
                #     dir_toggle = self.new_harvest.get_direction()
                #     # print(f"Direction: {dir_toggle}")
                #     if dir_toggle == "acw":
                #         dir_toggle = False
                #     if dir_toggle == "cw":
                #         dir_toggle = True

            set_calibration_file = self.new_harvest.get_calibration_filename()
            slope = round(self.new_harvest.get_slope(), 3)

            current_set_pwm = int(self.new_harvest.get_pwm())
            if current_set_pwm > MAX_PWM:
                display_pwm_warning = True
            # print(f"Set calibration file: {set_calibration_file}")

            

            return [], set_calibration_file, slope, current_set_pwm, pwm_dialog_message, display_pwm_warning

    def graph_update_callbacks(self):

        @app.callback(
            Output("flow-speed-graph", "figure"),
            [
                Input("graph-refresh-interval", "n_intervals"),
            ],
            [
                State("variable-checklist", "value"),
                State("flow-speed-graph", "figure")
            ]
        )
        def update_single_speed_graph(n, variables, flow_figure):
            
            state = self.new_harvest.get_state()
            data = []
            titles = []
            colors = []

            if variables is not None and len(variables) > 0:
                for v in variables:
                    data.append(state[v])
                    titles.append(map_title(v))
                    colors.append(map_color(v))
                new_data = generate_figure_data(data, titles, colors)

                flow_figure["data"] = new_data
            else:
                flow_figure["data"] = []
                
            return flow_figure

    def speed_profile_callbacks(self):

        # stop motor when loading new layout
        self.new_harvest.stop_motor()

        @app.callback(
            [
                Output("hidden-div-sp", "children"),
                Output("speed-profile-filename", "children"),
                Output("current-flow-span", "children"),
                Output("confirm-dialog-sp", "displayed"),
                Output("confirm-dialog-sp", "message"),
                Output("calibration-filename-sp", "children"),
                Output("slope-sp", "children"),
                Output("speed-profile-plot", "figure")
            ],
            [
                Input("btn-start-sp", "n_clicks"),
                Input("btn-stop-sp", "n_clicks"),
                Input("direction-toggle-sp", "checked"),
                Input("upload-speed-profile", "contents"),
                Input("select-speed-profile-dropdown", "value"),
                Input("confirm-dialog-sp", "submit_n_clicks"),
                Input("upload-calibration-sp", "contents"),
                Input("select-calibration-sp-dropdown", "value"),
                Input("flow-update-interval", "n_intervals"),
                Input("num-repeat-input", "value")
            ],
            [
                State("direction-toggle-sp", "checked"),
                State("upload-speed-profile", "filename"),
                State("upload-calibration-sp", "filename")
            ]
        )
        def update_speed_profile_status(btn_start, btn_stop, dir, profile_contents, selected_profile, confirm, calib_contents, selected_calib, n, num_repeat, dir_state, profile_filename, calibration_filename):
            """Update single speed layout"""
            display_confirm_dialog = False
            confirm_dialog_message = ""

            ctx = dash.callback_context
            if ctx.triggered:
                split = ctx.triggered[0]["prop_id"].split(".")
                prop_id = split[0]
                # print(split)

                if prop_id == "btn-start-sp":
                    self.btn_click = "START"
                    display_confirm_dialog = True
                    confirm_dialog_message = "Press OK to start motor"
                    
                if prop_id == "btn-stop-sp":
                    self.btn_click = "STOP"
                    display_confirm_dialog = True
                    confirm_dialog_message = "Press OK to stop motor"

                if prop_id == "confirm-dialog-sp" and confirm:
                    if self.btn_click == "START":
                        self.new_harvest.run_thread(target=self.new_harvest.run_speed_profile, args=(dir_state, num_repeat, ))
                        self.btn_click = None
                    if self.btn_click == "STOP":
                        self.new_harvest.stop_thread()
                        self.btn_click = None

                if prop_id == "upload-speed-profile":
                    print(f"Uploaded: {profile_contents}")
                    if profile_contents is not None and ".json" in profile_filename:
                        json_profile = parse_json_contents(profile_contents)
                        profile = self.new_harvest.load_speed_profile(speed_profile_json=json_profile, profile_filename=profile_filename)
                        calibration = self.new_harvest.calibration
                        speed_profile_plot = generate_speed_profile(profile, calibration)
                        self.set_speed_profile_plot = speed_profile_plot

                if prop_id == "select-speed-profile-dropdown":
                    profile = self.new_harvest.load_speed_profile(profile_filename=selected_profile)
                    calibration = self.new_harvest.calibration
                    speed_profile_plot = generate_speed_profile(profile, calibration)
                    self.set_speed_profile_plot = speed_profile_plot
                    # print(selected_profile)
                
                if prop_id == "upload-calibration-sp":
                    if calib_contents is not None and ".json" in calibration_filename:
                        calib = Calibration()
                        calib.set_calibration(parse_json_contents(calib_contents), calibration_filename)
                        self.new_harvest.set_calibration(calib)

                if prop_id == "select-calibration-sp-dropdown":
                    # print(selected_calib)
                    if ".json" in selected_calib:
                        calib = Calibration()
                        calib.load_calibration(selected_calib)
                        self.new_harvest.set_calibration(calib)

            flow = round(self.new_harvest.get_flow(), 2)
            set_calibration_file = self.new_harvest.get_calibration_filename()
            set_profile_filename = self.new_harvest.get_profile_filename()
            if set_profile_filename is None:
                set_profile_filename = "No File Selected"
            else:
                set_profile_filename = set_profile_filename.split("/")[-1]
            # print(f"Set calibration file: {set_calibration_file}")
            slope = round(self.new_harvest.get_slope(), 3)
            return [], set_profile_filename, flow, display_confirm_dialog, confirm_dialog_message, set_calibration_file, slope, self.set_speed_profile_plot

    def postep_config_callbacks(self):

        @app.callback(
            [
                Output("confirm-settings-dialog", "displayed"),
                Output("confirm-settings-dialog", "message"),
                Output("javascript", "run")
            ],
            [
                Input("save-btn", "n_clicks"),
                Input("confirm-settings-dialog", "submit_n_clicks")
            ],
            [
                State("fs-current-input", "value"),
                State("idle-current-input", "value"),
                State("overheat-current-input", "value"),
                State("acceleration-input", "value"),
                State("step-mode-dropdown", "value")
            ]
        )
        def update_postep_config_page(btn, confirm, fsc, idlec, occ, acc, step):
            display_confirm_dialog = False
            confirm_dialog_message = ""
            js = ""

            ctx = dash.callback_context
            if ctx.triggered:
                split = ctx.triggered[0]["prop_id"].split(".")
                prop_id = split[0]
                print(split)
                if prop_id == "save-btn":
                    display_confirm_dialog = True
                    confirm_dialog_message = "Press OK to confirm settings. Page will refresh after confirmation"
                if prop_id == "confirm-settings-dialog":
                    self.new_harvest.set_postep_config(fsc=fsc, idlec=idlec, overheatc=occ, step_mode=step)
                    self.new_harvest.set_acceleration(int(acc))
                    js = "location.reload();"

            return display_confirm_dialog, confirm_dialog_message, js