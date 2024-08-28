import pandas as pd
from dash import Dash, dcc, html, dash_table, Input, Output, State 
import math
import numpy as np
import plotly.graph_objs as go
import datetime
from stable import summary
import bisect

#storing data for updating graphs
class DataPing:
    def __init__(self, data: pd.DataFrame):
        self.data = data                             #all data
        self.display_start = 0
        self.display_range = len(self.data)
        self.graph_ping = None                       #the main graph
        self.graph_ping2 = None                      #the detail graph
        self.raw_len = len(self.data)

        self.infwww = 0     #how many times www disconnection
        self.inf192 = 0     #how many times 192 disconnection

        #stats contains mean, max, min, std
        self.stats192 = [0, 0, 0, 0]
        self.statswww = [0, 0, 0, 0]
        #lags
        self.lag192 = 0
        self.lagwww = 0

        #all xy of dots on graphs
        self.inf_indices_www = []
        self.inf_values_www = []
        self.inf_indices_192 = []
        self.inf_values_192 = []

    def construct_data(self):
        # 标记 inf 值# 获取所有 inf 的索引
        #wws
        temp = 0
        for row in self.data.iterrows():
            if np.isinf(row[1]['ip_www']):
                self.inf_indices_www.append(row[1]['time'])
                self.inf_values_www.append(temp)
                self.infwww += 1
            else:
                temp= row[1]['ip_www']
                if row[1]["ip_www"] >= 100:
                    self.lagwww += 1
        #192s
        temp = 0
        for row in self.data.iterrows():
            if np.isinf(row[1]['ip_192']):
                self.inf_indices_192.append(row[1]['time'])
                self.inf_values_192.append(temp)
                self.inf192 += 1
            else:
                temp= row[1]['ip_192']
                if row[1]["ip_192"] >= 100:
                    self.lag192 += 1

    #update everytimes the state changes, works for both graph, 
    # 1 is the main graph, 2 is the sub graph

    def update_graph(self, which_graph, s = "", e = ""):
        if which_graph == 1:
            self.graph_ping = go.Figure()
            graph = self.graph_ping
        elif which_graph == 2:
            self.graph_ping2 = go.Figure()
            graph = self.graph_ping2

        if not s:
            start_time = data_ping.data['time'][data_ping.display_start]
            end_time = data_ping.data['time'][data_ping.display_start+data_ping.display_range - 1]
            data  = self.data[self.display_start:self.display_start+self.display_range]
        else:
            start_time = s
            end_time = e
            index1 = self.data[self.data['time'] == start_time].index[0]
            index2 = self.data[self.data['time'] == end_time].index[0]
            data = self.data[index1 : index2]

        # Locate the indices
        start_www = bisect.bisect_right(self.inf_indices_www, start_time)
        end_www = bisect.bisect_right(self.inf_indices_www, end_time)

        start_192 = bisect.bisect_right(self.inf_indices_192, start_time)
        end_192 = bisect.bisect_right(self.inf_indices_192, end_time)

        #cut the graph in the range we need
        inf_indices_www = self.inf_indices_www[start_www : end_www]
        inf_values_www = self.inf_values_www[start_www : end_www]
        inf_indices_192 = self.inf_indices_192[start_192 : end_192]
        inf_values_192 = self.inf_values_192[start_192 : end_192]
        
        hovertext = [f"Band: {row['band']}<br>SINR: {row['sinr']}<br>RSRP: {row['rsrp']}" 
        for index, row in data.iterrows()]

        #drawing lines
        graph.add_trace(go.Scatter(
            x=data['time'],
            y=data['ip_www'],
            mode='lines',
            name='ip_www',
            marker=dict(color='#22aaff'),
            hovertext = hovertext,
        ))
        graph.add_trace(go.Scatter(
            x=data['time'],
            y=data['ip_192'],
            mode='lines',
            name='ip_192',
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
        self.stats192 = summary.summarize(data, "ip_192")
        self.statswww = summary.summarize(data, "ip_www")

        return graph
        
        

class DataStuck:
    def __init__(self, data: pd.DataFrame):
        self.data = data 
        self.year = str(datetime.datetime.now().year)
        
    def get_range(self, start, end):
        data =  self.data[(self.data['start'] >= start) & (self.data['end'] <= end)]
        return data


# path = sys.argv[1]
path = r"D:\fly\speedtest\log\2024-08-27_17-53"
data_ping = DataPing(pd.read_csv(f'{path}/ping.csv'))
data_stuck = DataStuck(pd.read_csv(f'{path}/stuck.csv'))
data_ping.construct_data()

app = Dash(__name__)

# Layout of the app
app.layout = html.Div([
    html.H1(f"192断网次数:            {data_ping.inf192},     高延迟： {data_ping.lag192}", id = "192c"),
    html.H1(f"www断网次数:            {data_ping.infwww}      高延迟： {data_ping.lagwww}", id = "wwwc"),
    html.H1("192:"),
    # mean, max, low, std
    html.H1(
        f"  平均值: {data_ping.stats192[0]}   "
        f"  最大值: {data_ping.stats192[1]}   "
        f"  最小值: {data_ping.stats192[2]}   "
        f"  平均差: {data_ping.stats192[3]}   ",
        id="stats192",
        style={'whiteSpace': 'pre-line'}
    ),
    html.H1("www:"),
    html.H1(
        f"  平均值: {data_ping.statswww[0]}"
        f"  最大值: {data_ping.statswww[1]}"
        f"  最小值: {data_ping.statswww[2]}"
        f"  平均差: {data_ping.statswww[3]}",
        id="statswww",
        style={'whiteSpace': 'pre-line'}
    ),
    html.H1("显示起点"),
    dcc.Slider(0, 1,
        step=1e-6,
        marks=None,
        value=0,
        id='start-from-raw',
    ),
    html.H1("显示范围"),
    dcc.Slider(0, 1,
        step=1e-6,
        marks=None,
        value=0.2,
        id='range-raw',
    ),
    
    html.H1(id='range-display'),
    dcc.Graph(id='pings'),
    html.H1("直播卡顿"),
    html.Div([
        dcc.Graph(id='range_graph'),  # Placeholder for your graph
    ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}),

    html.Div([
        dash_table.DataTable(
            id='stuck-table',
            data=data_stuck.data.to_dict('records'),
            columns=[{"name": i, "id": i} for i in data_stuck.data.columns],
            filter_action='native',
        ),
    ], style={'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'})
], style={'textAlign': 'center', 'font-size': '10px', 'marginTop': '50px', 'marginBottom': '20px'})


# Callback to update the output based on the selected datetime
@app.callback(
    Output('range-display', 'children'),
    Output('pings', 'figure'),
    Output('stuck-table', 'data'),
    Output("192c", "children"),
    Output("wwwc", "children"),
    Output("stats192", "children"),
    Output("statswww", "children"),
    Input('range-raw', 'value'), 
    Input('start-from-raw', 'value'),
    Input('stuck-table', 'active_cell'),
    # 获取筛选后的数据 ??? stupid things!!!
    State('stuck-table', 'derived_viewport_data')
)
#getting the new range for updating the graph(two bars)
def update_range(range_raw, start_raw, active_cell, table):
    global data_ping, data_stuck

    if range_raw is not None:
        if start_raw is None:
            start_raw = data_ping.display_start / data_ping.raw_len
        # 指数缩放
        data_ping.display_range = max(1, math.ceil(range_raw**2 * data_ping.raw_len))
    
    if start_raw is not None:
        data_ping.display_start = math.ceil(start_raw * (data_ping.raw_len - data_ping.display_range))

    #parameter: mode(which graph)
    data_ping.update_graph(1)
    start_time = data_ping.data['time'][data_ping.display_start]
    end_time = data_ping.data['time'][data_ping.display_start+data_ping.display_range - 1]

    stuck = data_stuck.get_range(start_time,end_time)


    return (f"显示范围: {start_time} - {end_time}", 
            data_ping.graph_ping, stuck.to_dict('records'),
            f"192断网次数:            {data_ping.inf192},     高延迟： {data_ping.lag192}",
            f"www断网次数:            {data_ping.infwww}      高延迟： {data_ping.lagwww}",  
            f"  平均值: {data_ping.stats192[0]}   "
            f"  最大值: {data_ping.stats192[1]}   "
            f"  最小值: {data_ping.stats192[2]}   "
            f"  平均差: {data_ping.stats192[3]}   ",
            f"  平均值: {data_ping.statswww[0]}"
            f"  最大值: {data_ping.statswww[1]}"
            f"  最小值: {data_ping.statswww[2]}"
            f"  平均差: {data_ping.statswww[3]}"
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

    data_ping.update_graph(2, s, e)

    return (data_ping.graph_ping2)


if __name__ == '__main__':
    app.run_server(debug=True)
