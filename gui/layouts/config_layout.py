import visdcc
from dash import dcc, html
import dash_bootstrap_components as dbc
from ..components.input_fields import text_field, dropdown

def generate_config_layout(postep_settings, measurements):
    """
    Postep config layout generation with all widgets (buttons, sliders, and input windows).
    """
    step_mode=[
        {"label": "Full-step", "value": 0},
        {"label": "Half step", "value": 1},
        {"label": "1/4 step", "value": 2},
        {"label": "1/8 step", "value": 3},
        {"label": "1/16 step", "value": 4},
        {"label": "1/32 step", "value": 5},
        {"label": "1/64 step", "value": 6},
        {"label": "1/128 step", "value": 7},
        {"label": "1/256 step", "value": 8}
    ]

    microstep_setting = postep_settings.get("microstepping")
    print(f"Microstep setting: {microstep_setting}")

    layout = dbc.Container(
        # id="main-layout",
        style={"padding-right": "0px", "padding-left": "0px"},
        className="d-flex flex-row",
        children=[
            visdcc.Run_js("javascript"),  # run javascript to refresh page on demand
            dcc.ConfirmDialog(
                id="confirm-settings-dialog",
                message=""
            ),
            html.Div(
                id="postep-config-layout",
                className="mt-2 d-flex flex-column",
                style={"width": "210px", "margin-right": "20px"},
                children=[
                    #Header(),
                    dbc.Row(
                        # className="input-row",
                        children=[
                            dbc.Col(
                                # width=4,
                                children=[
                                    html.Span("PoStep Settings", className="h3", style={"font-weight": "bold"})
                                ]
                            )
                        ]
                    ),
                    dbc.Row(
                        className="input-row mt-2",
                        children=[
                            dbc.Col(
                                # width=4,
                                children=[
                                    text_field(id="fs-current", label="Full-scale current (A)", type="number", default_value=postep_settings.get("fullscale_current"), min=0, max=6, step=0.1)
                                ]
                            )
                        ]
                    ),
                    dbc.Row(
                        className="input-row mt-2",
                        children=[
                            dbc.Col(
                                # width=4,
                                children=[
                                    text_field(id="idle-current", label="Idle current (A)", type="number", default_value=postep_settings.get("idle_current"), min=0, max=6, step=0.1)
                                ]
                            )
                        ]
                    ),
                    dbc.Row(
                        className="input-row mt-2",
                        children=[
                            dbc.Col(
                                # width=4,
                                children=[
                                    text_field(id="overheat-current", label="Overheat current (A)", type="number", default_value=postep_settings.get("overheat_current"), min=0, max=6, step=0.1)
                                ]
                            )
                        ]
                    ),
                    dbc.Row(
                        className="input-row mt-2",
                        children=[
                            dbc.Col(
                                children=[
                                    html.Span(
                                        style={"font-size": "16px", "font-weight": "bold"},
                                        children=[
                                            "Step Mode"
                                        ]
                                    ),
                                    dcc.Dropdown(
                                        id=f"step-mode-dropdown",
                                        options=step_mode,
                                        className="mt-1",
                                        value=microstep_setting,
                                        persistence=True,
                                        searchable=False
                                    )
                                ]
                            )
                        ]
                    ),
                    dbc.Row(
                        className="input-row mt-4",
                        children=[
                            dbc.Col(
                                # width=4,
                                children=[
                                    dbc.Button("Save", id="save-btn", style={"width": "100px"}, n_clicks=0)
                                ]
                            )
                        ]
                    )
                ]
            ),
            html.Div(
                style={"width": "260px", "margin-right": "20px"},
                className="mt-2 d-flex flex-column",
                children=[
                    dbc.Row(
                        # className="input-row",
                        children=[
                            dbc.Col(
                                # width=4,
                                children=[
                                    html.Span("WiFi Settings", className="h3", style={"font-weight": "bold"})
                                ]
                            )
                        ]
                    ),
                    dbc.Row(
                        className="input-row mt-2",
                        children=[
                            dbc.Col(
                                # width=4,
                                children=[
                                    text_field(id="wifi-ssid", label="SSID", type="text", default_value="", persistence=False)
                                ]
                            )
                        ]
                    ),
                    dbc.Row(
                        className="input-row mt-2",
                        children=[
                            dbc.Col(
                                # width=4,
                                children=[
                                    text_field(id="wifi-password", label="Password", type="text", default_value="", persistence=False)
                                ]
                            )
                        ]
                    )
                ]
            ),
            html.Div(
                style={"width": "260px"},
                className="mt-2",
                children=[
                    html.Span("Select Logfile:", style={"font-size": "20px", "font-weight": "bold"}),
                    dcc.Dropdown(
                        id=f"select-logfile-dropdown",
                        className="mt-1",
                        style={"width": "100%"},
                        options=measurements,
                        persistence=True,
                        searchable=False
                    ),
                    # dropdown(id="select-logfile", label="Select Logfile", fields=measurements, dd_style={"width": "100%", "height": "30px"}),
                    html.Br(),
                    html.Button("Download Log", id="btn-download-log"),
                    dcc.Download(id="download-log")
                ]
            ),
        ]
    )

    return layout