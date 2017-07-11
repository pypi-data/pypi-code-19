# import os
from setuptools import setup, find_packages

# here = os.path.abspath(os.path.dirname(__file__))
# version_path = os.path.join(here, 'version.txt')
# version = open(version_path).read().strip()

requires = [ 'numpy', 'pyperclip>=1.5.0', 'mahotas', 'matplotlib>=2.0.0' ]

try:
    import cv2
    ver = cv2.__version__[0]
    if int(ver) < 3:
        raise ImportError("[*] Error: OpenCV version requirement not met: must have 3 or higher")

except ImportError:
    raise ImportError("[*] Error: Could not find a working instance of OpenCV")

except:
    raise ImportError("[*] Error: Problem checking for OpenCV install on your system.")

else:
    print("[+] Valid OpenCV installation located.")

CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Intended Audience :: Science/Research',
    'Intended Audience :: Telecommunications Industry',
    'Natural Language :: English',
    'Operating System :: Linux',
    'Operating System :: Windows',
    'Topic :: Scientific/Engineering :: Image Recognition',
    'Topic :: Scientific/Engineering :: Information Analysis',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Multimedia :: Images',
    'Topic :: Multimedia :: Video',
    'Topic :: Utilities',
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.6",
]

# wsdl_files = [ 'wsdl/' + item for item in os.listdir('wsdl') ]

setup(
      name='vtools',
      version='0.0.32',
      description='Visual Tools - an object oriented approach to image processing and analysis.',
      long_description=open('README.rst', 'r').read(),
      author='Vic Jackson',
      author_email='mr.vic.jackson@gmail.com',
      maintainer='Vic Jackson',
      maintainer_email='mr.vic.jackson@gmail.com',
      license='MIT',
      keywords=['vtools', 'vimg', 'OpenCV', 'image analysis', 'contours', 'computer', 'vision', 'visual',
                'contour', 'analysis', 'image', 'processing', 'image', 'processing', 'OO', 'Object', 'Oriented'],
      url='https://github.com/etherwar/vtools',
      download_url='https://github.com/etherwar/vtools/archive/master.zip',
      zip_safe=False,
      packages=find_packages(exclude=['docs', 'examples', 'tests']),
      install_requires=requires,
      include_package_data=True,
     )




