"""
主程式模組 - 甘藍價格報表生成器主要入口點
"""

import logging
import os
import sys
from datetime import datetime, timedelta
from typing import List, Optional
import argparse

from .config import get_global_config, AppConfig
from .data_fetcher import DataFetcher
from .report_logic import ReportGenerator
from .export import export_report


logger = logging.getLogger(__name__)


class CabbageReportGenerator:
    """
    甘藍報表生成器主類別

    整合資料擷取、分析處理與報表匯出功能
    """

    def __init__(self, config: Optional[AppConfig] = None):
        """
        初始化報表生成器

        Args:
            config: 應用程式配置，若未提供則使用預設配置
        """
        self.config = config or get_global_config()
        self.data_fetcher = DataFetcher(api_key=self.config.api.api_key)
        self.report_generator = ReportGenerator()

        logger.info("甘藍報表生成器已初始化")

    def generate_daily_report(self,
                            date: Optional[datetime] = None,
                            output_dir: str = './reports',
                            formats: Optional[List[str]] = None) -> List[str]:
        """
        生成每日報表

        Args:
            date: 指定日期，若未指定則使用今日
            output_dir: 輸出目錄
            formats: 輸出格式列表，若未指定則使用配置中的格式

        Returns:
            List[str]: 生成的報表檔案路徑列表

        Raises:
            Exception: 當報表生成失敗時
        """
        if date is None:
            date = datetime.now()

        if formats is None:
            formats = self.config.report.output_formats

        logger.info("開始生成 %s 的每日報表", date.strftime('%Y-%m-%d'))

        try:
            # 1. 擷取資料
            logger.info("正在擷取價格資料...")
            data = self.data_fetcher.fetch_daily_prices(date)

            if data.empty:
                logger.warning("指定日期無資料，報表生成中止")
                return []

            # 2. 載入資料到報表生成器
            self.report_generator.load_data(data)

            # 3. 計算統計數據
            logger.info("正在計算統計數據...")
            statistics = self.report_generator.calculate_statistics()

            # 4. 生成洞察
            logger.info("正在生成洞察分析...")
            insights = self.report_generator.generate_insights()

            # 5. 匯出報表
            return self._export_reports(
                data, statistics, insights,
                output_dir, date, formats, 'daily'
            )

        except Exception as e:
            logger.error("生成每日報表時發生錯誤: %s", str(e))
            raise

    def generate_historical_report(self,
                                 start_date: datetime,
                                 end_date: datetime,
                                 output_dir: str = './reports',
                                 formats: Optional[List[str]] = None) -> List[str]:
        """
        生成歷史期間報表

        Args:
            start_date: 起始日期
            end_date: 結束日期
            output_dir: 輸出目錄
            formats: 輸出格式列表

        Returns:
            List[str]: 生成的報表檔案路徑列表
        """
        if formats is None:
            formats = self.config.report.output_formats

        period_str = f"{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}"
        logger.info("開始生成歷史報表: %s", period_str)

        try:
            # 1. 擷取歷史資料
            logger.info("正在擷取歷史價格資料...")
            data = self.data_fetcher.fetch_historical_prices(start_date, end_date)

            if data.empty:
                logger.warning("指定期間無資料，報表生成中止")
                return []

            # 2. 載入資料到報表生成器
            self.report_generator.load_data(data)

            # 3. 計算統計數據
            logger.info("正在計算統計數據...")
            statistics = self.report_generator.calculate_statistics()

            # 4. 生成洞察
            logger.info("正在生成洞察分析...")
            insights = self.report_generator.generate_insights()

            # 5. 匯出報表
            return self._export_reports(
                data, statistics, insights,
                output_dir, start_date, formats, 'historical',
                end_date=end_date
            )

        except Exception as e:
            logger.error("生成歷史報表時發生錯誤: %s", str(e))
            raise

    def generate_weekly_report(self,
                             week_start: Optional[datetime] = None,
                             output_dir: str = './reports',
                             formats: Optional[List[str]] = None) -> List[str]:
        """
        生成週報表

        Args:
            week_start: 週起始日期，若未指定則使用本週
            output_dir: 輸出目錄
            formats: 輸出格式列表

        Returns:
            List[str]: 生成的報表檔案路徑列表
        """
        if week_start is None:
            today = datetime.now()
            # 計算本週一
            week_start = today - timedelta(days=today.weekday())

        # 計算週結束日期
        week_end = week_start + timedelta(days=6)

        logger.info("生成週報表: %s 至 %s",
                   week_start.strftime('%Y-%m-%d'),
                   week_end.strftime('%Y-%m-%d'))

        return self.generate_historical_report(week_start, week_end, output_dir, formats)

    def generate_monthly_report(self,
                              year: Optional[int] = None,
                              month: Optional[int] = None,
                              output_dir: str = './reports',
                              formats: Optional[List[str]] = None) -> List[str]:
        """
        生成月報表

        Args:
            year: 年份，若未指定則使用當年
            month: 月份，若未指定則使用當月
            output_dir: 輸出目錄
            formats: 輸出格式列表

        Returns:
            List[str]: 生成的報表檔案路徑列表
        """
        now = datetime.now()
        if year is None:
            year = now.year
        if month is None:
            month = now.month

        # 計算月份起始和結束日期
        month_start = datetime(year, month, 1)
        if month == 12:
            month_end = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = datetime(year, month + 1, 1) - timedelta(days=1)

        logger.info("生成月報表: %d年%d月", year, month)

        return self.generate_historical_report(month_start, month_end, output_dir, formats)

    def _export_reports(self,
                       data, statistics, insights,
                       output_dir: str,
                       date: datetime,
                       formats: List[str],
                       report_type: str,
                       end_date: Optional[datetime] = None) -> List[str]:
        """
        匯出報表到指定格式

        Args:
            data: 價格資料
            statistics: 統計數據
            insights: 洞察分析
            output_dir: 輸出目錄
            date: 報表日期
            formats: 輸出格式列表
            report_type: 報表類型
            end_date: 結束日期 (用於歷史報表)

        Returns:
            List[str]: 生成的檔案路徑列表
        """
        # 確保輸出目錄存在
        os.makedirs(output_dir, exist_ok=True)

        output_files = []

        # 產生檔案名稱
        if end_date:
            filename_base = f"cabbage_report_{report_type}_{date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
        else:
            filename_base = f"cabbage_report_{report_type}_{date.strftime('%Y%m%d')}"

        for format_type in formats:
            try:
                if format_type.lower() == 'excel':
                    file_path = os.path.join(output_dir, f"{filename_base}.xlsx")
                    export_report(
                        data, statistics, insights, file_path,
                        'excel', self.config.report.include_charts
                    )
                    output_files.append(file_path)

                elif format_type.lower() == 'pdf':
                    file_path = os.path.join(output_dir, f"{filename_base}.pdf")
                    export_report(data, statistics, insights, file_path, 'pdf')
                    output_files.append(file_path)

                else:
                    logger.warning("不支援的輸出格式: %s", format_type)

            except Exception as e:
                logger.error("匯出 %s 格式時發生錯誤: %s", format_type, str(e))

        logger.info("報表已匯出，共 %d 個檔案", len(output_files))
        return output_files


