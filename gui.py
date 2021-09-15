from flask import Flask

import sys
import dash
import dash_daq as daq
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from postep256 import PoStep256USB

postep = PoStep256USB()
# Check if driver was detected and configuration could be established
if postep.device is None:
    print("Driver not found, exiting.")
    sys.exit(0)

# made with the help of: https://github.com/davidcomfort/dash_sample_dashboard

# application scope configs
# logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%d/%m/%Y %H:%M:%S", level=int(10))

# log = logging.getLogger("werkzeug")
# log.setLevel(logging.ERROR)

# flask config
# bootstrap theme url

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.MATERIA],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
)
server = app.server
app.config["suppress_callback_exceptions"] = True

@app.callback(
    Output("hidden-div", "children"),
    [
        Input("btn-start", "n_clicks"),
        Input("btn-stop", "n_clicks"),
        Input("btn-set", "n_clicks"),
        Input("direction-slider", "value")
    ],
    [
        State("speed-txt-input", "value"),
        State("direction-slider", "value")
    ]
)
def update_btn_click(start, stop, set, dir, speed, dir_state):
    ctx = dash.callback_context
    print(ctx.triggered)

    dir_str = "cw" if dir_state == 100 else "acw"

    print(f"Current direction: {dir_str}")

    if ctx.triggered and ctx.triggered[0]["value"] > 0:
        split = ctx.triggered[0]["prop_id"].split(".")
        prop_id = split[0]
        print(split)

        try:
            speed = int(speed)
        except Exception as e:
            print(e)

        if prop_id == "btn-start":
            postep.move_speed(speed, direction=dir_str)
            postep.run_sleep(True)

        if prop_id == "btn-stop":
            postep.run_sleep(False)

        if speed is None:
            speed = 0
        if speed < 0 or speed > 10000:
            speed = 0

        if prop_id == "btn-set":
            postep.move_speed(speed, direction=dir_str)

        if prop_id == "direction-slider":
            postep.move_speed(speed, direction=dir_str)
        


    return ""

app.layout = dbc.Container(
    id="main-layout",
    style={"width": "300px", "padding-right": "0px"},
    children=[
        dcc.Interval(id="graph-refresh-interval-component", interval=100, n_intervals=0),
        html.Div(id="hidden-div", style={"display": "none"}),
        html.Div(
            style={"margin-top": "10px", "text-align": "center"},
            children=[
                html.Span("Set Speed", style={"margin-right": "10px", "font-size": "18px"}),
                dcc.Input(
                    type="text",
                    id="speed-txt-input", value="50"
                )
            ]
        ),
        html.Div(
            style={"margin-top": "20px", "text-align": "center"},
            children=[
                dcc.Slider(
                    id="direction-slider",
                    min=99,
                    max=100,
                    value=100,
                    marks={
                        99: {"label": "ACW", "style": {"font-size": "18px", "font-weight": "bold"}},
                        100: {"label": "CW", "style": {"font-size": "18px", "font-weight": "bold"}}
                    },
                    included=False,
                    persistence=True,
                    persistence_type="local"
                )
            ]
        ),
        html.Div(
            style={"margin-top": "20px", "text-align": "center"},
            children=[
                dbc.Button("Start", id="btn-start", n_clicks=0, style={"margin-right": "10px"}),
                dbc.Button("Stop", id="btn-stop", n_clicks=0, style={"margin-right": "10px"}),
                dbc.Button("Set", id="btn-set", n_clicks=0)
            ]
        )
    ]
)

if __name__ == "__main__":
    hostname = "0.0.0.0"
    port = "1234"  # set port > 1024 to run as unprivileged userlayout_pressure_control
    app.scripts.config.serve_locally = True

    app.run_server(
        port=port,
        debug=False,
        host=hostname,
        #dev_tools_ui=False,
        #dev_tools_props_check=False
    )