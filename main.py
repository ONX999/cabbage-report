"""
主要執行腳本 - 自動化甘藍價格報表產生
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Optional
import argparse
import logging
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 設定路徑以便匯入自訂模組
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cabbage_report.data_fetcher import DataFetcher
from cabbage_report.report_logic import ReportGenerator
from cabbage_report.output_formatter import OutputFormatter


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    設定日誌記錄

    Args:
        log_level: 日誌等級

    Returns:
        Logger 實例
    """
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('cabbage_report.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


def generate_daily_report(target_date: Optional[datetime] = None,
                         output_dir: str = "output",
                         formats: list = None,
                         use_demo_data: bool = False) -> bool:
    """
    產生每日報表

    Args:
        target_date: 目標日期，預設為昨日
        output_dir: 輸出目錄
        formats: 輸出格式列表 ['excel', 'pdf']
        use_demo_data: 是否使用示範資料

    Returns:
        bool: 是否成功產生報表
    """
    logger = logging.getLogger(__name__)

    if target_date is None:
        # 預設使用昨日資料（因為當日資料可能尚未更新）
        target_date = datetime.now() - timedelta(days=1)

    if formats is None:
        formats = ['excel', 'pdf']

    try:
        logger.info(f"開始產生 {target_date.strftime('%Y-%m-%d')} 的甘藍價格報表")

        # 1. 擷取資料
        logger.info("正在擷取價格資料...")
        fetcher = DataFetcher(use_demo_data=use_demo_data)
        data = fetcher.fetch_daily_prices(target_date)

        if data.empty:
            logger.warning(f"查無 {target_date.strftime('%Y-%m-%d')} 的交易資料")
            return False

        logger.info(f"成功擷取 {len(data)} 筆交易資料")

        # 2. 分析資料
        logger.info("正在分析資料...")
        report_gen = ReportGenerator()
        report_gen.load_data(data)

        statistics = report_gen.calculate_statistics()
        insights = report_gen.generate_insights()
        summary_table = report_gen.generate_summary_table()

        logger.info("資料分析完成")

        # 3. 產生報表
        formatter = OutputFormatter(output_dir)
        output_files = []

        date_suffix = target_date.strftime("%Y%m%d")

        if 'excel' in formats:
            logger.info("正在產生Excel報表...")
            excel_filename = f"甘藍價格報表_{date_suffix}.xlsx"
            excel_path = formatter.export_to_excel(
                data, statistics, insights, summary_table, excel_filename
            )
            output_files.append(excel_path)
            logger.info(f"Excel報表已產生: {excel_path}")

        if 'pdf' in formats:
            logger.info("正在產生PDF報表...")
            pdf_filename = f"甘藍價格報表_{date_suffix}.pdf"
            pdf_path = formatter.export_to_pdf(
                statistics, insights, summary_table, pdf_filename
            )
            output_files.append(pdf_path)
            logger.info(f"PDF報表已產生: {pdf_path}")

        logger.info(f"報表產生完成，共產生 {len(output_files)} 個檔案")
        return True

    except Exception as e:
        logger.error(f"報表產生失敗: {e}")
        return False


def generate_historical_report(start_date: datetime, end_date: datetime,
                              output_dir: str = "output",
                              formats: list = None,
                              use_demo_data: bool = False) -> bool:
    """
    產生歷史期間報表

    Args:
        start_date: 起始日期
        end_date: 結束日期
        output_dir: 輸出目錄
        formats: 輸出格式列表
        use_demo_data: 是否使用示範資料

    Returns:
        bool: 是否成功產生報表
    """
    logger = logging.getLogger(__name__)

    if formats is None:
        formats = ['excel', 'pdf']

    try:
        logger.info(f"開始產生 {start_date.strftime('%Y-%m-%d')} 至 "
                   f"{end_date.strftime('%Y-%m-%d')} 的歷史報表")

        # 1. 擷取歷史資料
        logger.info("正在擷取歷史價格資料...")
        fetcher = DataFetcher(use_demo_data=use_demo_data)
        data = fetcher.fetch_historical_prices(start_date, end_date)

        if data.empty:
            logger.warning(f"查無指定期間的交易資料")
            return False

        logger.info(f"成功擷取 {len(data)} 筆歷史交易資料")

        # 2. 分析資料
        logger.info("正在分析歷史資料...")
        report_gen = ReportGenerator()
        report_gen.load_data(data)

        statistics = report_gen.calculate_statistics()
        insights = report_gen.generate_insights()
        summary_table = report_gen.generate_summary_table()

        logger.info("歷史資料分析完成")

        # 3. 產生報表
        formatter = OutputFormatter(output_dir)
        output_files = []

        date_range = f"{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"

        if 'excel' in formats:
            logger.info("正在產生Excel歷史報表...")
            excel_filename = f"甘藍價格歷史報表_{date_range}.xlsx"
            excel_path = formatter.export_to_excel(
                data, statistics, insights, summary_table, excel_filename
            )
            output_files.append(excel_path)
            logger.info(f"Excel歷史報表已產生: {excel_path}")

        if 'pdf' in formats:
            logger.info("正在產生PDF歷史報表...")
            pdf_filename = f"甘藍價格歷史報表_{date_range}.pdf"
            pdf_path = formatter.export_to_pdf(
                statistics, insights, summary_table, pdf_filename
            )
            output_files.append(pdf_path)
            logger.info(f"PDF歷史報表已產生: {pdf_path}")

        logger.info(f"歷史報表產生完成，共產生 {len(output_files)} 個檔案")
        return True

    except Exception as e:
        logger.error(f"歷史報表產生失敗: {e}")
        return False


def main():
    """主要執行函數"""
    parser = argparse.ArgumentParser(description='甘藍價格報表自動產生器')

    # 日誌等級
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                       default='INFO', help='日誌等級')

    subparsers = parser.add_subparsers(dest='command', help='可用指令')

    # 每日報表指令
    daily_parser = subparsers.add_parser('daily', help='產生每日報表')
    daily_parser.add_argument('--date', type=str, help='指定日期 (YYYY-MM-DD)，預設為昨日')
    daily_parser.add_argument('--output', type=str, default='output', help='輸出目錄')
    daily_parser.add_argument('--format', nargs='+', choices=['excel', 'pdf'],
                             default=['excel', 'pdf'], help='輸出格式')
    daily_parser.add_argument('--demo', action='store_true', help='使用示範資料模式')

    # 歷史報表指令
    history_parser = subparsers.add_parser('history', help='產生歷史期間報表')
    history_parser.add_argument('--start', type=str, required=True, help='起始日期 (YYYY-MM-DD)')
    history_parser.add_argument('--end', type=str, required=True, help='結束日期 (YYYY-MM-DD)')
    history_parser.add_argument('--output', type=str, default='output', help='輸出目錄')
    history_parser.add_argument('--format', nargs='+', choices=['excel', 'pdf'],
                               default=['excel', 'pdf'], help='輸出格式')
    history_parser.add_argument('--demo', action='store_true', help='使用示範資料模式')

    args = parser.parse_args()

    # 設定日誌
    logger = setup_logging(args.log_level)

    if args.command == 'daily':
        target_date = None
        if args.date:
            try:
                target_date = datetime.strptime(args.date, '%Y-%m-%d')
            except ValueError:
                logger.error("日期格式錯誤，請使用 YYYY-MM-DD 格式")
                sys.exit(1)

        success = generate_daily_report(target_date, args.output, args.format, 
                                       getattr(args, 'demo', False))
        sys.exit(0 if success else 1)

    elif args.command == 'history':
        try:
            start_date = datetime.strptime(args.start, '%Y-%m-%d')
            end_date = datetime.strptime(args.end, '%Y-%m-%d')
        except ValueError:
            logger.error("日期格式錯誤，請使用 YYYY-MM-DD 格式")
            sys.exit(1)

        if start_date > end_date:
            logger.error("起始日期不能晚於結束日期")
            sys.exit(1)

        success = generate_historical_report(start_date, end_date, args.output, args.format,
                                            getattr(args, 'demo', False))
        sys.exit(0 if success else 1)

    else:
        # 預設執行每日報表
        logger.info("執行預設每日報表產生")
        success = generate_daily_report()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()