def main():
    """主程式入口點"""
    parser = argparse.ArgumentParser(description='甘藍價格報表生成器')

    # 報表類型
    parser.add_argument('--type', choices=['daily', 'weekly', 'monthly', 'historical'],
                       default='daily', help='報表類型')

    # 日期參數
    parser.add_argument('--date', type=str, help='指定日期 (YYYY-MM-DD)')
    parser.add_argument('--start-date', type=str, help='起始日期 (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, help='結束日期 (YYYY-MM-DD)')
    parser.add_argument('--year', type=int, help='年份')
    parser.add_argument('--month', type=int, help='月份')

    # 輸出設定
    parser.add_argument('--output-dir', default='./reports', help='輸出目錄')
    parser.add_argument('--formats', nargs='+', choices=['excel', 'pdf'],
                       help='輸出格式')

    # 其他選項
    parser.add_argument('--debug', action='store_true', help='啟用除錯模式')

    args = parser.parse_args()

    try:
        # 初始化配置和報表生成器
        config = get_global_config()
        if args.debug:
            config.debug = True
            config.logging.level = 'DEBUG'

        generator = CabbageReportGenerator(config)

        # 解析日期參數
        def parse_date(date_str):
            return datetime.strptime(date_str, '%Y-%m-%d') if date_str else None

        # 根據報表類型生成報表
        if args.type == 'daily':
            date = parse_date(args.date)
            output_files = generator.generate_daily_report(
                date=date,
                output_dir=args.output_dir,
                formats=args.formats
            )

        elif args.type == 'weekly':
            week_start = parse_date(args.start_date)
            output_files = generator.generate_weekly_report(
                week_start=week_start,
                output_dir=args.output_dir,
                formats=args.formats
            )

        elif args.type == 'monthly':
            output_files = generator.generate_monthly_report(
                year=args.year,
                month=args.month,
                output_dir=args.output_dir,
                formats=args.formats
            )

        elif args.type == 'historical':
            if not args.start_date or not args.end_date:
                parser.error("歷史報表需要指定起始日期和結束日期")

            start_date = parse_date(args.start_date)
            end_date = parse_date(args.end_date)

            output_files = generator.generate_historical_report(
                start_date=start_date,
                end_date=end_date,
                output_dir=args.output_dir,
                formats=args.formats
            )

        # 顯示結果
        if output_files:
            print(f"報表生成成功！生成了 {len(output_files)} 個檔案：")
            for file_path in output_files:
                print(f"  - {file_path}")
        else:
            print("無資料可生成報表")

    except KeyboardInterrupt:
        print("\n程式被使用者中斷")
        sys.exit(1)
    except Exception as e:
        logger.error("程式執行時發生錯誤: %s", str(e))
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()