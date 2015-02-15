# coding=utf-8
import brevity
import unittest


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

        expected = u'Hey #indieweb, the coming storm of webmention Spam may not be far away. Those of us that have input fields to send… ' + permalink
        result = brevity.shorten(text=text, permalink=permalink,
                                 permashortlink=psl)
        self.assertEqual(expected, result)
