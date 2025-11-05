import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch
import pandas as pd
from app import app

class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('yfinance.download')
    def test_plot(self, mock_download):
        # 1. For plot_data
        plot_data_df = pd.DataFrame({
            'Open': [150, 151, 152], 'High': [155, 156, 157], 'Low': [149, 150, 151],
            'Close': [152, 153, 154], 'Volume': [1000, 1100, 1200]
        }, index=pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03']))

        # 2. For perf_data (5y)
        perf_data_df = pd.DataFrame({'Close': range(100, 100 + 1260)}, index=pd.to_datetime(pd.date_range(start='2018-01-01', periods=1260)))

        # 3. For market indices (S&P 500, DOW, NASDAQ) - 5y and max
        index_df = pd.DataFrame({'Close': range(1000, 1000 + 1260)}, index=pd.to_datetime(pd.date_range(start='2018-01-01', periods=1260)))

        # 4. For ticker max performance
        perf_data_max_df = pd.DataFrame({'Close': range(50, 50 + 2520)}, index=pd.to_datetime(pd.date_range(start='2010-01-01', periods=2520)))

        mock_download.side_effect = [
            plot_data_df,       # 1. plot_data
            perf_data_df,       # 2. perf_data (5y)
            index_df,           # 3. S&P 500 (5y)
            index_df,           # 3. S&P 500 (max)
            index_df,           # 3. DOW (5y)
            index_df,           # 3. DOW (max)
            index_df,           # 3. NASDAQ (5y)
            index_df,           # 3. NASDAQ (max)
            perf_data_max_df    # 4. ticker (max)
        ]

        response = self.app.post('/plot', data={
            'ticker': 'AAPL',
            'start_date': '2023-01-01',
            'end_date': '2023-01-03'
        })

        self.assertEqual(response.status_code, 200)

    @patch('yfinance.download')
    def test_plot_long_range(self, mock_download):
        # 1. For plot_data
        plot_data_df = pd.DataFrame({
            'Open': [150 + i for i in range(30)], 'High': [155 + i for i in range(30)], 'Low': [149 + i for i in range(30)],
            'Close': [152 + i for i in range(30)], 'Volume': [1000 + i * 10 for i in range(30)]
        }, index=pd.to_datetime(pd.date_range(start='2023-01-01', periods=30)))

        # 2. For perf_data (5y)
        perf_data_df = pd.DataFrame({'Close': range(100, 100 + 1260)}, index=pd.to_datetime(pd.date_range(start='2018-01-01', periods=1260)))

        # 3. For market indices (S&P 500, DOW, NASDAQ) - 5y and max
        index_df = pd.DataFrame({'Close': range(1000, 1000 + 1260)}, index=pd.to_datetime(pd.date_range(start='2018-01-01', periods=1260)))

        # 4. For ticker max performance
        perf_data_max_df = pd.DataFrame({'Close': range(50, 50 + 2520)}, index=pd.to_datetime(pd.date_range(start='2010-01-01', periods=2520)))

        mock_download.side_effect = [
            plot_data_df,       # 1. plot_data
            perf_data_df,       # 2. perf_data (5y)
            index_df,           # 3. S&P 500 (5y)
            index_df,           # 3. S&P 500 (max)
            index_df,           # 3. DOW (5y)
            index_df,           # 3. DOW (max)
            index_df,           # 3. NASDAQ (5y)
            index_df,           # 3. NASDAQ (max)
            perf_data_max_df    # 4. ticker (max)
        ]

        response = self.app.post('/plot', data={
            'ticker': 'AAPL',
            'start_date': '2023-01-01',
            'end_date': '2023-01-30'
        })

        self.assertEqual(response.status_code, 200)

    @patch('yfinance.download')
    def test_plot_no_data(self, mock_download):
        # Mock yfinance.download to return an empty DataFrame
        mock_download.return_value = pd.DataFrame()

        response = self.app.post('/plot', data={
            'ticker': 'INVALID',
            'start_date': '2023-01-01',
            'end_date': '2023-01-03'
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<title>Error</title>', response.data)
        self.assertIn(b'No data found for the given ticker and date range.', response.data)
        self.assertIn(b'<a href="/" class="btn btn-primary btn-block">Go Back</a>', response.data)

    @patch('yfinance.download')
    def test_plot_ytd(self, mock_download):
        mock_download.return_value = pd.DataFrame({
            'Open': [150], 'High': [155], 'Low': [149],
            'Close': [152], 'Volume': [1000]
        }, index=pd.to_datetime(['2023-01-01']))
        response = self.app.get('/plot/AAPL/YTD')
        self.assertEqual(response.status_code, 200)

    @patch('yfinance.download')
    def test_plot_1y(self, mock_download):
        mock_download.return_value = pd.DataFrame({
            'Open': [150], 'High': [155], 'Low': [149],
            'Close': [152], 'Volume': [1000]
        }, index=pd.to_datetime(['2023-01-01']))
        response = self.app.get('/plot/AAPL/1y')
        self.assertEqual(response.status_code, 200)

    @patch('yfinance.download')
    def test_plot_5y(self, mock_download):
        mock_download.return_value = pd.DataFrame({
            'Open': [150], 'High': [155], 'Low': [149],
            'Close': [152], 'Volume': [1000]
        }, index=pd.to_datetime(['2023-01-01']))
        response = self.app.get('/plot/AAPL/5y')
        self.assertEqual(response.status_code, 200)

    @patch('yfinance.download')
    def test_plot_max(self, mock_download):
        mock_download.return_value = pd.DataFrame({
            'Open': [150], 'High': [155], 'Low': [149],
            'Close': [152], 'Volume': [1000]
        }, index=pd.to_datetime(['2023-01-01']))
        response = self.app.get('/plot/AAPL/MAX')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
