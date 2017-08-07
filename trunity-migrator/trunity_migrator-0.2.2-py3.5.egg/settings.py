#####################################################
#                  EXAMPLE OF CONF FILE
# Attention!! The following settings must be filled
# before running this script!
#####################################################

# set here your user name and password:
TRUNITY_2_LOGIN = "my-trunity-2-login"
TRUNITY_2_PASSWORD = "secret"

TRUNITY_3_LOGIN = "my-trunity-3-login"
TRUNITY_3_PASSWORD = "verysecret"

# the name of Trunity book you need to import:
TRUNITY_2_BOOK_NAME = "Integrating Concepts in Biology"
TRUNITY_3_BOOK_NAME = "Integrating Concepts in Biology v13"

# All of these content types will be imported.
# You may comment out what you don't need:
CONTENT_TYPES = [
    "article",
    # "questionpool",
    # "exam"
    # "news",
    # "video",
    # "podcast",
    # "gallery",
    "game",
    # "assignment",
    # "whitepaper",
    # "casestudy",
    # "presentation",
    # "lecture",
    # "exercise",
    # "teachingunit",
]




TRUNITY_2_API_ENDPOINT = "http://api.trunity.net/v1/"
# TRUNITY_2_API_ENDPOINT = "http://api2.trunity.net/v1/"


TRUNITY_2_APP_CODE = 'your-app-code'


###############################################################################
#                           FIXERS SETTINGS
###############################################################################
FIXERS_ALLOWED = [
    'fix_img_src',
    'fix_table_width',
]


FIX_IMG_SRC = {
    "base_url": "http://www.trunity.net",
}

FIX_TABLE_WIDTH = {
    "old_widths": ["766", "770"],
    "new_widths": ["100%", "100%"],
}

