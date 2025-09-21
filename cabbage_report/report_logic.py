"""
報表處理邏輯 - 負責分析價格資料並產生報表內容
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import pandas as pd
import numpy as np


logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    報表生成器

    負責分析甘藍價格資料，計算統計指標，產生價格趨勢洞察
    並支援匯出Excel與PDF格式報表
    """

    def __init__(self):
        """初始化報表生成器"""
        self.data = None
        self.statistics = None
        self.insights = []

    def load_data(self, df: pd.DataFrame) -> None:
        """
        載入價格資料進行分析

        Args:
            df: 包含價格資料的DataFrame，應包含以下欄位：
                - date: 交易日期
                - market_name: 市場名稱
                - product_name: 品種名稱
                - avg_price: 平均價格
                - high_price: 最高價格
                - low_price: 最低價格
                - volume: 交易量

        Raises:
            ValueError: 當DataFrame格式不正確或為空時
        """
        if df is None or df.empty:
            raise ValueError("輸入的DataFrame不能為空")

        # 驗證必要欄位
        required_columns = ['date', 'avg_price', 'volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"DataFrame缺少必要欄位: {missing_columns}")

        # 複製並清理資料
        self.data = df.copy()
        self.data = self._validate_and_clean_data(self.data)

        logger.info("已載入 %d 筆價格資料", len(self.data))

        # 重置計算結果
        self.statistics = None
        self.insights = []

    def calculate_statistics(self) -> Dict:
        """
        計算關鍵統計數據

        Returns:
            Dict 包含各項統計結果：
            - basic_stats: 基本統計資料 (平均價格、最高價、最低價等)
            - price_trends: 價格趨勢指標
            - volume_stats: 交易量統計
            - market_analysis: 市場分析
            - volatility_metrics: 價格波動性指標

        Raises:
            ValueError: 當未載入資料時
        """
        if self.data is None or self.data.empty:
            raise ValueError("請先載入資料")

        try:
            statistics = {}

            # 1. 基本統計資料
            statistics['basic_stats'] = self._calculate_basic_stats()

            # 2. 價格趨勢分析
            statistics['price_trends'] = self._calculate_price_trends()

            # 3. 交易量統計
            statistics['volume_stats'] = self._calculate_volume_stats()

            # 4. 市場分析
            statistics['market_analysis'] = self._calculate_market_analysis()

            # 5. 價格波動性指標
            statistics['volatility_metrics'] = self._calculate_volatility_metrics()

            # 6. 價格區間分佈
            statistics['price_distribution'] = self._calculate_price_distribution()

            self.statistics = statistics
            logger.info("統計計算完成")

            return statistics

        except Exception as e:
            logger.error("計算統計數據時發生錯誤: %s", str(e))
            raise

    def generate_insights(self) -> List[str]:
        """
        產生價格趨勢洞察

        Returns:
            List[str] 包含重要發現的文字描述

        Raises:
            ValueError: 當未載入資料或未計算統計數據時
        """
        if self.data is None or self.data.empty:
            raise ValueError("請先載入資料")

        if self.statistics is None:
            logger.info("尚未計算統計數據，自動執行計算")
            self.calculate_statistics()

        try:
            insights = []

            # 1. 價格水準洞察
            insights.extend(self._generate_price_level_insights())

            # 2. 價格趨勢洞察
            insights.extend(self._generate_trend_insights())

            # 3. 市場活躍度洞察
            insights.extend(self._generate_volume_insights())

            # 4. 價格波動性洞察
            insights.extend(self._generate_volatility_insights())

            # 5. 市場表現洞察
            insights.extend(self._generate_market_performance_insights())

            self.insights = insights
            logger.info("生成了 %d 項洞察", len(insights))

            return insights

        except Exception as e:
            logger.error("生成洞察時發生錯誤: %s", str(e))
            raise

    def get_summary_report(self) -> Dict:
        """
        取得完整的報表摘要

        Returns:
            Dict 包含統計數據與洞察的完整報表
        """
        if self.statistics is None:
            self.calculate_statistics()

        if not self.insights:
            self.generate_insights()

        return {
            'data_period': self._get_data_period(),
            'data_summary': self._get_data_summary(),
            'statistics': self.statistics,
            'insights': self.insights,
            'generated_at': datetime.now().isoformat()
        }

    def _validate_and_clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """驗證並清理輸入資料"""
        try:
            # 確保日期欄位為datetime型別
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
                # 移除日期轉換失敗的資料
                df = df.dropna(subset=['date'])

            # 確保數值欄位為數值型別
            numeric_columns = ['avg_price', 'high_price', 'low_price', 'volume']
            for col in numeric_columns:
                if col in df.columns:
                    df.loc[:, col] = pd.to_numeric(df[col], errors='coerce')

            # 移除價格為負數或NaN的資料
            if 'avg_price' in df.columns:
                df = df[df['avg_price'] > 0]

            # 移除交易量為負數的資料
            if 'volume' in df.columns:
                df = df[df['volume'] >= 0]

            return df.reset_index(drop=True)

        except Exception as e:
            logger.error("資料驗證與清理時發生錯誤: %s", str(e))
            raise ValueError(f"資料清理失敗: {str(e)}")

    def _calculate_basic_stats(self) -> Dict:
        """計算基本統計資料"""
        stats = {}

        # 價格統計
        price_data = self.data['avg_price']
        stats['avg_price'] = float(price_data.mean())
        stats['median_price'] = float(price_data.median())
        stats['max_price'] = float(price_data.max())
        stats['min_price'] = float(price_data.min())
        stats['price_std'] = float(price_data.std())

        # 交易量統計
        if 'volume' in self.data.columns:
            volume_data = self.data['volume']
            stats['avg_volume'] = float(volume_data.mean())
            stats['total_volume'] = float(volume_data.sum())
            stats['max_volume'] = float(volume_data.max())

        # 資料覆蓋範圍
        stats['data_points'] = len(self.data)
        stats['unique_markets'] = self.data['market_name'].nunique() if 'market_name' in self.data.columns else 0

        return stats

    def _calculate_price_trends(self) -> Dict:
        """計算價格趨勢指標"""
        trends = {}

        if len(self.data) < 2:
            trends['trend_direction'] = 'insufficient_data'
            return trends

        # 按日期排序
        data_sorted = self.data.sort_values('date')
        prices = data_sorted['avg_price'].values

        # 計算價格變化率
        price_changes = np.diff(prices) / prices[:-1] * 100
        trends['avg_daily_change_pct'] = float(np.mean(price_changes))
        trends['total_change_pct'] = float((prices[-1] - prices[0]) / prices[0] * 100)

        # 趨勢方向
        if trends['total_change_pct'] > 5:
            trends['trend_direction'] = 'upward'
        elif trends['total_change_pct'] < -5:
            trends['trend_direction'] = 'downward'
        else:
            trends['trend_direction'] = 'stable'

        # 最大漲跌幅
        trends['max_increase_pct'] = float(np.max(price_changes)) if len(price_changes) > 0 else 0
        trends['max_decrease_pct'] = float(np.min(price_changes)) if len(price_changes) > 0 else 0

        return trends

    def _calculate_volume_stats(self) -> Dict:
        """計算交易量統計"""
        volume_stats = {}

        if 'volume' not in self.data.columns:
            return volume_stats

        volume_data = self.data['volume']
        volume_stats['avg_daily_volume'] = float(volume_data.mean())
        volume_stats['volume_volatility'] = float(volume_data.std())
        volume_stats['volume_growth_rate'] = 0.0

        if len(self.data) >= 2:
            data_sorted = self.data.sort_values('date')
            first_volume = data_sorted['volume'].iloc[0]
            last_volume = data_sorted['volume'].iloc[-1]
            if first_volume > 0:
                volume_stats['volume_growth_rate'] = float((last_volume - first_volume) / first_volume * 100)

        return volume_stats

    def _calculate_market_analysis(self) -> Dict:
        """計算市場分析指標"""
        market_analysis = {}

        if 'market_name' in self.data.columns:
            # 各市場價格比較
            market_prices = self.data.groupby('market_name')['avg_price'].agg(['mean', 'count']).reset_index()
            market_prices.columns = ['market_name', 'avg_price', 'data_points']

            # 找出最高價與最低價市場
            if len(market_prices) > 0:
                highest_market = market_prices.loc[market_prices['avg_price'].idxmax()]
                lowest_market = market_prices.loc[market_prices['avg_price'].idxmin()]

                market_analysis['highest_price_market'] = {
                    'name': highest_market['market_name'],
                    'avg_price': float(highest_market['avg_price'])
                }
                market_analysis['lowest_price_market'] = {
                    'name': lowest_market['market_name'],
                    'avg_price': float(lowest_market['avg_price'])
                }

                # 市場價格差異
                price_spread = highest_market['avg_price'] - lowest_market['avg_price']
                market_analysis['market_price_spread'] = float(price_spread)
                market_analysis['market_price_spread_pct'] = float(price_spread / lowest_market['avg_price'] * 100)

        return market_analysis

    def _calculate_volatility_metrics(self) -> Dict:
        """計算價格波動性指標"""
        volatility = {}

        prices = self.data['avg_price']
        volatility['coefficient_of_variation'] = float(prices.std() / prices.mean() * 100)

        # 計算價格範圍指標
        if 'high_price' in self.data.columns and 'low_price' in self.data.columns:
            daily_ranges = self.data['high_price'] - self.data['low_price']
            volatility['avg_daily_range'] = float(daily_ranges.mean())
            volatility['avg_daily_range_pct'] = float(daily_ranges.mean() / prices.mean() * 100)

        return volatility

    def _calculate_price_distribution(self) -> Dict:
        """計算價格分佈"""
        distribution = {}

        prices = self.data['avg_price']

        # 價格四分位數
        distribution['q1'] = float(prices.quantile(0.25))
        distribution['q2'] = float(prices.quantile(0.5))
        distribution['q3'] = float(prices.quantile(0.75))
        distribution['iqr'] = distribution['q3'] - distribution['q1']

        return distribution

    def _generate_price_level_insights(self) -> List[str]:
        """生成價格水準洞察"""
        insights = []
        basic_stats = self.statistics['basic_stats']

        avg_price = basic_stats['avg_price']
        max_price = basic_stats['max_price']
        min_price = basic_stats['min_price']

        insights.append(f"期間內甘藍平均價格為 ${avg_price:.2f}，最高價 ${max_price:.2f}，最低價 ${min_price:.2f}")

        price_range_pct = (max_price - min_price) / avg_price * 100
        if price_range_pct > 50:
            insights.append(f"價格波動幅度較大，最高價與最低價差距達 {price_range_pct:.1f}%")
        elif price_range_pct < 20:
            insights.append(f"價格相對穩定，波動幅度僅 {price_range_pct:.1f}%")

        return insights

    def _generate_trend_insights(self) -> List[str]:
        """生成趨勢洞察"""
        insights = []
        trends = self.statistics['price_trends']

        total_change = trends.get('total_change_pct', 0)
        trend_direction = trends.get('trend_direction', 'unknown')

        if trend_direction == 'upward':
            insights.append(f"價格呈現上漲趨勢，累計漲幅 {total_change:.1f}%")
        elif trend_direction == 'downward':
            insights.append(f"價格呈現下跌趨勢，累計跌幅 {abs(total_change):.1f}%")
        else:
            insights.append("價格走勢相對平穩，無明顯上漲或下跌趨勢")

        avg_daily_change = trends.get('avg_daily_change_pct', 0)
        if abs(avg_daily_change) > 2:
            insights.append(f"日均價格變化幅度較大，約 {avg_daily_change:.1f}%")

        return insights

    def _generate_volume_insights(self) -> List[str]:
        """生成交易量洞察"""
        insights = []

        if 'volume_stats' not in self.statistics:
            return insights

        volume_stats = self.statistics['volume_stats']
        avg_volume = volume_stats.get('avg_daily_volume', 0)
        volume_growth = volume_stats.get('volume_growth_rate', 0)

        insights.append(f"平均日交易量為 {avg_volume:.1f} 公斤")

        if abs(volume_growth) > 10:
            direction = "增加" if volume_growth > 0 else "減少"
            insights.append(f"交易量較期初{direction} {abs(volume_growth):.1f}%")

        return insights

    def _generate_volatility_insights(self) -> List[str]:
        """生成波動性洞察"""
        insights = []
        volatility = self.statistics['volatility_metrics']

        cv = volatility.get('coefficient_of_variation', 0)
        if cv > 15:
            insights.append("價格波動性較高，市場不穩定性增加")
        elif cv < 5:
            insights.append("價格波動性較低，市場相對穩定")

        return insights

    def _generate_market_performance_insights(self) -> List[str]:
        """生成市場表現洞察"""
        insights = []

        if 'market_analysis' not in self.statistics:
            return insights

        market_analysis = self.statistics['market_analysis']

        if 'highest_price_market' in market_analysis:
            highest_market = market_analysis['highest_price_market']
            lowest_market = market_analysis['lowest_price_market']

            insights.append(f"價格最高市場：{highest_market['name']} (${highest_market['avg_price']:.2f})")
            insights.append(f"價格最低市場：{lowest_market['name']} (${lowest_market['avg_price']:.2f})")

            spread_pct = market_analysis.get('market_price_spread_pct', 0)
            if spread_pct > 20:
                insights.append(f"不同市場間價格差異較大，達 {spread_pct:.1f}%")

        return insights

    def _get_data_period(self) -> Dict:
        """取得資料期間資訊"""
        if 'date' not in self.data.columns:
            return {}

        dates = self.data['date']
        return {
            'start_date': dates.min().strftime('%Y-%m-%d'),
            'end_date': dates.max().strftime('%Y-%m-%d'),
            'total_days': (dates.max() - dates.min()).days + 1
        }

    def _get_data_summary(self) -> Dict:
        """取得資料摘要資訊"""
        return {
            'total_records': len(self.data),
            'markets_covered': self.data['market_name'].nunique() if 'market_name' in self.data.columns else 0,
            'products_covered': self.data['product_name'].nunique() if 'product_name' in self.data.columns else 0
        }
