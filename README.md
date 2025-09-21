# CabbageReport

自動化甘藍品種批發/零售價格報表產生器

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 專案簡介

CabbageReport 是一個自動化的甘藍價格分析與報表生成系統，能夠：

- 🔄 **自動抓取農糧署 API 資料** - 從台灣行政院農業委員會農糧署取得最新價格資料
- 📊 **支援多種輸出格式** - Excel 與 PDF 格式報表，含圖表分析
- ⚡ **自動化部署與排程** - 內建 GitHub Actions 自動排程功能
- 🎯 **彈性化報表客製設定** - 可配置報表內容與格式
- 📈 **深度價格分析** - 統計分析、趨勢預測與市場洞察

## 功能特色

### 📋 資料擷取
- 支援每日、週、月報表生成
- 歷史資料區間查詢 (最多90天)
- 自動重試與錯誤處理
- 資料驗證與清理

### 📊 分析功能
- 基本統計分析 (平均價、最高價、最低價、標準差)
- 價格趨勢分析與變化率計算
- 市場比較分析
- 價格波動性指標
- 交易量統計分析
- 智能洞察生成

### 📄 報表輸出
- **Excel 格式**：包含多個工作表、圖表與格式化
- **PDF 格式**：專業排版與表格呈現
- 可配置的報表模板
- 自動檔案命名與組織

### ⚙️ 系統特性
- 完整的配置管理系統
- 結構化日誌記錄
- 命令列介面
- 單元測試覆蓋
- 錯誤處理與重試機制

## 安裝說明

### 環境需求
- Python 3.8 或更高版本
- pip 套件管理器

### 快速安裝

```bash
# 克隆專案
git clone https://github.com/ONX999/cabbage-report.git
cd cabbage-report

# 安裝相依套件
pip install -r requirements.txt

# 或使用 setup.py 安裝
pip install -e .
```

### 開發環境安裝

```bash
# 安裝開發相依套件
pip install -e ".[dev]"
```

## 配置設定

### 1. 環境變數配置

複製範例配置檔案：
```bash
cp .env.example .env
```

編輯 `.env` 檔案設定必要參數：
```bash
# API 設定
CABBAGE_API_KEY=your_api_key_here

# 報表設定
OUTPUT_FORMATS=excel,pdf
LOG_LEVEL=INFO
```

### 2. 主要配置參數

| 參數 | 說明 | 預設值 |
|------|------|--------|
| `CABBAGE_API_KEY` | 農糧署 API 金鑰 | 無 |
| `OUTPUT_FORMATS` | 輸出格式 | excel,pdf |
| `MAX_QUERY_DAYS` | 最大查詢天數 | 90 |
| `LOG_LEVEL` | 日誌等級 | INFO |
| `INCLUDE_CHARTS` | 是否包含圖表 | true |

## 使用說明

### 命令列介面

```bash
# 生成今日報表
cabbage-report --type daily

# 生成指定日期報表
cabbage-report --type daily --date 2024-01-15

# 生成週報表
cabbage-report --type weekly

# 生成月報表
cabbage-report --type monthly --year 2024 --month 1

# 生成歷史報表
cabbage-report --type historical --start-date 2024-01-01 --end-date 2024-01-31

# 指定輸出格式與目錄
cabbage-report --type daily --formats excel pdf --output-dir ./my_reports
```

### Python API 使用

```python
from datetime import datetime
from cabbage_report.main import CabbageReportGenerator

# 初始化報表生成器
generator = CabbageReportGenerator()

# 生成每日報表
output_files = generator.generate_daily_report(
    date=datetime(2024, 1, 15),
    output_dir='./reports',
    formats=['excel', 'pdf']
)

# 生成歷史報表
output_files = generator.generate_historical_report(
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 1, 31),
    output_dir='./reports'
)
```

### 進階使用

