import pandas as pd
from dash import Dash, dcc, html, Input, Output, State
import dash
import math
import numpy as np
import plotly.graph_objs as go
import os
import webbrowser
from common import convert_old_time_str


# make stats of mean, max, min std
def summarize(df, column):
    # Convert the column to numeric, forcing errors to NaN
    df[column] = pd.to_numeric(df[column], errors="coerce")

    # Replace inf values with NaN
    df[column] = df[column].replace([np.inf, -np.inf], np.nan)

    # Calculate statistics
    mean = df[column].mean()
    max = df[column].max()
    low = df[column].min()
    std = df[column].std()

    return [round(mean, 2), max, low, round(std, 2)]


# 被遗弃的得分算法
def score(download, lag):
    if download != 0.0 and lag != 0.0:
        download_score = 100 / download
        lag_score = 1 - (100 / lag)
        return (0.5 * download_score) + (0.5 * lag_score)
    return 0


# Define a list of colors to be used for different traces
colors = ["#22aaff", "#ff9900", "#ff0066", "#6600ff", "#ffcc00", "#00ffcc", "#ff33cc"]
colors_rsrp = [
    "#2e4053",
    "#ffe119",
    "#3cb44b",
    "#4363d8",
    "#f58231",
    "#911eb4",
    "#42d4f4",
    "#f032e6",
]
colors_sinr = [
    "##808b96",
    "#154360",
    "#ffdfba",
    "#ffffba",
    "#baffc9",
    "#bae1ff",
    "#ffb7ff",
    "#ffd9e6",
]

empty_speed = pd.DataFrame(
    {
        "time": [0],
        "lag": [0],
        "jit": [0],
        "download": [0],
        "upload": [0],
        "rsrp": [0],
        "rsrq": [0],
        "sinr": [0],
        "band": [0],
        "pci": [0],
        "ber": [0],
    }
)


