from setuptools import setup, find_packages
from distutils.extension import Extension
from Cython.Distutils import build_ext

setup(name='pydepta',
      version='0.1',
      description="A Python implementation of DEPTA",
      long_description="A Python implementation of DEPTA (Data Extraction with Partial Tree Alignment",
      author="Terry Peng",
      author_email="pengtaoo@gmail.com",
      install_requires=['w3lib', 'pyquery'],
      packages=find_packages(),
      cmdclass={'build_ext': build_ext},
      ext_modules=[
          Extension("pydepta.trees_cython", ['pydepta/trees_cython.pyx'])
      ]
)
