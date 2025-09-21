"""
報表處理邏輯 - 負責分析價格資料並產生報表內容
"""

from typing import Dict, List
import pandas as pd


class ReportGenerator:
    """
    處理價格資料分析與報表產生的類別
    """

    def __init__(self):
        self.data = None

    def load_data(self, df: pd.DataFrame):
        """
        載入價格資料進行分析

        Args:
            df: 包含價格資料的DataFrame
        """
        self.data = df

    def calculate_statistics(self) -> Dict:
        """
        計算關鍵統計數據

        Returns:
            Dict 包含各項統計結果
        """
        if self.data is None or self.data.empty:
            raise ValueError("請先載入資料")

        stats = {}

        try:
            # 基本統計
            if 'AvgPrice' in self.data.columns:
                stats['平均價格'] = float(self.data['AvgPrice'].mean())
                stats['最高平均價'] = float(self.data['AvgPrice'].max())
                stats['最低平均價'] = float(self.data['AvgPrice'].min())
                stats['價格標準差'] = float(self.data['AvgPrice'].std())

            if 'UpperPrice' in self.data.columns:
                stats['最高上價'] = float(self.data['UpperPrice'].max())

            if 'LowerPrice' in self.data.columns:
                stats['最低下價'] = float(self.data['LowerPrice'].min())

            # 交易量統計
            if 'TransQuantity' in self.data.columns:
                stats['總交易量'] = float(self.data['TransQuantity'].sum())
                stats['平均交易量'] = float(self.data['TransQuantity'].mean())

            # 市場數量
            if 'MarketName' in self.data.columns:
                stats['交易市場數'] = len(self.data['MarketName'].unique())

            # 資料日期範圍
            if 'TransDate' in self.data.columns:
                dates = self.data['TransDate'].dropna()
                if not dates.empty:
                    # 處理字串日期
                    if dates.dtype == 'object':
                        dates = pd.to_datetime(dates, errors='coerce').dropna()
                    if not dates.empty:
                        stats['資料起始日'] = dates.min().strftime('%Y-%m-%d')
                        stats['資料結束日'] = dates.max().strftime('%Y-%m-%d')
                        stats['資料天數'] = len(dates.dt.date.unique())

        except (ValueError, AttributeError, KeyError) as e:
            print(f"統計計算錯誤: {e}")
            stats['錯誤'] = str(e)

        return stats

    def generate_insights(self) -> List[str]:
        """
        產生價格趨勢洞察

        Returns:
            List[str] 包含重要發現的文字描述
        """
        if self.data is None or self.data.empty:
            raise ValueError("請先載入資料")

        insights = []

        try:
            # 基本資料檢查
            if len(self.data) == 0:
                insights.append("本期間無甘藍交易資料")
                return insights

            # 價格分析
            if 'AvgPrice' in self.data.columns:
                avg_price = self.data['AvgPrice'].mean()
                max_price = self.data['AvgPrice'].max()
                min_price = self.data['AvgPrice'].min()

                insights.append(f"平均價格為 {avg_price:.2f} 元/公斤")

                if max_price > avg_price * 1.2:
                    insights.append(
                        f"最高價格 {max_price:.2f} 元，"
                        f"較平均價格高出 {((max_price/avg_price-1)*100):.1f}%"
                    )

                if min_price < avg_price * 0.8:
                    insights.append(
                        f"最低價格 {min_price:.2f} 元，"
                        f"較平均價格低 {((1-min_price/avg_price)*100):.1f}%"
                    )

            # 市場分析
            if 'MarketName' in self.data.columns and 'AvgPrice' in self.data.columns:
                market_prices = self.data.groupby('MarketName')['AvgPrice'].mean()
                market_prices = market_prices.sort_values(ascending=False)
                if len(market_prices) > 1:
                    highest_market = market_prices.index[0]
                    lowest_market = market_prices.index[-1]
                    insights.append(
                        f"價格最高市場: {highest_market} ({market_prices.iloc[0]:.2f} 元)"
                    )
                    insights.append(
                        f"價格最低市場: {lowest_market} ({market_prices.iloc[-1]:.2f} 元)"
                    )

            # 交易量分析
            if 'TransQuantity' in self.data.columns:
                total_quantity = self.data['TransQuantity'].sum()
                insights.append(f"總交易量: {total_quantity:.0f} 公斤")

                if 'MarketName' in self.data.columns:
                    market_quantity = self.data.groupby('MarketName')['TransQuantity'].sum()
                    market_quantity = market_quantity.sort_values(ascending=False)
                    if len(market_quantity) > 0:
                        top_market = market_quantity.index[0]
                        insights.append(
                            f"交易量最大市場: {top_market} "
                            f"({market_quantity.iloc[0]:.0f} 公斤)"
                        )

            # 時間趨勢分析
            if 'TransDate' in self.data.columns and 'AvgPrice' in self.data.columns:
                daily_prices = self.data.groupby('TransDate')['AvgPrice'].mean()
                if len(daily_prices) > 1:
                    price_trend = daily_prices.iloc[-1] - daily_prices.iloc[0]
                    if abs(price_trend) > 1:
                        trend_direction = "上漲" if price_trend > 0 else "下跌"
                        insights.append(f"期間價格趨勢: {trend_direction} {abs(price_trend):.2f} 元")

        except (ValueError, AttributeError, KeyError) as e:
            insights.append(f"分析過程發生錯誤: {e}")

        return insights

    def generate_summary_table(self) -> pd.DataFrame:
        """
        產生摘要統計表

        Returns:
            DataFrame 包含市場別統計摘要
        """
        if self.data is None or self.data.empty:
            return pd.DataFrame()

        try:
            if 'MarketName' not in self.data.columns:
                return pd.DataFrame()

            summary = self.data.groupby('MarketName').agg({
                'AvgPrice': ['mean', 'max', 'min', 'std'],
                'TransQuantity': ['sum', 'mean'],
                'TransDate': 'count'
            }).round(2)

            # 平坦化列名
            summary.columns = [
                '平均價格', '最高價格', '最低價格', '價格標準差',
                '總交易量', '平均交易量', '交易次數'
            ]

            summary = summary.sort_values('平均價格', ascending=False)
            return summary

        except (ValueError, AttributeError, KeyError) as e:
            print(f"摘要表產生錯誤: {e}")
            return pd.DataFrame()
