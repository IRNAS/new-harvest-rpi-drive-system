# import matplotlib.pyplot as plt
import math
from dash import dcc, html
# def get_rpm(flow, calibration):
#     """Return required rpm to get desired flow"""
#     # print(f"Calculating rpm from selected flow: {flow} and slope: {self.slope}")
#     return flow / 0.058

def generate_speed_profile_plot_container(id, speed_profile_json, calibration):
    """
    Generate speed profile plot section of GUI
    """
    fig = generate_speed_profile(speed_profile_json, calibration)
    # print(f"Figure: {fig}")

    graph_container = html.Div(
        className="d-flex flex-direction-row mt-3",
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
                            "staticPlot": True,
                            "editable": False,
                            "displayModeBar": False,
                            "displaylogo": False,
                            "modeBarButtonsToRemove": ["autoScale2d", "toggleSpikelines", "hoverCompareCartesian", "hoverClosestCartesian"],
                        },
                        style={"margin-left": "12px", "width": "500px", "height": "180px"}
                    )
                ]
            )
        ]
    )

    # print(graph_container)
    return graph_container

def generate_speed_profile(speed_profile_json, calibration=None):
    """Generates figure for given speed_profile_json"""
    rpm_list = []  # we're storing flow data
    flow_list = []
    # print(speed_profile_json)
    # print(calibration)
    if speed_profile_json is not None and calibration is not None:
        rpm_list.append(0)  # first value is 0 as the motor is stopped
        flow_list.append(0)
        for speed_setting in speed_profile_json["profile"]:
            # read data from the json speed_profile settings
            duration = speed_setting.get("duration", 0)
            flow = speed_setting.get("flow", 0)
            rpm_per_second = speed_setting.get("rpm_per_second", 100)

            rpm = int(calibration.get_rpm(flow))
            # print(f"Target rpm: {rpm}")
            start = rpm_list[-1]
            stop = rpm
            # print(f"Start rpm: {start}, stop rpm: {stop}")
            if stop > rpm_list[-1]:
                step = rpm_per_second
            else:
                step = -rpm_per_second

            if rpm_per_second < abs(start-stop):
                # print(f"ABS START - STOP: {abs(start-stop)}")
                # print(f"rpm PER SECOND: {rpm_per_second}")
                num_stops = math.ceil(abs(start-stop) / rpm_per_second)
                # print(f"Number of stops: {num_stops}")
                for i in range(1, math.ceil(num_stops) + 1):
                    middle_rpm = int((((stop - start) / num_stops)  * i) + start)
                    # middle_rpm = min(middle_rpm, 100)  # cap rpm to 100
                    # print(f"Calculated rpm: {middle_rpm}")
                    rpm_list.append(middle_rpm)
                    flow_list.append(flow)
            else:
                rpm_list.append(rpm)
                flow_list.append(flow)

            last_rpm = rpm_list[-1]
            for _ in range(0, duration):
                rpm_list.append(last_rpm)
                flow_list.append(flow)

        rpm_list.append(0)  # last value is 0
        flow_list.append(0)
        # plt.plot(data)
        # plt.savefig("test.jpg")
        # print(rpm_list)

    data_count = len(rpm_list)

    tickvals = [*range(0, data_count+5, 60)]
    ticktext = [val // 60 for val in tickvals]

    ## generate figure
    fig = {
        # https://plotly.com/javascript/reference/index/
        "data": [
            {
                "type": "scatter",
                "name": "Flow",
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
                "name": "Speed",
                # "x": df["Time"].tolist(),
                "x": list(range(0, data_count)),  # take first 300 data points
                # "y": df[item].tolist(),
                "y": rpm_list,
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
                "t": 35,
                "b": 30,
                "l": 46,
                "r": -5
            },
            "xaxis": {
                "title": "<b>Time (min)</b>",
                "range": [-10, data_count+5],
                "fixedrange": False,
                "tickmode": "array",
                "tickvals": tickvals,
                "ticktext": ticktext,
                # "zeroline": False,
                "gridcolor": "rgb(50, 50, 50)",
                "showticklabels": True
            },
            "yaxis": {
                "title": "<b> RPM </b>",
                # "range": [-5, 105],
                "fixedrange": False,
                "gridcolor": "rgb(50, 50, 50)"
            }
        }
    }

    return fig



speed_profile_json = {
    "profile": [
        {"flow": 3.0, "duration": 30, "rpm_per_second": 50},
        {"flow": 3.4, "duration": 30, "rpm_per_second": 70},
        {"flow": 3.6, "duration": 30, "rpm_per_second": 100},
        {"flow": 3.1, "duration": 30, "rpm_per_second": 25},
        {"flow": 2.7, "duration": 30, "rpm_per_second": 50},
        {"flow": 4.3, "duration": 30, "rpm_per_second": 15}
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