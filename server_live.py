import pandas as pd
from dash import Dash, dcc, html, dash_table, Input, Output, State
import math
import numpy as np
import plotly.graph_objs as go
import datetime
import bisect
import os
import webbrowser
import datetime

#same thing with the server_speed, pls read comments there
def summarize(df, column):
    df[column] = df[column].replace([np.inf, -np.inf], np.nan)

    mean = df[column].mean()
    max = df[column].max()
    low = df[column].min()
    std = df[column].std()

    return [round(mean, 2), max, low, round(std, 2)]



#storing data for updating graphs
class DataPing:
    def __init__(self, data: pd.DataFrame):
        self.data = data         #all data
        self.display_start = 0
        self.display_range = len(self.data)
        self.graph_ping = None              #the main graph
        self.devices = 0                    #how many devices

        self.upload = None
        self.download = None

        self.raw_len = len(self.data)

        self.infwww_cnt = 0     # how many times www disconnection
        self.inf192_cnt = 0     # in the given range
        self.lag192_cnt = 0     #
        self.lagwww_cnt = 0     #

        #stats contains mean, max, min, std
        self.stats192 = [0, 0, 0, 0]
        self.statswww = [0, 0, 0, 0]


        #all xy of dots on graphs
        self.lag_www = empty_ping
        self.inf_www = empty_ping
        self.lag_192 = empty_ping
        self.inf_192 = empty_ping

        self.construct_data()

    def construct_data(self):
        # 标记 inf 值
        # 获取所有 inf 的索引

        #wwws
        temp = 0
        for index, row in self.data.iterrows():
            if np.isinf(row['ping_www']):
                row_new = row.copy()
                row_new['ping_www'] = temp
                self.inf_www = pd.concat([self.inf_www, pd.DataFrame([row_new])])
            else:
                temp= row['ping_www']
                if row["ping_www"] >= 100:
                    self.lag_www = pd.concat([self.lag_www, pd.DataFrame([row])])
        #192s
        temp = 0
        for index, row in self.data.iterrows():
            if np.isinf(row['ping_192']):
                row_new = row.copy()
                row_new['ping_192'] = temp
                self.inf_192 = pd.concat([self.inf_192, pd.DataFrame([row_new])])
            else:
                temp= row['ping_192']
                if row["ping_192"] >= 20:
                    self.lag_192 = pd.concat([self.lag_192, pd.DataFrame([row])])

    #update everytimes the state changes
    def gen_graph(self, s = "", e = ""):
        self.graph_ping = go.Figure()              #the main graph

        self.upload = go.Figure()   
        self.download = go.Figure()   

        if not s:
            start_time = self.data['time'][self.display_start]
            end_time = self.data['time'][self.display_start+self.display_range - 1]
        else:
            start_time = s
            end_time = e

        def time_filter(data:pd.DataFrame):
            index = (data.index[data['time'] >= start_time]).intersection(data.index[data['time'] <= end_time])
            return data.loc[index]
        
        data = time_filter(self.data)
        inf_www = time_filter(self.inf_www)
        inf_192 = time_filter(self.inf_192)
        lag_www = time_filter(self.lag_www)
        lag_192 = time_filter(self.lag_192)
        
        
        if self.devices > 0:
            data = data[data['neighbor'] == self.devices]
            inf_www = inf_www[inf_www['neighbor'] == self.devices]
            inf_192 = inf_192[inf_192['neighbor'] == self.devices]
            lag_www = lag_www[lag_www['neighbor'] == self.devices]
            lag_192 = lag_192[lag_192['neighbor'] == self.devices]
        
        
        hovertext = [f"设备数量: {row['neighbor']}<br>Band: {row['band']}<br>ber: {row['ber']}<br>PCI: {row['pci']}" for index, row in data.iterrows()]

        #drawing lines
        self.graph_ping.add_trace(go.Scatter(
            x=data['time'],
            y=data['ping_www'],
            mode='lines',
            name='ping_www',
            marker=dict(color = '#F20C0C'),
            hovertext = hovertext,
        ))
        self.graph_ping.add_trace(go.Scatter(
            x=data['time'],
            y=data['ping_192'],
            mode='lines',
            name='ping_192',
            marker=dict(color = '#F2960C'),
            hovertext = hovertext
        ))

        self.graph_ping.add_trace(go.Scatter(
            x=data['time'],
            y=data['sinr'],
            mode='lines',
            name='sinr',
            marker=dict(color = '#FF00FF'),
            hovertext = hovertext
        ))


        self.graph_ping.add_trace(go.Scatter(
            x=data['time'],
            y=data['rsrq'],
            mode='lines',
            name='rsrq',
            marker=dict(color = '#3AF20C'),
            hovertext = hovertext
        ))


        self.graph_ping.add_trace(go.Scatter(
            x=data['time'],
            y=data['rsrp'],
            mode='lines',
            name='rsrp',
            marker=dict(color = '#0C68F2'),
            hovertext = hovertext
        ))

        self.upload.add_trace(go.Scatter(
            x=data['time'],
            y=data['up'],
            mode='lines',
            name='upload',
            marker=dict(color = '#FF00FF'),
            hovertext = hovertext
        ))


        self.download.add_trace(go.Scatter(
            x=data['time'],
            y=data['down'],
            mode='lines',
            name='download',
            marker=dict(color = '#0C68F2'),
            hovertext = hovertext
        ))
        
        # print(inf_www,inf_192)

        #drawing disconnection dots
        self.graph_ping.add_trace(go.Scatter(
            x=list(inf_www['time']),
            y=list(inf_www['ping_www']),
            mode='markers',
            marker=dict(color = '#0CF2F2', size = 5),
            name='www_不可达'
        ))

        self.graph_ping.add_trace(go.Scatter(
            x=list(inf_192['time']),
            y=list(inf_192['ping_192']),
            mode='markers',
            marker=dict(color = '#3A0CF2', size = 5),
            name='192_不可达'
        ))


        self.graph_ping.update_layout(
            title={
                'text': 'Ping(ms)',  # Set the title text
                'font': {
                    'size': 24,  # Set the font size
                    'family': 'Arial, sans-serif',  # Set the font family
                    'color': 'RebeccaPurple'  # Set the font color
                },
                'x': 0.5,  # Set the x position (0 = left, 1 = right, 0.5 = center)
                'xanchor': 'center',  # Anchor the title to the center
                'y': 0.95,  # Set the y position (0 = bottom, 1 = top)
                'yanchor': 'top'  # Anchor the title to the top
            },
            height=600
        )
        self.download.update_layout(
            title={
                'text': 'Download(Mb/s)',  # Set the title text
                'font': {
                    'size': 24,  # Set the font size
                    'family': 'Arial, sans-serif',  # Set the font family
                    'color': 'RebeccaPurple'  # Set the font color
                },
                'x': 0.5,  # Set the x position (0 = left, 1 = right, 0.5 = center)
                'xanchor': 'center',  # Anchor the title to the center
                'y': 0.95,  # Set the y position (0 = bottom, 1 = top)
                'yanchor': 'top'  # Anchor the title to the top
            },
            height=600
        )

        self.upload.update_layout(
            title={
                'text': 'Upload(Mb/s)',  # Set the title text
                'font': {
                    'size': 24,  # Set the font size
                    'family': 'Arial, sans-serif',  # Set the font family
                    'color': 'RebeccaPurple'  # Set the font color
                },
                'x': 0.5,  # Set the x position (0 = left, 1 = right, 0.5 = center)
                'xanchor': 'center',  # Anchor the title to the center
                'y': 0.95,  # Set the y position (0 = bottom, 1 = top)
                'yanchor': 'top'  # Anchor the title to the top
            },
            height=600
        )


        #stats
        self.stats192 = summarize(data, "ping_192")
        self.statswww = summarize(data, "ping_www")