# storing data for updating graphs
class Speed:
    def __init__(self, files: list):
        self.data = [empty_speed] if len(files) == 0 else []
        # storing files name

        for file in files:
            data = pd.read_csv(f"{file}/speed.csv")
            data["time"] = data["time"].apply(convert_old_time_str)
            self.data.append(data)  # all data

        self.files_name = files if len(files) > 0 else ["empty"]

        self.display_start = 0
        self.display_range = len(self.data)

        self.graph_upload = None  # each data has a graph
        self.graph_lag = None
        self.graph_download = None
        self.graph_jit = None

        self.raw_len = len(self.data[0])

        self.uploads = []
        self.downloads = []
        self.jits = []
        self.lags = []

        # #stats contains mean, max, min, std

        # score
        self.score = []

    # update everytimes the state changes

    # update the whole page after the call back function is called
    def update_graph(self):
        self.graph_upload = go.Figure()
        self.graph_lag = go.Figure()
        self.graph_download = go.Figure()
        self.graph_jit = go.Figure()

        i = 1

        for data in self.data:
            d: pd.DataFrame = data[
                self.display_start : self.display_start + self.display_range
            ]

            self.uploads.append(summarize(d, "upload"))
            self.downloads.append(summarize(d, "download"))

            self.jits.append(summarize(d, "jit"))
            self.lags.append(summarize(d, "lag"))

            # hovertext data
            # hovertext = [
            #     f"Time: {row['time']}<br>Band: {row['band']}<br>PCI: {row['pci']}<br>rsrq: {row['rsrq']}db<br>ber: {row['ber']}"
            #     for index, row in d.iterrows()
            # ]
            hovertext = d.apply(
                lambda row: "<br>".join(
                    f"{key}: {row[key]}"
                    for key in ["time", "band", "pci", "rsrq", "ber"]
                ),
                axis=1,
            ).to_list()
            # Apply score function to each row
            # for _, row in d.iterrows():
            #     calculated_score = score(row['download'], row['lag'])
            #     self.score.append(calculated_score)

            self.graph_download.update_layout(
                title_text="Download(Mb/s)",
                title_x=0.5,
            )
            self.graph_upload.update_layout(
                title_text="Upload(Mb/s)",
                title_x=0.5,
            )
            self.graph_lag.update_layout(
                title_text="Lag(ms)",
                title_x=0.5,
            )
            self.graph_jit.update_layout(
                title_text="Jit(ms)",
                title_x=0.5,
            )

            self.graph_download.update_yaxes(title_text="Download speed")
            self.graph_upload.update_yaxes(title_text="Upload speed")
            self.graph_lag.update_yaxes(title_text="Lag")
            self.graph_jit.update_yaxes(title_text="Jit")

            color = colors[i % len(colors)]
            color_rsrp = colors_rsrp[i % len(colors_rsrp)]
            color_sinr = colors_sinr[i % len(colors_sinr)]

            # drawing lines
            self.graph_upload.add_trace(
                go.Scatter(
                    x=d.index,
                    y=d["upload"],
                    mode="lines",
                    name=f"Upload {self.files_name[i - 1][12:]}",
                    marker=dict(color=color),
                    hovertext=hovertext,
                )
            )

            self.graph_download.add_trace(
                go.Scatter(
                    x=d.index,
                    y=d["download"],
                    mode="lines",
                    name=f"Download {self.files_name[i - 1][12:]}",
                    marker=dict(color=color),
                    hovertext=hovertext,
                )
            )

            self.graph_download.add_trace(
                go.Scatter(
                    x=d.index,
                    y=d["rsrp"],
                    mode="lines",
                    name=f"rsrp {self.files_name[i - 1][12:]}",
                    marker=dict(color=color_rsrp),
                    hovertext=hovertext,
                )
            )

            self.graph_download.add_trace(
                go.Scatter(
                    x=d.index,
                    y=d["sinr"],
                    mode="lines",
                    name=f"sinr {self.files_name[i - 1][12:]}",
                    marker=dict(color=color_sinr),
                    hovertext=hovertext,
                )
            )

            self.graph_lag.add_trace(
                go.Scatter(
                    x=d.index,
                    y=d["lag"],
                    mode="lines",
                    name=f"Lag {self.files_name[i - 1][12:]}",
                    marker=dict(color=color),
                    hovertext=hovertext,
                )
            )

            self.graph_jit.add_trace(
                go.Scatter(
                    x=d.index,
                    y=d["jit"],
                    mode="lines",
                    name=f"Jit {self.files_name[i - 1][12:]}",
                    marker=dict(color=color),
                    hovertext=hovertext,
                )
            )

            i += 1
            # 更新图表，数据一些烂玩意儿


# Function to list folders in the fixed path
def get_folders(path):
    if os.path.isdir(path):
        # List all folders in the given path
        folders = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
        return [
            {"label": folder, "value": os.path.join(path, folder)} for folder in folders
        ]
    return []


# base path
PATH = r".\log\speed"

app = Dash(__name__, title="测速数据整理")

speed = Speed([])

