"""
資料擷取模組 - 負責從農產品交易市場API獲取甘藍價格資料
"""

from datetime import datetime, timedelta
from typing import Optional
import requests
import pandas as pd
from .demo_data import generate_demo_data, generate_demo_historical_data


class DataFetcher:
    """
    從農糧署API獲取甘藍價格資料的類別
    """

    def __init__(self, api_key: str = None, use_demo_data: bool = False):
        self.api_key = api_key
        self.base_url = "https://data.coa.gov.tw/api/v1/AgriProductsTransType"
        self.use_demo_data = use_demo_data

    def fetch_daily_prices(self, date: Optional[datetime] = None) -> pd.DataFrame:
        """
        擷取指定日期的甘藍價格資料

        Args:
            date: 指定日期，若未指定則使用今日

        Returns:
            DataFrame 包含價格資料
        """
        if date is None:
            date = datetime.now()

        # 如果啟用示範模式，直接返回示範資料
        if self.use_demo_data:
            print("使用示範資料模式")
            return generate_demo_data(date)

        params = {
            'format': 'json',
            'TransType': '甘藍',
            'StartTime': date.strftime('%Y-%m-%d'),
            'EndTime': date.strftime('%Y-%m-%d')
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if 'Data' in data and data['Data']:
                df = pd.DataFrame(data['Data'])
                # 標準化列名
                df = self._standardize_columns(df)
                return df

            # 如果沒有資料，返回空的DataFrame但包含預期的列
            return pd.DataFrame(columns=[
                'TransDate', 'CropName', 'MarketName', 'UpperPrice',
                'MiddlePrice', 'LowerPrice', 'AvgPrice', 'TransQuantity'
            ])
        except requests.RequestException as e:
            print(f"API請求失敗: {e}")
            print("改用示範資料模式")
            # API失敗時改用示範資料
            return generate_demo_data(date)

    def fetch_historical_prices(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """
        擷取指定期間的歷史價格資料

        Args:
            start_date: 起始日期
            end_date: 結束日期

        Returns:
            DataFrame 包含歷史價格資料
        """
        # 如果啟用示範模式，直接返回示範資料
        if self.use_demo_data:
            print("使用歷史示範資料模式")
            return generate_demo_historical_data(start_date, end_date)

        all_data = []
        current_date = start_date

        # 分批次獲取資料，每次最多30天
        while current_date <= end_date:
            batch_end = min(current_date + timedelta(days=29), end_date)

            params = {
                'format': 'json',
                'TransType': '甘藍',
                'StartTime': current_date.strftime('%Y-%m-%d'),
                'EndTime': batch_end.strftime('%Y-%m-%d')
            }

            try:
                response = requests.get(self.base_url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()

                if 'Data' in data and data['Data']:
                    all_data.extend(data['Data'])

                current_date = batch_end + timedelta(days=1)

            except requests.RequestException as e:
                print(f"API請求失敗 ({current_date.strftime('%Y-%m-%d')}): {e}")
                current_date = batch_end + timedelta(days=1)
                continue

        if all_data:
            df = pd.DataFrame(all_data)
            df = self._standardize_columns(df)
            return df

        print("API無資料，改用歷史示範資料模式")
        # API無資料時改用示範資料
        return generate_demo_historical_data(start_date, end_date)

    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        標準化DataFrame的列名和資料類型

        Args:
            df: 原始DataFrame

        Returns:
            標準化後的DataFrame
        """
        # 價格欄位轉換為數值
        price_columns = ['UpperPrice', 'MiddlePrice', 'LowerPrice', 'AvgPrice']
        for col in price_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # 交易量轉換為數值
        if 'TransQuantity' in df.columns:
            df['TransQuantity'] = pd.to_numeric(df['TransQuantity'], errors='coerce')

        # 日期轉換
        if 'TransDate' in df.columns:
            df['TransDate'] = pd.to_datetime(df['TransDate'], errors='coerce')

        return df
