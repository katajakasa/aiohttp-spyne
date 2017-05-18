from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='aiohttp-spyne',
    version='0.1.0',
    description='Aiohttp transport for Spyne RPC library',
    long_description=long_description,
    url='https://github.com/katajakasa/aiohttp-spyne',
    author='Tuomas Virtanen',
    author_email='katajakasa@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    packages=['aiohttp_spyne'],
    install_requires=['aiohttp>=2.0.0', 'spyne>=2.12.7']
)
