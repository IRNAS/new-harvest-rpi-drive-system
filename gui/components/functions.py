import os
import json
import base64

from src.new_harvest_stepper import CalibrationStep

def generate_figure(x_axis_label, y_axis_label, y, y_range=None, h=250, data_count=600, mt=50, mb=40, fixed_x=True, fixed_y=True):
    """Generates figure for given data"""
    data = y
    #print(data)

    time = [t for t in range(-data_count, 0)]

    xaxis = {
        "title": "<b>Time (min)</b>",            
        "gridcolor": "rgb(50, 50, 50)",
        "showticklabels": True,
    },

    if data_count != 0:

        tickvals = [*range(-data_count, 30, 60)]
        tickvals.reverse()
        ticktext = [val // 60 for val in tickvals]

        xaxis = {
            "title": "<b>Time (min)</b>",            
            "gridcolor": "rgb(50, 50, 50)",
            "showticklabels": True,
            "range": [-data_count, 30],
            "tickmode": "array",
            "tickvals": tickvals,
            "ticktext": ticktext
        }


    fig = {
        # https://plotly.com/javascript/reference/index/
        "data": [
            {
                "type": "scatter",
                # "x": df["Time"].tolist(),
                "x": time[-len(data):],
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
            "xaxis": xaxis,
            "yaxis": {
                "title": "<b>" + y_axis_label + "</b>",
                "range": y_range,
                "showgrid": False,
                "zeroline": False,
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

    annotations = []

    for y_data, name, color in zip(y, x_names, trace_colors):
    
        # print(y_data)
        trace = {
            "type": "scatter",
            "name": name,
            # "x": df["Time"].tolist(),
            "x": time[-len(y_data):],  # take first 300 data points
            # "y": df[item].tolist(),
            "y": y_data,
            "mode": "lines+text",
            "marker": {
                # more about "marker.color": #scatter-marker-color
                "color": 'rgb(55, 0, 255)'
            },
            "line": {
                "color": color
            }
        }

        if len(y_data) != 0:
            annotation = {
                "x": 6,
                "y": y_data[-1],
                "text": "<b>" + str(y_data[-1]) + "</b>",
                "showarrow": False,
                "xanchor": "left",
                "xref": 0,
                "font": {
                    "color": color
                }
            }
            annotations.append(annotation)
        data.append(trace)

    return data, annotations

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
    num = "Current step"
    if step == CalibrationStep.IDLE:
        text = "Idle"
        num = num + " (0/5)" + ": "
    if step == CalibrationStep.COMPLETED:
        text = "Completed"
        num = num + " (5/5)" + ": "
    if step == CalibrationStep.LOW_RPM_RUNNING:
        text = "Low RPM"
        num = num + " (1/5)" + ": "
    if step == CalibrationStep.LOW_RPM_DONE:
        text = "Low RPM Done"
        num = num + " (2/5)" + ": "
    if step == CalibrationStep.HIGH_RPM_RUNNING:
        text = "High RPM"
        num = num + " (3/5)" + ": "
    if step == CalibrationStep.HIGH_RPM_DONE:
        text = "High RPM Done"
        num = num + " (4/5)" + ": "

    return num, text

def map_title(variable):
    title = ""
    if variable == "flow" or variable == "Flow":
        title = "Flow"
    if variable == "rpm" or variable == "Rpm":
        title = "Speed"
    if variable == "temp" or variable == "Temperature":
        title = "Temp"
    return title

def map_color(variable):
    color = "rgb(0,0,255)"
    if variable == "flow" or variable == "Flow":
        color = "rgb(50,160,235)"
    if variable == "rpm" or variable == "Rpm":
        color = "rgb(250,185,50)"
    if variable == "temp" or variable == "Temperature":
        color = "rgb(250,50,80)"
    return color

def add_wifi_network(ssid="", password=""):
    """Adds wifi network to wpa_supplicant.conf file"""
    if ssid == "" or password == "":
        return False

    wpa_supp_file = None
    with open("/etc/wpa_supplicant/wpa_supplicant.conf", "r") as file:
        wpa_supp_file = file.read().strip()
    
    # save backup of current settings file
    with open("/etc/wpa_supplicant/wpa_supplicant_bak.conf", "w") as file:
        file.write(wpa_supp_file)

    wpa_supp_lines = wpa_supp_file.split("\n")

    existing_ssid_line = -1
    for idx, string in enumerate(wpa_supp_lines):
        if f'ssid="{ssid}"' in string:
            existing_ssid_line = idx
            break
    print(f"SSID exists on index: {existing_ssid_line}")
    if existing_ssid_line != -1:
        existing_psk_line = -1
        for idx, string in enumerate(wpa_supp_lines):
            if idx >= existing_ssid_line:
                if "psk" in string:
                    existing_psk_line = idx
                    break
        print(f"psk exists on index: {existing_psk_line}")

        # if already exists replace the password
        if existing_psk_line - existing_ssid_line == 1:
            old_psk_idx = wpa_supp_lines[existing_psk_line].find("=")
            old_psk = wpa_supp_lines[existing_psk_line][old_psk_idx+1:]
            print(f"Old psk: {old_psk}")
            curr_psk_line = wpa_supp_lines[existing_psk_line]
            print(f"Curr psk line: {curr_psk_line}")
            wpa_supp_lines[existing_psk_line] = curr_psk_line.replace(old_psk, f'"{password}"')
            print(f"New psk: {password}")
            print(f"Replaced old password with new password")

            with open("/etc/wpa_supplicant/wpa_supplicant.conf", "w") as f:
                f.writelines(s + '\n' for s in wpa_supp_lines)
                return True

    # if ssid does not exist yet, add it
    if existing_ssid_line == -1:
        with open("/etc/wpa_supplicant/wpa_supplicant.conf", "a") as file:
            file.write('\nnetwork={\n\tssid="' + ssid + '"\n\tpsk="' + password + '"\n}\n')
            return True
    print(wpa_supp_lines)

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