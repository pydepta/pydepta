try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='pydepta',
      version='0.1',
      description="A Python implementation of DEPTA",
      long_description="A Python implementation of DEPTA (Data Extraction with Partial Tree Alignment",
      author="Terry Peng",
      author_email="pengtaoo@gmail.com",
      install_requires=['w3lib', 'pyquery'],
      py_modules=['depta', 'mdr', 'htmls', 'trees']
)