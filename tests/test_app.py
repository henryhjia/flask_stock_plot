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
        # Create a sample DataFrame to be returned by the mock
        data = {
            'Open': [150, 151, 152],
            'High': [155, 156, 157],
            'Low': [149, 150, 151],
            'Close': [152, 153, 154],
            'Volume': [1000, 1100, 1200]
        }
        dates = pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03'])
        df = pd.DataFrame(data, index=dates)
        mock_download.return_value = df

        response = self.app.post('/plot', data={
            'ticker': 'AAPL',
            'start_date': '2023-01-01',
            'end_date': '2023-01-03'
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'AAPL Stock Price', response.data)
        self.assertIn(b'<strong>Min Price:</strong> 152.00', response.data)
        self.assertIn(b'<strong>Max Price:</strong> 154.00', response.data)
        self.assertIn(b'<strong>Mean Price:</strong> 153.00', response.data)
        self.assertIn(b'data:image/png;base64,', response.data)
        self.assertIn(b'<table border="1" class="dataframe table table-striped">', response.data)

    @patch('yfinance.download')
    def test_plot_long_range(self, mock_download):
        # Create a sample DataFrame with 30 days of data
        dates = pd.to_datetime(pd.date_range(start='2023-01-01', periods=30))
        data = {
            'Open': [150 + i for i in range(30)],
            'High': [155 + i for i in range(30)],
            'Low': [149 + i for i in range(30)],
            'Close': [152 + i for i in range(30)],
            'Volume': [1000 + i * 10 for i in range(30)]
        }
        df = pd.DataFrame(data, index=dates)
        mock_download.return_value = df

        response = self.app.post('/plot', data={
            'ticker': 'AAPL',
            'start_date': '2023-01-01',
            'end_date': '2023-01-30'
        })

        self.assertEqual(response.status_code, 200)
        # Check that the data is truncated to 20 days
        self.assertIn(b'2023-01-30', response.data)
        self.assertNotIn(b'2023-01-10', response.data)

if __name__ == '__main__':
    unittest.main()
