from dash import dcc, html
import dash_bootstrap_components as dbc
from ..components.flow_graph import generate_graph_section
from ..components.functions import generate_figure

def generate_static_graph():
    fig = generate_figure(y=[], x_axis_label="Time (s)", y_axis_label="", data_count=0)

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
    measurements = sorted(measurements, key=lambda x: x['label'], reverse=True)
    # Remove duplicates
    seen = set()
    unique_measurements = []
    for measurement in measurements:
        if measurement['label'] not in seen:
            unique_measurements.append(measurement)
            seen.add(measurement['label'])
    measurements = unique_measurements

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
                            ),
                            html.Div(
                                className="d-flex justify-content-left",
                                style={"margin-top": "10px"},
                                children=[
                                    html.Span(id="microstepping-setting-span", children="Microstepping: "),
                                    html.Span(id="microstepping-val-span-static-graph", children="", style={"margin-left": "6px"})
                                ]
                            ),
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
            html.Span(id="static-plot-title", style={"font-size": "20px", "font-weight": "bold"}),
            generate_plot_layout(measurements)
        ]
    )