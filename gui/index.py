import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# see https://community.plot.ly/t/nolayoutexception-on-deployment-of-multi-page-dash-app-example-code/12463/2?u=dcomfort
from gui.app import server
from gui.app import app
from gui.layouts import no_page
from gui.layouts.calibration_layout import layout_calibration
from gui.layouts.single_speed_layout import layout_single_speed
from gui.layouts.speed_profile_layout import layout_speed_profile
from gui.components.header import Header
from src.new_harvest import NewHarvest
from gui.callbacks import NewHarvestCallbacks

# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

new_harvest = NewHarvest()  # instantiate RHmicro class, measurements start on press of "Start" button

NewHarvestCallbacks(new_harvest).calibration_callbacks()
NewHarvestCallbacks(new_harvest).single_speed_callbacks()

# see https://dash.plot.ly/external-resources to alter header, footer and favicon
app.index_string = ''' 
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>new Harvest Graphical User Interface</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    Header(),
    html.Div(id='page-content')
])

# Update page
# # # # # # # # #
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == "/calibration":
        return layout_calibration
    if pathname == "/single-speed-control":
        return layout_single_speed
    if pathname == "/speed-profile":
        return layout_speed_profile
    # else:
    #     return no_page

if __name__ == '__main__':
    hostname = "0.0.0.0"
    port = "1234"  # set port > 1024 to run as unprivileged userlayout_pressure_control

    app.run_server(
        port=port,
        debug=True,
        host=hostname,
        #dev_tools_ui=False,
        #dev_tools_props_check=False
    )