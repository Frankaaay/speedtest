import pandas as pd
from dash import Dash, dcc, html, Input, Output, State, MATCH, ALL
import math
import numpy as np
import plotly.graph_objs as go
import os
import webbrowser

def summarize(df, column):
    df[column] = df[column].replace([np.inf, -np.inf], np.nan)

    mean = df[column].mean()
    max = df[column].max()
    low = df[column].min()
    std = df[column].std()

    return [round(mean, 2), max, low, round(std, 2)]

def score(download, lag):
    if download != 0.0 and lag != 0.0:
        download_score = 100 / download
        lag_score = 1- (100 / lag)
        return (0.5 * download_score) + (0.5 * lag_score)
    return 0

# Define a list of colors to be used for different traces
colors = ['#22aaff', '#ff9900', '#00cc44', '#ff0066', '#6600ff', '#ffcc00', '#00ffcc', '#ff33cc']
colors_rsrp = ['#2e4053','#ffe119', '#3cb44b',  '#4363d8', '#f58231', '#911eb4', '#42d4f4', '#f032e6']
colors_sinr = ['##808b96','#154360', '#ffdfba', '#ffffba', '#baffc9', '#bae1ff',  '#ffb7ff', '#ffd9e6']



#storing data for updating graphs
class Speed:
    def __init__(self, files: list):
        self.data = []
        for i in range(0, len(files)):
            self.data.append(pd.read_csv(f'{files[i]}/speed.csv'))        #all data
        self.display_start = 0
        self.display_range = len(self.data)

        self.graph_upload = None 
        self.graph_lag = None    
        self.graph_download = None 
        self.graph_jit = None    #the main graph

        self.raw_len = len(self.data[0])

        self.uploads = [] 
        self.downloads = []
        self.jits = []
        self.lags = []

        # #stats contains mean, max, min, std
        # self.upload = [0, 0, 0, 0]

        #score
        self.score = []

    #update everytimes the state changes 

    def update_graph(self):
        self.graph_upload = go.Figure()
        self.graph_lag = go.Figure()
        self.graph_download = go.Figure()
        self.graph_jit = go.Figure()

        i = 1

        for data in self.data:

            d : pd.DataFrame = data[self.display_start:self.display_start+self.display_range]

            hovertext = [f"Band: {row['band']}<br>Time: {row['time']}<br>PCI: {row['pci']}" 
            for index, row in d.iterrows()]

            # Apply score function to each row
            # for _, row in d.iterrows():
            #     calculated_score = score(row['download'], row['lag'])
            #     self.score.append(calculated_score)

            
            self.graph_download.update_layout(
                title_text = "Download"
            )
            self.graph_upload.update_layout(
                title_text = "Upload"
            )
            self.graph_lag.update_layout(
                title_text = "Lag"
            )
            self.graph_jit.update_layout(
                title_text = "Jit"
            )

            self.graph_download.update_yaxes(title_text = "Download speed")
            self.graph_upload.update_yaxes(title_text = "Upload speed")
            self.graph_lag.update_yaxes(title_text = "Lag")
            self.graph_jit.update_yaxes(title_text = "Jit")

            color = colors[i % len(colors)]
            color_rsrp = colors_rsrp[i % len(colors_rsrp)]
            color_sinr = colors_sinr[i % len(colors_sinr)]

            #drawing lines
            self.graph_upload.add_trace(go.Scatter(
                x=d.index,
                y=d['upload'],
                mode='lines',
                name=f'Upload{i}',
                marker=dict(color=color),
                hovertext = hovertext
            ))

            self.graph_download.add_trace(go.Scatter(
                x=d.index,
                y=d['download'],
                mode='lines',
                name=f'Download{i}',
                marker=dict(color=color),
                hovertext = hovertext
            ))

            self.graph_download.add_trace(go.Scatter(
                x=d.index,
                y=d['rsrp'],
                mode='lines',
                name=f'rsrp{i}',
                marker=dict(color=color_rsrp),
                hovertext = hovertext
            ))

            self.graph_download.add_trace(go.Scatter(
                x=d.index,
                y=d['sinr'],
                mode='lines',
                name=f'sinr{i}',
                marker=dict(color=color_sinr),
                hovertext = hovertext
            ))
            
            self.graph_lag.add_trace(go.Scatter(
                x=d.index,
                y=d['lag'],
                mode='lines',
                name=f'Lag{i}',
                marker=dict(color=color),
            ))

            self.graph_jit.add_trace(go.Scatter(
                x=d.index,
                y=d['jit'],
                mode='lines',
                name=f'Jit{i}',
                marker=dict(color=color),
            ))  
            self.uploads.append(summarize(d, "upload"))
            self.downloads.append(summarize(d, "download"))

            self.jits.append(summarize(d, "jit"))
            self.lags.append(summarize(d, "lag"))

            i += 1
            # print(len(self.uploads))






# Function to list folders in the fixed path
def get_folders(path):
    if os.path.isdir(path):
        # List all folders in the given path
        folders = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
        return [{'label': folder, 'value': os.path.join(path, folder)} for folder in folders]
    return []


path = r".\log\speed"


app = Dash(__name__, title = "测速数据整理")


speed = Speed(['empty_speed'])

