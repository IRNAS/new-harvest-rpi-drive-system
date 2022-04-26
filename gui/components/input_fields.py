import dash_html_components as html
import dash_core_components as dcc

def dropdown(id, label, fields, value="", dd_style={"width": "83%", "height": "30px"}):
    """
    Return div with label and dropdown fields.
    Fields has to be a list of dicts in the for of [{"label": dd_label, "value": dd_value}, {"label": dd_label, "value": dd_value}]
    """
    dd = html.Div(
        style={"display": "flex", "flex-direction": "column", "text-align": "left", "margin-top": "10px"},
        children=[
            html.Span(
                style={"font-size": "16px", "font-weight": "bold"},
                children=[
                    label
                ]
            ),
            dcc.Dropdown(
                id=f"{id}-dropdown",
                options=fields,
                style=dd_style,
                className="mt-1",
                value=value
            ),
        ]
    )
    return dd

def text_field(id, label, type, default_value):
    """
    Generate user input div of type [text, number].
    """
    text_input_div = html.Div(
        style={"display": "flex", "flex-direction": "column", "text-align": "left"},
        children=[
            html.Span(
                style={"font-size": "20px", "font-weight": "bold"},
                children=[
                    label
                ]
            ),
            dcc.Input(
                id=f"{id}-input",
                type=type,
                debounce=True,  # must be set to true for onscreen keyboard to work
                value=default_value,
                style={"width": "70%", "height": "30px", "font-size": "20px", "font-weight": "bold", "background": "aliceblue", "border-radius": "5px"},
                className="mt-1"
            )
        ]
    )
    return text_input_div