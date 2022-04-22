import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from ..components.flow_graph import generate_graph_section
from ..components.custom_toggle import custom_toggle
from ..components.input_fields import dropdown

def generate_speed_profile_layout(calibs, profiles):
    """
    Control layout generation with all widgets (buttons, sliders, and input windows).
    """
    
    speed_profile_layout = html.Div(
        id="singles-speed-display",
        className="d-flex flex-row",
        children=[
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
                                    dbc.Label("No Calibration Loaded", className="wrap", id="calibration-filename-sp", html_for="upload-calibration-sp"),
                                    dcc.Upload(
                                        id="upload-calibration-sp",
                                        accept=".json",
                                        #style={"display": "flex", "height": "100%", "width": "100%"},
                                        children=[
                                            dbc.Button("Browse", style={"width": "100px"})
                                        ]
                                    ),
                                    dropdown(id="select-calibration-sp", label="Select Calibration", fields=calibs)
                               ] 
                            )
                        ]
                    ),
                    html.Div(
                        className="mt-4",
                        children=[
                            html.Span("Loaded Speed Profile:", style={"font-size": "20px", "font-weight": "bold"}),
                            html.Div(
                               className="mt-1",
                               children=[
                                    dbc.Label("No File Selected", className="wrap", id="speed-profile-filename", html_for="upload-speed-profile"),
                                    dcc.Upload(
                                        id="upload-speed-profile",
                                        accept=".json",
                                        #style={"display": "flex", "height": "100%", "width": "100%"},
                                        children=[
                                            dbc.Button("Browse", style={"width": "100px"})
                                        ]
                                    ),
                                    dropdown(id="select-speed-profile", label="Select Flow Profile", fields=profiles)
                               ] 
                            )
                        ]
                    ),
                    html.Div(
                        className="d-flex flex-column mt-5",
                        children=[
                            html.Span("Slope (mL/min)/pwm:", style={"font-size": "20px", "font-weight": "bold"}),
                            html.Span(id="slope-sp", children="0")
                        ]
                    ),
                    html.Div(
                        className="d-flex flex-column mt-3",                        
                        children=[
                            html.Span("Set Flow (mL/min):", style={"font-size": "20px", "font-weight": "bold"}),
                            html.Span(id="current-flow-span", children="0")
                        ]
                    ),
                    html.Div(
                        className="d-flex flex-row mt-4 justify-content-between",
                        style={"width": "50%"},
                        children=[
                            html.Span("ACW"),
                            custom_toggle(id="direction-toggle-sp"),
                            html.Span("CW")
                        ]
                    ),
                    html.Div(
                        className="mt-4",
                        children=[
                            dbc.Button("START", id="btn-start-sp", style={"width": "100px"}, n_clicks=0, className="mr-4"),
                            dbc.Button("STOP", id="btn-stop-sp", style={"width": "100px"}, n_clicks=0, className="mr-2")
                        ]
                    )
                ]
            ),
            html.Div(
                style={"width": "80%"},
                className="d-flex flex-row mt-4",
                children=[
                    generate_graph_section(id="flow-speed-graph", x_axis_label="Time (s)", y_axis_label="", y_range=[0,500])
                ]
            )
        ]
    )

    return speed_profile_layout

def layout_speed_profile(calibs, profiles):
    return dbc.Container(
        id="main-layout",
        style={"padding-right": "0px", "padding-left": "0px"},
        children=[
            html.Div(id="hidden-div-sp", style={"visibility":"hidden"}),
            dcc.ConfirmDialog(
                id="confirm-dialog-sp",
                message=""
            ),
            dcc.Interval(id="flow-update-interval", interval=1000, n_intervals=0),
            dcc.Interval(id="graph-refresh-interval", interval=1000, n_intervals=0),
            generate_speed_profile_layout(calibs, profiles)
        ]
    )