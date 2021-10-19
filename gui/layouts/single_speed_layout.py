import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from ..components.flow_graph import generate_graph_section
from ..components.custom_toggle import custom_toggle

def generate_single_speed_layout():
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
                            html.Span(
                                "Flow speed (mL/min): ", className="h4 font-weight-bold"),
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
                        className="mt-4",
                        children=[
                            dbc.Button("SET", id="btn-set", style={"width": "100px"}, n_clicks=0)
                        ]
                    ),
                    html.Div(
                        className="d-flex flex-row mt-4 justify-content-between",
                        style={"width": "50%"},
                        children=[
                            html.Span("ACW"),
                            custom_toggle(id="direction-toggle"),
                            html.Span("CW")
                        ]
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
                    generate_graph_section(id="flow-speed-graph", x_axis_label="", y_axis_label="", y_range=[0,100])
                ]
            )
        ]
    )

    return control_layout

layout_single_speed = dbc.Container(
    id="main-layout",
    style={"padding-right": "0px", "padding-left": "0px"},
    children=[
        dcc.Interval(id="graph-refresh-interval", interval=1000, n_intervals=0),
        generate_single_speed_layout()
    ]
)