from dash import dcc, html
import dash_bootstrap_components as dbc
# from ..components.flow_graph import generate_graph_section
from ..components.custom_toggle import custom_toggle
from ..components.input_fields import dropdown

def generate_single_speed_layout(calibs, measurements):
    """
    Control layout generation with all widgets (buttons, sliders, and input windows).
    """

    control_layout = html.Div(
        id="singles-speed-display",
        className="d-flex flex-column",
        children=[
            # html.Div(id="hidden-div", style={"visibility":"hidden"}),
            html.Div(
                # style={"width": "20%"},
                className="d-flex flex-row",
                children=[
                    html.Div(
                        className="d-flex flex-column",
                        style={"width": "420px"},
                        children=[
                            html.Div(
                                className="d-flex flex-column mt-2",
                                children=[
                                    html.Span("Loaded Calibration:", style={"font-size": "20px", "font-weight": "bold"}),
                                    html.Div(
                                        className="mt-1",
                                        children=[
                                            dbc.Label("No Calibration Loaded", className="wrap", id="calibration-filename", html_for="upload-calibration", style={"font-size": "18px"}),
                                            dcc.Upload(
                                                id="upload-calibration",
                                                accept=".json",
                                                children=[
                                                    dbc.Button("Browse", style={"width": "100px"})
                                                ]
                                            )
                                        ]
                                    ),

                                ]
                            ),
                            html.Div(
                                className="d-flex flex-column mt-2",
                                children=[
                                    html.Span("Select Calibration:", style={"font-size": "20px", "font-weight": "bold"}),
                                    dcc.Dropdown(
                                        id=f"select-calibration-dropdown",
                                        className="mt-1",
                                        style={"width": "240px"},
                                        options=calibs,
                                        persistence=True
                                    ),
                                ]
                            ),
                            
                        ],
                    ),
                    
                    # dropdown(id="select-calibration", label="Select Calibration", fields=calibs),
                    html.Div(
                        className="d-flex flex-column",
                        # style={"margin-left": "174px"},
                        children=[
                            html.Div(
                                className="d-flex flex-row mt-2",
                                children=[
                                    html.Span("Slope (mL/revol):", className="sfs-title"),
                                    html.Span(id="slope", children="0", className="sfs-value", style={"margin-left": "153px"}),
                                ]
                            ),
                            html.Div(
                                className="d-flex flex-row mt-2",
                                children=[
                                    html.Span("Set rpm:", className="sfs-title"),
                                    html.Span(id="set-rpm", children="0", className="sfs-value", style={"margin-left": "238px"}),
                                ]
                            ),
                            html.Div(
                                className="d-flex flex-row mt-2",
                                children=[
                                    html.Span(
                                        "Set Flow (mL/min): ", className="h4 font-weight-bold", style={"width": "325px"}),
                                    dcc.Input(
                                        id="flow-speed-input",
                                        type="number",
                                        debounce=True,  # must be set to true for onscreen keyboard to work
                                        value=10,
                                        persistence=True,
                                        # max=90,
                                        # min=10,
                                        style={"width": "26%", "height": "100%", "padding-left": "5px", "font-weight": "bold", "background": "aliceblue", "border-radius": "5px"},
                                    )
                                ]
                            ),
                            html.Div(
                                className="d-flex flex-row mt-2",
                                children=[
                                    html.Span(
                                        "Set Acceleration (rpm/sec): ", className="h4 font-weight-bold", style={"width": "325px"}),
                                    dcc.Input(
                                        id="accel-rpm-input",
                                        type="number",
                                        debounce=True,  # must be set to true for onscreen keyboard to work
                                        value=10000,
                                        persistence=True,
                                        max=100000,
                                        min=1,
                                        style={"width": "26%", "height": "100%", "padding-left": "5px", "font-weight": "bold", "background": "aliceblue", "border-radius": "5px"},
                                    )
                                ]
                            ),
                            html.Div(
                                className="d-flex flex-row mt-2",
                                children=[
                                    html.Span("Select Direction", style={"width": "325px"}, className="h4 font-weight-bold"),
                                    dcc.Dropdown(
                                        id=f"select-direction-dropdown",
                                        options=[{"label": "CCW", "value": "acw"}, {"label": "CW", "value": "cw"}],
                                        value="acw",
                                        style={"width": "112px"},
                                        persistence=True
                                    ),
                                ]
                                # style={"width": "50%"},
                                # children=[
                                #     html.Span("ACW"),
                                #     custom_toggle(id="direction-toggle"),
                                #     html.Span("CW")
                                # ]
                            ),
                        ]
                    ),
                    
                ]
            ),
            html.Div(
                className="mt-2 d-flex flex-row justify-content-end",
                style={"width": "438px", "margin-left": "42.6%"},
                children=[
                    html.Div("Control", className="h4 font-weight-bold", style={"width": "100px", "padding-top": "14px"}),
                    dbc.Button("START", id="btn-start", style={"width": "110px", "margin-left": "98px"}, n_clicks=0, className="mt-2"),
                    dbc.Button("STOP", id="btn-stop", style={"width": "110px", "margin-left": "20px"}, n_clicks=0, className="mt-2")
                ]
            ),
            # html.Div(
            #     style={"width": "80%"},
            #     className="d-flex flex-row mt-4",
            #     children=[
            #         generate_graph_section(id="flow-speed-graph", x_axis_label="", y_axis_label="", measurements=measurements)
            #     ]
            # )
        ]
    )

    return control_layout

def layout_single_speed(calibs, measurements):
    return dbc.Container(
        id="main-layout",
        style={"padding-right": "0px", "padding-left": "0px"},
        children=[
            dcc.ConfirmDialog(
                id="confirm-dialog-rpm-alert",
                message=""
            ),
            dcc.Interval(id="graph-refresh-interval", interval=1000, n_intervals=0),
            # dcc.Interval(id="check-dir-interval", interval=500, n_intervals=0),
            generate_single_speed_layout(calibs, measurements)
        ]
    )