"""
資料擷取模組 - 負責從農產品交易市場API獲取甘藍價格資料
"""

import logging
from datetime import datetime
from typing import Dict, Optional
import os

import pandas as pd
import requests


logger = logging.getLogger(__name__)


class DataFetcher:
    """
    農產品價格資料擷取器

    負責從行政院農業委員會農糧署API獲取甘藍價格相關資料
    支援單日查詢與歷史區間查詢功能
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化資料擷取器

        Args:
            api_key: API密鑰，若未提供則從環境變數CABBAGE_API_KEY讀取
        """
        self.api_key = api_key or os.getenv('CABBAGE_API_KEY')
        self.base_url = "https://data.coa.gov.tw/api/v1/AgriProductsTransType"
        self.timeout = 30  # API請求超時時間(秒)
        self.retry_count = 3  # 重試次數

        # 甘藍相關的作物代碼 (根據農糧署API文件)
        self.cabbage_codes = ['FC01', 'FC02', 'FC03']  # 甘藍相關品種代碼

    def fetch_daily_prices(self, date: Optional[datetime] = None) -> pd.DataFrame:
        """
        擷取指定日期的甘藍價格資料

        Args:
            date: 指定日期，若未指定則使用今日

        Returns:
            DataFrame 包含價格資料，欄位包括：
            - date: 交易日期
            - market_name: 市場名稱
            - product_name: 品種名稱
            - avg_price: 平均價格
            - high_price: 最高價格
            - low_price: 最低價格
            - volume: 交易量

        Raises:
            ValueError: 當日期格式不正確時
            ConnectionError: 當API連線失敗時
            Exception: 當API回應格式異常時
        """
        if date is None:
            date = datetime.now()

        if not isinstance(date, datetime):
            raise ValueError("日期必須為datetime物件")

        date_str = date.strftime('%Y-%m-%d')
        logger.info("正在擷取 %s 的甘藍價格資料", date_str)

        try:
            # 建構API參數
            params = {
                'StartDate': date_str,
                'EndDate': date_str,
                'CropCode': ','.join(self.cabbage_codes)
            }

            if self.api_key:
                params['api_key'] = self.api_key

            # 發送API請求
            response = self._make_api_request(params)

            # 處理回應資料
            df = self._process_api_response(response)

            logger.info("成功擷取 %d 筆價格資料", len(df))
            return df

        except Exception as e:
            logger.error("擷取每日價格資料時發生錯誤: %s", str(e))
            raise

    def fetch_historical_prices(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        擷取指定期間的歷史價格資料

        Args:
            start_date: 起始日期
            end_date: 結束日期

        Returns:
            DataFrame 包含歷史價格資料

        Raises:
            ValueError: 當日期範圍不正確時
            ConnectionError: 當API連線失敗時
        """
        # 驗證日期參數
        if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
            raise ValueError("起始日期與結束日期必須為datetime物件")

        if start_date > end_date:
            raise ValueError("起始日期不能晚於結束日期")

        # 檢查日期範圍是否過大 (限制90天以內)
        if (end_date - start_date).days > 90:
            raise ValueError("查詢日期範圍不能超過90天")

        start_str = start_date.strftime('%Y-%m-%d')
        end_str = end_date.strftime('%Y-%m-%d')

        logger.info("正在擷取 %s 至 %s 的歷史價格資料", start_str, end_str)

        try:
            # 建構API參數
            params = {
                'StartDate': start_str,
                'EndDate': end_str,
                'CropCode': ','.join(self.cabbage_codes)
            }

            if self.api_key:
                params['api_key'] = self.api_key

            # 發送API請求
            response = self._make_api_request(params)

            # 處理回應資料
            df = self._process_api_response(response)

            logger.info("成功擷取 %d 筆歷史價格資料", len(df))
            return df

        except Exception as e:
            logger.error("擷取歷史價格資料時發生錯誤: %s", str(e))
            raise

    def _make_api_request(self, params: Dict) -> Dict:
        """
        發送API請求並處理重試邏輯

        Args:
            params: API請求參數

        Returns:
            API回應的JSON資料

        Raises:
            ConnectionError: 當所有重試都失敗時
        """
        for attempt in range(self.retry_count):
            try:
                response = requests.get(
                    self.base_url,
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()

            except requests.exceptions.RequestException as e:
                logger.warning("API請求失敗 (嘗試 %d/%d): %s",
                             attempt + 1, self.retry_count, str(e))
                if attempt == self.retry_count - 1:
                    raise ConnectionError(f"API請求失敗，已重試{self.retry_count}次: {str(e)}")

        # 不應該執行到這裡
        raise ConnectionError("API請求失敗")

    def _process_api_response(self, response_data: Dict) -> pd.DataFrame:
        """
        處理API回應資料並轉換為DataFrame

        Args:
            response_data: API回應的JSON資料

        Returns:
            處理後的DataFrame

        Raises:
            Exception: 當資料格式異常時
        """
        try:
            # 檢查API回應狀態
            if 'Data' not in response_data:
                raise Exception("API回應格式異常：缺少Data欄位")

            data_list = response_data['Data']

            if not data_list:
                logger.warning("API回應無資料")
                # 回傳空的DataFrame但包含正確的欄位結構
                return pd.DataFrame(columns=[
                    'date', 'market_name', 'product_name',
                    'avg_price', 'high_price', 'low_price', 'volume'
                ])

            # 轉換資料格式
            processed_data = []
            for item in data_list:
                processed_item = {
                    'date': item.get('TransDate', ''),
                    'market_name': item.get('MarketName', ''),
                    'product_name': item.get('CropName', ''),
                    'avg_price': self._safe_float_convert(item.get('AvgPrice', '0')),
                    'high_price': self._safe_float_convert(item.get('HighPrice', '0')),
                    'low_price': self._safe_float_convert(item.get('LowPrice', '0')),
                    'volume': self._safe_float_convert(item.get('TransQuantity', '0'))
                }
                processed_data.append(processed_item)

            df = pd.DataFrame(processed_data)

            # 資料清理與型別轉換
            df = self._clean_dataframe(df)

            return df

        except Exception as e:
            logger.error("處理API回應資料時發生錯誤: %s", str(e))
            raise Exception(f"資料處理失敗: {str(e)}")

    def _safe_float_convert(self, value: str) -> float:
        """
        安全地將字串轉換為浮點數

        Args:
            value: 待轉換的字串值

        Returns:
            轉換後的浮點數，轉換失敗時回傳0.0
        """
        try:
            # 移除可能的逗號分隔符號
            cleaned_value = str(value).replace(',', '').strip()
            return float(cleaned_value) if cleaned_value else 0.0
        except (ValueError, TypeError):
            return 0.0

    def _clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        清理並標準化DataFrame資料

        Args:
            df: 原始DataFrame

        Returns:
            清理後的DataFrame
        """
        try:
            # 轉換日期欄位
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')

            # 移除價格為0或負數的異常資料
            numeric_columns = ['avg_price', 'high_price', 'low_price', 'volume']
            for col in numeric_columns:
                if col in df.columns:
                    df = df[df[col] >= 0]

            # 移除重複資料
            df = df.drop_duplicates()

            # 按日期排序
            if 'date' in df.columns:
                df = df.sort_values('date').reset_index(drop=True)

            return df

        except Exception as e:
            logger.error("清理DataFrame時發生錯誤: %s", str(e))
            return df  # 回傳原始資料而不是引發錯誤
