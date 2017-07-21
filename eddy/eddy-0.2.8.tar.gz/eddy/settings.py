from eddy import defaults
import importlib.util

from pprint import pprint

def load_site_settings(logger, settings_path: str) -> dict:
    logger.debug("Loading user settings")
    spec = importlib.util.spec_from_file_location("settings", settings_path)
    settings = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(settings)

    return settings.__dict__

def merge_settings(logger, settings_path: str) -> dict:
    """merge default settings with user settings. User """
    settings = load_site_settings(logger, settings_path)
    defaults_dict = defaults.__dict__

    new_settings = {}
    for some_setting, value in defaults_dict.items():
        if some_setting[:2] == "__":
            continue
        #if some_setting[:2] == "__"
        new_settings[some_setting] = settings.get(some_setting, None) or value
   
    return new_settings

def merge(logger, file_data: dict, settings: dict) -> dict:
    """merge user settings with file settings"""
    merged = {}
    for key, value in settings.items():
        merged[key] = value

    for key, value in file_data.items():
        merged[key] = value

    return merged
