"""
CabbageReport - 自動化甘藍品種批發/零售價格報表產生器

預設使用繁體中文介面
"""

__version__ = '0.1.0'
__author__ = 'ONX999'

# 匯入並初始化 i18n 模組，預設為繁體中文
from .i18n import _, set_language, get_current_language, get_supported_languages

# 確保預設語言為繁體中文
set_language('zh_TW')