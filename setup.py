#!/usr/bin/env python
from setuptools import setup, find_packages
setup(
    name = "testudo-crawler",
    version = "0.1",
    author = "Brady Law",
    author_email = "brady@bablhost.com",
    description = "Scrapes the University of Maryland College Park course listings off of Testudo.",
    keywords = "testudo umd maryland course scrape crawler",
    url = "https://github.com/babldev/testudo-crawler",

    packages = find_packages('src'),  # include all packages under src
    package_dir = {'':'src'},

    test_suite='test',
)
