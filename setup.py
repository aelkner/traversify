#!/usr/bin/env/python

import os
from traversify import Traverser

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open(os.path.join(os.path.dirname(__file__), "README.rst")) as file:
    long_description = file.read()

setup(
    name='traversify',
    version=metadata.__version__,
    url='https://github.com/aelkner/traversify',
    license=metadata.__license__,
    long_description=long_description,
    description='Handy python wrapper class for json data that makes it easier to traverse to items and list elements.',
    author=metadata.__author__,
    author_email=metadata.__email__,
    packages=['traversify'],
    test_suite='traversify.tests',
    use_2to3=True,
    package_data={'': ['LICENSE', 'README.rst']}
)
