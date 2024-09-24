import pandas as pd
from dash import Dash, dcc, html, Input, Output, State, ALL
import math
import numpy as np
import datetime
import os
import webbrowser


def summarize(df, column):
    df[column] = df[column].replace([np.inf, -np.inf], np.nan)

    mean = df[column].mean()
    max = df[column].max()
    low = df[column].min()
    std = df[column].std()

    return [round(mean, 2), max, low, round(std, 2)]


empty_ping = pd.DataFrame(
    {
        "time": [0],
        "ping_www": [0],
        "ping_192": [0],
        "rsrp": [0],
        "rsrq": [0],
        "sinr": [0],
        "band": [0],
        "pci": [0],
        "ber": [0],
        "up": [0],
        "down": [0],
        "neighbor": [0],
    }
)


# storing data for updating graphs
class DataPing:
    def __init__(self, files: list[str]):
        self.data = [empty_ping, empty_ping] if len(files) == 0 else []

        for file in files:
            self.data.append(pd.read_csv(f"{file}/ping.csv"))  # all data

        self.files_name = files if len(files) > 0 else ["empty", "also empty"]

        self.display_start = 0
        self.display_range = len(self.data)
        self.raw_len = len(self.data[0])

        # stats contains mean, max, min, std
        self.stats192 = []
        self.statswww = []

    def gen_graph(self):
        for data in self.data:
            d: pd.DataFrame = data[
                self.display_start : self.display_start + self.display_range
            ]

            # stats
            self.stats192.append(summarize(d, "ping_192"))
            self.statswww.append(summarize(d, "ping_www"))


class DataStuck:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.year = str(datetime.datetime.now().year)

    def get_range(self, start: str, end: str):
        if len(self.data) == 0:
            return pd.DataFrame()
        data = self.data[(self.data["start"] >= start) & (self.data["end"] <= end)]
        return data


# Function to list folders in the fixed path
def get_folders(path):
    if os.path.isdir(path):
        # List all folders in the given path
        folders = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
        return [
            {"label": folder, "value": os.path.join(path, folder)} for folder in folders
        ]
    return []


PATH = r"./log/live"

data_ping = DataPing([])
# data_stuck = DataStuck(pd.DataFrame({'start': [], 'end': [], 'duration': []}))

app = Dash(__name__, title="ping数据对比")


# Layout of the app
app.layout = html.Div(
    [
        html.Div(
            [
                html.Label(
                    "Enter number of files to upload:",
                    style={
                        "fontSize": "20px",  # Increase font size
                        "fontWeight": "bold",  # Optional: make the text bold
                        "marginBottom": "10px",  # Add some spacing below the label
                    },
                ),
                dcc.Input(
                    id="file-count-input",
                    type="number",
                    min=2,
                    value=2,
                    style={
                        "fontSize": "18px",  # Increase the input's font size
                        "padding": "10px",  # Add padding to make the input bigger
                        "width": "100px",  # Adjust width as needed
                        "marginRight": "15px",  # Add margin to the right for spacing
                    },
                ),
                # Button with adjusted spacing
                html.Button(
                    "Confirm",
                    id="generate-button",
                    n_clicks=0,
                    style={
                        "fontSize": "20px",
                        "padding": "5px 15px",  # Increase padding for a bigger button
                        "marginBottom": "20px",  # Add margin bottom for spacing
                    },
                ),
            ]
        ),
        # Container to dynamically generate upload fields
        html.Div(id="upload-container"),
        # Select folder button
        html.Button(
            "Select Folder",
            id="select-folder-button",
            n_clicks=0,
            style={
                "fontSize": "20px",
                "padding": "15px 25px",
                "marginBottom": "30px",  # Add margin bottom for spacing
                "marginTop": "10px",  # Add margin top for spacing between elements
            },
        ),
        html.Div(id="output-folder-path", style={"marginBottom": "20px"}),
        html.Div(
            [
                html.Div(
                    [
                        html.H1(
                            "显示起点",
                        ),
                        dcc.Slider(
                            0,
                            1,
                            step=1e-6,
                            marks=None,
                            value=0,
                            id="start-from-raw",
                        ),
                    ],
                    style={"width": "30%", "display": "inline-block"},
                ),
                html.Div(
                    [
                        html.H1("显示范围"),
                        dcc.Slider(
                            0,
                            1,
                            step=1e-6,
                            marks=None,
                            value=1,
                            id="range-raw",
                        ),
                    ],
                    style={"width": "30%", "display": "inline-block"},
                ),
            ]
        ),
        html.H1(id="range-display"),
        # Container for dynamically generated tables
        html.Div(id="stats"),
    ],
    style={
        "textAlign": "center",
        "font-size": "10px",
        "marginTop": "50px",
        "marginBottom": "20px",
    },
)


