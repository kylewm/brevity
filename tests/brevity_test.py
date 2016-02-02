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

    def test_tokenize_ignore_cc_tlds(self):
        text = 'Despite names,\nind.ie&indie.vc are NOT #indieweb @indiewebcamp\nindiewebcamp.com/2014-review#Indie_Term_Re-use\n@iainspad @sashtown @thomatronic'
        self.assertEqual([
            brevity.Token(tag='text', content='Despite names,\nind.ie&indie.vc are NOT #indieweb @indiewebcamp\n'),
            brevity.Token(tag='link', content='indiewebcamp.com/2014-review#Indie_Term_Re-use'),
            brevity.Token(tag='text', content='\n@iainspad @sashtown @thomatronic')
        ], brevity.tokenize(text, skip_bare_cc_tlds=True))

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
