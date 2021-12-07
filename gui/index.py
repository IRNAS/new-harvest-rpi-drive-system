import logging

import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# see https://community.plot.ly/t/nolayoutexception-on-deployment-of-multi-page-dash-app-example-code/12463/2?u=dcomfort
from gui.app import server
from gui.app import app
from gui.layouts import no_page
from gui.layouts.calibration_layout import layout_calibration
from gui.layouts.postep_config_layout import generate_postep_config_layout
from gui.layouts.single_speed_layout import layout_single_speed
from gui.layouts.speed_profile_layout import layout_speed_profile
from gui.components.header import Header
# from src.new_harvest import NewHarvest
from gui.callbacks import NewHarvestCallbacks
from gui.components.functions import load_filenames

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# new_harvest = NewHarvest()  # instantiate RHmicro class, measurements start on press of "Start" button
new_harvest = None

# NewHarvestCallbacks(new_harvest).calibration_callbacks()
# NewHarvestCallbacks(new_harvest).single_speed_callbacks()
# NewHarvestCallbacks(new_harvest).graph_update_callbacks()
# NewHarvestCallbacks(new_harvest).speed_profile_callbacks()
# NewHarvestCallbacks(new_harvest).postep_config_callbacks()

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
        calibs = load_filenames("/mnt/storage/calibrations")
        return layout_single_speed(calibs)
    if pathname == "/speed-profile":
        calibs = load_filenames("/mnt/storage/calibrations")
        profiles = load_filenames("/mnt/storage/profiles")
        return layout_speed_profile(calibs, profiles)
    if pathname == "/postep-config":
        current_postep_config = new_harvest.get_postep_config()
        current_accel = new_harvest.get_acceleration()
        print(f"Current postep settings: {current_postep_config}")
        # stop motor before changing settings
        new_harvest.stop_motor()
        return generate_postep_config_layout(current_postep_config, current_accel)
    else:
        return no_page

if __name__ == '__main__':
    hostname = "0.0.0.0"
    port = "1234"  # set port > 1024 to run as unprivileged userlayout_pressure_control

    app.run_server(
        port=port,
        debug=False,
        host=hostname,
        #dev_tools_ui=False,
        #dev_tools_props_check=False
    )