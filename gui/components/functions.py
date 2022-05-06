import os
import json
import base64

from src.new_harvest import CalibrationStep

def generate_figure(x_axis_label, y_axis_label, y, y_range=None, h=250, data_count=600, mt=50, mb=40, fixed_x=True, fixed_y=True):
    """Generates figure for given data"""
    data = y
    #print(data)
    time = [t for t in range(-data_count, 0)]
    fig = {
        # https://plotly.com/javascript/reference/index/
        "data": [
            {
                "type": "scatter",
                # "x": df["Time"].tolist(),
                "x": time[-len(data):],  # take first 300 data points
                # "y": df[item].tolist(),
                "y": data,
                "mode": "lines",
                "marker": {
                    # more about "marker.color": #scatter-marker-color
                    "color": "rgb(55, 0, 255)"
                },
                "line": {
                    "color": "rgb(10, 100, 200)"
                }
            }
        ],
        "layout":
        {
            # "width": 700,
            # "height": h,
            "showlegend": True,
            "margin": {
                "t": mt,
                "b": mb,
                "l": 50,
                "r": 40
            },
            "xaxis": {
                "title": "<b>Time (s)</b>",
                "range": [-data_count, 0],
                # "fixedrange": fixed_x,
                # "zeroline": False,
                "gridcolor": "rgb(50, 50, 50)",
                "showticklabels": True
            },
            "yaxis": {
                "title": "<b>" + y_axis_label + "</b>",
                "range": y_range,
                # "fixedrange": fixed_y,
                "gridcolor": "rgb(50, 50, 50)"
            }
        }
    }

    return fig

def generate_figure_data(y, x_names, trace_colors, y_range=None, data_count=2000):
    """Generates figure for given data"""

    time = [t for t in range(-data_count, 0)]
    data = []
    if len(trace_colors) == 0:
        color = 'rgb(10, 100, 200)'
    for y_data, name, color in zip(y, x_names, trace_colors):
    
        trace = {
            "type": "scatter",
            "name": name,
            # "x": df["Time"].tolist(),
            "x": time[-len(y_data):],  # take first 300 data points
            # "y": df[item].tolist(),
            "y": y_data,
            "mode": "lines",
            "marker": {
                # more about "marker.color": #scatter-marker-color
                "color": 'rgb(55, 0, 255)'
            },
            "line": {
                "color": color
            }
        }
        data.append(trace)

    return data

def parse_json_contents(contents):
    """Parse procedure file contents"""
    print(contents)
    split = contents.split(',')
    content_string = split[1]

    decoded = base64.b64decode(content_string)
    json_obj = None  # value to return
    print(decoded)
    try:  # check if json is valid
        json_obj = json.loads(decoded.decode('utf-8'))
    except Exception as e:
        print(f"An exceptin occured when decoding json file: {e}")

    return json_obj

def load_filenames(file_root):
    """Load all filenames"""
    filenames = []
    # print(f"File root: {file_root}")
    for root, dirs, files in os.walk(file_root):
        for name in files:
            # print("file!")
            filenames.append({"label": name, "value": os.path.join(root, name)})
            # print(os.path.join(root, name))

    return filenames

def map_calibration_step(step):
    """Map calibration step to text"""
    text = ""
    if step == CalibrationStep.IDLE:
        text = "Idle 0/5"
    if step == CalibrationStep.COMPLETED:
        text = "Completed 5/5"
    if step == CalibrationStep.LOW_PWM_RUNNING:
        text = "Low PWM 1/5"
    if step == CalibrationStep.LOW_PWM_DONE:
        text = "Low PWM Done 2/5"
    if step == CalibrationStep.HIGH_PWM_RUNNING:
        text = "High PWM 3/5"
    if step == CalibrationStep.HIGH_PWM_DONE:
        text = "High PWM Done 4/5"

    return text

def map_title(variable):
    title = ""
    if variable == "flow":
        title = "Flow (mL/min)"
    if variable == "pwm":
        title = "Speed (PWM (%))"
    if variable == "temp":
        title = "Temperature (°C)"
    return title

def map_color(variable):
    color = "rgb(0,0,255)"
    if variable == "flow":
        color = "rgb(50,160,235)"
    if variable == "pwm":
        color = "rgb(250,185,50)"
    if variable == "temp":
        color = "rgb(250,50,80)"
    return color

def shutdown_pi():
    """Shuts pi down on button click"""
    os.system("sudo shutdown now")

def restart_service():
    """Restarts service on button click"""
    os.system("systemctl --user restart new_harvest")

def restart_pi():
    """Restarts service on button click"""
    os.system("sudo reboot now")

def update_device():
    """Restart service and update device"""
    os.system("systemctl --user restart git_pull")
    os.system("systemctl --user restart new_harvest")