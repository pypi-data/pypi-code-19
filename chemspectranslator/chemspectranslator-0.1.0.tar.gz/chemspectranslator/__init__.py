try:
    from .google_sheets_api import Translator
except:
    from .local_csv import Translator

import _console