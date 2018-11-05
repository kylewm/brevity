# coding=utf-8
from __future__ import unicode_literals, print_function

import collections
import json
import os
import unittest

from brevity.tokenize import Token, tokenize

class TokenizeTest(unittest.TestCase):
    def test_tokenize_ignore_html(self):
        text = 'this should <a href="http://example.com">not be linkified</a>'
        self.assertEqual([Token(tag='text', content=text)],
                         tokenize(text))

    def test_tokenize_ignore_email(self):
        text = 'this should not.be@linkified.com'
        self.assertEqual([Token(tag='text', content=text)],
                         tokenize(text))
