#!/usr/bin/env python3
"""
CabbageReport i18n 功能示範

此範例展示如何使用 CabbageReport 的國際化功能，
預設語言為繁體中文，並支援語言切換。
"""

import sys
import os
# 將上層目錄加入路徑以便匯入 cabbage_report
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import cabbage_report
from cabbage_report import _, set_language, get_current_language
from cabbage_report.report_logic import ReportGenerator

def main():
    """主要示範程序"""
    print("=== CabbageReport 國際化功能示範 ===")
    print(f"版本: {cabbage_report.__version__}")
    print(f"預設語言: {get_current_language()}")
    
    # 展示繁體中文介面（預設）
    print("\n--- 繁體中文介面 ---")
    generator = ReportGenerator()
    try:
        generator.calculate_statistics()
    except ValueError as e:
        print(f"錯誤訊息: {e}")
    
    # 切換到英文
    print("\n--- English Interface ---")
    set_language('en')
    print(f"Current Language: {get_current_language()}")
    try:
        generator.generate_insights()
    except ValueError as e:
        print(f"Error Message: {e}")
    
    # 切換回繁體中文
    print("\n--- 切換回繁體中文 ---")
    set_language('zh_TW')
    print(f"目前語言: {get_current_language()}")
    print("示範完成！")

if __name__ == "__main__":
    main()