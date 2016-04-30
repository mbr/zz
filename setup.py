#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from setuptools import setup, find_packages


def read(fname):
    buf = open(os.path.join(os.path.dirname(__file__), fname), 'rb').read()
    return buf.decode('utf8')


setup(name='zz',
      version='0.1.dev1',
      description='A plaintext time-tracking tool for freelance work',
      long_description=read('README.rst'),
      author='Marc Brinkmann',
      author_email='git@marcbrinkmann.de',
      url='https://github.com/mbr/zz',
      license='MIT',
      packages=find_packages(exclude=['tests']),
      install_requires=['click', 'arrow'],
      entry_points={
          'console_scripts': [
              'zz = zz.cli:cli',
          ],
      },
      classifiers=[
          'Programming Language :: Python :: 3',
      ])