# Layout of the app
app.layout = html.Div([
    html.Div([
        html.Label("Enter number of files to upload:", style={
                'fontSize': '20px',  # Increase font size
                'fontWeight': 'bold',  # Optional: make the text bold
                'marginBottom': '10px'  # Add some spacing below the label
            }
        ),
        dcc.Input(
            id='file-count-input', 
            type='number', 
            min=1, 
            value=1, 
            style={
                'fontSize': '18px',  # Increase the input's font size
                'padding': '10px',  # Add padding to make the input bigger
                'width': '100px',  # Adjust width as needed
                'marginRight': '15px'  # Add margin to the right for spacing
            }
        ),
        
        # Button with adjusted spacing
        html.Button(
            'Confirm', 
            id='generate-button', 
            n_clicks=0, 
            style={
                'fontSize': '20px', 
                'padding': '10px 20px',  # Increase padding for a bigger button
                'marginBottom': '20px'  # Add margin bottom for spacing
            }
        )
    ]),
    
    # Container to dynamically generate upload fields
    html.Div(id='upload-container'),

    # Select folder button
    html.Button(
        'Select Folder', 
        id='select-folder-button', 
        n_clicks=0, 
        style={
            'fontSize': '20px', 
            'padding': '15px 25px', 
            'marginBottom': '30px',  # Add margin bottom for spacing
            'marginTop': '10px'      # Add margin top for spacing between elements
        }
    ),

    html.Div(
        id='output-folder-path', 
        style={'marginBottom': '20px'}),
    
    
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
        value=1,
        id='range-raw',
    ),
    

    # Container for dynamically generated tables
    html.Div(id='stats'),

    html.H1(""),

    #speed graph
    html.H1(id = 'range-display'),

    dcc.Graph(id = 'download'),
    dcc.Graph(id = 'upload'),
    dcc.Graph(id = 'lag'),
    dcc.Graph(id = 'jit'),

], style={'textAlign': 'center', 'font-size': '10px', 'marginTop': '50px', 'marginBottom': '20px'})

@app.callback(
    Output('upload-container', 'children'),
    Input('generate-button', 'n_clicks'),
    State('file-count-input', 'value')
)
def generate_upload_fields(n_clicks, file_count):
    if n_clicks > 0 and file_count > 0:
        upload_fields = []
        for i in range(file_count):
            upload_fields.append(
                html.Div([
                    dcc.Dropdown(
                        options=get_folders(path),
                        value=None,
                        placeholder="Select a folder",
                        id={'type': 'upload-dropdown', 'index': i+1},
                        style={'fontSize': '18px', 'marginBottom': '20px'}
                    ),
                ])
            )
        return upload_fields
    return None



@app.callback(
    Output('range-display', 'children'),
    Output('download', 'figure'),
    Output('upload', 'figure'),
    Output('lag', 'figure'),
    Output('jit', 'figure'),
    Output('stats', 'children'),

    Input('select-folder-button', 'n_clicks'),
    Input('range-raw', 'value'), 
    Input('start-from-raw', 'value'),

    Input({'type': 'upload-dropdown', 'index': ALL}, 'value'),
)


#getting the new range for updating the graph(two bars), positional arguments, same order with call back
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
        speed.display_start = math.ceil(start_raw * (speed.raw_len - speed.display_range))

    speed.update_graph()

    start_time: str = speed.data[0]['time'][speed.display_start]
    end_time: str = speed.data[0]['time'][speed.display_start+speed.display_range - 1]

    tables = []
    if selected_folder:
        for i in range(0, len(selected_folder)):

            upload = speed.uploads[i]
            download = speed.downloads[i]
            lag = speed.lags[i]
            jit = speed.jits[i]

            table_header =html.Thead(
                    html.Tr([
                        html.Th(""),
                        html.Th("Upload"),
                        html.Th("Download"),
                        html.Th("Jit"),
                        html.Th("Lag")
                    ])
                )
            table_body = html.Tbody([
                    html.Tr([
                        html.Td("Mean(ms)"),
                        html.Td(upload[0]),
                        html.Td(download[0]),
                        html.Td(jit[0]),
                        html.Td(lag[0])
                    ]),
                    html.Tr([
                        html.Td("Max(ms)"),
                        html.Td(upload[1]),
                        html.Td(download[1]),
                        html.Td(jit[1]),
                        html.Td(lag[1])
                    ]),
                    html.Tr([
                        html.Td("Min(ms)"),
                        html.Td(upload[2]),
                        html.Td(download[2]),
                        html.Td(jit[2]),
                        html.Td(lag[2])
                    ]),
                    html.Tr([
                        html.Td("SDσ(ms)"),
                        html.Td(upload[3]),
                        html.Td(download[3]),
                        html.Td(jit[3]),
                        html.Td(lag[3])
                    ])
                ])
            table_title = html.Caption(
            f"Speed Data for Folder {i+1}",  # Customize the title as needed
            style={
                'captionSide': 'top',  # 'top' or 'bottom'
                'fontSize': '25px',
                'fontWeight': 'bold',
                'padding': '10px'
            }
        )

            tables.append(html.Table([table_title, table_header, table_body], style={
                'width': '50%',
                'border': '1px solid black',
                'borderCollapse': 'collapse',
                'textAlign': 'center',
                'margin': '20px auto',
                'fontSize': '25px',
            }))
            


    return (f"显示范围: {start_time} - {end_time}", 
            speed.graph_download,
            speed.graph_upload,
            speed.graph_lag,
            speed.graph_jit,
            tables,
            )


# Function to open the browser automatically
def open_browser():
    webbrowser.open_new("http://127.0.0.1:250/")

# def main():
app.run_server(debug = True, port = 250)