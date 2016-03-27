#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of DocOps, a documentation operations support library.
# Copyright © 2016 seamus tuohy, <s2e@seamustuohy.com>
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the included LICENSE file for details.

from distutils.core import setup

setup(name='DocOps',
      version='0.1.0',
      description='Documentation operations support library.',
      author='Seamus Tuohy',
      author_email='s2e@seamustuohy.com',
      url='https://github.com/elationfoundation/DocOps',
      packages=['docops'],
      keywords='documentation automation',
      classifiers=[
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Development Status :: 2 - Pre-Alpha',
          'Environment :: Console',
          'Topic :: Documentation',
          'Topic :: Text Processing',
          'Programming Language :: Python :: 3',
          'Intended Audience :: Developers']
)
