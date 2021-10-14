import dash
import logging
import dash_bootstrap_components as dbc  # replace with statically served css

# made with the help of: https://github.com/davidcomfort/dash_sample_dashboard

# application scope configs
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S', level=int(10))

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# flask config
# bootstrap theme url

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.MATERIA],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}]
)
server = app.server
app.config["suppress_callback_exceptions"] = True