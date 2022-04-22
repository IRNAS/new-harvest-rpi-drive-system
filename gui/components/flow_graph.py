import dash_core_components as dcc
import dash_html_components as html
from .functions import generate_figure

def generate_graph_section(id, x_axis_label, y_axis_label, y_range, h=250, remove_buttons=False, mt=50, mb=40, fixed_x=True, fixed_y=True, show_x_labels=False):
    """
    Generate graph section of GUI
    """
    fig = generate_figure(x_axis_label, y_axis_label, [], y_range, h=h, mt=mt, mb=mb, fixed_x=fixed_x, fixed_y=fixed_y)

    graph_container = html.Div(
        className="d-flex flex-direction-row",
        children=[
            html.Div(
                # style={"width": "85%"},
                children=[
                    dcc.Graph(
                        # remove mode bar buttons
                        # https://github.com/plotly/plotly.js/blob/master/src/plot_api/plot_config.js
                        # button list: https://github.com/plotly/plotly.js/blob/master/src/components/modebar/buttons.js
                        id=id,
                        figure=fig,
                        config={
                            "staticPlot": False,
                            "editable": False,
                            "displayModeBar": True,
                            "displaylogo": False,
                            "modeBarButtonsToRemove": ["toImage", "autoScale2d", "toggleSpikelines", "hoverCompareCartesian", "hoverClosestCartesian"],
                            "displayModeBar": not remove_buttons
                        },
                        style={"margin-left": "12px", "width": "1000px", "height": "360px"}
                    )
                ]
            ),
            html.Div(
                children=[
                    html.Span("Select variables to plot", style={"margin-left": "20px", "font-size": "20px"}),
                    html.Div(
                        style={"width": "170px", "margin-left": "20px", "margin-top": "10px"},
                        children=[
                            dcc.Checklist(
                                id="variable-checklist",
                                # className="d-flex flex-direction-column",
                                style={"display":"block"},
                                options=[
                                    {"label": " Flow (mL/min)", "value": "flow"},
                                    {"label": " Speed (PWM)", "value": "pwm"},
                                    {"label": " Temperature (°C)", "value": "temp"}
                                ],
                                value=["flow", "pwm", "temp"]
                            )
                        ]
                    )
                ]
            )
        ]
    )

    return graph_container