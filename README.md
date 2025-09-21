# CabbageReport

自動化每日「甘藍品種」批發/零售價格報表產生器
- 自動抓取農糧署 API 資料
- 支援 Excel 與 PDF 輸出格式
- 內建 GitHub Actions 自動排程功能

## 功能特色
- 每日自動更新價格資訊
- 支援多種輸出格式 (Excel, PDF)
- 自動化部署與排程
- 彈性化報表客製設定
- 智慧型資料分析與趨勢洞察
- 完整的錯誤處理與日誌記錄

## 安裝與設定

### 環境需求
- Python 3.8 或以上版本
- 網路連線 (用於存取農糧署 API)

### 安裝步驟
```bash
# 複製專案
git clone https://github.com/ONX999/cabbage-report.git
cd cabbage-report

# 安裝依賴套件
pip install -r requirements.txt
```

## 使用說明

### 基本用法

#### 產生每日報表
```bash
# 產生昨日的甘藍價格報表 (Excel + PDF)
python main.py daily

# 指定日期產生報表
python main.py daily --date 2024-01-15

# 只產生 Excel 格式
python main.py daily --format excel

# 指定輸出目錄
python main.py daily --output reports/

# 使用示範資料模式 (測試用)
python main.py daily --demo
```

#### 產生歷史期間報表
```bash
# 產生指定期間的歷史報表
python main.py history --start 2024-01-01 --end 2024-01-31

# 只產生 PDF 格式的歷史報表
python main.py history --start 2024-01-01 --end 2024-01-31 --format pdf
```

### 進階選項

#### 設定日誌等級
```bash
# 詳細日誌模式
python main.py --log-level DEBUG daily

# 僅顯示錯誤
python main.py --log-level ERROR daily
```

#### 查看說明
```bash
# 查看主要說明
python main.py --help

# 查看每日報表選項
python main.py daily --help

# 查看歷史報表選項
python main.py history --help
```

## 自動化排程

### GitHub Actions 自動執行

專案內建 GitHub Actions 工作流程，支援：

1. **每日自動執行**：每天早上 8:00 UTC (台灣時間 16:00) 自動產生前一日報表
2. **手動觸發執行**：可透過 GitHub 網頁介面手動執行

#### 手動執行步驟
1. 前往 GitHub 專案的 Actions 頁面
2. 選擇 "自動產生甘藍價格報表" 工作流程
3. 點選 "Run workflow"
4. 選擇報表類型、日期範圍與輸出格式
5. 執行完成後可在 Artifacts 下載報表檔案

### 本地排程設定

#### Linux/macOS (使用 crontab)
```bash
# 編輯 crontab
crontab -e

# 新增每日早上 8:00 執行
0 8 * * * cd /path/to/cabbage-report && python main.py daily
```

#### Windows (使用工作排程器)
1. 開啟「工作排程器」
2. 建立基本工作
3. 設定觸發程序為每日執行
4. 動作設定為執行 Python 腳本

## 報表內容說明

### Excel 報表包含
- **摘要報告**：統計數據與重要發現
- **市場統計**：各市場的詳細統計表
- **原始資料**：完整的交易資料明細

### PDF 報表包含
- 統計摘要
- 重要發現與趨勢分析
- 市場別統計表格

### 統計指標
- 平均價格、最高價、最低價
- 價格標準差與變異性分析
- 交易量統計
- 市場別比較分析
- 價格趨勢變化

## 輸出檔案命名規則

- 每日報表：`甘藍價格報表_YYYYMMDD.xlsx/pdf`
- 歷史報表：`甘藍價格歷史報表_YYYYMMDD_YYYYMMDD.xlsx/pdf`
- 日誌檔案：`cabbage_report.log`

## 錯誤處理

系統具備完整的錯誤處理機制：

1. **API 連線失敗**：自動切換至示範資料模式
2. **資料格式錯誤**：自動清理與標準化資料
3. **檔案寫入失敗**：詳細錯誤日誌記錄
4. **日期格式錯誤**：友善的錯誤提示

## 開發與貢獻

### 專案結構
```
cabbage-report/
├── cabbage_report/          # 主要程式模組
│   ├── __init__.py
│   ├── data_fetcher.py      # 資料擷取模組
│   ├── report_logic.py      # 報表分析邏輯
│   ├── output_formatter.py  # 輸出格式化
│   └── demo_data.py         # 示範資料產生
├── main.py                  # 主要執行腳本
├── requirements.txt         # 依賴套件清單
└── .github/workflows/       # GitHub Actions 設定
```

### 程式碼品質
- Pylint 評分：9.33/10
- 完整的類型提示
- 詳細的文件字串
- 錯誤處理與日誌記錄

## 授權與版權

本專案採用 MIT 授權條款。

## 作者

ONX999

## 更新日誌

### v0.1.0 (2024-09-21)
- 初始版本發布
- 實作基本的資料擷取與報表產生功能
- 新增 GitHub Actions 自動化工作流程
- 支援 Excel 與 PDF 輸出格式
- 完整的錯誤處理與日誌記錄