# Layout of the app
app.layout = html.Div(
    [
        html.Div(
            [
                html.Label(
                    "日志数量",
                    style={
                        "fontSize": "20px",  # Increase font size
                        "fontWeight": "bold",  # Optional: make the text bold
                        "marginBottom": "10px",  # Add some spacing below the label
                    },
                ),
                dcc.Input(
                    id="file-count-input",
                    type="number",
                    min=1,
                    value=1,
                    style={
                        "fontSize": "18px",  # Increase the input's font size
                        "padding": "10px",  # Add padding to make the input bigger
                        "width": "100px",  # Adjust width as needed
                        "marginRight": "15px",  # Add margin to the right for spacing
                    },
                ),
                # Button with adjusted spacing
                html.Button(
                    "确认",
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
        # Select folder button
        html.Div(
            [
                # Container to dynamically generate upload fields
                html.Div(id="upload-container"),
                html.Hr(),
                html.Button(
                    "导入日志",
                    id="select-folder-button",
                    n_clicks=0,
                    style={
                        "fontSize": "18px",
                        "padding": "5px 15px",
                        "marginBottom": "30px",
                    },
                ),
            ],
            style={"width": "40%", "display": "inline-block"},
        ),
        html.Div(id="output-folder-path", style={"marginBottom": "20px"}),
        html.Hr(),
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
        # Container for dynamically generated tables
        html.Div(id="stats"),
        html.H1(""),
        # speed graph
        html.H1(id="range-display"),
        dcc.Graph(id="download"),
        dcc.Graph(id="upload"),
        dcc.Graph(id="lag"),
        dcc.Graph(id="jit"),
    ],
    style={
        "textAlign": "center",
        "font-size": "10px",
        "marginTop": "50px",
        "marginBottom": "20px",
    },
)


# upload's callback
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


# select range 's call back
@app.callback(
    Output("range-display", "children"),
    Output("download", "figure"),
    Output("upload", "figure"),
    Output("lag", "figure"),
    Output("jit", "figure"),
    Output("stats", "children"),
    Input("select-folder-button", "n_clicks"),
    Input("range-raw", "value"),
    Input("start-from-raw", "value"),
    State({"type": "upload-dropdown", "index": dash.ALL}, "value"),
)

# getting the new range for updating the graph(two bars), positional arguments, same order with call back
def update_range(n_clicks, range_raw, start_raw, selected_folder):
    global speed
    if n_clicks > 0 and selected_folder:
        speed = Speed(selected_folder)
    if range_raw is not None:
        if start_raw is None:
            start_raw = speed.display_start / speed.raw_len
        # 指数缩放
        speed.display_range = max(1, math.ceil(range_raw**2 * speed.raw_len))

    if start_raw is not None:
        speed.display_start = math.ceil(
            start_raw * (speed.raw_len - speed.display_range)
        )

    speed.update_graph()

    start_time: str = speed.data[0]["time"][speed.display_start]
    end_time: str = speed.data[0]["time"][speed.display_start + speed.display_range - 1]

    tables = []
    if selected_folder:
        for i in range(0, len(selected_folder)):
            upload = speed.uploads[i]
            download = speed.downloads[i]
            lag = speed.lags[i]
            jit = speed.jits[i]

            table_header = html.Thead(
                html.Tr(
                    [
                        html.Th(""),
                        html.Th("Upload"),
                        html.Th("Download"),
                        html.Th("Jit"),
                        html.Th("Lag"),
                    ]
                )
            )
            table_body = html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td("Mean"),
                            html.Td(upload[0]),
                            html.Td(download[0]),
                            html.Td(jit[0]),
                            html.Td(lag[0]),
                        ]
                    ),
                    html.Tr(
                        [
                            html.Td("Max"),
                            html.Td(upload[1]),
                            html.Td(download[1]),
                            html.Td(jit[1]),
                            html.Td(lag[1]),
                        ]
                    ),
                    html.Tr(
                        [
                            html.Td("Min"),
                            html.Td(upload[2]),
                            html.Td(download[2]),
                            html.Td(jit[2]),
                            html.Td(lag[2]),
                        ]
                    ),
                    html.Tr(
                        [
                            html.Td("SDσ"),
                            html.Td(upload[3]),
                            html.Td(download[3]),
                            html.Td(jit[3]),
                            html.Td(lag[3]),
                        ]
                    ),
                ]
            )
            table_title = html.Caption(
                f"{speed.files_name[i][12:]}",  # Customize the title as needed
                style={
                    "captionSide": "top",  # 'top' or 'bottom'
                    "fontSize": "25px",
                    "fontWeight": "bold",
                    "padding": "10px",
                },
            )

            tables.append(
                html.Table(
                    [table_title, table_header, table_body],
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
        speed.graph_download,
        speed.graph_upload,
        speed.graph_lag,
        speed.graph_jit,
        tables,
    )


# Function to open the browser automatically
def open_browser():
    webbrowser.open_new("http://127.0.0.1:250/")


def main():
    app.run_server(debug=False, port=250)


if __name__ == "__main__":
    app.run_server(debug=True, port=250)
