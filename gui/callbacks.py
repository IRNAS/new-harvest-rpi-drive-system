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

        self.motor_running = None

        self.abort = False
        self.btn_click = None

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
                State("low-rpm-input", "value"),
                State("low-rpm-volume-input", "value"),
                State("high-rpm-input", "value"),
                State("high-rpm-volume-input", "value"),
                State("set-time-input", "value"),
                State("filename-input", "value"),
                State("current-step-span", "children"),
                # State("calib-progress", "value")
            ]
        )
        def update_calib_status(n, btn_start, btn_stop, btn_cont, btn_save, confirm, low_rpm_in, low_rpm_vol, high_rpm_in, high_rpm_vol, set_time, filename, current_step):
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
                        if self.current_calibration_step == CalibrationStep.LOW_RPM_DONE:
                            display_calib_dialog = True
                            calib_dialog_message = "Enter low rpm calibration volume (mL) and press continue"
                    
                        if self.current_calibration_step == CalibrationStep.HIGH_RPM_DONE:
                            display_calib_dialog = True
                            calib_dialog_message = "Calibration done. Enter high rpm calibration volume (mL) and press save"

                        if self.current_calibration_step == CalibrationStep.COMPLETED:

                            calib = Calibration()
                            calib.load_calibration(filename)
                            slope = calib.get_slope()
                            self.new_harvest.set_calibration(calib)

                            display_calib_dialog = True
                            calib_dialog_message = f"Calibration saved to {filename}.\nCalculated (mL/min)/rpm: {round(slope, 2)}"

                    if self.current_calibration_step == CalibrationStep.LOW_RPM_RUNNING:
                        self.calibration_percent_done = min((((time.time() - self.calibration_start_time) / set_time) * 49), 49)
                    if self.current_calibration_step == CalibrationStep.LOW_RPM_DONE:
                        self.calibration_percent_done = 49
                    if self.current_calibration_step == CalibrationStep.HIGH_RPM_RUNNING:
                        self.calibration_percent_done = 49 + min((((time.time() - self.calibration_start_time) / set_time) * 49), 49)
                    if self.current_calibration_step == CalibrationStep.HIGH_RPM_DONE:
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
                        confirm_dialog_message = "Press OK to start calibration process with low rpm"

                if prop_id == "btn-stop-calib":
                    if self.current_calibration_step != CalibrationStep.IDLE and self.current_calibration_step != CalibrationStep.COMPLETED:
                        self.abort = True
                        self.btn_click = "STOP"
                        self.calibration_percent_done = 0
                        display_confirm_dialog = True
                        confirm_dialog_message = "Press OK to abort calibration"

                if prop_id == "btn-continue-calib":
                    if self.current_calibration_step == CalibrationStep.LOW_RPM_DONE:
                        self.btn_click = "CNT"
                        self.calibration_start_time = time.time()
                        display_confirm_dialog = True
                        confirm_dialog_message = "Press OK to start calibration process with high rpm"

                if prop_id == "confirm-dialog" and confirm:
                    if self.abort:
                        self.new_harvest.abort_calibration()
                        self.abort = False
                    if self.btn_click == "START":
                        self.new_harvest.run_thread(target=self.new_harvest.run_low_rpm_calibration, args=(low_rpm_in, set_time, ))
                        self.btn_click = None
                    if self.btn_click == "CNT":
                        self.new_harvest.run_thread(target=self.new_harvest.run_high_rpm_calibration, args=(high_rpm_in, set_time, ))
                        self.btn_click = None
                    if self.btn_click == "SAVE":
                        self.new_harvest.save_calibration_data(filename, low_rpm_in, high_rpm_in, low_rpm_vol, high_rpm_vol, set_time)
                        self.btn_click = None

                if prop_id == "btn-save-calib":
                    if self.current_calibration_step == CalibrationStep.HIGH_RPM_DONE or self.current_calibration_step == CalibrationStep.COMPLETED:
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
                Output("direction-toggle", "checked"),
                Output("slope", "children"),
                Output("set-rpm", "children"),
                Output("confirm-dialog-rpm-alert", "message"),
                Output("confirm-dialog-rpm-alert", "displayed")
            ],
            [
                Input("btn-start", "n_clicks"),
                Input("btn-set", "n_clicks"),
                Input("btn-stop", "n_clicks"),
                Input("direction-toggle", "checked"),
                Input("upload-calibration", "contents"),
                Input("check-dir-interval", "n_intervals"),
                Input("select-calibration-dropdown", "value")
            ],
            [
                State("direction-toggle", "checked"),
                State("flow-speed-input", "value"),
                State("upload-calibration", "filename")
            ]
        )
        def update_single_speed_status(btn_start, btn_set, btn_stop, dir, calib_contents, n_intervals, selected_calib, dir_state, speed, calibration_filename):
            """Update single speed layout"""

            dir_toggle = self.new_harvest.get_direction()
            MAX_RPM = 5000
            display_rpm_warning = False
            rpm_dialog_message = f"Set rpm exceeds the maximum allowed rpm of {MAX_RPM}!"
            
            ctx = dash.callback_context
            # print(ctx)
            if ctx.triggered:
                split = ctx.triggered[0]["prop_id"].split(".")
                prop_id = split[0]
                # print(split)

                if prop_id == "btn-start":
                    self.motor_running = True
                    self.new_harvest.set_flow(dir_state, speed, new_log=True, type="single_speed", accel=True)
                    
                if prop_id == "btn-stop":
                    self.motor_running = False
                    self.new_harvest.stop_motor()
                    
                if prop_id == "btn-set":
                    if self.motor_running:
                        self.new_harvest.set_flow(dir_state, speed, accel=True)

                if prop_id == "direction-toggle":
                    if self.motor_running:
                        # self.new_harvest.set_flow(dir_state, speed, accel=True)
                        self.new_harvest.change_direction(dir_state)
                    else:
                        self.new_harvest.set_direction(dir_state)

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

                if prop_id == "check-dir-interval":
                    dir_toggle = self.new_harvest.get_direction()
                    # print(f"Direction: {dir_toggle}")
                    if dir_toggle == "acw":
                        dir_toggle = False
                    if dir_toggle == "cw":
                        dir_toggle = True

            set_calibration_file = self.new_harvest.get_calibration_filename()
            slope = round(self.new_harvest.get_slope(), 3)

            current_set_rpm = int(self.new_harvest.get_rpm())
            if current_set_rpm > MAX_RPM:
                display_rpm_warning = True
            # print(f"Set calibration file: {set_calibration_file}")

            return [], set_calibration_file, dir_toggle, slope, current_set_rpm, rpm_dialog_message, display_rpm_warning

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
                Output("slope-sp", "children")
            ],
            [
                Input("btn-start-sp", "n_clicks"),
                Input("btn-stop-sp", "n_clicks"),
                Input("direction-toggle-sp", "checked"),
                Input("upload-speed-profile", "contents"),
                Input("confirm-dialog-sp", "submit_n_clicks"),
                Input("upload-calibration-sp", "contents"),
                Input("select-calibration-sp-dropdown", "value"),
                Input("flow-update-interval", "n_intervals"),
            ],
            [
                State("direction-toggle-sp", "checked"),
                State("upload-speed-profile", "filename"),
                State("upload-calibration-sp", "filename")
            ]
        )
        def update_speed_profile_status(btn_start, btn_stop, dir, contents, confirm, calib_contents, selected_calib, n, dir_state, profile_filename, calibration_filename):
            """Update single speed layout"""
            display_confirm_dialog = False
            confirm_dialog_message = ""

            if not profile_filename:
                profile_filename = "No File Selected"

            ctx = dash.callback_context
            if ctx.triggered:
                split = ctx.triggered[0]["prop_id"].split(".")
                prop_id = split[0]
                # print(split)

                if prop_id == "btn-start-sp":
                    self.btn_click = "START"
                    display_confirm_dialog = True
                    confirm_dialog_message = "Press OK to start stepper motor"
                    
                if prop_id == "btn-stop-sp":
                    self.btn_click = "STOP"
                    display_confirm_dialog = True
                    confirm_dialog_message = "Press OK to stop stepper motor"

                if prop_id == "confirm-dialog-sp" and confirm:
                    if self.btn_click == "START":
                        self.new_harvest.run_thread(target=self.new_harvest.run_speed_profile, args=(dir_state, ))
                        self.btn_click = None
                    if self.btn_click == "STOP":
                        self.new_harvest.stop_thread()
                        self.btn_click = None

                if prop_id == "upload-speed-profile":
                    if contents is not None and ".json" in profile_filename:
                        self.new_harvest.load_speed_profile(parse_json_contents(contents))
                
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
            # print(f"Set calibration file: {set_calibration_file}")
            slope = round(self.new_harvest.get_slope(), 3)
            return [], profile_filename, flow, display_confirm_dialog, confirm_dialog_message, set_calibration_file, slope

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