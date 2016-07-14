#!/usr/bin/env python
"""
Copyright 2013 Parse.ly, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import sys
import os

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

install_requires = [
    'pymongo<=2.8.1',
    'redis',
]

lint_requires = [
    'pep8',
    'pyflakes'
]


def read_lines(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.readlines()

tests_require = [x.strip() for x in read_lines('test-requirements.txt')]


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup_requires = []
if 'nosetests' in sys.argv[1:]:
    setup_requires.append('nose')

setup(
    name='testinstances',
    version='0.3.0',
    author='Keith Bourgoin',
    author_email='keith at parsely dot com',
    url='https://github.com/Parsely/testinstances',
    description='Managed test instances for integration tests',
    license='Apache License 2.0',
    packages=find_packages(),
    install_requires=install_requires,
    tests_require=tests_require,
    setup_requires=setup_requires,
    extras_require={
        'test': tests_require,
        'all': install_requires + tests_require,
    },
    cmdclass={'test': PyTest},
    zip_safe=False,
    test_suite='nose.collector',
    include_package_data=True,
)
