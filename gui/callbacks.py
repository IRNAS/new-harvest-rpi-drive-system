import json
import dash
import logging
import datetime

from gui.app import app
from dash.dependencies import Input, Output, State
from gui.components.functions import generate_figure, generate_figure_data, shutdown_pi, restart_pi, update_device, restart_service
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

color_pin_high = "#ff2929"
color_pin_low = "#3a3a3a"
class RhMicroCallbacks():
    """Wrapper class so callbacks can be defined in this file"""
    def __init__(self, rh_micro):
        """
        Initialize RhMicroCallbaks class. Creates an instance of rhmicro main class and relates all GUI commands to functions in main class:
        Functions called:
        - update_graphs()
        - update_button_funcs()
        - update_settings
        """
        self.rh_micro = rh_micro

        # keep track of 200 last values
        self.press_data = []
        self.analog_press_data = []
        self.power_data = []
        self.set_press_data = []
        self.temp_data = []
        self.set_temp_data = []

        self.data_count = 2000

        self.prev_usb_state = None
        self.usb_state = None
        self.first_mount = None

        self.current_state = None

        self.regulation_on = False

    def callbacks(self):

        @app.callback(
            [
                Output("save-input-hidden-div", "children"),
                Output("save-measurement-dialog", "displayed"),
                Output("save-measurement-dialog", "message")
            ],
            [
                Input("btn-save-user-input", "n_clicks"),
                Input("save-measurement-dialog", "submit_n_clicks")
            ],
            [
                State("id-rheo-input", "value"),
                State("sub-id-rheo-input", "value"),
                State("description-input", "value"),
                State("meas-date", "value"),
                State("extraction-date-input", "value"),
                State("liquid-type-input", "value"),
                State("set-temp-input", "value"),
                State("channel-type-input", "value"),
                State("channel-id-input", "value"),
                State("device-id-input", "value"),
                State("sample-class-dropdown", "value"),
                State("behaviour-dropdown", "value"),
                State("type-dropdown", "value"),
                State("base-dropdown", "value"),
                State("system-input", "value"),
                State("filename-input", "value")
            ]
        )
        def save_user_input(btn_save, confirm_save, id_rheo, sub_id_rheo, desc, meas_date, ext_date, liq_type, set_temp, ch_type, ch_id, dev_id, sample_cls, behaviour, type, base, system, filename):
            
            ctx = dash.callback_context
            print(ctx.triggered)

            display_save_dialog = False
            save_dialog_message = "Saving file to PATH"

            user_input_json = {}
            user_input_json["id_rheo"] = id_rheo
            user_input_json["sub_id_rheo"] = sub_id_rheo
            user_input_json["desc"] = desc
            user_input_json["meas_date"] = meas_date
            user_input_json["ext_date"] = ext_date
            user_input_json["liq_type"] = liq_type
            user_input_json["set_temp"] = set_temp
            user_input_json["ch_type"] = ch_type
            user_input_json["ch_id"] = ch_id
            user_input_json["dev_id"] = dev_id
            user_input_json["sample_cls"] = sample_cls
            user_input_json["behaviour"] = behaviour
            user_input_json["type"] = type
            user_input_json["base"] = base
            user_input_json["system"] = system

            if ctx.triggered and ctx.triggered[0]['value'] > 0:
                split = ctx.triggered[0]["prop_id"].split(".")
                prop_id = split[0]
                print(split)

                if prop_id == "save-measurement-dialog":
                    with open(f"/mnt/storage/measurements/{filename}.json", 'w') as outfile:
                        json.dump(user_input_json, outfile)

                    self.rh_micro.current_measurement_filename = filename

                    # trigger temperature control
                    temp = 28
                    try:
                        temp = float(set_temp)
                    except Exception as e:
                        print(e)
                        
                    self.rh_micro.thermal_control.set_temp_target(temp)

                if prop_id == "btn-save-user-input":

                    display_save_dialog = True
                    save_dialog_message = f"Saving measurement to {filename}.json"

            return [None], display_save_dialog, save_dialog_message

        @app.callback(
            [
                Output("confirm-close-alert", "displayed"),
                Output("confirm-refresh-alert", "displayed"),
                Output("confirm-update-alert", "displayed"),
                Output("USB-mounted-alert", "displayed"),
                Output("USB-unmounted-alert", "displayed")
            ],
            [
                Input("confirm-close-alert", "submit_n_clicks"),
                Input("confirm-refresh-alert", "submit_n_clicks"),
                Input("confirm-update-alert", "submit_n_clicks"),
                Input("btn-shutdown", "n_clicks"),
                Input("btn-restart-device", "n_clicks"),
                Input("btn-update-service", "n_clicks"),
                Input("USB-mounted-alert", "submit_n_clicks")
            ]
        )
        def update_header_click(close, refresh, update, btn_close, btn_restart, btn_update, usb_mounted):
            ctx = dash.callback_context

            display_update_alert = False
            display_close_alert = False
            display_refresh_alert = False

            self.prev_usb_state = self.usb_state
            self.usb_state, mounted_at_start = self.rh_micro.get_usb_mounted()
            #print(f"usb state: {self.usb_state}, prev state: {self.prev_usb_state}, mounted at start: {mounted_at_start}")
            display_usb_mounted_alert = False
            display_usb_unmounted_alert = False
            if self.prev_usb_state != self.usb_state:
                if self.usb_state == True and self.prev_usb_state == False:
                    display_usb_mounted_alert = True
                    #if not mounted_at_start:
                if self.usb_state == False and self.prev_usb_state == True:
                    display_usb_unmounted_alert = True

            if ctx.triggered and ctx.triggered[0]['value'] > 0:

                split = ctx.triggered[0]["prop_id"].split(".")
                prop_id = split[0]
                print(split)

                if prop_id == "btn-shutdown":
                    display_close_alert = True

                if prop_id == "btn-restart-device":
                    display_refresh_alert = True

                if prop_id == "btn-update-service":
                    display_update_alert = True

                if prop_id == "confirm-close-alert":
                    shutdown_pi()
                
                if prop_id == "confirm-refresh-alert":
                    restart_service()

                if prop_id == "confirm-update-alert":
                    update_device()

                if prop_id == "USB-mounted-alert":
                    restart_pi()

                if prop_id == "pump-control-navlink":
                    pump_control_navitem_class = True
                if prop_id == "pressure-control-navlink":
                    pressure_control_navitem_class = True


            return display_close_alert, display_refresh_alert, display_update_alert, display_usb_mounted_alert, display_usb_unmounted_alert
        ############## Pump control layout callbacks #############
        ## graph refresh callback
        @app.callback(
            [
                Output("press-graph", "figure"),
                Output("power-graph", "figure"),
                Output("press-span", "children"),
                Output("pump-state-span", "children"),
                Output("interrupt-state-div", "children")  # return current state of interrupts
                
                # Output("USB-mounted-alert", "displayed"),
                # Output("USB-unmounted-alert", "displayed")
            ],
            [
                Input("graph-refresh-interval-component", "n_intervals")
            ],
            [
                State("power-graph", "figure"),
                State("press-graph", "figure")
            ]
        )
        def update_graphs_pump_control(n, power_graph, press_graph):
            """
            Calls get_data() from rh_micro class and updates all graphs on set interval.
            
            power_graph = frequency graph instance
            press_graph = pressure graph instance
            
            """
            press_data, analog_press_data, power_data, _, pins_0_data, pins_1_data, _, _ = self.rh_micro.get_data()

            # print(analog_press_data)
            self.press_data += press_data
            self.analog_press_data += analog_press_data
            self.power_data += power_data

            self.press_data = self.press_data[-self.data_count:]  # keep track of last 200 values
            self.analog_press_data = self.analog_press_data[-self.data_count:]
            self.power_data = self.power_data[-self.data_count:]  # keep track of last 200 values

            new_press = generate_figure_data([self.press_data, self.analog_press_data], ["Pressure (Pa)", "Analog Pressure (Pa)"], ['rgb(10, 100, 200)', 'rgb(250, 140, 15)'])
            new_power = generate_figure_data([self.power_data], ["Power (mW)"], ['rgb(10, 100, 200)'])
            # new_power = None

            press_graph["data"] = new_press
            power_graph["data"] = new_power

            pump_state = self.rh_micro.pump_control.get_pump_state()
            if pump_state == 0:
                pump_state = "Not Running"
            if pump_state == 1:
                pump_state = "Manual Mode"
            if pump_state == 2:
                pump_state = "PID Mode"
            if pump_state == -1:
                pump_state = "Not Connected"

            interrupt_state = generate_interrupt_state(pins_0_data, pins_1_data)

            if len(press_data) > 0:
                last_press = str(round(press_data[-1], 2)) + " Pa"
            elif len(self.press_data):
                last_press = str(round(self.press_data[-1], 2)) + " Pa"
            else:
                last_press = "N/A Pa"
            return press_graph,  power_graph, last_press, pump_state, interrupt_state

        @app.callback(
            [
                Output("pump-output-alert", "displayed"),
                Output("power-input-alert", "displayed"),
            ],
            [
                Input("btn-start-meas", "n_clicks"),
                Input("btn-stop-meas", "n_clicks"),
                Input("btn-start-pump", "n_clicks"),
                Input("btn-stop-pump", "n_clicks"),
                Input("btn-config-pump", "n_clicks"),
            ],
            [
                State("power-input", "value")
            ]
        )
        def update_button_funcs_pump_control(btn_start_meas, btn_stop_meas, btn_start_pump, btn_stop_pump, btn_config_pump, set_power):
            """
            this function handles user input by calling appropriate function from rh_micro class upon user click/touch.
            """
            ctx = dash.callback_context
            display_power_alert = False
            display_pump_alert = False
            display_close_alert = False
            display_refresh_alert = False
            display_update_alert = False

            # print(ctx.triggered)

            if ctx.triggered and ctx.triggered[0]['value'] > 0:

                split = ctx.triggered[0]["prop_id"].split(".")
                prop_id = split[0]
                print(split)

                if prop_id == "btn-start-meas":
                    filename = None
                    if self.rh_micro.current_measurement_filename is not None:
                        filename = f"/mnt/storage/measurements/{self.rh_micro.current_measurement_filename}.csv"
                        try:
                            self.rh_micro.pressure_control.set_start_measuring(filename)
                        except:
                            pass
                    else:
                        try:
                            self.rh_micro.pressure_control.set_start_measuring()
                        except:
                            pass
                if prop_id == "btn-stop-meas":
                    try:
                        self.rh_micro.pressure_control.set_stop_measuring()
                    except:
                        pass

                if prop_id == "btn-start-pump":
                    try:
                        power_val = int(set_power)
                        if power_val >= 10 and power_val <= 1400:
                            if not self.rh_micro.pump_control.set_power(int(set_power)):
                                display_power_alert = True
                    except:
                        display_power_alert = True
                        pass
                    
                    if not display_power_alert:
                        self.rh_micro.pump_control.disable_pid()
                        ret = self.rh_micro.pump_control.enable_pump()
                        if not ret:
                            display_pump_alert = True

                if prop_id == "btn-stop-pump":
                    if not self.rh_micro.pump_control.disable_pump():
                        display_pump_alert = True

                if prop_id == "btn-config-pump":
                    try:
                        power_val = int(set_power)
                        if power_val >= 10 and power_val <= 1400:
                            if not self.rh_micro.pump_control.set_power(int(set_power)):
                                display_power_alert = True
                    except:
                        display_power_alert = True
                        pass

            return display_pump_alert, display_power_alert

    ########## Setpoint Pressure control layout callbacks ############
    ## graph refresh callback
        @app.callback(
            [
                Output("press-graph-p", "figure"),
                # Output("power-graph-p", "figure"),
                Output("press-span-p", "children"),
                Output("pump-state-span-p", "children"),
                Output("interrupt-state-div-p", "children")  # return current state of interrupts
                # Output("USB-mounted-alert-p", "displayed"),
                # Output("USB-unmounted-alert-p", "displayed")
            ],
            [
                Input("graph-refresh-interval-component-p", "n_intervals")
            ],
            [
                State("press-graph-p", "figure"),
                # State("set-press-graph-p", "figure")
            ]
        )

        def update_graphs_press_control(n, press_graph):
            """
            Calls get_data() from rh_micro class and updates all graphs on set interval.
            
            power_graph = power graph instance
            press_graph = pressure graph instance
            
            """
            press_data, analog_press_data, _, set_press_data, pins_0_data, pins_1_data, _, _ = self.rh_micro.get_data()

            # print(self.set_press_data)
            self.press_data += analog_press_data
            self.set_press_data += set_press_data

            self.press_data = self.press_data[-self.data_count:]  # keep track of last 200 values
            self.set_press_data = self.set_press_data[-self.data_count:]

            new_data = generate_figure_data([self.press_data, self.set_press_data], ["Pressure (Pa)", "Set Pressure (Pa)"], ['rgb(10, 100, 200)', 'rgb(250, 140, 15)'])

            press_graph["data"] = new_data
            pump_state = "Not Connected"

            try:
                pump_state = self.rh_micro.pump_control.get_pump_state()
                if pump_state == 0:
                    pump_state = "Not Running"
                if pump_state == 1:
                    pump_state = "Manual Mode"
                if pump_state == 2:
                    pump_state = "PID Mode"
                if pump_state == -1:
                    pump_state = "Not Connected"
            except Exception as e:
                pass

            interrupt_state = generate_interrupt_state(pins_0_data, pins_1_data)
            
            if len(press_data) > 0:
                last_press = str(round(press_data[-1], 2)) + " Pa"
            elif len(self.press_data):
                last_press = str(round(self.press_data[-1], 2)) + " Pa"
            else:
                last_press = "N/A Pa"
            return press_graph, last_press, pump_state, interrupt_state

        @app.callback(
            [
                Output("pump-output-alert-p", "displayed"),
                Output("press-input-alert-p", "displayed"),
                Output("csv-path-p", "children")
            ],
            [
                Input("btn-start-meas-p", "n_clicks"),
                Input("btn-stop-meas-p", "n_clicks"),
                Input("btn-start-pump-p", "n_clicks"),
                Input("btn-stop-pump-p", "n_clicks"),
                Input("btn-config-pump-p", "n_clicks")

            ],
            [
                State("pressure-input-p", "value")
            ]
        )
        def update_button_funcs_press_control(btn_start_meas, btn_stop_meas, btn_start_pump, btn_stop_pump, btn_config_pump, set_press):
            """
            this function handles user input by calling appropriate function from rh_micro class upon user click/touch.
            """
            ctx = dash.callback_context
            display_press_alert = False
            display_pump_alert = False
            display_close_alert = False

            # print(ctx.triggered)
            if ctx.triggered and ctx.triggered[0]['value'] > 0:

                split = ctx.triggered[0]["prop_id"].split(".")
                prop_id = split[0]
                print(split)

                if prop_id == "btn-start-meas-p":
                    filename = None
                    if self.rh_micro.current_measurement_filename is None:
                        self.rh_micro.current_measurement_filename = datetime.datetime.now().strftime('%d_%m_%Y_%H_%M_%S')

                    if self.rh_micro.current_measurement_filename is not None:
                        filename = f"/mnt/storage/measurements/{self.rh_micro.current_measurement_filename}.csv"
                        try:
                            self.rh_micro.pressure_control.set_start_measuring(filename)
                        except:
                            pass
                    else:
                        try:
                            self.rh_micro.pressure_control.set_start_measuring()
                        except:
                            pass
                if prop_id == "btn-stop-meas-p":
                    try:
                        self.rh_micro.pressure_control.set_stop_measuring()
                    except:
                        pass

                if prop_id == "btn-start-pump-p":
                    try:
                        press_val = int(set_press)
                        if press_val < -100 and press_val  >= -43000:
                            if not self.rh_micro.pump_control.set_pressure(int(press_val)):
                                display_pump_alert = True
                        else:
                            display_press_alert = True
                    except:
                        display_press_alert = True
                        pass

                    if not display_press_alert:
                        self.rh_micro.pump_control.enable_pid()
                        ret = self.rh_micro.pump_control.enable_pump()
                        if not ret:
                            display_pump_alert = True

                if prop_id == "btn-stop-pump-p":
                    if not self.rh_micro.pump_control.disable_pump():
                        display_pump_alert = True

                if prop_id == "btn-config-pump-p":
                    try:
                        press_val = int(set_press)
                        if press_val < -100 and press_val  >= -43000:
                            if not self.rh_micro.pump_control.set_pressure(int(press_val)):
                                display_pump_alert = True
                        else:
                            display_press_alert = True
                    except:
                        display_press_alert = True
                        pass

            return display_pump_alert, display_press_alert, f"{self.rh_micro.current_measurement_filename}.csv" #display_close_alert, display_refresh_alert, display_update_alert

    ########## Electrode Pressure control layout callbacks ############
    ## graph refresh callback
        @app.callback(
            [
                Output("press-graph-e", "figure"),
                # Output("power-graph-p", "figure"),
                Output("press-span-e", "children"),
                Output("pump-state-span-e", "children"),
                Output("interrupt-state-div-e", "children"),  # return current state of interrupts
                # Output("td-on", "children"),
                # Output("td-g1", "children"),
                # Output("td-g2", "children"),
                # Output("td-g3", "children"),
                # Output("td-g4", "children"),
                # Output("td-g5", "children"),
                # Output("td-g6", "children")
                # Output("USB-mounted-alert-p", "displayed"),
                # Output("USB-unmounted-alert-p", "displayed")
            ],
            [
                Input("graph-refresh-interval-component-e", "n_intervals")
            ],
            [
                State("press-graph-e", "figure"),
                # State("set-press-graph-p", "figure")
            ]
        )

        def update_graphs_press_control(n, press_graph):
            """
            Calls get_data() from rh_micro class and updates all graphs on set interval.
            
            power_graph = power graph instance
            press_graph = pressure graph instance
            
            """

            press_data, analog_press_data, _, set_press_data, pins_0_data, pins_1_data, _, _ = self.rh_micro.get_data()

            # print(self.set_press_data)
            self.press_data += analog_press_data
            self.set_press_data += set_press_data

            self.press_data = self.press_data[-self.data_count:]  # keep track of last 200 values
            self.set_press_data = self.set_press_data[-self.data_count:]

            new_data = generate_figure_data([self.press_data, self.set_press_data], ["Pressure (Pa)", "Set Pressure (Pa)"], ['rgb(10, 100, 200)', 'rgb(250, 140, 15)'])

            press_graph["data"] = new_data
            pump_state = "Not Connected"

            try:
                pump_state = self.rh_micro.pump_control.get_pump_state()
                if pump_state == 0:
                    pump_state = "Not Running"
                if pump_state == 1:
                    pump_state = "Manual Mode"
                if pump_state == 2:
                    pump_state = "PID Mode"
                if pump_state == -1:
                    pump_state = "Not Connected"
            except Exception as e:
                pass
                # if pump_state == -1:
                #     pump_state = "Not Connected"


            interrupt_state = generate_interrupt_state(pins_0_data, pins_1_data)

            # timestamps = self.rh_micro.timestamps

            if len(press_data) > 0:
                last_press = str(round(press_data[-1], 2)) + " Pa"
            elif len(self.press_data):
                last_press = str(round(self.press_data[-1], 2)) + " Pa"
            else:
                last_press = "N/A Pa"
            return press_graph, last_press, pump_state, interrupt_state #, f"{round(timestamps[0], 2)} ms", f"{round(timestamps[1], 2)} ms", f"{round(timestamps[2], 2)} ms", f"{round(timestamps[3], 2)} ms", f"{round(timestamps[4], 2)} ms", f"{round(timestamps[5], 2)} ms", f"{round(timestamps[6], 2)} ms"

        @app.callback(
            [
                Output("pump-output-alert-e", "displayed"),
                Output("press-input-alert-e", "displayed"),
                Output("press-input-alert-e", "message"),
                Output("csv-path-e", "children")
            ],
            [
                Input("btn-start-meas-e", "n_clicks"),
                Input("btn-stop-meas-e", "n_clicks"),
                Input("btn-start-pump-e", "n_clicks"),
                Input("btn-stop-pump-e", "n_clicks"),
                Input("btn-config-pump-e", "n_clicks")

            ],
            [
                State("elec-cd", "value"),
                State("elec-g1", "value"),
                State("elec-g2", "value"),
                State("elec-g3", "value"),
                State("elec-g4", "value"),
                State("elec-g5", "value"),
                State("elec-on", "value")
            ]
        )
        def update_button_funcs_electrode_press_control(btn_start_meas, btn_stop_meas, btn_start_pump, btn_stop_pump, btn_config_pump,
                CD, G1, G2, G3, G4, G5, ON                                         
            ):
            """
            this function handles user input by calling appropriate function from rh_micro class upon user click/touch.
            """
            ctx = dash.callback_context
            display_press_alert = False
            display_pump_alert = False
            display_close_alert = False

            press_alert_text = "Pressure input must be an integer between -43000 and -100!"
            press_alert_fields = []

            print(ctx.triggered)
            if ctx.triggered and ctx.triggered[0]['value'] > 0:

                split = ctx.triggered[0]["prop_id"].split(".")
                prop_id = split[0]
                print(split)

                if prop_id == "btn-start-meas-e":
                    filename = None
                    if self.rh_micro.current_measurement_filename is None:
                        self.rh_micro.current_measurement_filename = datetime.datetime.now().strftime('%d_%m_%Y_%H_%M_%S')

                    if self.rh_micro.current_measurement_filename is not None:
                        print("Starting measurements")
                        filename = f"/mnt/storage/measurements/{self.rh_micro.current_measurement_filename}.csv"
                        try:
                            self.rh_micro.pressure_control.set_start_measuring(filename)
                        except:
                            pass
                    else:
                        try:
                            self.rh_micro.pressure_control.set_start_measuring()
                        except:
                            pass
                if prop_id == "btn-stop-meas-e":
                    try:
                        self.rh_micro.pressure_control.set_stop_measuring()
                    except:
                        pass

                if prop_id == "btn-start-pump-e":
                    
                    try:
                        if CD > -100 or CD < -43000:
                            press_alert_fields.append("P_0")
                            display_press_alert = True
                    except:
                        press_alert_fields.append("CD")
                        display_press_alert = True
                    try:
                        if G1 > -100 or G1 < -43000:
                            press_alert_fields.append("P_2")
                            display_press_alert = True
                    except:
                        press_alert_fields.append("P_2")
                        display_press_alert = True
                    try:
                        if G2 > -100 or G2 < -43000:
                            press_alert_fields.append("P_3")
                            display_press_alert = True
                    except:
                        press_alert_fields.append("P_3")
                        display_press_alert = True
                    try:
                        if G3 > -100 or G3 < -43000:
                            press_alert_fields.append("P_4")
                            display_press_alert = True
                    except:
                        press_alert_fields.append("P_4")
                        display_press_alert = True
                    try:
                        if G4 > -100 or G4 < -43000:
                            press_alert_fields.append("P_5")
                            display_press_alert = True
                    except:
                        press_alert_fields.append("P_5")
                        display_press_alert = True
                    try:
                        if G5 > -100 or G5 < -43000:
                            press_alert_fields.append("P_6")
                            display_press_alert = True
                    except:
                        press_alert_fields.append("P_6")
                        display_press_alert = True
                    # try:
                    #     if G6 > -100 or G6 < -43000:
                    #         press_alert_fields.append("G6")
                    #         display_press_alert = True
                    # except:
                    #     press_alert_fields.append("G6")
                    #     display_press_alert = True
                    try:
                        if ON > -100 or ON < -43000:
                            press_alert_fields.append("P_1")
                            display_press_alert = True
                    except:
                        press_alert_fields.append("P_1")
                        display_press_alert = True

                    if not display_press_alert:
                        try:
                            self.rh_micro.set_electrode_pressure_targets([CD, G1, G2, G3, G4, G5, ON])
                            self.rh_micro.pump_control.enable_pid()
                            # ret = self.rh_micro.pump_control.enable_pump()
                            self.rh_micro.start_electrode_set_pressure_regulation_thread()
                        except:
                            pass
                        # if not ret:
                        #     display_pump_alert = True

                    else:
                        press_alert_text = f"Pressure input on {', '.join(press_alert_fields)} must be an integer between -43000 and -100!"

                if prop_id == "btn-stop-pump-e":
                    if not self.rh_micro.pump_control.disable_pump():
                        display_pump_alert = True

                if prop_id == "btn-config-pump-e":
                    try:
                        if CD > -100 or CD < -43000:
                            press_alert_fields.append("CD")
                            display_press_alert = True
                    except:
                        press_alert_fields.append("CD")
                        display_press_alert = True
                    try:
                        if G1 > -100 or G1 < -43000:
                            press_alert_fields.append("G1")
                            display_press_alert = True
                    except:
                        press_alert_fields.append("G1")
                        display_press_alert = True
                    try:
                        if G2 > -100 or G2 < -43000:
                            press_alert_fields.append("G2")
                            display_press_alert = True
                    except:
                        press_alert_fields.append("G2")
                        display_press_alert = True
                    try:
                        if G3 > -100 or G3 < -43000:
                            press_alert_fields.append("G3")
                            display_press_alert = True
                    except:
                        press_alert_fields.append("G3")
                        display_press_alert = True
                    try:
                        if G4 > -100 or G4 < -43000:
                            press_alert_fields.append("G4")
                            display_press_alert = True
                    except:
                        press_alert_fields.append("G4")
                        display_press_alert = True
                    try:
                        if G5 > -100 or G5 < -43000:
                            press_alert_fields.append("G5")
                            display_press_alert = True
                    except:
                        press_alert_fields.append("G5")
                        display_press_alert = True
                    # try:
                    #     if G6 > -100 or G6 < -43000:
                    #         press_alert_fields.append("G6")
                    #         display_press_alert = True
                    # except:
                    #     press_alert_fields.append("G6")
                    #     display_press_alert = True
                    try:
                        if ON > -100 or ON < -43000:
                            press_alert_fields.append("ON")
                            display_press_alert = True
                    except:
                        press_alert_fields.append("ON")
                        display_press_alert = True

                    if not display_press_alert:
                        try:
                            self.rh_micro.set_electrode_pressure_targets([CD, G1, G2, G3, G4, G5, ON])
                        except:
                            pass
                        # if not ret:
                        #     display_pump_alert = True

                    else:
                        press_alert_text = f"Pressure input on {', '.join(press_alert_fields)} must be an integer between -43000 and -100!"

            print(f"Press alert text: {press_alert_fields}")

            return display_pump_alert, display_press_alert, press_alert_text, f"{self.rh_micro.current_measurement_filename}.csv" 


 ########## Temperature control layout callbacks ############
        ## graph refresh callback
        @app.callback(
            [
                Output("temp-graph", "figure"),
                # Output("power-graph-p", "figure"),
                # Output("temp-span", "children"),
                Output("tc-state-span", "children")
                # Output("USB-mounted-alert-p", "displayed"),
                # Output("USB-unmounted-alert-p", "displayed")
            ],
            [
                Input("tc-refresh-interval-component", "n_intervals")
            ],
            [
                State("temp-graph", "figure"),
                # State("set-press-graph-p", "figure")
            ]
        )

        def update_graphs_temp_control(n, temp_graph):
            """
            Calls get_data() from rh_micro class and updates all graphs on set interval.
            
            power_graph = power graph instance
            press_graph = pressure graph instance
            
            """

            # print("THERMAL CONTROL UPDATE")
            _, _, _, _, _, _, set_temp_data, temp_data = self.rh_micro.get_data()

            self.temp_data += temp_data
            self.set_temp_data += set_temp_data

            new_data = generate_figure_data([self.temp_data, self.set_temp_data], ["Temperature (°C)", "Set Temperature (°C)"], ['rgb(10, 100, 200)', 'rgb(250, 140, 15)'])

            temp_graph["data"] = new_data

            tc_state = self.rh_micro.thermal_control.get_tc_state()
            if tc_state == 0:
                tc_state = "Not Running"
            if tc_state == 1:
                tc_state = "Running"
            if tc_state == -1:
                tc_state = "Not Connected"
            
            # if (len(temp_data)) > 0:
            #     last_temp = str(round(temp_data[-1], 2)) + " °C"
            # else:
            #     last_temp = "N/A Pa"
            return temp_graph, tc_state

        @app.callback(
            [
                Output("tc-output-alert", "displayed"),
                Output("temp-input-alert", "displayed")
            ],
            [
                Input("btn-start-tc", "n_clicks"),
                Input("btn-stop-tc", "n_clicks"),
                Input("btn-config-tc", "n_clicks")

            ],
            [
                State("temp-input", "value")
            ]
        )
        def update_button_funcs_temp_control(btn_start_tc, btn_stop_tc, bt_config_tc, set_temp):
            """
            this function handles user input by calling appropriate function from rh_micro class upon user click/touch.
            """
            ctx = dash.callback_context
            display_tc_alert = False
            display_temp_alert = False

            # print(f"Set temp value: {set_temp}")

            # print(ctx.triggered)
            if ctx.triggered and ctx.triggered[0]['value'] > 0:

                split = ctx.triggered[0]["prop_id"].split(".")
                prop_id = split[0]
                # print(split)

                if prop_id == "btn-start-tc":
                    try:
                        temp_val = int(set_temp)
                        # print(f"Temp val: {temp_val}")
                        if temp_val > 0 and temp_val <= 30:
                            ret = self.rh_micro.thermal_control.set_temp_target(float(temp_val))
                            # print(ret)
                            if not ret:
                                # print(f"Unable to set temp target 1")
                                display_tc_alert = True
                        else:
                            display_temp_alert = True
                    except Exception as e:
                        # print(f"Error: {e}")
                        # print(f"Unable to set temp target 2")
                        display_temp_alert = True
                        pass

                    if not display_temp_alert:
                        ret = self.rh_micro.thermal_control.enable_TEC()
                        print(f"Enabling TEC from gui")
                        if not ret:
                            display_tc_alert = True
                    
                if prop_id == "btn-stop-tc":
                    if not self.rh_micro.thermal_control.disable_TEC():
                        display_tc_alert = True

                if prop_id == "btn-config-tc":
                    try:
                        temp_val = int(set_temp)
                        if temp_val > 0 and temp_val  <= 30:
                            if not self.rh_micro.thermal_control.set_temp_target(float(temp_val)):
                                display_tc_alert = True
                        else:
                            display_temp_alert = True
                    except:
                        display_temp_alert = True
                        pass

            return display_tc_alert, display_temp_alert

