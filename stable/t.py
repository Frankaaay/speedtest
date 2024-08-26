import dash
from dash import html

app = dash.Dash(__name__)

# Read your HTML file
with open('stable\s.html', 'r') as file:
    html_content = file.read()

# Define the layout of the app
app.layout = html.Div([html.Iframe(srcDoc=html_content, style={'width': '100%', 'height': '100vh'})])

if __name__ == '__main__':
    app.run_server(debug=True)
