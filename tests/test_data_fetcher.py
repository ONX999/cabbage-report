"""
測試資料擷取模組
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import pandas as pd
import requests

from cabbage_report.data_fetcher import DataFetcher


class TestDataFetcher(unittest.TestCase):
    """DataFetcher 類別測試"""
    
    def setUp(self):
        """設定測試環境"""
        self.api_key = "test_api_key"
        self.fetcher = DataFetcher(api_key=self.api_key)
        
        # 模擬API回應資料
        self.mock_response_data = {
            'Data': [
                {
                    'TransDate': '2024-01-15',
                    'MarketName': '台北一市場',
                    'CropName': '甘藍',
                    'AvgPrice': '25.5',
                    'HighPrice': '30.0',
                    'LowPrice': '20.0',
                    'TransQuantity': '1500.0'
                },
                {
                    'TransDate': '2024-01-15',
                    'MarketName': '台中一市場',
                    'CropName': '甘藍',
                    'AvgPrice': '23.0',
                    'HighPrice': '28.0',
                    'LowPrice': '18.0',
                    'TransQuantity': '1200.0'
                }
            ]
        }
    
    def test_init(self):
        """測試初始化"""
        # 測試有API key的情況
        fetcher = DataFetcher(api_key="test_key")
        self.assertEqual(fetcher.api_key, "test_key")
        
        # 測試無API key的情況
        fetcher = DataFetcher()
        self.assertIsNone(fetcher.api_key)
        
        # 測試其他屬性
        self.assertEqual(fetcher.base_url, "https://data.coa.gov.tw/api/v1/AgriProductsTransType")
        self.assertEqual(fetcher.timeout, 30)
        self.assertEqual(fetcher.retry_count, 3)
    
    @patch('cabbage_report.data_fetcher.requests.get')
    def test_fetch_daily_prices_success(self, mock_get):
        """測試成功擷取每日價格"""
        # 設定mock回應
        mock_response = Mock()
        mock_response.json.return_value = self.mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # 執行測試
        test_date = datetime(2024, 1, 15)
        result = self.fetcher.fetch_daily_prices(test_date)
        
        # 驗證結果
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        self.assertIn('date', result.columns)
        self.assertIn('avg_price', result.columns)
        
        # 驗證API呼叫參數
        expected_params = {
            'StartDate': '2024-01-15',
            'EndDate': '2024-01-15',
            'CropCode': 'FC01,FC02,FC03',
            'api_key': self.api_key
        }
        mock_get.assert_called_once_with(
            self.fetcher.base_url,
            params=expected_params,
            timeout=30
        )
    
    @patch('cabbage_report.data_fetcher.requests.get')
    def test_fetch_daily_prices_default_date(self, mock_get):
        """測試使用預設日期擷取價格"""
        mock_response = Mock()
        mock_response.json.return_value = self.mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # 使用預設日期
        result = self.fetcher.fetch_daily_prices()
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
    
    def test_fetch_daily_prices_invalid_date(self):
        """測試無效日期參數"""
        with self.assertRaises(ValueError):
            self.fetcher.fetch_daily_prices("invalid_date")
    
    @patch('cabbage_report.data_fetcher.requests.get')
    def test_fetch_historical_prices_success(self, mock_get):
        """測試成功擷取歷史價格"""
        mock_response = Mock()
        mock_response.json.return_value = self.mock_response_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 15)
        
        result = self.fetcher.fetch_historical_prices(start_date, end_date)
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)
        
        # 驗證API呼叫參數
        expected_params = {
            'StartDate': '2024-01-01',
            'EndDate': '2024-01-15',
            'CropCode': 'FC01,FC02,FC03',
            'api_key': self.api_key
        }
        mock_get.assert_called_once_with(
            self.fetcher.base_url,
            params=expected_params,
            timeout=30
        )
    
    def test_fetch_historical_prices_invalid_dates(self):
        """測試無效日期範圍"""
        start_date = datetime(2024, 1, 15)
        end_date = datetime(2024, 1, 10)  # 結束日期早於開始日期
        
        with self.assertRaises(ValueError):
            self.fetcher.fetch_historical_prices(start_date, end_date)
    
    def test_fetch_historical_prices_date_range_too_large(self):
        """測試日期範圍過大"""
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 4, 1)  # 超過90天
        
        with self.assertRaises(ValueError):
            self.fetcher.fetch_historical_prices(start_date, end_date)
    
    @patch('cabbage_report.data_fetcher.requests.get')
    def test_api_request_retry_logic(self, mock_get):
        """測試API請求重試邏輯"""
        # 設定前兩次請求失敗，第三次成功
        mock_response = Mock()
        mock_response.json.return_value = self.mock_response_data
        mock_response.raise_for_status.return_value = None
        
        mock_get.side_effect = [
            requests.exceptions.RequestException("First failure"),
            requests.exceptions.RequestException("Second failure"),
            mock_response
        ]
        
        test_date = datetime(2024, 1, 15)
        result = self.fetcher.fetch_daily_prices(test_date)
        
        # 驗證結果成功且重試了3次
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(mock_get.call_count, 3)
    
    @patch('cabbage_report.data_fetcher.requests.get')
    def test_api_request_all_retries_fail(self, mock_get):
        """測試所有重試都失敗的情況"""
        mock_get.side_effect = requests.exceptions.RequestException("API Error")
        
        test_date = datetime(2024, 1, 15)
        
        with self.assertRaises(ConnectionError):
            self.fetcher.fetch_daily_prices(test_date)
        
        # 驗證重試了指定次數
        self.assertEqual(mock_get.call_count, self.fetcher.retry_count)
    
    @patch('cabbage_report.data_fetcher.requests.get')
    def test_process_empty_api_response(self, mock_get):
        """測試處理空的API回應"""
        mock_response = Mock()
        mock_response.json.return_value = {'Data': []}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        test_date = datetime(2024, 1, 15)
        result = self.fetcher.fetch_daily_prices(test_date)
        
        # 應該回傳空的DataFrame但有正確的欄位結構
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)
        expected_columns = ['date', 'market_name', 'product_name', 
                          'avg_price', 'high_price', 'low_price', 'volume']
        self.assertListEqual(list(result.columns), expected_columns)
    
    @patch('cabbage_report.data_fetcher.requests.get')
    def test_process_malformed_api_response(self, mock_get):
        """測試處理格式錯誤的API回應"""
        mock_response = Mock()
        mock_response.json.return_value = {'Error': 'Invalid request'}  # 缺少Data欄位
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        test_date = datetime(2024, 1, 15)
        
        with self.assertRaises(Exception):
            self.fetcher.fetch_daily_prices(test_date)
    
    def test_safe_float_convert(self):
        """測試安全浮點數轉換"""
        # 正常數值
        self.assertEqual(self.fetcher._safe_float_convert("25.5"), 25.5)
        self.assertEqual(self.fetcher._safe_float_convert("1,500.0"), 1500.0)
        
        # 異常值
        self.assertEqual(self.fetcher._safe_float_convert(""), 0.0)
        self.assertEqual(self.fetcher._safe_float_convert("invalid"), 0.0)
        self.assertEqual(self.fetcher._safe_float_convert(None), 0.0)
    
    def test_clean_dataframe(self):
        """測試DataFrame清理功能"""
        # 建立測試資料
        test_data = pd.DataFrame({
            'date': ['2024-01-15', '2024-01-16', 'invalid_date'],
            'avg_price': [25.5, -10.0, 30.0],  # 包含負數
            'volume': [1500, 1200, 0]
        })
        
        cleaned_data = self.fetcher._clean_dataframe(test_data)
        
        # 驗證清理結果
        self.assertEqual(len(cleaned_data), 2)  # 移除了負價格和無效日期的資料
        self.assertTrue(all(cleaned_data['avg_price'] >= 0))
        self.assertTrue(all(cleaned_data['volume'] >= 0))


if __name__ == '__main__':
    unittest.main()