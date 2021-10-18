import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

def generate_calibration_layout():
    """
    Control layout generation with all widgets (buttons, sliders, and input windows).
    """
    control_layout = html.Div(
        id="calibration-control-display",
        children=[
            html.Div(
                style={"width": "40%"},
                className="d-flex flex-row mt-3",
                children=[
                    html.Div(
                        className="d-flex justify-content-between",
                        style={"width": "50%", "padding-right": "50px"},
                        children=[
                            html.Span(
                                "Low rpm: ", className="h4 font-weight-bold"),
                            dcc.Input(
                                id="low-rpm-input",
                                type="number",
                                debounce=True,  # must be set to true for onscreen keyboard to work
                                value=10,
                                # max=90,
                                # min=10,
                                style={"width": "40%", "height": "100%", "padding-left": "5px", "font-weight": "bold", "background": "aliceblue", "border-radius": "5px"},
                            )
                        ]
                    ),
                    html.Div(
                        className="d-flex justify-content-between",
                        style={"width": "50%"},
                        children=[
                            html.Span(
                                "Low rpm Volume (mL): ", className="h4 font-weight-bold"),
                            dcc.Input(
                                id="low-rpm-volume-input",
                                type="number",
                                debounce=True,  # must be set to true for onscreen keyboard to work
                                value=0,
                                # max=90,
                                # min=10,
                                style={"width": "25%", "height": "100%", "padding-left": "5px", "font-weight": "bold", "background": "aliceblue", "border-radius": "5px"},
                            )
                        ]
                    ),
                ]
            ),
            html.Div(
                style={"width": "40%"},
                className="d-flex flex-row mt-3",
                children=[
                    html.Div(
                        className="d-flex justify-content-between",
                        style={"width": "50%", "padding-right": "50px"},
                        children=[
                            html.Span(
                                "High rpm: ", className="h4 font-weight-bold"),
                            dcc.Input(
                                id="high-rpm-input",
                                type="number",
                                debounce=True,  # must be set to true for onscreen keyboard to work
                                value=1000,
                                # max=90,
                                # min=10,
                                style={"width": "40%", "height": "100%", "padding-left": "5px", "font-weight": "bold", "background": "aliceblue", "border-radius": "5px"},                                
                            )
                        ]
                    ),
                    html.Div(
                        className="d-flex justify-content-between",
                        style={"width": "50%"},
                        children=[
                            html.Span(
                                "High rpm Volume (mL): ", className="h4 font-weight-bold"),
                            dcc.Input(
                                id="high-rpm-volume-input",
                                type="number",
                                debounce=True,  # must be set to true for onscreen keyboard to work
                                value=0,
                                # max=90,
                                # min=10,
                                style={"width": "25%", "height": "100%", "padding-left": "5px", "font-weight": "bold", "background": "aliceblue", "border-radius": "5px"},                                
                            )
                        ]
                    ),
                ]
            ),
            html.Div(
                style={"width": "40%"},
                className="d-flex flex-row mt-3",
                children=[
                    html.Div(
                        className="d-flex justify-content-between",
                        style={"width": "50%", "padding-right": "50px"},
                        children=[
                            html.Span(
                                "Set time (s): ", className="h4 font-weight-bold"),
                            dcc.Input(
                                id="set-time-input",
                                type="number",
                                debounce=True,  # must be set to true for onscreen keyboard to work
                                value=10,
                                # max=90,
                                # min=10,
                                style={"width": "40%", "height": "100%", "padding-left": "5px", "font-weight": "bold", "background": "aliceblue", "border-radius": "5px"},
                            )
                        ]
                    ),
                    html.Div(
                        className="d-flex justify-content-between",
                        style={"width": "50%", "padding-right": "50px"},
                        children=[
                            html.Span(
                                "Current step: ", className="h4 font-weight-bold"),
                            html.Span(id="current-step-span", children="Idle", className="h4 font-weight-bold")
                        ]
                    )
                ]
            ),
            html.Div(
                style={"width": "40%"},
                className="d-flex flex-row mt-3",
                children=[
                    html.Div(
                        className="d-flex justify-content-left",
                        style={"width": "50%", "padding-right": "50px"},
                        children=[
                            dbc.Button("START", id="btn-start-calib", n_clicks=0, style={"width": "100px"}, className="mr-4"),
                            dbc.Button("STOP", id="btn-stop-calib", n_clicks=0, style={"width": "100px"}, className="mr-2")
                        ]
                    ),
                    html.Div(
                        className="d-flex justify-content-left",
                        # style={"width": "50%"},
                        children=[
                            dbc.Button("CONTINUE", id="btn-continue-calib", n_clicks=0, style={"width": "100px"}, className="mr-4"),
                            dbc.Button("SAVE", id="btn-save-calib", n_clicks=0, style={"width": "100px"}, className="mr-2")
                        ]
                    )
                ]
            )                 
        ]
    )

    return control_layout

layout_calibration = dbc.Container(
    id="main-layout",
    style={"padding-right": "0px", "padding-left": "0px"},
    children=[
        dcc.Interval(id="check-state-interval", interval=500, n_intervals=0),
        dcc.ConfirmDialog(
            id="calib-dialog",
            message=""
        ),
        dcc.ConfirmDialog(
            id="confirm-dialog",
            message=""
        ),
        generate_calibration_layout()
    ]
)