from dash import dcc, html
import dash_bootstrap_components as dbc
# from ..components.flow_graph import generate_graph_section
from ..components.custom_toggle import custom_toggle
from ..components.input_fields import dropdown
from ..components.speed_profile_plot import generate_speed_profile_plot_container

def generate_speed_profile_layout(calibs, profiles, measurements, dir_state):
    """
    Control layout generation with all widgets (buttons, sliders, and input windows).
    """
    
    speed_profile_layout = html.Div(
        className="d-flex flex-column",
        id="singles-speed-display",
        children=[
            html.Div(
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
                                            dbc.Label("No Calibration Loaded", className="wrap", id="calibration-filename-sp", html_for="upload-calibration", style={"font-size": "18px"}),
                                            dcc.Upload(
                                                id="upload-calibration-sp",
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
                                        id=f"select-calibration-sp-dropdown",
                                        className="mt-1",
                                        style={"width": "240px"},
                                        options=calibs,
                                        persistence=True,
                                        searchable=False
                                    ),
                                ]
                            ),
                            
                        ],
                    ),
                    html.Div(
                        className="d-flex flex-column",
                        children=[
                            
                            html.Div(
                                className="d-flex flex-row mt-2",
                                children=[
                                    html.Span("Slope (mL/min)/rpm:", className="sfs-title"),
                                    html.Span(id="slope-sp", children="0", className="sfs-value", style={"margin-left": "128px"})
                                ]
                            ),
                            html.Div(
                                className="d-flex flex-row mt-2",                        
                                children=[
                                    html.Span("Set Flow (mL/min):", className="sfs-title"),
                                    html.Span(id="current-flow-span", children="0", className="sfs-value", style={"margin-left": "144px"})
                                ]
                            ),
                            html.Div(
                                className="d-flex flex-row",
                                children=[
                                    html.Div("Set Direction", className="sfs-title", style={"width": "206px", "padding-top": "6px"}),
                                    html.Div(
                                        className="d-flex flex-row mt-2 justify-content-between",
                                        style={"width": "30%", "margin-left": "124px"},
                                        children=[
                                            html.Span("CW", style={"font-size": "16px", "margin-top": "3px"}),
                                            custom_toggle(id="direction-toggle-sp", checked=dir_state),
                                            html.Span("CCW", style={"font-size": "16px", "margin-top": "3px"})
                                        ]
                                    )
                                ]
                            ),
                            html.Div(
                                className="d-flex flex-row mt-2",
                                children=[
                                    html.Span(
                                        "Repeat: ", className="sfs-title", style={"width": "325px"}),
                                    dcc.Input(
                                        id="num-repeat-input",
                                        type="number",
                                        debounce=True,  # must be set to true for onscreen keyboard to work
                                        value=1,
                                        persistence=True,
                                        style={"width": "26%", "height": "100%", "padding-left": "5px", "font-weight": "bold", "background": "aliceblue", "border-radius": "5px"},
                                    )
                                ]
                            ),
                            html.Div(
                                className="mt-2 d-flex flex-row justify-content-end",
                                style={"width": "438px"},
                                children=[
                                    html.Div("Control", className="h4 font-weight-bold", style={"width": "100px", "padding-top": "14px"}),
                                    dbc.Button("START", id="btn-start-sp", style={"width": "110px", "margin-left": "98px"}, n_clicks=0, className="mt-2"),
                                    dbc.Button("STOP", id="btn-stop-sp", style={"width": "110px", "margin-left": "20px"}, n_clicks=0, className="mt-2")
                                ]
                            ),
                        ]
                    ),
                ]
            ),
            html.Div(
                className="d-flex flex-row",
                children=[
                    html.Div(
                        className="d-flex flex-column",
                        style={"width": "420px"},
                        children=[
                            html.Div(
                                className="mt-2",
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
                                            # dropdown(id="select-speed-profile", label="Select Flow Profile", fields=profiles, dd_style={"width": "240px", "height": "30px"})
                                            html.Div(
                                            className="d-flex flex-column mt-2",
                                                children=[
                                                    html.Span("Select Flow Profile:", style={"font-size": "20px", "font-weight": "bold"}),
                                                    dcc.Dropdown(
                                                        id=f"select-speed-profile-dropdown",
                                                        className="mt-1",
                                                        style={"width": "240px"},
                                                        options=profiles,
                                                        value=None,
                                                        persistence=True,
                                                        searchable=False
                                                    ),
                                                ]
                                            ),
                                        ] 
                                    )
                                ]
                            ),
                        ]
                    ),
                    html.Div(
                        className="d-flex flex-column",
                        children=[
                            generate_speed_profile_plot_container(id="speed-profile-plot", speed_profile_json=None, calibration=None)
                        ]
                    )
                ]
            ),
            # html.Div(
            #     style={"width": "80%"},
            #     className="d-flex flex-column mt-4",
            #     children=[
            #         generate_graph_section(id="flow-speed-graph", x_axis_label="Time (s)", y_axis_label="", remove_buttons=False, measurements=measurements),
            #     ]
            # )
        ]
    )
    

    return speed_profile_layout

def layout_speed_profile(calibs, profiles, measurements, dir_state):
    return dbc.Container(
        id="main-layout",
        style={"padding-right": "0px", "padding-left": "0px"},
        children=[
            # html.Div(id="hidden-div-sp", style={"visibility":"hidden"}),
            dcc.ConfirmDialog(
                id="confirm-dialog-sp",
                message=""
            ),
            dcc.Interval(id="flow-update-interval", interval=1000, n_intervals=0),
            dcc.Interval(id="graph-refresh-interval", interval=1000, n_intervals=0),
            generate_speed_profile_layout(calibs, profiles, measurements, dir_state)
        ]
    )
