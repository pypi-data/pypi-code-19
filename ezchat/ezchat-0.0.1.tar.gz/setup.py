# necessary to push to PyPI
# cf. http://peterdowns.com/posts/first-time-with-pypi.html
# cf. https://tom-christie.github.io/articles/pypi/
# cf. https://pythonhosted.org/setuptools/setuptools.html
# cf. http://peterdowns.com/posts/first-time-with-pypi.html


from setuptools import setup
from distutils.util import convert_path

main_ns = {}
ver_path = convert_path('ezchat/__meta__.py')
with open(ver_path) as ver_file:
    exec(ver_file.read(), main_ns)

with open('README.rst') as f:
    long_description = f.read()

name = main_ns['__name__']
version = main_ns['__version__']


setup(
  name = name,
  packages = [name],
  version = version,
  description = 'easy instant chat webapp',
  long_description = long_description,
  author = 'oscar6echo',
  author_email = 'olivier.borderies@gmail.com',
  url = 'https://gitlab.com/oscar6echo/ezchat',
  download_url = 'https://gitlab.com/oscar6echo/ezchat/tarball/' + version,
  keywords = ['chat', 'notebook', 'javascript', 'vuejs'],
  license='MIT',
  classifiers = [ 'Development Status :: 4 - Beta',
                  'License :: OSI Approved :: MIT License',
                  'Programming Language :: Python :: 3.5',
                  'Programming Language :: Python :: 3.6'
  ],
  install_requires = [
    'Flask>=0.12.2',
    'Flask-SocketIO>=2.9.1'
  ],
  include_package_data=True,
  package_data={
    'templates':
         ['templates/info.html'
         ],
    'chatbox':
        ['chatbox/src/components/App/component.html',
         'chatbox/src/components/App/component.js',
         'chatbox/src/components/App/component.less',
         'chatbox/src/components/App/component.vue',
         'chatbox/src/components/ChatBox/component.html',
         'chatbox/src/components/ChatBox/component.js',
         'chatbox/src/components/ChatBox/component.less',
         'chatbox/src/components/ChatBox/component.vue',
         'chatbox/src/components/ChatLine/component.html',
         'chatbox/src/components/ChatLine/component.js',
         'chatbox/src/components/ChatLine/component.less',
         'chatbox/src/components/ChatLine/component.vue',
         'chatbox/src/css/main.less',
         'chatbox/src/css/variables.less',
         'chatbox/src/img/favicon.ico',
         'chatbox/src/main.js',
         'chatbox/src/top.html',
         'chatbox/.babelrc',
         'chatbox/index.html',
         'chatbox/package.json',
         'chatbox/README.md',
         'chatbox/webpack.config.js',
         'chatbox/dist/index.html',
         'chatbox/dist/assets/app.js',
         'chatbox/dist/assets/favicon.ico',
         'chatbox/dist/assets/style/app.css',
         'chatbox/dist/assets/style/app-less.css',
         'chatbox/dist/assets/font/fontawesome-webfont.eot',
         'chatbox/dist/assets/font/fontawesome-webfont.svg',
         'chatbox/dist/assets/font/fontawesome-webfont.ttf',
         'chatbox/dist/assets/font/fontawesome-webfont.woff',
         'chatbox/dist/assets/font/fontawesome-webfont.woff2',
         'chatbox/dist/assets/font/glyphicons-halflings-regular.eot',
         'chatbox/dist/assets/font/glyphicons-halflings-regular.svg',
         'chatbox/dist/assets/font/glyphicons-halflings-regular.ttf',
         'chatbox/dist/assets/font/glyphicons-halflings-regular.woff',
         'chatbox/dist/assets/font/glyphicons-halflings-regular.woff2'
        ]
    },
)

