# coding=utf-8
from __future__ import unicode_literals, print_function

import collections
import json
import os
import unittest

import brevity

with open('testcases/tests.json') as f:
    TESTS = json.load(f)

class BrevityTest(unittest.TestCase):

    def test_tokenize_ignore_html(self):
        text = 'this should <a href="http://example.com">not be linkified</a>'
        self.assertEqual([brevity.Token(tag='text', content=text)],
                         brevity.tokenize(text))

    def test_tokenize_ignore_email(self):
        text = 'this should not.be@linkified.com'
        self.assertEqual([brevity.Token(tag='text', content=text)],
                         brevity.tokenize(text))

    def test_shorten(self):
        for testcase in TESTS['shorten']:
            params = dict([
                (k, testcase[k]) for k in (
                    'text', 'permalink', 'permashortlink', 'permashortcitation',
                    'target_length', 'link_length', 'format',
                )
                if k in testcase])
            result = brevity.shorten(**params)
            expected = testcase['expected']
            self.assertEqual(expected, result)

    def test_autolink(self):
        for testcase in TESTS['autolink']:
            self.assertEqual(
                testcase['expected'], brevity.autolink(testcase['text']))
