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

            filename = f"./calibration/{filename}.json"

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
                            calib_dialog_message = "Enter low rpm calibration volume (mL/min) and press continue"
                    
                        if self.current_calibration_step == CalibrationStep.HIGH_RPM_DONE:
                            display_calib_dialog = True
                            calib_dialog_message = "Calibration done. Enter high rpm calibration volume (mL/min) and press save"

                        if self.current_calibration_step == CalibrationStep.COMPLETED:
                            calibration = Calibration(filename)
                            slope = calibration.get_slope()
                            display_calib_dialog = True
                            calib_dialog_message = f"Calibration saved to {filename}.\nCalculated mL/rpm: {round(slope, 2)}"

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
                Output("confirm-dialog-sf", "displayed"),
                Output("confirm-dialog-sf", "message")
            ],
            [
                Input("btn-start", "n_clicks"),
                Input("btn-set", "n_clicks"),
                Input("btn-stop", "n_clicks"),
                Input("direction-toggle", "checked"),
                Input("confirm-dialog-sf", "submit_n_clicks")
            ],
            [
                State("direction-toggle", "checked"),
                State("flow-speed-input", "value")
            ]
        )
        def update_single_speed_status(btn_start, btn_set, btn_stop, dir, dir_state, speed, confirm):
            """Update single speed layout"""

            display_confirm_dialog = False
            confirm_dialog_message = ""
            
            ctx = dash.callback_context
            if ctx.triggered:
                split = ctx.triggered[0]["prop_id"].split(".")
                prop_id = split[0]
                print(split)

                if prop_id == "btn-start":
                    self.btn_click = "START"
                    display_confirm_dialog = True
                    confirm_dialog_message = "Press OK to start stepper motor"
                    
                if prop_id == "btn-stop":
                    self.btn_click = "STOP"
                    display_confirm_dialog = True
                    confirm_dialog_message = "Press OK to stop stepper motor"
                    
                if prop_id == "btn-set":
                    self.btn_click = "SET"
                    display_confirm_dialog = True
                    confirm_dialog_message = "Press OK to set adjust flow"

                if prop_id == "direction-toggle":
                    if self.motor_running:
                        self.new_harvest.run_motor(dir_state, speed)

                if prop_id == "confirm-dialog-sf" and confirm:
                    if self.btn_click == "START":
                        if not self.motor_running:
                            self.motor_running = True
                            self.new_harvest.run_motor(dir_state, speed, new_log=True, type="single_speed")
                        self.btn_click = None
                    if self.btn_click == "STOP":
                        self.motor_running = False
                        self.new_harvest.stop_motor()
                        self.btn_click = None
                    if self.btn_click == "SET":
                        if self.motor_running:
                            self.new_harvest.run_motor(dir_state, speed)
                        self.btn_click = None

            return [], display_confirm_dialog, confirm_dialog_message

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
                new_data = generate_figure_data(data, titles, ['rgb(10, 100, 200)', 'rgb(250, 140, 15)'])

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
                Output("procedure-sequence-filename", "children"),
                Output("current-flow-span", "children"),
                Output("confirm-dialog-sp", "displayed"),
                Output("confirm-dialog-sp", "message")
            ],
            [
                Input("btn-start-sp", "n_clicks"),
                Input("btn-stop-sp", "n_clicks"),
                Input("direction-toggle-sp", "checked"),
                Input("upload-speed-profile", "contents"),
                Input("confirm-dialog-sp", "submit_n_clicks")
            ],
            [
                State("direction-toggle-sp", "checked"),
                State("upload-speed-profile", "filename")
            ]
        )
        def update_single_speed_status(btn_start, btn_stop, dir, contents, dir_state, profile, confirm):
            """Update single speed layout"""
            display_confirm_dialog = False
            confirm_dialog_message = ""

            if not profile:
                profile = "No File Selected"

            ctx = dash.callback_context
            if ctx.triggered:
                split = ctx.triggered[0]["prop_id"].split(".")
                prop_id = split[0]
                print(split)

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

                if prop_id == "direction-toggle-sp":
                    self.new_harvest.run_thread(target=self.new_harvest.run_speed_profile, args=(dir_state, ))

                if prop_id == "upload-speed-profile":
                    if contents is not None and ".json" in profile:
                        self.new_harvest.load_speed_profile(parse_json_contents(contents))
                    pass

            rpm = self.new_harvest.get_rpm()

            return [], profile, rpm, display_confirm_dialog, confirm_dialog_message