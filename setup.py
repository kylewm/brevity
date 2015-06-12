#!/usr/bin/env python
from setuptools import setup
import os.path
import codecs


def readme():
    with codecs.open(
            os.path.join(os.path.dirname(__file__), 'README.rst'),
            encoding='utf-8') as f:
        return f.read()


setup(name='brevity',
      version='0.1.6',
      description='Tweet shortening utility',
      long_description=readme(),
      author='Kyle Mahan',
      author_email='kyle@kylewm.com',
      url='http://indiewebcamp.com/brevity',
      py_modules=['brevity'],
      test_suite='tests',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Natural Language :: English',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Topic :: Text Processing',
          'Topic :: Utilities',
      ])
