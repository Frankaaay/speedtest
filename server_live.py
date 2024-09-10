import pandas as pd
from dash import Dash, dcc, html, dash_table, Input, Output, State
import math
import numpy as np
import plotly.graph_objs as go
import datetime
import bisect
import os
import webbrowser


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
        self.data = data                             #all data
        self.display_start = 0
        self.display_range = len(self.data)
        self.graph_ping = None                       #the main graph
        self.graph_ping_detail = None                      #the detail graph
        self.raw_len = len(self.data)

        self.infwww_cnt = 0     # how many times www disconnection
        self.inf192_cnt = 0     # in the given range
        self.lag192_cnt = 0     #
        self.lagwww_cnt = 0     #

        #stats contains mean, max, min, std
        self.stats192 = [0, 0, 0, 0]
        self.statswww = [0, 0, 0, 0]


        #all xy of dots on graphs
        self.inf_indices_www = []
        self.lag_indices_www = []
        self.inf_values_www = []
        self.inf_indices_192 = []
        self.lag_indices_192 = []
        self.inf_values_192 = []

    def construct_data(self):
        # 标记 inf 值
        # 获取所有 inf 的索引
        #wwws
        temp = 0
        for row in self.data.iterrows():
            if np.isinf(row[1]['ping_www']):
                self.inf_indices_www.append(row[1]['time'])
                self.inf_values_www.append(temp)
                # self.infwww_cnt += 1
            else:
                temp= row[1]['ping_www']
                if row[1]["ping_www"] >= 100:
                    self.lag_indices_www.append(row[1]['time'])
                    # self.lagwww_cnt += 1
        #192s
        temp = 0
        for row in self.data.iterrows():
            if np.isinf(row[1]['ping_192']):
                self.inf_indices_192.append(row[1]['time'])
                self.inf_values_192.append(temp)
                # self.inf192_cnt += 1
            else:
                temp= row[1]['ping_192']
                if row[1]["ping_192"] >= 20:
                    self.lag_indices_192.append(row[1]['time'])
                    # self.lag192_cnt += 1

    #update everytimes the state changes, works for both graph, 
    # 1 is the main graph, 2 is the sub graph

    def gen_graph(self, s = "", e = ""):
        graph =  go.Figure()

        if not s:
            start_time = self.data['time'][self.display_start]
            end_time = self.data['time'][self.display_start+self.display_range - 1]
            data  = self.data[self.display_start:self.display_start+self.display_range]
        else:
            start_time = s
            end_time = e
            index1 = self.data[self.data['time'] < start_time].index[-1]
            index2 = self.data[self.data['time'] > end_time].index[1]
            data = self.data[index1 : index2]

        # Locate the indices
        start_www = bisect.bisect_right(self.inf_indices_www, start_time)
        end_www = bisect.bisect_right(self.inf_indices_www, end_time)
        self.infwww_cnt = end_www - start_www

        start_192 = bisect.bisect_right(self.inf_indices_192, start_time)
        end_192 = bisect.bisect_right(self.inf_indices_192, end_time)
        self.inf192_cnt = end_192 - start_192

        #cut the graph in the range we need
        inf_indices_www = self.inf_indices_www[start_www : end_www]
        inf_values_www = self.inf_values_www[start_www : end_www]
        inf_indices_192 = self.inf_indices_192[start_192 : end_192]
        inf_values_192 = self.inf_values_192[start_192 : end_192]

        self.lagwww_cnt = bisect.bisect_right(self.lag_indices_www, end_time) - bisect.bisect_right(self.lag_indices_www, start_time)
        self.lag192_cnt = bisect.bisect_right(self.lag_indices_192, end_time) - bisect.bisect_right(self.lag_indices_192, start_time)
        
        hovertext = [f"Band: {row['band']}<br>SINR: {row['sinr']}<br>RSRP: {row['rsrp']}" 
        for index, row in data.iterrows()]

        #drawing lines
        graph.add_trace(go.Scatter(
            x=data['time'],
            y=data['ping_www'],
            mode='lines',
            name='ping_www',
            marker=dict(color='#22aaff'),
            hovertext = hovertext,
        ))
        graph.add_trace(go.Scatter(
            x=data['time'],
            y=data['ping_192'],
            mode='lines',
            name='ping_192',
            marker=dict(color='#8888ff'),
            hovertext = hovertext
        ))

        #drawing disconnection dots
        graph.add_trace(go.Scatter(
            x=inf_indices_www,
            y=inf_values_www,
            mode='markers',
            marker=dict(color='#ff0000', size=5),
            name='www网络不可达'
        ))

        graph.add_trace(go.Scatter(
            x=inf_indices_192,
            y=inf_values_192,
            mode='markers',
            marker=dict(color='#5aff54', size=5),
            name='192网络不可达'
        ))

        #stats
        self.stats192 = summarize(data, "ping_192")
        self.statswww = summarize(data, "ping_www")

        return graph
        




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