```python
from cabbage_report.data_fetcher import DataFetcher
from cabbage_report.report_logic import ReportGenerator
from cabbage_report.export import export_report

# 自訂資料處理流程
fetcher = DataFetcher(api_key="your_api_key")
generator = ReportGenerator()

# 擷取資料
data = fetcher.fetch_daily_prices()

# 分析資料
generator.load_data(data)
statistics = generator.calculate_statistics()
insights = generator.generate_insights()

# 匯出報表
export_report(data, statistics, insights, 'report.xlsx', 'excel')
```

## 報表內容

### Excel 報表包含
1. **報表摘要** - 基本統計與重要洞察
2. **原始資料** - 完整的價格資料表
3. **統計分析** - 詳細的統計指標
4. **價格趨勢圖** - 視覺化圖表 (可選)

### PDF 報表包含
1. **統計摘要表** - 關鍵指標概覽
2. **重要洞察** - 文字化分析結果
3. **資料摘要** - 資料來源與覆蓋範圍
4. **資料樣本** - 部分原始資料展示

## 自動化部署

### GitHub Actions 排程

專案包含預配置的 GitHub Actions 工作流程：

- **每日自動執行** - 自動生成每日報表
- **週報與月報** - 定期生成彙總報表
- **程式碼品質檢查** - 自動執行 linting 與測試

### 本地排程設定

使用 cron 設定定時執行：
```bash
# 每日早上 8 點生成報表
0 8 * * * /path/to/python /path/to/cabbage-report/cabbage_report/main.py --type daily
```

## 開發指南

### 執行測試

```bash
# 執行所有測試
python -m pytest tests/

# 執行特定測試檔案
python -m pytest tests/test_data_fetcher.py

# 執行測試並顯示覆蓋率
python -m pytest tests/ --cov=cabbage_report
```

### 程式碼品質檢查

```bash
# 執行 linting
pylint cabbage_report/

# 執行程式碼格式化
black cabbage_report/
isort cabbage_report/
```

### 專案結構

```
cabbage-report/
├── cabbage_report/          # 主要程式碼
│   ├── __init__.py         # 套件初始化
│   ├── main.py             # 主程式入口
│   ├── config.py           # 配置管理
│   ├── data_fetcher.py     # 資料擷取
│   ├── report_logic.py     # 報表邏輯
│   └── export.py           # 報表匯出
├── tests/                   # 測試檔案
├── .github/workflows/       # GitHub Actions
├── requirements.txt         # Python 相依套件
├── setup.py                # 安裝配置
├── .env.example            # 環境變數範例
└── README.md               # 專案說明
```

## API 資料來源

本專案使用台灣行政院農業委員會農糧署開放資料：
- **API 端點**：`https://data.coa.gov.tw/api/v1/AgriProductsTransType`
- **資料內容**：甘藍品種批發市場交易行情
- **更新頻率**：每日更新
- **資料格式**：JSON

## 授權條款

本專案採用 MIT 授權條款。詳見 [LICENSE](LICENSE) 檔案。

## 貢獻指南

歡迎提交 Issue 和 Pull Request！

1. Fork 專案
2. 建立功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交變更 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 開啟 Pull Request

## 變更日誌

### v0.1.0 (2024-01-15)
- ✨ 初始版本發布
- 📊 完整的資料擷取與分析功能
- 📄 Excel 與 PDF 報表匯出
- ⚙️ 配置管理系統
- 🧪 完整的測試覆蓋
- 📚 詳細的使用文件

## 常見問題

### Q: 如何取得 API 金鑰？
A: 請至農糧署開放資料平台申請 API 金鑰。

### Q: 支援哪些 Python 版本？
A: 支援 Python 3.8 以上版本。

### Q: 報表無法生成怎麼辦？
A: 檢查 API 金鑰設定、網路連線，並查看日誌檔案中的錯誤訊息。

## 聯絡資訊

- **GitHub Issues**: [https://github.com/ONX999/cabbage-report/issues](https://github.com/ONX999/cabbage-report/issues)
- **作者**: ONX999