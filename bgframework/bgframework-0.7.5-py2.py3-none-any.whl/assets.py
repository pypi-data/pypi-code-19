from django_assets import Bundle, register

js = Bundle(
    'bower/jquery/dist/jquery.min.js',
    # 'bootstrap/js/bootstrap.min.js',
    'bower/bootstrap/dist/js/bootstrap.min.js',
    'ajaxcsrftoken.js',
    # 'ace/ace.min.js',
    # 'ace/ace-elements.min.js',
    # 'ace/ace-extra.min.js',
    'bower/tkliuxing-ace/js/ace.min.js',
    'bower/tkliuxing-ace/js/ace-elements.min.js',
    'bower/tkliuxing-ace/js/ace-extra.min.js',
    'bgframework.js',
    filters='jsmin', output='bgframework/packed.js'
)

css = Bundle(
    'bower/bootstrap/dist/css/bootstrap.min.css',
    # 'ace/ace.css',
    # 'ace/ace-rtl.min.css',
    # 'ace/ace-skins.css',
    'bower/tkliuxing-ace/css/ace.css',
    'bower/tkliuxing-ace/css/ace-rtl.css',
    'bower/tkliuxing-ace/css/ace-skins.css',
    'bower/font-awesome/css/font-awesome.min.css',
    'base.css',
    filters='cssmin,cssrewrite', output='bgframework/packed.css'
)

register('bgframework_js', js)
register('bgframework_css', css)
