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

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/plot', methods=['POST'])
def plot():
    ticker = request.form['ticker']
    start_date = request.form['start_date']
    end_date = request.form['end_date']

    # Download the data
    data = yf.download(ticker, start=start_date, end=end_date, auto_adjust=True)

    if data.empty:
        return "No data found for the given ticker and date range."

    data = data.sort_index(ascending=False)

    if len(data) > 20:
        data = data.head(20)

    # Calculate statistics
    min_val = data['Close'].min()
    min_price = min_val.iloc[0] if isinstance(min_val, pd.Series) else min_val
    max_val = data['Close'].max()
    max_price = max_val.iloc[0] if isinstance(max_val, pd.Series) else max_val
    mean_val = data['Close'].mean()
    mean_price = mean_val.iloc[0] if isinstance(mean_val, pd.Series) else mean_val

    # Generate the plot
    plt.figure(figsize=(10, 6))
    plt.plot(data.index, data['Close'])
    plt.title(f'{ticker} Stock Price')
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.grid(True)

    # Format the x-axis to show dates
    ax = plt.gca()
    ax.xaxis.set_major_locator(mdates.DayLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=90) # Rotates the x-axis labels to be vertical


    # Save it to a temporary buffer.
    buf = BytesIO()
    plt.savefig(buf, format="png")
    # Embed the result in the html output.
    plot_data = base64.b64encode(buf.getbuffer()).decode("ascii")
    plot_url = f'data:image/png;base64,{plot_data}'


    return render_template('result.html',
                           ticker=ticker,
                           min_price=f'{min_price:.2f}',
                           max_price=f'{max_price:.2f}',
                           mean_price=f'{mean_price:.2f}',
                           plot_url=plot_url,
                           data_table=data.to_html(classes=['table', 'table-striped'], header="true"))

if __name__ == '__main__':
    app.run(debug=True)
