import os

from src.new_harvest import CalibrationStep

def generate_figure(x_axis_label, y_axis_label, y, y_range=None, h=250, data_count=2000, mt=50, mb=40, fixed_x=True, fixed_y=True, show_x_labels=False):
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
            "margin": {
                "t": mt,
                "b": mb,
                "l": 50,
                "r": 40
            },
            # "paper_bgcolor": "rgba(213, 237, 255, 0.2)",
            # "plot_bgcolor": "rgba(213, 237, 255, 0.2)",
            #"autosize": True,
            "xaxis": {
                "title": "<b>" + x_axis_label + "</b>",
                "range": [-data_count, 0],
                "fixedrange": fixed_x,
                "zeroline": False,
                "gridcolor": "rgb(50, 50, 50)",
                "showticklabels": show_x_labels
            },
            "yaxis": {
                "title": "<b>" + y_axis_label + "</b>",
                "range": y_range,
                "fixedrange": fixed_y,
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
    # data = [
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
        # ]

    # print(f"Returning {data}")

    return data

def map_calibration_step(step):
    """Map calibration step to text"""
    text = ""
    if step == CalibrationStep.IDLE:
        text = "Idle"
    if step == CalibrationStep.COMPLETED:
        text = "Completed"
    if step == CalibrationStep.LOW_RPM_RUNNING:
        text = "Low Rpm Calibration"
    if step == CalibrationStep.LOW_RPM_DONE:
        text = "Low Rpm Calibration Done"
    if step == CalibrationStep.HIGH_RPM_RUNNING:
        text = "High Rpm Calibration"
    if step == CalibrationStep.HIGH_RPM_DONE:
        text = "High Rpm Calibration Done"

    return text

def shutdown_pi():
    """Shuts pi down on button click"""
    os.system("sudo shutdown now")

def restart_service():
    """Restarts service on button click"""
    os.system("systemctl --user restart rh_micro")

def restart_pi():
    """Restarts service on button click"""
    os.system("sudo reboot now")

def update_device():
    """Restart service and update device"""
    os.system("systemctl --user restart git_pull")
    os.system("systemctl --user restart rh_micro")