class DataStuck:
    def __init__(self, data: pd.DataFrame):
        self.data = data 
        self.year = str(datetime.datetime.now().year)
        
    def get_range(self, start : str, end: str):
        if len(self.data) == 0:
            return pd.DataFrame()
        data =  self.data[(self.data['start'] >= start) & (self.data['end'] <= end)]
        return data

# Function to list folders in the fixed path
def get_folders(path):
    if os.path.isdir(path):
        # List all folders in the given path
        folders = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
        return [{'label': folder, 'value': os.path.join(path, folder)} for folder in folders]
    return []





PATH = r"./log/live"
empty_ping = pd.DataFrame({
    'time': ['01-01 11:45:15'],
    'ping_www': [0],
    'ping_192': [0],
    'rsrp': [0],
    'rsrq': [0],
    'sinr': [0],
    'band': [0],
    'pci' : [0],
    'ber': [0],
    'up': [0],
    'down': [0],
    'neighbor': [0],
})
data_ping = DataPing(empty_ping)
data_stuck = DataStuck(pd.DataFrame({'start': [], 'end': [], 'duration': []}))

app = Dash(__name__, title = "ping数据整理")



# Layout of the app
app.layout = html.Div([
    dcc.Dropdown(
        id='folders-dropdown',
        options=get_folders(PATH),  # Populate with folders from the fixed path
        value=None,
        placeholder="Select a folder",
        style={'fontSize': '18px', 'marginBottom': '20px'}  # Add margin bottom
    ),
    html.Button(
        'Select Folder',
        id='select-folder-button', 
        n_clicks=0,
        style={'fontSize': '18px', 'padding': '10px 20px', 'marginBottom': '30px'}  
    ),# Add margin bottom
    html.Hr(),
    html.Div([
        html.Div([
            html.H1(
                "显示起点",
            ),
            dcc.Slider(
                0, 1,
                step=1e-6,
                marks=None,
                value=0,
                id='start-from-raw',
            )
        ], style={'width': '30%', 'display': 'inline-block'}),
        html.Div([
            html.H1("显示范围"),
            dcc.Slider(0, 1,
                step=1e-6,
                marks=None,
                value=0.2,
                id='range-raw',
            ),
        ], style={'width': '30%', 'display': 'inline-block'}),
        html.Div([
            html.H1("筛选同时测试设备数量"),
            dcc.Input(
            id='device-num', 
            type='number', 
            min=0, 
            value=0, 
        ),
        ], style={'width': '20%', 'display': 'inline-block'}),
    ]),
    html.Button(
        'Confirm', 
        id='range-button', 
        n_clicks=0, 
        style={
            'fontSize': '20px', 
            'padding': '10px 20px',  # Increase padding for a bigger button
            'marginBottom': '20px'  # Add margin bottom for spacing
        }
    ),
    

    html.H1(id='range-display'),

    dcc.Graph(id='pings'),
    dcc.Graph(id='ups'),
    dcc.Graph(id='downs'),

    dcc.Store(id='visibility-store', data={'ping_www': True, 'ping_192': True, 'www_network_unreachable': True, 'network_192_unreachable': True}),


    html.Div([
        html.H1("192断网次数高延迟", id="192c", style={'marginBottom': '20px'}),  
    ], style={'width': '50%', 'display': 'inline-block'}),


    html.Div([
        html.H1("www断网次数高延迟", id="wwwc", style={'marginBottom': '20px'}),  
    ], style={'width': '50%', 'display': 'inline-block'}),
    html.Hr(),

    html.Table([
        html.Thead([
            html.Tr([
                html.Th(""),
                html.Th("网关"),
                html.Th("外网")
            ])
        ]),
        html.Tbody([
            html.Tr([
                html.Td("平均值(ms)"),
                html.Td(data_ping.stats192[0]),
                html.Td(data_ping.statswww[0])
            ]),
            html.Tr([
                html.Td("最大值(ms)"),
                html.Td(data_ping.stats192[1]),
                html.Td(data_ping.statswww[1])
            ]),
            html.Tr([
                html.Td("最小值(ms)"),
                html.Td(data_ping.stats192[2]),
                html.Td(data_ping.statswww[2])
            ]),
            html.Tr([
                html.Td("平均差(ms)"),
                html.Td(data_ping.stats192[3]),
                html.Td(data_ping.statswww[3])
            ])
        ])
    ],style = {
        'width': '50%',
        'border': '1px solid black',
        'borderCollapse': 'collapse',
        'textAlign': 'center',
        'fontSize': '20px',
        'marginTop': '40px',
        'margin' : '0 auto'
    },
    id = "table"),

    html.Div([
        html.H4("卡顿局部图", style= {'fontSize': '20px'}),
        dcc.Graph(id='sub-graph-pings'),  # Placeholder for your graph
        dcc.Graph(id='sub-graph-ups'),  # Placeholder for your graph
        dcc.Graph(id='sub-graph-downs'),  # Placeholder for your graph
    ], style={'width': '77%', 'display': 'inline-block', 'vertical-align': 'top'}),

    html.Div([
        html.H1("直播卡顿",
            # style={'marginTop': '5em'}  
            ),
        dash_table.DataTable(
            id='stuck-table',
            data=data_stuck.data.to_dict('records'),
            columns=[{"name": i, "id": i} for i in data_stuck.data.columns],
            filter_action='native',
            
        ),
    ], style={'width': '23%', 'display': 'inline-block', 'vertical-align': 'top'})
], style={'textAlign': 'center', 'font-size': '10px', 'marginTop': '50px', 'marginBottom': '20px'})



