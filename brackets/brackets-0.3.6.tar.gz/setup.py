from distutils.core import setup

setup(
    name='brackets',
    version='0.3.6',
    author='Pooya Eghbali',
    author_email='persian.writer@gmail.com',
    packages=['brackets'],
    url='https://github.com/pooya-eghbali/brackets',
    license='BSD',
    description="""Use brackets instead of indentation. Plus much more candies.""",
    classifiers= ['Intended Audience :: Developers',
                  'License :: OSI Approved :: BSD License',
                  'Operating System :: OS Independent',
                  'Programming Language :: Python :: 2',
                  'Programming Language :: Python :: 3'],
    keywords = 'brackets, indentation, indent, indenting, parser, encoding',
    platforms = ["Any"],
    long_description=open('README.txt').read(),
    install_requires=['yapf','regex'],
)
