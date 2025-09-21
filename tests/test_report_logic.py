"""
測試報表邏輯模組
"""

import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from cabbage_report.report_logic import ReportGenerator


class TestReportGenerator(unittest.TestCase):
    """ReportGenerator 類別測試"""
    
    def setUp(self):
        """設定測試環境"""
        self.generator = ReportGenerator()
        
        # 建立測試資料
        dates = pd.date_range(start='2024-01-01', end='2024-01-10', freq='D')
        self.test_data = pd.DataFrame({
            'date': dates,
            'market_name': ['台北一市場', '台中一市場'] * 5,
            'product_name': '甘藍',
            'avg_price': [25.0, 23.0, 27.0, 24.0, 26.0, 22.0, 28.0, 25.0, 24.0, 26.0],
            'high_price': [30.0, 28.0, 32.0, 29.0, 31.0, 27.0, 33.0, 30.0, 29.0, 31.0],
            'low_price': [20.0, 18.0, 22.0, 19.0, 21.0, 17.0, 23.0, 20.0, 19.0, 21.0],
            'volume': [1500, 1200, 1300, 1400, 1350, 1250, 1450, 1300, 1200, 1400]
        })
    
    def test_init(self):
        """測試初始化"""
        generator = ReportGenerator()
        self.assertIsNone(generator.data)
        self.assertIsNone(generator.statistics)
        self.assertEqual(generator.insights, [])
    
    def test_load_data_success(self):
        """測試成功載入資料"""
        self.generator.load_data(self.test_data)
        
        self.assertIsNotNone(self.generator.data)
        self.assertEqual(len(self.generator.data), 10)
        self.assertIn('date', self.generator.data.columns)
        self.assertIn('avg_price', self.generator.data.columns)
    
    def test_load_data_empty_dataframe(self):
        """測試載入空DataFrame"""
        empty_df = pd.DataFrame()
        
        with self.assertRaises(ValueError):
            self.generator.load_data(empty_df)
    
    def test_load_data_missing_columns(self):
        """測試載入缺少必要欄位的DataFrame"""
        incomplete_df = pd.DataFrame({
            'date': ['2024-01-01'],
            'avg_price': [25.0]
            # 缺少 volume 欄位
        })
        
        with self.assertRaises(ValueError):
            self.generator.load_data(incomplete_df)
    
    def test_calculate_statistics_without_data(self):
        """測試未載入資料時計算統計數據"""
        with self.assertRaises(ValueError):
            self.generator.calculate_statistics()
    
    def test_calculate_statistics_success(self):
        """測試成功計算統計數據"""
        self.generator.load_data(self.test_data)
        statistics = self.generator.calculate_statistics()
        
        # 驗證統計數據結構
        expected_keys = ['basic_stats', 'price_trends', 'volume_stats', 
                        'market_analysis', 'volatility_metrics', 'price_distribution']
        for key in expected_keys:
            self.assertIn(key, statistics)
        
        # 驗證基本統計數據
        basic_stats = statistics['basic_stats']
        self.assertAlmostEqual(basic_stats['avg_price'], 25.0, places=1)
        self.assertEqual(basic_stats['data_points'], 10)
        self.assertEqual(basic_stats['unique_markets'], 2)
    
    def test_calculate_basic_stats(self):
        """測試基本統計計算"""
        self.generator.load_data(self.test_data)
        stats = self.generator._calculate_basic_stats()
        
        expected_avg = self.test_data['avg_price'].mean()
        expected_max = self.test_data['avg_price'].max()
        expected_min = self.test_data['avg_price'].min()
        
        self.assertAlmostEqual(stats['avg_price'], expected_avg, places=2)
        self.assertEqual(stats['max_price'], expected_max)
        self.assertEqual(stats['min_price'], expected_min)
        self.assertEqual(stats['data_points'], len(self.test_data))
    
    def test_calculate_price_trends(self):
        """測試價格趨勢計算"""
        self.generator.load_data(self.test_data)
        trends = self.generator._calculate_price_trends()
        
        self.assertIn('trend_direction', trends)
        self.assertIn('total_change_pct', trends)
        self.assertIn('avg_daily_change_pct', trends)
        
        # 趨勢方向應該為穩定、上漲或下跌
        self.assertIn(trends['trend_direction'], ['upward', 'downward', 'stable'])
    
    def test_calculate_price_trends_insufficient_data(self):
        """測試資料不足時的趨勢計算"""
        single_row_data = self.test_data.iloc[:1].copy()
        self.generator.load_data(single_row_data)
        trends = self.generator._calculate_price_trends()
        
        self.assertEqual(trends['trend_direction'], 'insufficient_data')
    
    def test_calculate_volume_stats(self):
        """測試交易量統計計算"""
        self.generator.load_data(self.test_data)
        volume_stats = self.generator._calculate_volume_stats()
        
        expected_avg_volume = self.test_data['volume'].mean()
        self.assertAlmostEqual(volume_stats['avg_daily_volume'], expected_avg_volume, places=1)
        self.assertIn('volume_volatility', volume_stats)
        self.assertIn('volume_growth_rate', volume_stats)
    
    def test_calculate_market_analysis(self):
        """測試市場分析計算"""
        self.generator.load_data(self.test_data)
        market_analysis = self.generator._calculate_market_analysis()
        
        if 'highest_price_market' in market_analysis:
            self.assertIn('name', market_analysis['highest_price_market'])
            self.assertIn('avg_price', market_analysis['highest_price_market'])
        
        if 'lowest_price_market' in market_analysis:
            self.assertIn('name', market_analysis['lowest_price_market'])
            self.assertIn('avg_price', market_analysis['lowest_price_market'])
    
    def test_calculate_volatility_metrics(self):
        """測試波動性指標計算"""
        self.generator.load_data(self.test_data)
        volatility = self.generator._calculate_volatility_metrics()
        
        self.assertIn('coefficient_of_variation', volatility)
        
        # 如果有高低價資料，應該包含日價格範圍指標
        if 'high_price' in self.test_data.columns:
            self.assertIn('avg_daily_range', volatility)
            self.assertIn('avg_daily_range_pct', volatility)
    
    def test_calculate_price_distribution(self):
        """測試價格分佈計算"""
        self.generator.load_data(self.test_data)
        distribution = self.generator._calculate_price_distribution()
        
        expected_q1 = self.test_data['avg_price'].quantile(0.25)
        expected_q3 = self.test_data['avg_price'].quantile(0.75)
        
        self.assertAlmostEqual(distribution['q1'], expected_q1, places=2)
        self.assertAlmostEqual(distribution['q3'], expected_q3, places=2)
        self.assertAlmostEqual(distribution['iqr'], expected_q3 - expected_q1, places=2)
    
    def test_generate_insights_without_data(self):
        """測試未載入資料時生成洞察"""
        with self.assertRaises(ValueError):
            self.generator.generate_insights()
    
    def test_generate_insights_success(self):
        """測試成功生成洞察"""
        self.generator.load_data(self.test_data)
        insights = self.generator.generate_insights()
        
        self.assertIsInstance(insights, list)
        self.assertGreater(len(insights), 0)
        
        # 驗證洞察內容都是字串
        for insight in insights:
            self.assertIsInstance(insight, str)
            self.assertGreater(len(insight), 0)
    
    def test_generate_insights_auto_calculate_statistics(self):
        """測試洞察生成時自動計算統計數據"""
        self.generator.load_data(self.test_data)
        self.assertIsNone(self.generator.statistics)
        
        insights = self.generator.generate_insights()
        
        # 應該自動計算統計數據
        self.assertIsNotNone(self.generator.statistics)
        self.assertGreater(len(insights), 0)
    
    def test_validate_and_clean_data(self):
        """測試資料驗證與清理"""
        # 建立包含問題的測試資料
        dirty_data = pd.DataFrame({
            'date': ['2024-01-01', '2024-01-02', 'invalid_date'],
            'avg_price': [25.0, -10.0, 30.0],  # 包含負價格
            'volume': [1500, 1200, -100]  # 包含負交易量
        })
        
        cleaned_data = self.generator._validate_and_clean_data(dirty_data)
        
        # 驗證清理結果
        self.assertEqual(len(cleaned_data), 1)  # 只有第一筆資料有效
        self.assertTrue(all(cleaned_data['avg_price'] > 0))
        self.assertTrue(all(cleaned_data['volume'] >= 0))
    
    def test_get_summary_report(self):
        """測試取得完整報表摘要"""
        self.generator.load_data(self.test_data)
        summary = self.generator.get_summary_report()
        
        expected_keys = ['data_period', 'data_summary', 'statistics', 'insights', 'generated_at']
        for key in expected_keys:
            self.assertIn(key, summary)
        
        # 驗證各部分內容
        self.assertIsInstance(summary['statistics'], dict)
        self.assertIsInstance(summary['insights'], list)
        self.assertIsInstance(summary['generated_at'], str)
    
    def test_get_data_period(self):
        """測試取得資料期間資訊"""
        self.generator.load_data(self.test_data)
        period = self.generator._get_data_period()
        
        self.assertEqual(period['start_date'], '2024-01-01')
        self.assertEqual(period['end_date'], '2024-01-10')
        self.assertEqual(period['total_days'], 10)
    
    def test_get_data_summary(self):
        """測試取得資料摘要資訊"""
        self.generator.load_data(self.test_data)
        summary = self.generator._get_data_summary()
        
        self.assertEqual(summary['total_records'], 10)
        self.assertEqual(summary['markets_covered'], 2)
        self.assertEqual(summary['products_covered'], 1)
    
    def test_generate_price_level_insights(self):
        """測試價格水準洞察生成"""
        self.generator.load_data(self.test_data)
        self.generator.calculate_statistics()
        
        insights = self.generator._generate_price_level_insights()
        
        self.assertIsInstance(insights, list)
        self.assertGreater(len(insights), 0)
        
        # 第一個洞察應該包含價格資訊
        first_insight = insights[0]
        self.assertIn('平均價格', first_insight)
        self.assertIn('最高價', first_insight)
        self.assertIn('最低價', first_insight)
    
    def test_generate_trend_insights(self):
        """測試趨勢洞察生成"""
        self.generator.load_data(self.test_data)
        self.generator.calculate_statistics()
        
        insights = self.generator._generate_trend_insights()
        
        self.assertIsInstance(insights, list)
        self.assertGreater(len(insights), 0)
        
        # 洞察應該包含趨勢相關資訊
        insight_text = ' '.join(insights)
        trend_keywords = ['上漲', '下跌', '平穩', '趨勢', '漲幅', '跌幅']
        self.assertTrue(any(keyword in insight_text for keyword in trend_keywords))
    
    def test_data_with_missing_optional_columns(self):
        """測試處理缺少可選欄位的資料"""
        minimal_data = pd.DataFrame({
            'date': pd.date_range(start='2024-01-01', periods=5),
            'avg_price': [25.0, 26.0, 24.0, 27.0, 25.5],
            'volume': [1500, 1600, 1400, 1700, 1550]
        })
        
        self.generator.load_data(minimal_data)
        statistics = self.generator.calculate_statistics()
        insights = self.generator.generate_insights()
        
        # 應該能正常處理缺少可選欄位的情況
        self.assertIsInstance(statistics, dict)
        self.assertIsInstance(insights, list)


if __name__ == '__main__':
    unittest.main()