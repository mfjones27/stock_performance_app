import dash

from dash import dcc, html, Dash
from flask_cors import CORS
from utils.get_data import *
from utils.graphing import *
from flask import Flask, session, request, redirect, render_template, url_for, jsonify

app = Flask(__name__)
app.secret_key = 'supersecretkey'
CORS(app)

primary_dash_app = Dash(
    __name__,
    server=app,
    url_base_pathname='/dash/primary/'
)

# Comparison Dash app
comparison_dash_app = Dash(
    __name__,
    server=app,
    url_base_pathname='/dash/comparison/'
)

# Initial layout for the primary graph
primary_dash_app.layout = html.Div(id='primary-graph-container', children=[])

# Initial layout for the comparison graph
comparison_dash_app.layout = html.Div(id='comparison-graph-container', children=[])

@app.route('/')
def home():
    return render_template('home.html', stock_data=None)

@app.route('/get_stock_data', methods=['POST'])
def get_stock_data():
    data = request.get_json()
    # Store data in the session
    session['ticker'] = data['mainTicker']
    session['chart_type'] = data['chartType']
    session['compare'] = data['compare']
    session['comparison_ticker'] = data['comparisonTicker'] if data['compare'] else None
    session['date_range'] = data['range']
    
    # Redirect to display_stock_data route
    return redirect(url_for('display_stock_data', ticker=session['ticker']))

@app.route('/confirm_ticker', methods=['POST'])
def confirm_ticker():
    valid = verify_ticker(request.get_json().get('ticker'))
    return jsonify({'validity': valid})

@app.route('/stock/<ticker>')
def display_stock_data(ticker):
    chart_type = session.get('chart_type')
    compare = session.get('compare')
    comparison_ticker = session.get('comparison_ticker')
    date_range = session.get('date_range')

    print(chart_type, compare, comparison_ticker, date_range)
    # Create primary graph
    primary_fig = create_ohlc_graph(ticker, date_range, chart_type)
    primary_dash_app.layout = html.Div([
        dcc.Graph(figure=primary_fig)  # Primary graph
    ])

    # Create comparison graph if applicable
    if compare and comparison_ticker:
        comparison_fig = create_ohlc_graph(comparison_ticker, date_range, chart_type)
        comparison_dash_app.layout = html.Div([
            dcc.Graph(figure=comparison_fig)  # Comparison graph
        ])

    # Fetch stock data for rendering in Jinja
    stock_data = fetch_stock_data(ticker)
    comp_stock_data = fetch_stock_data(comparison_ticker) if compare and comparison_ticker else None
    
    return render_template('data.html', stock_data=stock_data, comp_stock_data=comp_stock_data)

if __name__ == '__main__':
    app.run(debug=True)