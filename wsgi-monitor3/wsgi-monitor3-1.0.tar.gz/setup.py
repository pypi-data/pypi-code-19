from setuptools import setup

setup(
    name="wsgi-monitor3",
    version="1.0",
    description="Auto-reload WSGI server when files change - Python 3",
    author="Mark Flanagan",
    author_email="mark.mflanagan@gmail.com",
    url="https://github.com/flanaman/wsgi_monitor3",
    download_url="https://github.com/flanaman/wsgi_monitor3/archive/1.0.tar.gz",
    py_modules=[
        "wsgi_monitor3",
    ],
    classifiers=[
        'Programming Language :: Python',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Framework :: Django',
    ],
)
