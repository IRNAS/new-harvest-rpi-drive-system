import logging

# import dash_core_components as dcc
# import dash_html_components as html
from dash import dcc, html
from dash.dependencies import Input, Output

# see https://community.plot.ly/t/nolayoutexception-on-deployment-of-multi-page-dash-app-example-code/12463/2?u=dcomfort
from gui.app import server
from gui.app import app
from gui.layouts.no_page import no_page
from gui.layouts.calibration_layout import layout_calibration
from gui.layouts.config_layout import generate_config_layout
from gui.layouts.single_speed_layout import layout_single_speed
from gui.layouts.speed_profile_layout import layout_speed_profile
from gui.layouts.plot_layout import layout_plot
from gui.components.header import Header
from src.new_harvest_stepper import NewHarvest
from gui.callbacks import NewHarvestCallbacks
from gui.components.functions import load_filenames

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

new_harvest = NewHarvest()  # instantiate RHmicro class, measurements start on press of "Start" button
# new_harvest = None

NewHarvestCallbacks(new_harvest).calibration_callbacks()
NewHarvestCallbacks(new_harvest).single_speed_callbacks()
NewHarvestCallbacks(new_harvest).graph_update_callbacks()
NewHarvestCallbacks(new_harvest).speed_profile_callbacks()
NewHarvestCallbacks(new_harvest).config_callbacks()
NewHarvestCallbacks(new_harvest).download_logs_callbacks()
# NewHarvestCallbacks(new_harvest).stop_app_button_callback()

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

    measurements = load_filenames("/mnt/storage/measurements")
    calibs = load_filenames("/mnt/storage/calibrations")
    
    if pathname == "/calibration":
        return layout_calibration
    elif pathname == "/single-speed-control":
        
        return layout_single_speed(calibs, measurements)
    elif pathname == "/speed-profile":
        
        profiles = load_filenames("/mnt/storage/profiles")
        return layout_speed_profile(calibs, profiles, measurements)
    elif pathname == "/postep-config":
        try:
            current_postep_config = new_harvest.get_postep_config()
        except Exception as e:
            current_postep_config = {}
        # current_accel = new_harvest.get_acceleration()
        print(f"Current postep settings: {current_postep_config}")
        # stop motor before changing settings
        new_harvest.stop_motor()
        return generate_config_layout(current_postep_config, measurements)
    elif pathname == "/flow-plot":
        return layout_plot(measurements)
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