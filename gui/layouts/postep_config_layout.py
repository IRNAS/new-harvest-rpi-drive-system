import visdcc
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
from ..components.input_fields import text_field, dropdown

def generate_postep_config_layout(postep_settings, acc):
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

    layout = dbc.Container(
        id="main-layout",
        style={"padding-right": "0px", "padding-left": "0px"},
        children=[
            visdcc.Run_js("javascript"),  # run javascript to refresh page on demand
            dcc.ConfirmDialog(
                id="confirm-settings-dialog",
                message=""
            ),
            html.Div(
                id="postep-config-layout",
                className="mt-3",
                # style={"margin-top": "12px"},
                children=[
                    #Header(),
                    dbc.Row(
                        className="input-row mt-2",
                        children=[
                            dbc.Col(
                                width=4,
                                children=[
                                    text_field(id="fs-current", label="Full-scale current (A)", type="text", default_value=postep_settings["fullscale_current"])
                                ]
                            )
                        ]
                    ),
                    dbc.Row(
                        className="input-row mt-2",
                        children=[
                            dbc.Col(
                                width=4,
                                children=[
                                    text_field(id="idle-current", label="Idle current (A)", type="text", default_value=postep_settings["idle_current"])
                                ]
                            )
                        ]
                    ),
                    dbc.Row(
                        className="input-row mt-2",
                        children=[
                            dbc.Col(
                                width=4,
                                children=[
                                    text_field(id="overheat-current", label="Overheat current (A)", type="text", default_value=postep_settings["overheat_current"])
                                ]
                            )
                        ]
                    ),
                    dbc.Row(
                        className="input-row mt-2",
                        children=[
                            dbc.Col(
                                width=4,
                                children=[
                                    text_field(id="acceleration", label="Acceleration (RPM)", type="text", default_value=acc)
                                ]
                            )
                        ]
                    ),
                    dbc.Row(
                        className="input-row mt-2",
                        children=[
                            dbc.Col(
                                width=4,
                                children=[
                                    dropdown(id="step-mode", label="Step Mode", fields=step_mode, value=postep_settings["microstepping"])
                                ]
                            )
                        ]
                    ),
                    dbc.Row(
                        className="input-row mt-4",
                        children=[
                            dbc.Col(
                                width=4,
                                children=[
                                    dbc.Button("Save", id="save-btn", style={"width": "100px"}, n_clicks=0)
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )

    return layout