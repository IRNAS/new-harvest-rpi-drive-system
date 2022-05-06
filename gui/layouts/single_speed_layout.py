import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from ..components.flow_graph import generate_graph_section
from ..components.custom_toggle import custom_toggle
from ..components.input_fields import dropdown

def generate_single_speed_layout(calibs, measurements):
    """
    Control layout generation with all widgets (buttons, sliders, and input windows).
    """

    control_layout = html.Div(
        id="singles-speed-display",
        className="d-flex flex-row",
        children=[
            html.Div(id="hidden-div", style={"visibility":"hidden"}),
            html.Div(
                style={"width": "20%"},
                className="d-flex flex-column mt-3",
                children=[
                    html.Div(
                        className="d-flex flex-column",                        
                        children=[
                            html.Span("Loaded Calibration:", style={"font-size": "20px", "font-weight": "bold"}),
                            html.Div(
                               className="mt-1",
                               children=[
                                    dbc.Label("No Calibration Loaded", className="wrap", id="calibration-filename", html_for="upload-calibration"),
                                    dcc.Upload(
                                        id="upload-calibration",
                                        accept=".json",
                                        children=[
                                            dbc.Button("Browse", style={"width": "100px"})
                                        ]
                                    ),
                                    dropdown(id="select-calibration", label="Select Calibration", fields=calibs)
                               ] 
                            ),
                            html.Span("Slope (mL/revol):", style={"font-size": "20px", "font-weight": "bold", "margin-top": "20px"}),
                            html.Span(id="slope", children="0"),
                            html.Span("Set pwm (%):", style={"font-size": "20px", "font-weight": "bold", "margin-top": "20px"}),
                            html.Span(id="set-pwm", children="0")
                        ]
                    ),
                    html.Div(
                        className="d-flex flex-column mt-4",
                        children=[
                            html.Span(
                                "Set Flow (mL/min): ", className="h4 font-weight-bold"),
                            dcc.Input(
                                id="flow-speed-input",
                                type="number",
                                debounce=True,  # must be set to true for onscreen keyboard to work
                                value=10,
                                # max=90,
                                # min=10,
                                style={"width": "50%", "height": "100%", "padding-left": "5px", "font-weight": "bold", "background": "aliceblue", "border-radius": "5px"},
                            )
                        ]
                    ),
                    html.Div(
                        className="d-flex flex-column mt-3",
                        children=[
                            html.Span(
                                "Set Acceleration (pwm/sec): ", className="h4 font-weight-bold"),
                            dcc.Input(
                                id="accel-pwm-input",
                                type="number",
                                debounce=True,  # must be set to true for onscreen keyboard to work
                                value=100,
                                max=100,
                                min=1,
                                style={"width": "50%", "height": "100%", "padding-left": "5px", "font-weight": "bold", "background": "aliceblue", "border-radius": "5px"},
                            )
                        ]
                    ),
                    html.Div(
                        className="mt-4",
                        children=[
                            dbc.Button("SET", id="btn-set", style={"width": "100px"}, n_clicks=0)
                        ]
                    ),
                    html.Div(
                        className="d-flex flex-row mt-4 justify-content-between",
                        children=[
                            dropdown(id="select-direction", label="Select Direction", fields=[{"label": "CCW", "value": "acw"}, {"label": "CW", "value": "cw"}], value="acw")
                        ]
                        # style={"width": "50%"},
                        # children=[
                        #     html.Span("ACW"),
                        #     custom_toggle(id="direction-toggle"),
                        #     html.Span("CW")
                        # ]
                    ),
                    html.Div(
                        className="mt-4",
                        children=[
                            dbc.Button("START", id="btn-start", style={"width": "100px"}, n_clicks=0, className="mr-4"),
                            dbc.Button("STOP", id="btn-stop", style={"width": "100px"}, n_clicks=0, className="mr-2")
                        ]
                    )
                ]
            ),
            html.Div(
                style={"width": "80%"},
                className="d-flex flex-row mt-4",
                children=[
                    generate_graph_section(id="flow-speed-graph", x_axis_label="", y_axis_label="", measurements=measurements)
                ]
            )
        ]
    )

    return control_layout

def layout_single_speed(calibs, measurements):
    return dbc.Container(
        id="main-layout",
        style={"padding-right": "0px", "padding-left": "0px"},
        children=[
            dcc.ConfirmDialog(
                id="confirm-dialog-pwm-alert",
                message=""
            ),
            dcc.Interval(id="graph-refresh-interval", interval=1000, n_intervals=0),
            # dcc.Interval(id="check-dir-interval", interval=500, n_intervals=0),
            generate_single_speed_layout(calibs, measurements)
        ]
    )