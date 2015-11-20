# coding=utf-8
from __future__ import unicode_literals, print_function
import brevity
import unittest
import collections


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

    def test_no_shorten_technorati(self):
        text = 'Despite Technorati dumping tag & blog search long ago, rel-tag succeeded on web, in #HTML spec https://html.spec.whatwg.org/multipage/semantics.html#linkTypes'
        permalink = 'http://tantek.com/2015/014/t3/rel-tag-succeeded-web-html-specs'
        psc = 'ttk.me t4_93'

        result = brevity.shorten(text=text, permalink=permalink,
                                 permashortcitation=psc)
        self.assertEqual('{} ({})'.format(text, psc), result)

    def test_no_shorten_with_cc_tlds(self):
        text = 'Despite names,\nind.ie&indie.vc are NOT #indieweb @indiewebcamp\nindiewebcamp.com/2014-review#Indie_Term_Re-use\n@iainspad @sashtown @thomatronic'
        permalink = 'http://tantek.com/2015/013/t1/names-ind-ie-indie-vc-not-indieweb'
        psc = 'ttk.me t4_81'

        result = brevity.shorten(text=text, permalink=permalink,
                                 permashortcitation=psc)
        self.assertEqual('{} ({})'.format(text, psc), result)

    def test_no_shorten_intl_characters(self):
        text = u"Si Hären Engel duurch all, Haus Benn dé blo, am wuel Kolrettchen Nuechtegall dén. Nun en schéi Milliounen, an wee drem d'Welt, do Ierd blénk"
        self.assertEqual(text, brevity.shorten(text=text))

    def test_shorten_coming_storm(self):
        text = 'Hey #indieweb, the coming storm of webmention Spam may not be far away. Those of us that have input fields to send send webmentions manually may already be getting them. Look at the mentions on http://aaronparecki.com/articles/2015/01/22/1/why-not-json'

        permalink = 'https://ben.thatmustbe.me/note/2015/1/31/1/'
        psl = 'http://btmb.me/s/6q'

        expected = 'Hey #indieweb, the coming storm of webmention Spam may not be far away. Those of us that have input fields to send… ' + permalink
        result = brevity.shorten(text=text, permalink=permalink,
                                 permashortlink=psl)
        self.assertEqual(expected, result)

    def test_mmddyyyy_false_positive(self):
        text = 'anybody have a wedding ring with the date engraved in ISO 8601? I’ll be damned if I’m going to wear mm.dd.yyyy anywhere on my person.'

        permalink = 'https://kylewm.com/2015/05/anybody-have-a-wedding-ring-with-the-date-engraved'

        result = brevity.shorten(text=text, permalink=permalink,
                                 permashortlink=None)
        self.assertEqual(text, result)

    def test_hamburg_tld(self):
        text = 'ix freue mich auf die nebenan.hamburg morgen. ich spreche auch ne halbe stunde übers #indieweb und @reclaim_fm.'

        permalink = 'http://wirres.net/article/articleview/7773/1/6/'
        psl = 'http://wirres.net/7773'

        expected = 'ix freue mich auf die nebenan.hamburg morgen. ich spreche auch ne halbe stunde übers #indieweb und… http://wirres.net/article/articleview/7773/1/6/'
        result = brevity.shorten(text=text, permalink=permalink,
                                 permashortlink=psl)
        self.assertEqual(expected, result)

    def test_shorten_cases_from_bridgy(self):
        orig = expected = (
          '@davewiner I stubbed a page on the wiki for '
          'https://indiewebcamp.com/River4. Edits/improvmnts from users are '
          'welcome! @kevinmarks @julien51 @aaronpk')
        result = brevity.shorten(orig)
        self.assertEquals(expected, result)

        orig = expected = (
          'This is a long tweet with (foo.com/parenthesized-urls) and urls '
          'that wikipedia.org/Contain_(Parentheses), a url with a query '
          'string;foo.withknown.com/example?query=parameters')
        result = brevity.shorten(orig)
        self.assertEquals(expected, result)

        orig = (
          'This is a long tweet with (foo.com/parenthesized-urls) and urls '
          'that wikipedia.org/Contain_(Parentheses), that is one charc too '
          'long:foo.withknown.com/example?query=parameters')
        expected = (
          'This is a long tweet with (foo.com/parenthesized-urls) and urls '
          'that wikipedia.org/Contain_(Parentheses), that is one charc too '
          'long:…')
        result = brevity.shorten(orig)
        self.assertEquals(expected, result)

        # test case-insensitive link matching
        orig = (
          'The Telegram Bot API is the best bot API ever. Everyone should '
          'learn from it, especially Matrix.org, which currently requires a '
          'particular URL structure and registration files.')
        expected = (
          'The Telegram Bot API is the best bot API ever. Everyone should learn '
          'from it, especially Matrix.org… '
          'https://unrelenting.technology/notes/2015-09-05-00-35-13')
        result = brevity.shorten(
          orig, permalink='https://unrelenting.technology/notes/2015-09-05-00-35-13')
        self.assertEquals(expected, result)

        orig = 'url http://foo.co/bar ellipsize http://foo.co/baz'
        expected = 'url http://foo.co/bar ellipsize…'
        result = brevity.shorten(orig, target_length=20, link_length=5)
        self.assertEquals(expected, result)

        orig = 'too long\nextra whitespace\tbut should include url'
        expected = 'too long… http://obj.ca'
        result = brevity.shorten(orig, permalink='http://obj.ca',
                                 target_length=20, link_length=5)
        self.assertEquals(expected, result)

        orig = expected = 'trailing slash http://www.foo.co/'
        result = brevity.shorten(orig, target_length=20, link_length=5)
        self.assertEquals(expected, result)

    def test_shorten_format_as_title(self):
        text = 'The Article Title'
        permalink = 'http://example.com/article'
        self.assertEqual(
            'The Article Title: http://example.com/article',
            brevity.shorten(text=text, permalink=permalink, format_as_title=True))

        text = 'The Article Title is Longer Than Will Fit in Just One Single Tweet, and I Find This Situation to be Awfully Frustrating; How About You?'
        permalink = 'https://example.org/article'
        self.assertEqual(
            'The Article Title is Longer Than Will Fit in Just One Single Tweet, and I Find This Situation to be Awfully… https://example.org/article',
            brevity.shorten(text=text, permalink=permalink, format_as_title=True))

    def test_autolink(self):
        TestCase = collections.namedtuple('TestCase', 'text expected')
        tests = [
            TestCase(
                text='This links to a weird domain deals.blackfriday.',
                expected='This links to a weird domain <a class="auto-link" href="http://deals.blackfriday">deals.blackfriday</a>.'),
            TestCase(
                text='starts.with.a.link and ends with <a href="https://kylewm.com/about#me">HTML</a>.',
                expected='<a class="auto-link" href="http://starts.with.a.link">starts.with.a.link</a> and ends with <a href="https://kylewm.com/about#me">HTML</a>.'),
            TestCase(
                text='includes Http://ipad-capitalization.com',
                expected='includes <a class="auto-link" href="http://ipad-capitalization.com">Http://ipad-capitalization.com</a>'),
            TestCase(
                text='a matched parenthesis: http://wikipedia.org/Python_(programming_language) and (an unmatched parenthesis https://en.wikipedia.org/wiki/Guido_van_Rossum)',
                expected='a matched parenthesis: <a class="auto-link" href="http://wikipedia.org/Python_(programming_language)">http://wikipedia.org/Python_(programming_language)</a> and (an unmatched parenthesis <a class="auto-link" href="https://en.wikipedia.org/wiki/Guido_van_Rossum">https://en.wikipedia.org/wiki/Guido_van_Rossum</a>)'),
        ]

        for test in tests:
            self.assertEqual(test.expected, brevity.autolink(test.text))