@app.callback(
    Output('start-from-raw', 'value'),
    Output('range-raw', 'value'), 
    Output('device-num', 'value'),
    Output('folders-dropdown', 'options'),
    Output('range-button', 'n_clicks'),
    Input('select-folder-button', 'n_clicks'),

    State('folders-dropdown', 'value'),
    prevent_initial_call=True,
)
def select_folder(n_clicks, selected_folder):
    global data_stuck, data_ping
    if n_clicks > 0 and selected_folder:
        data_ping = DataPing(pd.read_csv(f'{selected_folder}/ping.csv'))
        if os.path.exists(f'{selected_folder}/stuck.csv'):
            data_stuck = DataStuck(pd.read_csv(f'{selected_folder}/stuck.csv'))
        
    return 0, 0.2, 0, get_folders(PATH), 1



# Callback to update the output based on the selected datetime
@app.callback(
    Output('range-display', 'children'),
    Output('pings', 'figure'),
    Output('ups', 'figure'),
    Output('downs', 'figure'),
    Output('stuck-table', 'data'),
    Output("192c", "children"),
    Output("wwwc", "children"),
    Output('table', 'children'),

    Input('range-button', 'n_clicks'),

    State('range-raw', 'value'), 
    State('start-from-raw', 'value'),
    State('device-num', 'value'),
    State('visibility-store', 'data'),

    prevent_initial_call=True,
)
#getting the new range for updating the graph(two bars), positional arguments, same order with call back
def update_range(n_clicks, range_raw, start_raw, device_num, visibility_data):
    global data_stuck, data_ping

    data_ping.display_range = max(1, math.ceil(range_raw**2 * data_ping.raw_len))   
    data_ping.display_start = math.ceil(start_raw * (data_ping.raw_len - data_ping.display_range))
    data_ping.devices = device_num

    #parameter: mode(which graph)
    data_ping.gen_graph()

    for trace in data_ping.graph_ping['data']:
        if trace['name'] == 'ping_www':
            trace['visible'] = visibility_data.get('ping_www', True)
        elif trace['name'] == 'ping_192':
            trace['visible'] = visibility_data.get('ping_192', True)
        elif trace['name'] == 'www_不可达':
            trace['visible'] = visibility_data.get('www_不可达', True)
        elif trace['name'] == '192_不可达':
            trace['visible'] = visibility_data.get('192_不可达', True)
        elif trace['name'] == 'upload':
            trace['visible'] = visibility_data.get('upload', True)
        elif trace['name'] == 'download':
            trace['visible'] = visibility_data.get('download', True)
        elif trace['name'] == 'sinr':
            trace['visible'] = visibility_data.get('sinr', True)
        elif trace['name'] == 'rsrp':
            trace['visible'] = visibility_data.get('rsrp', True)
        elif trace['name'] == 'rsrq':
            trace['visible'] = visibility_data.get('rsrq', True)
        elif trace['name'] == 'ber':
            trace['visible'] = visibility_data.get('ber', True)
        

    start_time = data_ping.data['time'][data_ping.display_start]
    end_time = data_ping.data['time'][data_ping.display_start+data_ping.display_range - 1]

    stuck = data_stuck.get_range(start_time,end_time)

    start_time_obj = datetime.datetime.strptime(start_time, "%m-%d %H:%M:%S")
    end_time_obj = datetime.datetime.strptime(end_time, "%m-%d %H:%M:%S")
    total_minutes = (end_time_obj - start_time_obj).total_seconds()/60
    per_minute = lambda n : round( n / total_minutes,2)

    head = [
        html.Thead([
            html.Tr([
                html.Th(""),
                html.Th("网关"),
                html.Th("外网")
                ])
            ]   
        )
    ]
    body = [
        html.Tbody([
            html.Tr([
                html.Td("平均值(ms)"),
                html.Td(data_ping.stats192[0]),
                html.Td(data_ping.statswww[0])
            ]),
            html.Tr([
                html.Td("最大值(ms)"),
                html.Td(data_ping.stats192[1]),
                html.Td(data_ping.statswww[1])
            ]),
            html.Tr([
                html.Td("最小值(ms)"),
                html.Td(data_ping.stats192[2]),
                html.Td(data_ping.statswww[2])
            ]),
            html.Tr([
                html.Td("平均差(ms)"),
                html.Td(data_ping.stats192[3]),
                html.Td(data_ping.statswww[3])
            ])
        ])
    ]

    return (f"显示范围: {start_time} - {end_time}", 
            
            data_ping.graph_ping, data_ping.upload, data_ping.download, stuck.to_dict('records'),

            "到网关(192)"\
            f"断连{per_minute(data_ping.inf192_cnt)}次/分钟,      "
            f"高延迟{per_minute(data_ping.lag192_cnt)}次/分钟 ",
            
             f"到外网(www)\n"
            f"断连 {per_minute(data_ping.infwww_cnt)} 次/分钟,    "
            f"高延迟 {per_minute(data_ping.lagwww_cnt)} 次/分钟",

            head + body
            )

