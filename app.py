import base64
from io import BytesIO
import matplotlib
matplotlib.use('Agg')

from flask import Flask, render_template, request
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter

def date_format(x, pos=None):
    return mdates.num2date(x).strftime('%Y-%m-%d')

from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def index():
    today = datetime.now().strftime('%Y-%m-%d')
    default_start_date = (datetime.now() - timedelta(days=20)).strftime('%Y-%m-%d')
    return render_template('index.html', today=today, default_start_date=default_start_date)

def render_plot_page(ticker, start_date=None, end_date=None, period=None, date_range=None):
    # Download the data for the plot and table, based on user's date range
    if period:
        plot_data = yf.download(ticker, period=period, auto_adjust=True, progress=False)
    else:
        plot_data = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True, progress=False)
    
    new_columns = []
    for col in plot_data.columns:
        if isinstance(col, tuple):
            new_columns.append(col[0].lower())
        else:
            new_columns.append(col.lower())
    plot_data.columns = new_columns

    if plot_data.empty:
        return render_template('error.html')

    plot_data = plot_data.sort_index(ascending=False)

    # Download 5 years of data for performance calculation
    perf_data = yf.download(ticker, period='5y', auto_adjust=True, progress=False)
    if not perf_data.empty:
        new_columns_perf = []
        for col in perf_data.columns:
            if isinstance(col, tuple):
                new_columns_perf.append(col[0].lower())
            else:
                new_columns_perf.append(col.lower())
        perf_data.columns = new_columns_perf

    # Calculate statistics from plot_data
    min_val = plot_data['close'].min()
    min_price = min_val.iloc[0] if isinstance(min_val, pd.Series) else min_val
    max_val = plot_data['close'].max()
    max_price = max_val.iloc[0] if isinstance(max_val, pd.Series) else max_val
    mean_val = plot_data['close'].mean()
    mean_price = mean_val.iloc[0] if isinstance(mean_val, pd.Series) else mean_val

    # Generate the plot from plot_data
    plot_data_df = plot_data.sort_index(ascending=True)
    num_dates = len(plot_data_df.index)
    plt.figure(figsize=(10, 6))

    plot_series = plot_data_df['close']
    if date_range in ['5y', 'MAX']:
        plot_series = plot_series.rolling(window=30).mean()

    marker = ''
    markersize = 0
    linewidth = 1.5 # A slightly thicker default for mid-range plots
    if num_dates < 20:
        marker = 'o'
        markersize = 5
        linewidth = 1 # Thinner line for plots with markers
    elif num_dates > 252:
        linewidth = 0.8 # Thinner line for long plots

    plt.plot(range(num_dates), plot_series, marker=marker, markersize=markersize, linewidth=linewidth)
    plt.title(f'{ticker} Stock Price')
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.grid(True)

    # Format the x-axis to show dates
    ax = plt.gca()
    if num_dates > 20:
        step = num_dates // 10
        ticks = range(0, num_dates, step)
        labels = [plot_data_df.index[i].strftime('%Y-%m-%d') for i in ticks]
        ax.set_xticks(ticks)
        ax.set_xticklabels(labels, rotation=90)
    else:
        ax.set_xticks(range(num_dates))
        ax.set_xticklabels([d.strftime('%Y-%m-%d') for d in plot_data_df.index], rotation=90)
    plt.tight_layout() # Adjust layout to prevent labels from being cut off


    # Save it to a temporary buffer.
    buf = BytesIO()
    plt.savefig(buf, format="png")
    # Embed the result in the html output.
    plot_data_url = base64.b64encode(buf.getbuffer()).decode("ascii")
    plot_url = f'data:image/png;base64,{plot_data_url}'


    formatters = {
        'open': '{:.2f}'.format,
        'high': '{:.2f}'.format,
        'low': '{:.2f}'.format,
        'close': '{:.2f}'.format,
        'volume': '{:,}'.format
    }

    table_data = plot_data
    if len(plot_data) > 20:
        table_data = plot_data.head(20)

    market_data = []
    indices = {'S&P 500': '^GSPC', 'DOW': '^DJI', 'NASDAQ': '^IXIC'}

    for name, ticker_symbol in indices.items():
        index_data = yf.download(ticker_symbol, period='5y', auto_adjust=True, progress=False)
        current = index_data['Close'].values[-1].item()
        ytd_start = index_data[index_data.index.year == index_data.index.year[-1]]['Close'].values[0].item()
        ytd = (current - ytd_start) / ytd_start * 100
        one_year = (current - index_data['Close'].values[-252].item()) / index_data['Close'].values[-252].item() * 100
        five_year = (current - index_data['Close'].values[0].item()) / index_data['Close'].values[0].item() * 100

        index_data_max = yf.download(ticker_symbol, period='max', auto_adjust=True, progress=False)
        max_perf = (index_data_max['Close'].values[-1].item() - index_data_max['Close'].values[0].item()) / index_data_max['Close'].values[0].item() * 100

        market_data.append({
            'name': name,
            'current': f'{current:,.2f}',
            'ytd': f'{ytd:.2f}%',
            'one_year': f'{one_year:.2f}%',
            'five_year': f'{five_year:.2f}%',
            'max': f'{max_perf:.2f}%'
        })

    # Calculate performance for the selected ticker from perf_data
    if not perf_data.empty:
        ticker_current = perf_data['close'].values[-1].item()

        ytd_data = perf_data[perf_data.index.year == perf_data.index.year[-1]]
        if not ytd_data.empty:
            ticker_ytd_start = ytd_data['close'].values[0].item()
            ticker_ytd = (ticker_current - ticker_ytd_start) / ticker_ytd_start * 100
        else:
            ticker_ytd = "N/A"

        if len(perf_data) >= 252:
            ticker_1y = (ticker_current - perf_data['close'].values[-252].item()) / perf_data['close'].values[-252].item() * 100
        else:
            ticker_1y = "N/A"

        if len(perf_data) > 0:
            ticker_5y = (ticker_current - perf_data['close'].values[0].item()) / perf_data['close'].values[0].item() * 100
        else:
            ticker_5y = "N/A"

        perf_data_max = yf.download(ticker, period='max', auto_adjust=True, progress=False)
        if not perf_data_max.empty:
            new_columns_perf_max = []
            for col in perf_data_max.columns:
                if isinstance(col, tuple):
                    new_columns_perf_max.append(col[0].lower())
                else:
                    new_columns_perf_max.append(col.lower())
            perf_data_max.columns = new_columns_perf_max
            
            max_perf = (perf_data_max['close'].values[-1].item() - perf_data_max['close'].values[0].item()) / perf_data_max['close'].values[0].item() * 100
        else:
            max_perf = "N/A"

        market_data.append({
            'name': ticker,
            'current': f'{ticker_current:,.2f}',
            'ytd': f'{ticker_ytd:.2f}%' if isinstance(ticker_ytd, (int, float)) else ticker_ytd,
            'one_year': f'{ticker_1y:.2f}%' if isinstance(ticker_1y, (int, float)) else ticker_1y,
            'five_year': f'{ticker_5y:.2f}%' if isinstance(ticker_5y, (int, float)) else ticker_5y,
            'max': f'{max_perf:.2f}%' if isinstance(max_perf, (int, float)) else max_perf
        })

    return render_template('result.html',
                           ticker=ticker,
                           min_price=f'{min_price:.2f}',
                           max_price=f'{max_price:.2f}',
                           mean_price=f'{mean_price:.2f}',
                           plot_url=plot_url,
                           data_table=table_data.to_html(classes=['table', 'table-striped'], header="true", formatters=formatters),
                           market_data=market_data,
                           date_range=date_range)

@app.route('/plot', methods=['POST'])
def plot():
    ticker = request.form['ticker'].upper()
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    return render_plot_page(ticker, start_date=start_date, end_date=end_date, date_range="custom")

@app.route('/plot/<ticker>/<date_range>')
def plot_with_range(ticker, date_range):
    if date_range == 'MAX':
        return render_plot_page(ticker, period="max", date_range=date_range)
    
    end_date = datetime.now()
    if date_range == 'YTD':
        start_date = end_date.replace(month=1, day=1)
    elif date_range == '1y':
        start_date = end_date - timedelta(days=365)
    elif date_range == '5y':
        start_date = end_date - timedelta(days=365*5)
    else:
        return "Invalid date range", 400

    return render_plot_page(ticker, start_date=start_date.strftime('%Y-%m-%d'), end_date=end_date.strftime('%Y-%m-%d'), date_range=date_range)

if __name__ == '__main__':
    app.run(debug=True)
