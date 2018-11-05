# coding=utf-8
from __future__ import unicode_literals, print_function

import unittest

from brevity.shorten import str_length

class ShortenTest(unittest.TestCase):
    def test_str_length_weighted(self):
        s = 'Heart \u2764'
        self.assertEqual(str_length(s), 8)

    def test_str_length_emoji_variation(self):
        s = 'Emoji heart \u2764\ufe0f'
        self.assertEqual(str_length(s), 14)

    def test_str_length_emoji_gender(self):
        s = 'Gender modifiers: 👩‍❤️‍👩👨🏿‍⚕️👩🏻‍🔧'
        self.assertEqual(str_length(s), 24)

    def test_str_length_emoji_skin_tone(self):
        s = 'Skin tones: 👍🏻👍🏽👍🏿'
        self.assertEqual(str_length(s), 18)
