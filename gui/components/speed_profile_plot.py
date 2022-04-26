# import matplotlib.pyplot as plt
import math
import dash_html_components as html
import dash_core_components as dcc
# def get_pwm(flow, calibration):
#     """Return required pwm to get desired flow"""
#     # print(f"Calculating pwm from selected flow: {flow} and slope: {self.slope}")
#     return flow / 0.058

def generate_speed_profile_plot_container(id, speed_profile_json, calibration):
    """
    Generate speed profile plot section of GUI
    """
    fig = generate_speed_profile(speed_profile_json, calibration)
    # print(f"Figure: {fig}")

    graph_container = html.Div(
        className="d-flex flex-direction-row mt-5",
        children=[
            html.Div(
                # style={"width": "85%"},
                children=[
                    dcc.Graph(
                        # remove mode bar buttons
                        # https://github.com/plotly/plotly.js/blob/master/src/plot_api/plot_config.js
                        # button list: https://github.com/plotly/plotly.js/blob/master/src/components/modebar/buttons.js
                        id=id,
                        figure=fig,
                        config={
                            "staticPlot": False,
                            "editable": False,
                            "displayModeBar": True,
                            "displaylogo": False,
                            "modeBarButtonsToRemove": ["autoScale2d", "toggleSpikelines", "hoverCompareCartesian", "hoverClosestCartesian"],
                        },
                        style={"margin-left": "12px", "width": "1000px", "height": "360px"}
                    )
                ]
            )
        ]
    )

    # print(graph_container)
    return graph_container

def generate_speed_profile(speed_profile_json, calibration=None):
    """Generates figure for given speed_profile_json"""
    pwm_list = []  # we're storing flow data
    flow_list = []
    # print(speed_profile_json)
    # print(calibration)
    if speed_profile_json is not None and calibration is not None:
        pwm_list.append(0)  # first value is 0 as the motor is stopped
        flow_list.append(0)
        for speed_setting in speed_profile_json["profile"]:
            # read data from the json speed_profile settings
            duration = speed_setting.get("duration", 0)
            flow = speed_setting.get("flow", 0)
            pwm_per_second = speed_setting.get("pwm_per_second", 100)

            pwm = int(calibration.get_pwm(flow))
            # print(f"Target pwm: {pwm}")
            start = pwm_list[-1]
            stop = pwm
            # print(f"Start pwm: {start}, stop pwm: {stop}")
            if stop > pwm_list[-1]:
                step = pwm_per_second
            else:
                step = -pwm_per_second

            if pwm_per_second < abs(start-stop):
                # print(f"ABS START - STOP: {abs(start-stop)}")
                # print(f"PWM PER SECOND: {pwm_per_second}")
                num_stops = math.ceil(abs(start-stop) / pwm_per_second)
                # print(f"Number of stops: {num_stops}")
                for i in range(1, math.ceil(num_stops) + 1):
                    middle_pwm = int((((stop - start) / num_stops)  * i) + start)
                    # print(f"Calculated pwm: {middle_pwm}")
                    pwm_list.append(middle_pwm)
                    flow_list.append(flow)
            else:
                pwm_list.append(int(pwm))
                flow_list.append(flow)

            last_pwm = pwm_list[-1]
            for _ in range(0, duration):
                pwm_list.append(last_pwm)
                flow_list.append(flow)

        pwm_list.append(0)  # last value is 0
        flow_list.append(0)
        # plt.plot(data)
        # plt.savefig("test.jpg")
        # print(pwm_list)

    data_count = len(pwm_list)
    ## generate figure
    fig = {
        # https://plotly.com/javascript/reference/index/
        "data": [
            {
                "type": "scatter",
                "name": "Flow (mL/min))",
                # "name": name,
                # "x": df["Time"].tolist(),
                "x": list(range(0, data_count)),  # take first 300 data points
                # "y": df[item].tolist(),
                "y": flow_list,
                "mode": "lines",
                "marker": {
                    # more about "marker.color": #scatter-marker-color
                    "color": "rgb(50,160,235)"
                },
                "line": {
                    "color": "rgb(50,160,235)"
                }
            },
            {
                "type": "scatter",
                "name": "Speed(PWM (%))",
                # "x": df["Time"].tolist(),
                "x": list(range(0, data_count)),  # take first 300 data points
                # "y": df[item].tolist(),
                "y": pwm_list,
                "mode": "lines",
                "marker": {
                    # more about "marker.color": #scatter-marker-color
                    "color": "rgb(250,185,50)"
                },
                "line": {
                    "color": "rgb(250,185,50)"
                }
            }
        ],
        "layout":
        {
            "title": "Speed Profile Plot",
            # "width": 700,
            # "height": h,
            "showlegend": True,
            "margin": {
                "t": 40,
                "b": 40,
                "l": 50,
                "r": 40
            },
            "xaxis": {
                "title": "<b>Time (s)</b>",
                "range": [-10, data_count+5],
                "fixedrange": False,
                # "zeroline": False,
                "gridcolor": "rgb(50, 50, 50)",
                "showticklabels": True
            },
            "yaxis": {
                "title": "<b> PWM (%) </b>",
                "range": [0, 100],
                "fixedrange": False,
                "gridcolor": "rgb(50, 50, 50)"
            }
        }
    }

    return fig



speed_profile_json = {
    "profile": [
        {"flow": 3.0, "duration": 30, "pwm_per_second": 50},
        {"flow": 3.4, "duration": 30, "pwm_per_second": 70},
        {"flow": 3.6, "duration": 30, "pwm_per_second": 100},
        {"flow": 3.1, "duration": 30, "pwm_per_second": 25},
        {"flow": 2.7, "duration": 30, "pwm_per_second": 50},
        {"flow": 4.3, "duration": 30, "pwm_per_second": 15}
    ]
}

generate_speed_profile(speed_profile_json)
    # data = y
    # time = [t for t in range(-data_count, 0)]
    # fig = {
    #     # https://plotly.com/javascript/reference/index/
    #     "data": [
    #         {
    #             "type": "scatter",
    #             # "x": df["Time"].tolist(),
    #             "x": time[-len(data):],  # take first 300 data points
    #             # "y": df[item].tolist(),
    #             "y": data,
    #             "mode": "lines",
    #             "marker": {
    #                 # more about "marker.color": #scatter-marker-color
    #                 "color": "rgb(55, 0, 255)"
    #             },
    #             "line": {
    #                 "color": "rgb(10, 100, 200)"
    #             }
    #         }
    #     ],
    #     "layout":
    #     {
    #         # "width": 700,
    #         # "height": h,
    #         "showlegend": True,
    #         "margin": {
    #             "t": mt,
    #             "b": mb,
    #             "l": 50,
    #             "r": 40
    #         },
    #         "xaxis": {
    #             "title": "<b>Time (s)</b>",
    #             "range": [-data_count, 0],
    #             "fixedrange": fixed_x,
    #             # "zeroline": False,
    #             "gridcolor": "rgb(50, 50, 50)",
    #             "showticklabels": True
    #         },
    #         "yaxis": {
    #             "title": "<b>" + y_axis_label + "</b>",
    #             # "range": y_range,
    #             # "fixedrange": fixed_y,
    #             "gridcolor": "rgb(50, 50, 50)"
    #         }
    #     }
    # }

    # return fig