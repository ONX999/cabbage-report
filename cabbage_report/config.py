"""
配置管理模組 - 負責管理應用程式配置與設定
"""

import os
import logging
from typing import Dict, Optional
from dataclasses import dataclass, field

from dotenv import load_dotenv


@dataclass
class APIConfig:
    """API相關配置"""
    base_url: str = "https://data.coa.gov.tw/api/v1/AgriProductsTransType"
    api_key: Optional[str] = None
    timeout: int = 30
    retry_count: int = 3
    rate_limit_delay: float = 1.0  # 請求間隔秒數


@dataclass
class DataConfig:
    """資料處理相關配置"""
    cabbage_codes: list = field(default_factory=lambda: ['FC01', 'FC02', 'FC03'])
    max_query_days: int = 90
    cache_enabled: bool = True
    cache_duration_hours: int = 24


@dataclass
class ReportConfig:
    """報表相關配置"""
    output_formats: list = field(default_factory=lambda: ['excel', 'pdf'])
    excel_template_path: Optional[str] = None
    pdf_template_path: Optional[str] = None
    include_charts: bool = True
    chart_style: str = 'default'


@dataclass
class LoggingConfig:
    """日誌相關配置"""
    level: str = 'INFO'
    format: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    file_path: Optional[str] = None
    max_file_size_mb: int = 10
    backup_count: int = 5


@dataclass
class AppConfig:
    """應用程式主配置"""
    api: APIConfig = field(default_factory=APIConfig)
    data: DataConfig = field(default_factory=DataConfig)
    report: ReportConfig = field(default_factory=ReportConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    # 環境設定
    environment: str = 'production'
    debug: bool = False

    @classmethod
    def from_env(cls) -> 'AppConfig':
        """
        從環境變數載入配置

        Returns:
            AppConfig: 配置物件
        """
        # 載入 .env 檔案
        load_dotenv()

        config = cls()

        # API 配置
        config.api.api_key = os.getenv('CABBAGE_API_KEY')
        config.api.base_url = os.getenv('API_BASE_URL', config.api.base_url)
        config.api.timeout = int(os.getenv('API_TIMEOUT', config.api.timeout))
        config.api.retry_count = int(os.getenv('API_RETRY_COUNT', config.api.retry_count))

        # 資料配置
        cabbage_codes_env = os.getenv('CABBAGE_CODES')
        if cabbage_codes_env:
            config.data.cabbage_codes = cabbage_codes_env.split(',')

        config.data.max_query_days = int(os.getenv('MAX_QUERY_DAYS', config.data.max_query_days))
        config.data.cache_enabled = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'

        # 報表配置
        output_formats_env = os.getenv('OUTPUT_FORMATS')
        if output_formats_env:
            config.report.output_formats = output_formats_env.split(',')

        config.report.excel_template_path = os.getenv('EXCEL_TEMPLATE_PATH')
        config.report.pdf_template_path = os.getenv('PDF_TEMPLATE_PATH')
        config.report.include_charts = os.getenv('INCLUDE_CHARTS', 'true').lower() == 'true'

        # 日誌配置
        config.logging.level = os.getenv('LOG_LEVEL', config.logging.level).upper()
        config.logging.file_path = os.getenv('LOG_FILE_PATH')

        # 環境設定
        config.environment = os.getenv('ENVIRONMENT', config.environment)
        config.debug = os.getenv('DEBUG', 'false').lower() == 'true'

        return config

    def validate(self) -> bool:
        """
        驗證配置是否有效

        Returns:
            bool: 配置是否有效

        Raises:
            ValueError: 當配置無效時
        """
        errors = []

        # 驗證 API 配置
        if not self.api.base_url:
            errors.append("API base URL 不能為空")

        if self.api.timeout <= 0:
            errors.append("API timeout 必須大於 0")

        if self.api.retry_count < 0:
            errors.append("API retry count 不能為負數")

        # 驗證資料配置
        if not self.data.cabbage_codes:
            errors.append("甘藍品種代碼不能為空")

        if self.data.max_query_days <= 0:
            errors.append("最大查詢天數必須大於 0")

        # 驗證日誌配置
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.logging.level not in valid_log_levels:
            errors.append(f"日誌等級必須為 {valid_log_levels} 之一")

        if errors:
            raise ValueError("配置驗證失敗:\n" + "\n".join(f"- {error}" for error in errors))

        return True


def setup_logging(config: LoggingConfig) -> None:
    """
    設定日誌配置

    Args:
        config: 日誌配置物件
    """
    # 設定日誌等級
    level = getattr(logging, config.level, logging.INFO)

    # 設定日誌格式
    formatter = logging.Formatter(config.format)

    # 設定根日誌記錄器
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # 清除既有的處理器
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # 新增控制台處理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 新增檔案處理器 (如果指定了檔案路徑)
    if config.file_path:
        from logging.handlers import RotatingFileHandler

        # 確保日誌目錄存在
        log_dir = os.path.dirname(config.file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        file_handler = RotatingFileHandler(
            config.file_path,
            maxBytes=config.max_file_size_mb * 1024 * 1024,
            backupCount=config.backup_count,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)


def get_config() -> AppConfig:
    """
    取得應用程式配置

    Returns:
        AppConfig: 配置物件
    """
    config = AppConfig.from_env()
    config.validate()
    return config


# 全域配置實例 (延遲載入)
_config: Optional[AppConfig] = None


def get_global_config() -> AppConfig:
    """
    取得全域配置實例

    Returns:
        AppConfig: 全域配置物件
    """
    global _config
    if _config is None:
        _config = get_config()
        setup_logging(_config.logging)
    return _config