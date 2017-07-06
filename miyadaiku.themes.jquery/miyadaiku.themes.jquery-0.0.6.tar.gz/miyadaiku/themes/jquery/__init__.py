from miyadaiku.core.contents import get_content_from_package, bin_loader
from miyadaiku.core import config

JQUERY_MIN = 'jquery.min.js'
JQUERY = 'jquery.js'
DEST_PATH = '/static/jquery/'

def load_package(site):
    f = site.config.getbool('/', 'jquery_compressed')
    jquery = JQUERY_MIN if f else JQUERY
    src_path = 'externals/'+jquery
    
    content = get_content_from_package(
        site, __name__, src_path, DEST_PATH+jquery, bin_loader)
    site.contents.add(content)
    site.config.add('/', {'jquery_path': DEST_PATH+jquery})