@app.callback(
    Output('visibility-store', 'data'),
    Input('pings', 'restyleData'),
    State('pings', 'figure'),  # Get the figure object to access trace names
    State('visibility-store', 'data'),
    prevent_initial_call=True
)
def update_visibility(restyleData, figure, visibility_data):
    if restyleData:
        # Loop through the trace indices (second item in restyleData)
        for trace in restyleData[1]:
            # Get the trace name from the figure using the trace index
            trace_name = figure['data'][trace].get('name', f'Trace {trace}')
            
            # Since restyleData[0]['visible'] applies to all traces in restyleData[1],
            # we use the first (and only) visibility value
            visibility = restyleData[0]['visible'][0]
            
            # Update the visibility data using the trace name
            visibility_data[trace_name] = visibility

    return visibility_data



#second graph's callback
@app.callback(
    Output("sub-graph-pings", "figure"),
    Output('sub-graph-ups', 'figure'),
    Output('sub-graph-downs', 'figure'),
    Input('stuck-table', 'active_cell'),
    State('stuck-table', 'derived_viewport_data')
)
def update_subgraph(active_cell, table):
    s = ""
    e = ""
    if active_cell is not None and active_cell['row'] < len(table):
        s = table[active_cell['row']]['start']
        e = table[active_cell['row']]['end']

        year = str(datetime.datetime.now().year)
        s = datetime.datetime.strptime(year+"-"+s, '%Y-%m-%d %H:%M:%S') - datetime.timedelta(seconds=10)
        e = datetime.datetime.strptime(year+"-"+e, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(seconds=10)
        
        s = s.strftime('%m-%d %H:%M:%S')
        e = e.strftime('%m-%d %H:%M:%S')

    data_ping.gen_graph(s, e)
    return data_ping.graph_ping,data_ping.upload,data_ping.download


# Function to open the browser automatically
def open_browser():
    webbrowser.open_new("http://127.0.0.1:8050/")

def main():
    app.run_server(debug = False)

if __name__ == "__main__":
    app.run_server(debug = True)
