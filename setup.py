""" Brazillian Football CLI setup.py
"""
from setuptools import setup, find_packages

setup(
    name="brazfoot_cli",
    version="0.1.0",
    description="Brazillian football web scrapper command-line interface (CLI)",
    packages=find_packages(),
    install_requires=[
        "click",
        "questionary",
        "beautifulsoup4",
        "lxml",
        "requests_futures"
    ],
    entry_points={
        'console_scripts': ['brazfoot_cli=src.main:main']
    },
    author="Krauss",
    license="MIT"
)