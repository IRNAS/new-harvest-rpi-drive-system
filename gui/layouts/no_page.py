import dash_html_components as html
import dash_bootstrap_components as dbc

###################### 404 Page #####################################
no_page = html.Div(
    children=[
        html.P("Please select one of the tabs.")
    ],
    className="no-page"
)