path = r"./log/live"
empty_ping = {
    'time': [0],
    'ping_www': [0],
    'ping_192': [0],
    'rsrp': [0],
    'sinr': [0],
    'band': [0],
    'pci' : [0],
    }
data_ping = DataPing(pd.DataFrame(empty_ping))
data_stuck = DataStuck(pd.DataFrame({'start': [], 'end': [], 'duration': []}))

app = Dash(__name__, title = "ping数据整理")



# Layout of the app
app.layout = html.Div([
    dcc.Dropdown(
        id='folders-dropdown',
        options=get_folders(path),  # Populate with folders from the fixed path
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
    ]),
    

    html.H1(id='range-display'),

    # html.H1("ping线点图"),
    html.H1("ping图", style= {'fontSize': '20px'}),
    dcc.Graph(id='pings'),


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
        html.H4("放大ping图", style= {'fontSize': '20px'}),
        dcc.Graph(id='range_graph'),  # Placeholder for your graph
    ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}),

    html.Div([
        html.H1("直播卡顿",
            # style={'marginTop': '5em'}  
            ),
        dash_table.DataTable(
            id='stuck-table',
            data=data_stuck.data.to_dict('records'),
            columns=[{"name": i, "id": i} for i in data_stuck.data.columns],
            # filter_action='native',
            
        ),
    ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'})
], style={'textAlign': 'center', 'font-size': '10px', 'marginTop': '50px', 'marginBottom': '20px'})



@app.callback(
    Output('start-from-raw', 'value'),
    Output('range-raw', 'value'), 
    Input('select-folder-button', 'n_clicks'),

    State('folders-dropdown', 'value'),
    prevent_initial_call=True,
)
def select_folder(n_clicks, selected_folder):
    global data_stuck, data_ping
    # print(n_clicks)
    if n_clicks > 0 and selected_folder:
        data_ping = DataPing(pd.read_csv(f'{selected_folder}/ping.csv'))
        if os.path.exists(f'{selected_folder}/stuck.csv'):
            data_stuck = DataStuck(pd.read_csv(f'{selected_folder}/stuck.csv'))
        data_ping.construct_data()
    return 0, 0.2




# Callback to update the output based on the selected datetime
@app.callback(
    Output('range-display', 'children'),
    Output('pings', 'figure'),
    Output('stuck-table', 'data'),
    Output("192c", "children"),
    Output("wwwc", "children"),
    Output('table', 'children'),

    Input('range-raw', 'value'), 
    Input('start-from-raw', 'value'),
    prevent_initial_call=True,
)
#getting the new range for updating the graph(two bars), positional arguments, same order with call back
def update_range(range_raw, start_raw):
    global data_stuck, data_ping

    if range_raw is not None:
        if start_raw is None:
            start_raw = data_ping.display_start / data_ping.raw_len
        # 指数缩放
        data_ping.display_range = max(1, math.ceil(range_raw**2 * data_ping.raw_len))   
    
    if start_raw is not None:
        data_ping.display_start = math.ceil(start_raw * (data_ping.raw_len - data_ping.display_range))

    #parameter: mode(which graph)
    data_ping.graph_ping = data_ping.gen_graph()
    start_time = data_ping.data['time'][data_ping.display_start]
    end_time = data_ping.data['time'][data_ping.display_start+data_ping.display_range - 1]

    stuck = data_stuck.get_range(start_time,end_time)
    # print(start_time,end_time)
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
            
            data_ping.graph_ping, stuck.to_dict('records'),

            "到网关(192)"\
            f"断连{per_minute(data_ping.inf192_cnt)}次/分钟,      "
            f"高延迟{per_minute(data_ping.lag192_cnt)}次/分钟 ",
            
             f"到外网(www)\n"
            f"断连 {per_minute(data_ping.infwww_cnt)} 次/分钟,    "
            f"高延迟 {per_minute(data_ping.lagwww_cnt)} 次/分钟",

            head + body
            )


#second graph's callback
@app.callback(
    Output("range_graph", "figure"),
    Input('stuck-table', 'active_cell'),
    State('stuck-table', 'derived_viewport_data')
)
def update_subgraph(active_cell, table):
    s = ""
    e = ""
    if active_cell is not None and active_cell['row'] < len(table):
        s = table[active_cell['row']]['start']
        e = table[active_cell['row']]['end']
    data_ping.graph_ping_detail = data_ping.gen_graph(s, e)
    return data_ping.graph_ping_detail


# Function to open the browser automatically
def open_browser():
    webbrowser.open_new("http://127.0.0.1:8050/")

def main():
    app.run_server(debug = False)