@app.callback(
    Output("upload-container", "children"),
    Input("generate-button", "n_clicks"),
    State("file-count-input", "value"),
)
def generate_upload_fields(n_clicks, file_count):
    if n_clicks > 0 and file_count > 0:
        upload_fields = []
        for i in range(file_count):
            upload_fields.append(
                html.Div(
                    [
                        dcc.Dropdown(
                            options=get_folders(PATH),
                            value=None,
                            placeholder="Select a folder",
                            id={"type": "upload-dropdown", "index": i + 1},
                            style={"fontSize": "18px", "marginBottom": "20px"},
                        ),
                    ]
                )
            )
        return upload_fields
    return None


# Callback to update the output based on the selected datetime
@app.callback(
    Output("range-display", "children"),
    Output("stats", "children"),
    Input("select-folder-button", "n_clicks"),
    Input("range-raw", "value"),
    Input("start-from-raw", "value"),
    State({"type": "upload-dropdown", "index": ALL}, "value"),
)
# getting the new range for updating the graph(two bars), positional arguments, same order with call back
def update_range(n_clicks, range_raw, start_raw, selected_folder):
    global data_ping
    if n_clicks > 0 and selected_folder:
        data_ping = DataPing(selected_folder)

    if range_raw is not None:
        if start_raw is None:
            start_raw = data_ping.display_start / data_ping.raw_len
        # 指数缩放
        data_ping.display_range = max(1, math.ceil(range_raw**2 * data_ping.raw_len))

    if start_raw is not None:
        data_ping.display_start = math.ceil(
            start_raw * (data_ping.raw_len - data_ping.display_range)
        )

    # parameter: mode(which graph)
    data_ping.gen_graph()

    start_time = data_ping.data[0]["time"][data_ping.display_start]
    end_time = data_ping.data[0]["time"][
        data_ping.display_start + data_ping.display_range - 1
    ]

    # stuck = data_stuck.get_range(start_time,end_time)

    # start_time_obj = datetime.datetime.strptime(start_time, "%m-%d %H:%M:%S")
    # end_time_obj = datetime.datetime.strptime(end_time, "%m-%d %H:%M:%S")
    # total_minutes = (end_time_obj - start_time_obj).total_seconds()/60
    # per_minute = lambda n : round( n / total_minutes,2)

    tables = []
    if selected_folder:
        for i in range(0, len(selected_folder)):
            stats192 = data_ping.stats192[i]
            statswww = data_ping.statswww[i]

            head = html.Thead(
                [html.Tr([html.Th(""), html.Th("网关"), html.Th("外网")])]
            )
            body = html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td("Mean(ms)"),
                            html.Td(stats192[0]),
                            html.Td(statswww[0]),
                        ]
                    ),
                    html.Tr(
                        [html.Td("Max(ms)"), html.Td(stats192[1]), html.Td(statswww[1])]
                    ),
                    html.Tr(
                        [html.Td("Min(ms)"), html.Td(stats192[2]), html.Td(statswww[2])]
                    ),
                    html.Tr(
                        [html.Td("SDσ(ms)"), html.Td(stats192[3]), html.Td(statswww[3])]
                    ),
                ]
            )
            table_title = html.Caption(
                f"{data_ping.files_name[i][11:]}",  # Customize the title as needed
                style={
                    "captionSide": "top",  # 'top' or 'bottom'
                    "fontSize": "25px",
                    "fontWeight": "bold",
                    "padding": "10px",
                },
            )

            tables.append(
                html.Table(
                    [table_title, head, body],
                    style={
                        "width": "50%",
                        "border": "1px solid black",
                        "borderCollapse": "collapse",
                        "textAlign": "center",
                        "margin": "20px auto",
                        "fontSize": "25px",
                    },
                )
            )

    return (
        f"显示范围: {start_time} - {end_time}",
        # "到网关(192)"\
        # f"断连{per_minute(data_ping.inf192_cnt)}次/分钟,      "
        # f"高延迟{per_minute(data_ping.lag192_cnt)}次/分钟 ",
        #  f"到外网(www)\n"
        # f"断连 {per_minute(data_ping.infwww_cnt)} 次/分钟,    "
        # f"高延迟 {per_minute(data_ping.lagwww_cnt)} 次/分钟",
        tables,
    )


# Function to open the browser automatically
def open_browser():
    webbrowser.open_new("http://127.0.0.1:520/")


def main():
    app.run_server(debug=False, port=520)


if __name__ == "__main__":
    app.run_server(debug=True, port=520)
