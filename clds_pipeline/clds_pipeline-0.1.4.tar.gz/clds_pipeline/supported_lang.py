"""An enum for all of the supported languages."""
from enum import unique, Enum

@unique
class SupportedLang(Enum):
    """Contains all supported languages"""
    ENGLISH = 'en'
    MAINLAND_CHINESE = 'zh-cn'
