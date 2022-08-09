# import dash_core_components as dcc
# import dash_html_components as html
from dash import dcc, html
from .functions import generate_figure

def generate_graph_section(id, x_axis_label, y_axis_label, y_range=[], h=250, remove_buttons=False, mt=50, mb=40, fixed_x=True, fixed_y=True, show_x_labels=False, measurements={}):
    """
    Generate graph section of GUI
    """
    fig = generate_figure(x_axis_label, y_axis_label, [], y_range, h=h, mt=mt, mb=mb, fixed_x=fixed_x, fixed_y=fixed_y)

    graph_container = html.Div(
        # className="d-flex flex-direction-column",
        children=[
            
            dcc.Checklist(
                id="variable-checklist",
                inline=True,
                # style={"width": "340px"},
                # className="d-flex flex-direction-column",
                # style={"display":"block"},
                options=[
                    {"label": html.Span([" Flow (mL/min)"], style={"margin-right": "20px"}), "value": "flow"},
                    {"label": html.Span([" Speed (rpm)"], style={"margin-right": "20px"}), "value": "rpm"},
                    {"label": " Temperature (°C)", "value": "temp"}
                ],
                value=["flow", "rpm", "temp"]
            ),
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
                            "modeBarButtonsToRemove": ["autoScale2d", "toggleSpikelines", "hoverCompareCartesian", "hoverClosestCartesian"],
                        },
                        style={"width": "760px", "height": "340px"}
                    )
                ]
            )
        ]
    )

    return graph_container