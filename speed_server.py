import pandas as pd
from dash import Dash, dcc, html, dash_table, Input, Output, State
import math
import numpy as np
import plotly.graph_objs as go
import datetime
from stable import summary
import bisect
import os
import threading
import webbrowser



#storing data for updating graphs
class Speed:
    def __init__(self, data: pd.DataFrame):
        self.data = data                             #all data
        self.display_start = 0
        self.display_range = len(self.data)
        self.graph_ping = None                       #the main graph
        self.raw_len = len(self.data)

        #stats contains mean, max, min, std
        self.upload = [0, 0, 0, 0]
        self.download = [0, 0, 0, 0]

        #lags and jit
        self.jit = [0, 0, 0, 0]
        self.lag = [0, 0, 0, 0]


    #update everytimes the state changes 

    def update_graph(self):
        self.graph_speed = go.Figure()
        data  = self.data[self.display_start:self.display_start+self.display_range]

        #drawing lines
        self.graph_speed.add_trace(go.Scatter(
            x=data['time'],
            y=data['upload'],
            mode='lines',
            name='Upload',
            marker=dict(color='#22aaff'),
        ))

        self.graph_speed.add_trace(go.Scatter(
            x=data['time'],
            y=data['download'],
            mode='lines',
            name='Download',
            marker=dict(color='#8888ff'),
        ))

        #stats
        self.upload = summary.summarize(data, "upload")
        self.download = summary.summarize(data, "download")

        self.lag = summary.summarize(data, "lag")
        self.jit = summary.summarize(data, "jit")

        return self.graph_speed




# Function to list folders in the fixed path
def get_folders(path):
    if os.path.isdir(path):
        # List all folders in the given path
        folders = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
        return [{'label': folder, 'value': os.path.join(path, folder)} for folder in folders]
    return []


path = r".\log\speed"


app = Dash(__name__, title = "测速数据整理")


speed = Speed(pd.DataFrame({'time': [0], 'lag': [0], 'jit': [0], 'download': [0], 'upload': [0]}))

# Layout of the app
app.layout = html.Div([

    #select drop down
    dcc.Dropdown(
        id='folders-dropdown',
        options=get_folders(path),  # Populate with folders from the fixed path
        value=None,
        placeholder="Select a folder",
        style={'fontSize': '18px', 'marginBottom': '20px'}  # Add margin bottom
    ),

    #Select button
    html.Button(
        'Select Folder',
        id='select-folder-button', 
        n_clicks=0,
        style={'fontSize': '18px', 'padding': '10px 20px', 'marginBottom': '30px'}  # Add margin bottom for spacing
    ),

    html.Div(id='output-folder-path', style={'marginBottom': '20px'}),  # Add margin bottom
    
    #起点
    html.H1(
        "显示起点",
        style={'marginBottom': '20px'}  # Add margin bottom for spacing
    ),
    dcc.Slider(
        0, 1,
        step=1e-6,
        marks=None,
        value=0,
        id='start-from-raw',
    ),

    #范围
    html.H1("显示范围"),
    dcc.Slider(0, 1,
        step=1e-6,
        marks=None,
        value=0.2,
        id='range-raw',
    ),
    
    #speed graph
    html.H1(id='range-display'),
    dcc.Graph(id='speed'),

], style={'textAlign': 'center', 'font-size': '10px', 'marginTop': '50px', 'marginBottom': '20px'})



@app.callback(
    Output('range-display', 'children'),
    Output('speed', 'figure'),

    Input('select-folder-button', 'n_clicks'),
    Input('range-raw', 'value'), 
    Input('start-from-raw', 'value'),

    State('folders-dropdown', 'value')
)
#getting the new range for updating the graph(two bars), positional arguments, same order with call back
def update_range(n_clicks, range_raw, start_raw, selected_folder):
    global speed
    if n_clicks > 0 and selected_folder:
        speed = Speed(pd.read_csv(f'{selected_folder}/speed.csv'))

    if range_raw is not None:
        if start_raw is None:
            start_raw = speed.display_start / speed.raw_len
        # 指数缩放
        speed.display_range = max(1, math.ceil(range_raw**2 * speed.raw_len))
    
    if start_raw is not None:
        speed.display_start = math.ceil(start_raw * (speed.raw_len - speed.display_range))

    #parameter: mode(which graph)
    speed.update_graph()
    start_time = speed.data['time'][speed.display_start]
    end_time = speed.data['time'][speed.display_start+speed.display_range - 1]


    return (f"显示范围: {start_time} - {end_time}", 
            speed.graph_speed
            )


# Function to open the browser automatically
def open_browser():
    webbrowser.open_new("http://127.0.0.1:8050/")

# def main():
#     threading.Timer(0, open_browser).start()
app.run_server(debug = True)