from setuptools import setup, find_packages
from distutils.extension import Extension
try:
    from Cython.Distutils import build_ext
except ImportError:
    use_cython = False
else:
    use_cython = True

cmdclass = {}
ext_modules = []

if use_cython:
    ext_modules.append(Extension("pydepta.trees_cython", ['pydepta/trees_cython.pyx']))
    cmdclass.update({'build_ext': build_ext})
else:
    ext_modules.append(Extension("pydepta.trees_cython", ['pydepta/trees_cython.c']))

setup(name='pydepta',
      version='0.2',
      description="A Python implementation of DEPTA",
      long_description="A Python implementation of DEPTA (Data Extraction with Partial Tree Alignment)",
      author="Terry Peng",
      author_email="pengtaoo@gmail.com",
      install_requires=['w3lib', 'scrapely'],
      packages=find_packages(),
      cmdclass=cmdclass,
      ext_modules=ext_modules
)
