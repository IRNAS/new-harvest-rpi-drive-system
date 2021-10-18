import time
import dash
import logging
import datetime

from gui.app import app
from dash.dependencies import Input, Output, State
from src.new_harvest import CalibrationStep
from .components.functions import map_calibration_step

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)

ACW = 0
CW = 1

class NewHarvestCallbacks():
    """Wrapper class"""
    def __init__(self, new_harvest):
        self.new_harvest = new_harvest

        self.tracked_values = {}
        self.direction = self.new_harvest.get_direction()

        self.prev_state = self.new_harvest.get_state()
        self.current_state = self.new_harvest.get_state()

        self.prev_calibration_step = self.new_harvest.get_calibration_step()
        self.current_calibration_step = self.new_harvest.get_calibration_step()

        self.abort = False
        self.btn_click = None

    def callbacks(self):

        @app.callback(
            [
                Output("current-step-span", "children"),
                Output("calib-dialog", "message"),
                Output("calib-dialog", "displayed"),
                Output("confirm-dialog", "message"),
                Output("confirm-dialog", "displayed")
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
                State("current-step-span", "children")
            ]
        )
        def update_calib_status(n, btn_start, btn_stop, btn_cont, btn_save, confirm, low_rpm_in, low_rpm_vol, high_rpm_in, high_rpm_vol, set_time, current_step):
            """Update calib status and display dialogs"""

            display_calib_dialog = False
            calib_dialog_message = ""

            display_confirm_dialog = False
            confirm_dialog_message = ""

            current_step_text = current_step

            filename = f"calibration{time.time_ns()}.txt"

            ctx = dash.callback_context
            if ctx.triggered and ctx.triggered[0]['value'] > 0:
                split = ctx.triggered[0]["prop_id"].split(".")
                prop_id = split[0]
                print(split)

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
                            display_calib_dialog = True
                            calib_dialog_message = f"Calibration saved to {filename}"

                    current_step_text = map_calibration_step(self.current_calibration_step)

                if prop_id == "btn-start-calib":
                    if self.current_calibration_step == CalibrationStep.IDLE or self.current_calibration_step == CalibrationStep.COMPLETED:
                        self.btn_click = "START"
                        display_confirm_dialog = True
                        confirm_dialog_message = "Press OK to start calibration process with low rpm"

                if prop_id == "btn-stop-calib":
                    if self.current_calibration_step != CalibrationStep.IDLE and self.current_calibration_step != CalibrationStep.COMPLETED:
                        self.abort = True
                        self.btn_click = "STOP"
                        display_confirm_dialog = True
                        confirm_dialog_message = "Press OK to abort calibration"

                if prop_id == "btn-continue-calib":
                    if self.current_calibration_step == CalibrationStep.LOW_RPM_DONE:
                        self.btn_click = "CNT"
                        display_confirm_dialog = True
                        confirm_dialog_message = "Press OK to start calibration process with high rpm"

                if prop_id == "confirm-dialog" and confirm:
                    if self.abort:
                        self.new_harvest.abort_calibration()
                        self.abort = False
                    if self.btn_click == "START":
                        self.new_harvest.run_thread(self.new_harvest.run_low_rpm_calibration, (low_rpm_in, set_time))
                    if self.btn_click == "CNT":
                        self.new_harvest.run_thread(self.new_harvest.run_high_rpm_calibration, (high_rpm_in, set_time))
                    if self.btn_click == "SAVE":
                        self.new_harvest.save_calibration_data(filename, low_rpm_vol, high_rpm_vol)

                if prop_id == "btn-save-calib":
                    if self.current_calibration_step == CalibrationStep.HIGH_RPM_DONE:
                        self.btn_click = "SAVE"
                        display_confirm_dialog = True
                        confirm_dialog_message = "Press OK to confirm saving to file"

            return current_step_text, calib_dialog_message, display_calib_dialog, confirm_dialog_message, display_confirm_dialog
                    