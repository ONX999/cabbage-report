"""
示範資料產生器 - 用於測試和展示功能
"""

import pandas as pd
from datetime import datetime, timedelta
import random


def generate_demo_data(date: datetime, num_markets: int = 5) -> pd.DataFrame:
    """
    產生示範的甘藍價格資料

    Args:
        date: 目標日期
        num_markets: 市場數量

    Returns:
        DataFrame: 示範價格資料
    """
    markets = ['台北一', '台北二', '台中', '高雄', '彰化', '雲林', '嘉義'][:num_markets]
    
    data = []
    for market in markets:
        # 隨機產生價格（基於真實價格範圍）
        base_price = random.uniform(15, 25)
        upper_price = base_price + random.uniform(3, 7)
        lower_price = base_price - random.uniform(2, 5)
        middle_price = (upper_price + lower_price) / 2
        avg_price = base_price + random.uniform(-2, 2)
        quantity = random.randint(500, 2000)
        
        data.append({
            'TransDate': date.strftime('%Y-%m-%d'),
            'CropName': '甘藍',
            'MarketName': market,
            'UpperPrice': round(upper_price, 1),
            'MiddlePrice': round(middle_price, 1),
            'LowerPrice': round(max(lower_price, 5), 1),  # 確保不為負數
            'AvgPrice': round(avg_price, 1),
            'TransQuantity': quantity
        })
    
    return pd.DataFrame(data)


def generate_demo_historical_data(start_date: datetime, end_date: datetime, 
                                 num_markets: int = 5) -> pd.DataFrame:
    """
    產生歷史期間的示範資料

    Args:
        start_date: 起始日期
        end_date: 結束日期
        num_markets: 市場數量

    Returns:
        DataFrame: 歷史示範資料
    """
    all_data = []
    current_date = start_date
    
    while current_date <= end_date:
        # 週末可能沒有交易
        if current_date.weekday() < 5:  # 0-4 是週一到週五
            daily_data = generate_demo_data(current_date, num_markets)
            all_data.append(daily_data)
        
        current_date += timedelta(days=1)
    
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()