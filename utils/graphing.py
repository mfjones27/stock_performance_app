import plotly.graph_objs as go
from utils.get_data import get_ohlc_data  # Import your data-fetching function

def create_ohlc_graph(ticker, date_range, chart_type):
    # Fetch the OHLC data using your existing function
    ohlc_data = get_ohlc_data(ticker, date_range)
    print(ohlc_data)

    if chart_type == 'candlestick':
        fig = go.Figure(data=[go.Candlestick(x=ohlc_data.index,
                                              open=ohlc_data['Open'],
                                              high=ohlc_data['High'],
                                              low=ohlc_data['Low'],
                                              close=ohlc_data['Close'])])
        fig.update_layout(xaxis_rangeslider_visible=False)
    else:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ohlc_data.index, y=ohlc_data['Close'], mode='lines', name='Close Price'))


    # Customize layout if needed
    fig.update_layout(
        title=f'{ticker.upper()} OHLC Data',
        xaxis_title='Date',
        yaxis_title='Price',
        template='plotly_dark'  # Optional theme
    )

    return fig