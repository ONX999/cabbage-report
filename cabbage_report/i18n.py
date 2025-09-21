"""
國際化(i18n)支援模組 - 提供多語言支援，預設為繁體中文
"""

import gettext
import os
from typing import Optional

# 支援的語言列表
SUPPORTED_LANGUAGES = {
    'zh_TW': '繁體中文',
    'en': 'English'
}

# 預設語言為繁體中文
DEFAULT_LANGUAGE = 'zh_TW'

class I18nManager:
    """多語言管理器"""
    
    def __init__(self, language: Optional[str] = None):
        """
        初始化多語言管理器
        
        Args:
            language: 語言代碼，若未指定則使用預設語言(繁體中文)
        """
        self.language = language or DEFAULT_LANGUAGE
        self._translator = None
        self._setup_translator()
    
    def _setup_translator(self):
        """設定翻譯器"""
        try:
            locale_dir = os.path.join(os.path.dirname(__file__), 'locale')
            self._translator = gettext.translation(
                'cabbage_report', 
                localedir=locale_dir, 
                languages=[self.language],
                fallback=True
            )
        except Exception:
            # 如果翻譯檔案不存在，使用空的翻譯器
            self._translator = gettext.NullTranslations()
    
    def gettext(self, message: str) -> str:
        """
        翻譯訊息
        
        Args:
            message: 要翻譯的訊息
            
        Returns:
            翻譯後的訊息
        """
        if self._translator:
            return self._translator.gettext(message)
        return message
    
    def set_language(self, language: str):
        """
        設定語言
        
        Args:
            language: 語言代碼
        """
        if language in SUPPORTED_LANGUAGES:
            self.language = language
            self._setup_translator()

# 全域的i18n管理器實例，預設使用繁體中文
_global_i18n = I18nManager(DEFAULT_LANGUAGE)

def _(message: str) -> str:
    """
    翻譯訊息的快捷函數
    
    Args:
        message: 要翻譯的訊息
        
    Returns:
        翻譯後的訊息
    """
    return _global_i18n.gettext(message)

def set_language(language: str):
    """
    設定全域語言
    
    Args:
        language: 語言代碼
    """
    _global_i18n.set_language(language)

def get_current_language() -> str:
    """
    取得目前語言
    
    Returns:
        目前的語言代碼
    """
    return _global_i18n.language

def get_supported_languages() -> dict:
    """
    取得支援的語言列表
    
    Returns:
        支援的語言字典 {語言代碼: 語言名稱}
    """
    return SUPPORTED_LANGUAGES.copy()