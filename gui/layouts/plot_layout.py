from dash import dcc, html
import dash_bootstrap_components as dbc
from ..components.flow_graph import generate_graph_section

def generate_plot_layout(measurements):
    plot_layout = html.Div(
        id="plot-display",
        className="d-flex flex-column",
        children=[
            html.Div(
                # style={"width": "80%"},
                className="d-flex flex-row mt-2",
                children=[
                    generate_graph_section(id="flow-speed-graph", x_axis_label="", y_axis_label="", measurements=measurements),
                    # html.Span("Flow: ", style={"position": "absolute", "top": "300px", "right": "75px", "font-size": "16px", "font-weight": "bold"})
                    # html.Span("Rpm: ", style={"position": "absolute", "top": "230px", "right": "75px", "font-size": "16px", "font-weight": "bold"}),
                ]
            )
        ]
    )

    return plot_layout

def layout_plot(measurements):
    return dbc.Container(
        id="main-layout",
        style={"padding-right": "0px", "padding-left": "0px"},
        children=[
            dcc.ConfirmDialog(
                id="confirm-dialog-rpm-alert",
                message=""
            ),
            dcc.Interval(id="graph-refresh-interval", interval=1000, n_intervals=0),
            generate_plot_layout(measurements)
        ]
    )