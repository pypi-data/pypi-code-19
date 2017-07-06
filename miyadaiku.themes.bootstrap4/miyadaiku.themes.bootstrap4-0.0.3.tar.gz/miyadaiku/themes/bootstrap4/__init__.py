from miyadaiku.core.contents import get_content_from_package, bin_loader
from miyadaiku.core import config

CSS_MIN = 'bootstrap.min.css'
CSS = 'bootstrap.css'

JS_MIN = 'bootstrap.min.js'
JS = 'bootstrap.js'

DEST_PATH = '/static/bootstrap4/'

def load_package(site):
    f = site.config.getbool('/', 'bootstrap4_compressed')

    css = CSS_MIN if f else CSS
    css_path = 'externals/css/'+css

    content = get_content_from_package(site, __name__, css_path, DEST_PATH+css, bin_loader)
    site.contents.add(content)
    site.config.add('/', {'bootstrap4_css_path': DEST_PATH+css})


    js = JS_MIN if f else JS
    js_path = 'externals/js/'+js
    
    content = get_content_from_package(site, __name__, js_path, DEST_PATH+js, bin_loader)
    site.contents.add(content)
    site.config.add('/', {'bootstrap4_js_path': DEST_PATH+js})
