from dash import dcc, html
import dash_bootstrap_components as dbc
from ..components.flow_graph import generate_graph_section
from ..components.functions import generate_figure

def generate_static_graph():
    fig = generate_figure(y=[], x_axis_label="", y_axis_label="")

    graph_container = html.Div(
        # className="d-flex flex-direction-column",
        children=[
            html.Div(
                # style={"width": "85%"},
                children=[
                    dcc.Graph(
                        # remove mode bar buttons
                        # https://github.com/plotly/plotly.js/blob/master/src/plot_api/plot_config.js
                        # button list: https://github.com/plotly/plotly.js/blob/master/src/components/modebar/buttons.js
                        id="static-plot-graph",
                        figure=fig,
                        config={
                            "staticPlot": False,
                            "editable": False,
                            "displayModeBar": True,
                            "displaylogo": False,
                            "modeBarButtonsToRemove": ["autoScale2d", "toggleSpikelines", "hoverCompareCartesian", "hoverClosestCartesian"],
                        },
                        style={"width": "540px", "height": "340px"}
                    )
                ]
            )
        ]
    )

    return graph_container

def generate_plot_layout(measurements):
    # Reverse to sort descending by date
    measurements.reverse()

    plot_layout = html.Div(
        id="plot-display",
        className="d-flex flex-column",
        children=[
            html.Div(
                # style={"width": "80%"},
                className="d-flex flex-row mt-2",
                children=[
                    generate_static_graph(),
                    html.Div(
                        style={"width": "260px"},
                        className="mt-2",
                        children=[
                            html.Span("Select Measurement:", style={"font-size": "20px", "font-weight": "bold"}),
                            dcc.Dropdown(
                                id=f"select-measurement-dropdown",
                                className="mt-1",
                                style={"width": "100%"},
                                options=measurements,
                                persistence=True,
                                searchable=False
                            )
                        ]
                    ),
                ]
            )
        ]
    )

    return plot_layout

def layout_static_plot(measurements):
    return dbc.Container(
        id="main-layout",
        style={"padding-right": "0px", "padding-left": "0px"},
        children=[
            generate_plot_layout(measurements)
        ]
    )