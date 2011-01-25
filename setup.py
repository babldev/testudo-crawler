#!/usr/bin/env python

from distutils.core import setup

setup(name='testudo-crawl',
      version='0.1',
      description='Scrapes course data from the University of Maryland College Park Testudo system.',
      author='Brady Law',
      author_email='brady@bablhost.com',
      url='https://github.com/babldev/testudo-crawler',
      package_dir={'': 'src'},
      py_modules=[
              'testudo_crawl',
          ],
     )