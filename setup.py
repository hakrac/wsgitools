from setuptools import setup, find_packages
from lib import __version__

setup(
    name='wsgitoolbox',
    author='Hakim Rachidi',
    author_email='hakimrachidi02@gmail.com',
    version=__version__,
    description='Toolbox for python web development',
    install_requires=[
        'werkzeug>=0.16.0'
    ],
    packages=find_packages()
)