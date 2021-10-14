import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc

def Header():
    return html.Div(
        children=[
            dcc.ConfirmDialog(
                id="confirm-close-alert",
                message="Are you sure you want to exit?",
                submit_n_clicks=0
            ),
            dcc.ConfirmDialog(
                id="confirm-refresh-alert",
                message="Are you sure you want to restart the program?",
                submit_n_clicks=0
            ),
            dcc.ConfirmDialog(
                id="confirm-update-alert",
                message="Are you sure you want to update the device?",
                submit_n_clicks=0
            ),
            dcc.ConfirmDialog(
            id="USB-mounted-alert",
            message="USB storage device successfully mounted! Press OK to restart the device.",
            submit_n_clicks=0
            ),
            dcc.ConfirmDialog(
                id="USB-unmounted-alert",
                message="USB storage device was unmounted. Please reinsert and restart the device!",
                submit_n_clicks=0
            ),
            navbar
        ]
    )

btns = dbc.Row(
    no_gutters=True,
    className="mt-2",
    style={"width": "200px"},
    children=[
        dbc.Col(
            children=[
                dbc.Button(html.Span("Update", style={"position": "relative", "left": "-10px", "top": "-16px", "font-size": "22px", "font-weight": "bold"}), id="btn-update-service", n_clicks=0, className="mr-2", style={"height": "2px", "width": "102px", "margin-top": "-10px"}),
                dbc.Button(html.Span("\U000021BB", style={"position": "relative", "left": "-10px", "top": "-16px", "font-size": "24px", "font-weight": "bold"}), id="btn-restart-device", n_clicks=0, className="mr-2", style={"height": "2px", "width": "2px", "margin-top": "-10px"}),
                dbc.Button(html.Span("\U00002716", style={"position": "relative", "left": "-10px", "top": "-16px", "font-size": "24px", "font-weight": "bold"}), id="btn-shutdown", n_clicks=0, className="mr-2", style={"height": "2px", "width": "2px", "margin-top": "-10px"})
            ]
        )
    ]
)

navbar = dbc.Navbar(
    className="pt-0 pb-0 pr-0 pl-0 mb-1",
    children=[
        html.Div(
            className="navbar-collapse collapse",
            style={"background": "rgb(210, 220, 220)"},
            children=[
                html.Ul(
                    id="nav",
                    className="navbar-nav mr-auto",
                    children=[
                        # html.Li(
                        #     children=[
                        #         dbc.NavItem(dbc.NavLink(id="pump-control-navlink", children="Pump control", href="/pump-control", active="exact"))
                        #     ]
                        # ),
                        html.Li(
                            # style={"width": "25%"},
                            children=[
                                dbc.NavItem(dbc.NavLink(id="calibration-input-navlink", children="Flow Speed Calibration", href="/calibration", active="exact", style={"height": "65px", "text-align": "center", "padding-top": "24px"}))
                            ]
                        ),
                        html.Li(
                            # style={"width": "25%"},
                            children=[
                                dbc.NavItem(dbc.NavLink(id="single-speed-input-navlink", children="Single Flow Speed", href="/single-speed-control", active="exact", style={"height": "65px", "text-align": "center", "padding-top": "24px"}))
                            ]
                        ),
                        html.Li(
                            # style={"width": "25%"},
                            children=[
                                dbc.NavItem(dbc.NavLink(id="speed-graph-input-navlink", children="Speed Profile", href="/speed-profile", active="exact", style={"height": "65px", "text-align": "center", "padding-top": "24px"}))
                            ]
                        )
                    ]
                ),
                btns
            ]
        )
    ]
)