import dash_html_components as html
import dash_core_components as dcc

def custom_slider(id, min, max, step, initial_value, user_marks=None):
    """Create and return custom slider"""
    min = int(min)
    max = int(max)
    if user_marks is None:
        marks={
            int(min): {"label": str(int(min))},
            int(max/5): {"label": str(int(max/5))},
            int(2*max/5): {"label": str(int(2*max/5))},
            int(3*max/5): {"label": str(int(3*max/5))},
            int(4*max/5): {"label": str(int(4*max/5))},
            int(max): {"label": str(int(max))}
        }
    else:
        marks = {}
        for mark in user_marks:
            marks[str(mark)] = mark

    return html.Div(
        style={"margin-top": "0.2rem"},
        #className="slidecontainer",
        children=[
            dcc.Slider(
                id=id,
                #className="slider",
                # className="custom-range",
                value=initial_value,
                min=min,
                max=max,
                step=step,
                marks=marks
            ) 
        ]
    )
