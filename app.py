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

# Simple in-memory cache for stock data
stock_data_cache = {}

@app.route('/')
def index():
    today = datetime.now().strftime('%Y-%m-%d')
    default_start_date = (datetime.now() - timedelta(days=20)).strftime('%Y-%m-%d')
    return render_template('index.html', today=today, default_start_date=default_start_date)

def render_plot_page(ticker, start_date=None, end_date=None, period=None, date_range=None):
    # Check cache for full_data
    if ticker in stock_data_cache:
        full_data = stock_data_cache[ticker]
    else:
        # Download the maximum available data for the ticker once
        full_data = yf.download(ticker, period='max', auto_adjust=True, progress=False)
        if full_data.empty:
            return render_template('error.html')
        
        # Normalize column names
        new_columns = []
        for col in full_data.columns:
            if isinstance(col, tuple):
                new_columns.append(col[0].lower())
            else:
                new_columns.append(col.lower())
        full_data.columns = new_columns
        stock_data_cache[ticker] = full_data # Store in cache

    # Determine plot_data based on requested range by slicing full_data
    if start_date and end_date:
        plot_data = full_data[(full_data.index >= start_date) & (full_data.index <= end_date)]
    else: # This covers the 'MAX' case where start_date and end_date are None
        plot_data = full_data
    
    if plot_data.empty:
        return render_template('error.html')

    plot_data = plot_data.sort_index(ascending=False)

    # Use full_data for performance calculation, slicing as needed
    perf_data = full_data.copy() # Use a copy to avoid modifying full_data directly

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
        # Check cache for index_data_full
        if ticker_symbol in stock_data_cache:
            index_data_full = stock_data_cache[ticker_symbol]
        else:
            # Download max data for each index once
            index_data_full = yf.download(ticker_symbol, period='max', auto_adjust=True, progress=False)
            if index_data_full.empty:
                continue
            index_data_full.columns = [col[0].lower() if isinstance(col, tuple) else col.lower() for col in index_data_full.columns]
            stock_data_cache[ticker_symbol] = index_data_full # Store in cache

        current = index_data_full['close'].iloc[-1].item()

        # Calculate YTD
        ytd_start_date = datetime(index_data_full.index[-1].year, 1, 1)
        ytd_data = index_data_full[index_data_full.index >= ytd_start_date]
        ytd = None
        if not ytd_data.empty and len(ytd_data) > 0:
            ytd_start_price = ytd_data['close'].iloc[0].item()
            ytd = (current - ytd_start_price) / ytd_start_price * 100

        # Calculate 1-year performance
        one_year_ago = index_data_full.index[-1] - timedelta(days=365)
        one_year_data = index_data_full[index_data_full.index >= one_year_ago]
        one_year = None
        if not one_year_data.empty and len(one_year_data) >= 2: # At least two data points for calculation
            one_year_start_price = one_year_data['close'].iloc[0].item()
            one_year = (current - one_year_start_price) / one_year_start_price * 100

        # Calculate 5-year performance
        five_year_ago = index_data_full.index[-1] - timedelta(days=365*5)
        five_year_data = index_data_full[index_data_full.index >= five_year_ago]
        five_year = None
        if not five_year_data.empty and len(five_year_data) > 0:
            five_year_start_price = five_year_data['close'].iloc[0].item()
            five_year = (current - five_year_start_price) / five_year_start_price * 100

        # Calculate MAX performance
        max_perf = None
        if not index_data_full.empty and len(index_data_full) > 0:
            max_start_price = index_data_full['close'].iloc[0].item()
            max_perf = (current - max_start_price) / max_start_price * 100

        market_data.append({
            'name': name,
            'current': f'{current:,.2f}',
            'ytd': f'{ytd:.2f}%' if isinstance(ytd, (int, float)) else ytd,
            'one_year': f'{one_year:.2f}%' if isinstance(one_year, (int, float)) else one_year,
            'five_year': f'{five_year:.2f}%' if isinstance(five_year, (int, float)) else five_year,
            'max': f'{max_perf:.2f}%' if isinstance(max_perf, (int, float)) else max_perf
        })

    # Calculate performance for the selected ticker from perf_data (which is full_data)
    if not perf_data.empty:
        ticker_current = perf_data['close'].iloc[-1].item()

        # Calculate YTD for ticker
        ytd_start_date_ticker = datetime(perf_data.index[-1].year, 1, 1)
        ytd_data_ticker = perf_data[perf_data.index >= ytd_start_date_ticker]
        ticker_ytd = None
        if not ytd_data_ticker.empty and len(ytd_data_ticker) > 0:
            ticker_ytd_start = ytd_data_ticker['close'].iloc[0].item()
            ticker_ytd = (ticker_current - ticker_ytd_start) / ticker_ytd_start * 100

        # Calculate 1-year performance for ticker
        one_year_ago_ticker = perf_data.index[-1] - timedelta(days=365)
        one_year_data_ticker = perf_data[perf_data.index >= one_year_ago_ticker]
        ticker_1y = None
        if not one_year_data_ticker.empty and len(one_year_data_ticker) >= 2:
            ticker_1y_start = one_year_data_ticker['close'].iloc[0].item()
            ticker_1y = (ticker_current - ticker_1y_start) / ticker_1y_start * 100

        # Calculate 5-year performance for ticker
        five_year_ago_ticker = perf_data.index[-1] - timedelta(days=365*5)
        five_year_data_ticker = perf_data[perf_data.index >= five_year_ago_ticker]
        ticker_5y = None
        if not five_year_data_ticker.empty and len(five_year_data_ticker) > 0:
            ticker_5y_start = five_year_data_ticker['close'].iloc[0].item()
            ticker_5y = (ticker_current - ticker_5y_start) / ticker_5y_start * 100

        # Calculate MAX performance for ticker (using full_data)
        max_perf_ticker = None
        if not perf_data.empty and len(perf_data) > 0:
            max_perf_ticker_start = perf_data['close'].iloc[0].item()
            max_perf_ticker = (ticker_current - max_perf_ticker_start) / max_perf_ticker_start * 100

        market_data.append({
            'name': ticker,
            'current': f'{ticker_current:,.2f}',
            'ytd': f'{ticker_ytd:.2f}%' if isinstance(ticker_ytd, (int, float)) else ticker_ytd,
            'one_year': f'{ticker_1y:.2f}%' if isinstance(ticker_1y, (int, float)) else ticker_1y,
            'five_year': f'{ticker_5y:.2f}%' if isinstance(ticker_5y, (int, float)) else ticker_5y,
            'max': f'{max_perf_ticker:.2f}%' if isinstance(max_perf_ticker, (int, float)) else max_perf_ticker
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
    end_date = datetime.now()
    if date_range == 'MAX':
        # For MAX, we can just use the full data without specific start/end dates for slicing
        # The render_plot_page will handle it by default when start_date/end_date are None
        start_date = None
        end_date = None
    elif date_range == 'YTD':
        start_date = end_date.replace(month=1, day=1)
    elif date_range == '1y':
        start_date = end_date - timedelta(days=365)
    elif date_range == '5y':
        start_date = end_date - timedelta(days=365*5)
    else:
        return "Invalid date range", 400

    return render_plot_page(ticker, start_date=start_date.strftime('%Y-%m-%d') if start_date else None, end_date=end_date.strftime('%Y-%m-%d') if end_date else None, date_range=date_range)

if __name__ == '__main__':
    app.run(debug=True)
