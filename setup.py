import os
import traversify

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "README.md")) as file:
    long_description = file.read()

setup(
    name='traversify',
    version=traversify.__version__,
    url='https://github.com/aelkner/traversify',
    license=traversify.__license__,
    long_description=long_description,
    long_description_content_type='text/markdown',
    description='Handy python classes for manipulating json data, providing syntactic sugar for less verbose, easier to write code.',
    author=traversify.__author__,
    author_email=traversify.__email__,
    packages=['traversify'],
    test_suite='traversify.tests',
    use_2to3=True,
    package_data={'': ['LICENSE', 'README.md']}
)
