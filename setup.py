from setuptools import setup
from codecs import open
from os import path
from aiohttp_spyne import __version__

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='aiohttp-spyne',
    version=__version__,
    description='Aiohttp transport for Spyne RPC library',
    long_description=long_description,
    url='https://github.com/katajakasa/aiohttp-spyne',
    author='Tuomas Virtanen',
    author_email='katajakasa@gmail.com',
    license='LGPLv2.1',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
        'Operating System :: OS Independent',
        'Framework :: AsyncIO',
    ],
    packages=['aiohttp_spyne'],
    install_requires=['aiohttp>=3.0.0', 'spyne>=2.12.7']
)
