import pandas as pd
from dash import Dash, dcc, html, dash_table, Input, Output, State 
import math
import numpy as np
import plotly.graph_objs as go
import sys
import datetime
from stable import summary

class DataPing:
    def __init__(self, data: pd.DataFrame):
        # data['time']=pd.to_datetime(data['time'], format='%m-%d %H:%M:%S')
        self.data = data
        self.display_start = 0
        self.display_range = len(self.data)
        self.graph_ping = None
        self.raw_len = len(self.data)
        self.infwww = 0
        self.inf192 = 0
        self.stats192 = [0, 0, 0, 0]
        self.statswww = [0, 0, 0, 0]
        self.lag192 = 0
        self.lagwww = 0

    def update_graph(self, highlights):
        self.graph_ping = go.Figure()

        data  = self.data[self.display_start:self.display_start+self.display_range]
        
        self.graph_ping.add_trace(go.Scatter(
            x=data['time'],
            y=data['pingwww'],
            mode='lines',
            name='pingwww',
            marker=dict(color='#22aaff'),
        ))
        self.graph_ping.add_trace(go.Scatter(
            x=data['time'],
            y=data['ping192'],
            mode='lines',
            name='ping192',
            marker=dict(color='#8888ff'),
        ))

        # 标记 inf 值# 获取所有 inf 的索引
        inf_indices_www = []
        inf_values_www = []
        temp = 0
        for row in data.iterrows():
            if np.isinf(row[1]['pingwww']):
                inf_indices_www.append(row[1]['time'])
                inf_values_www.append(temp)
                self.infwww += 1
            else:
                temp= row[1]['pingwww']
                if row[1]["pingwww"] >= 100:
                    self.lagwww += 1
                    
                
        inf_indices_192 = []
        inf_values_192 = []
        temp = 0
        for row in data.iterrows():
            if np.isinf(row[1]['ping192']):
                inf_indices_192.append(row[1]['time'])
                inf_values_192.append(temp)
                self.inf192 += 1
            else:
                temp= row[1]['ping192']
                if row[1]["ping192"] >= 100:
                    self.lag192 += 1

        self.graph_ping.add_trace(go.Scatter(
            x=inf_indices_www,
            y=inf_values_www,
            mode='markers',
            marker=dict(color='#ff0000', size=15),
            name='www网络不可达'
        ))

        self.graph_ping.add_trace(go.Scatter(
            x=inf_indices_192,
            y=inf_values_192,
            mode='markers',
            marker=dict(color='#ff0000', size=15),
            name='192网络不可达'
        ))

        for highlight in highlights:
            self.graph_ping.add_vrect(
                x0=highlight[0],
                x1=highlight[1],
                fillcolor="LightSalmon",
                opacity=0.5,
                line_width=0
            )

        self.stats192 = summary.summarize(data, "ping192")
        self.statswww = summary.summarize(data, "pingwww")
        

class DataStuck:
    def __init__(self, data: pd.DataFrame):
        # data['start']=pd.to_datetime(data['start'], format='%m-%d %H:%M:%S')
        # data['end']=pd.to_datetime(data['end'], format='%m-%d %H:%M:%S')
        self.data = data 
        self.year = str(datetime.datetime.now().year)
        
    def get_range(self, start, end):
        data =  self.data[(self.data['start'] >= start) & (self.data['end'] <= end)]
        # data['start']=pd.to_datetime(self.year+"-"+data['start'], format='%Y-%m-%d %H:%M:%S')
        # data['end']=pd.to_datetime(self.year+"-"+data['end'], format='%Y-%m-%d %H:%M:%S')
        return data


# path = sys.argv[1]
path = r"D:\fly\speedtest\log\08-24_18-13"
data_ping = DataPing(pd.read_csv(f'{path}/ping.csv'))
data_stuck = DataStuck(pd.read_csv(f'{path}/stuck.csv'))

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
        # updatemode='drag',
    ),
    html.H1("显示范围"),
    dcc.Slider(0, 1,
        step=1e-6,
        marks=None,
        value=0.2,
        id='range-raw',
        # updatemode='drag',
    ),

    
    html.H1(id='range-display'),
    dcc.Graph(id='pings'),
    html.H1("直播卡顿"),
    dash_table.DataTable(
        id='stuck-table',
        data=data_stuck.data.to_dict('records'),
        columns=[{"name": i, "id": i} for i in data_stuck.data.columns],
        filter_action='native',
    ),
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
def update_range(range_raw, start_raw, active_cell, table):
    global data_ping, data_stuck

    if range_raw is not None:
        if start_raw is None:
            start_raw = data_ping.display_start / data_ping.raw_len
        # 指数缩放
        data_ping.display_range = math.ceil(range_raw**2 * data_ping.raw_len)
    
    if start_raw is not None:
        data_ping.display_start = math.ceil(start_raw * (data_ping.raw_len - data_ping.display_range))

    highlights = []
    if active_cell is not None and active_cell['row'] < len(table):
        s = table[active_cell['row']]['start']
        e = table[active_cell['row']]['end']
        highlights = [(s,e)]

    data_ping.update_graph(highlights)
    start_time = data_ping.data['time'][data_ping.display_start]
    end_time = data_ping.data['time'][data_ping.display_start+data_ping.display_range-1]

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
            
            


if __name__ == '__main__':
    app.run_server(debug=True)
