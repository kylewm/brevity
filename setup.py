#!/usr/bin/env python
from setuptools import setup


setup(name='brevity',
      version='0.1.1',
      description='Tweet shortening utility',
      long_description='Utility for shortening longer notes to at most 140 characters.',
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
      ]
  )
