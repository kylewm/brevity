# coding=utf-8
from __future__ import unicode_literals, print_function
import re
import sys
import warnings
if sys.version < '3':
    pass
else:
    xrange = range

from .definitions import WEIGHTS
from .tokenize import Token, tokenize

FORMAT_NOTE = 'note'
FORMAT_ARTICLE = 'article'

DELIMITERS = ',.;: \t\r\n'

def shorten(text, permalink=None, permashortlink=None, permashortcitation=None,
            target_length=WEIGHTS['maxWeightedTweetLength'],
            link_length=WEIGHTS['transformedURLLength'],
            format=FORMAT_NOTE):
    """Prepare note text for publishing as a tweet. Ellipsize and add a
    permalink or citation.

    If the full text plus optional '(permashortlink)' or
    '(permashortcitation)' can fit into the target length (defaults to
    280 characters), it will return the composed text.

    If format is FORMAT_ARTICLE, text is taken to be the title of a longer
    article. It will be formatted as '[text]: [permalink]'. The values of
    permashortlink and permashortcitation are ignored in this case.

    Otherwise, the text will be shortened to the nearest full word,
    with an ellipsis and permalink added at the end. A permalink
    should always be provided; otherwise text will be shortened with
    no way to find the original.

    Note: that the permashortlink does not actually have to be a
    "short" URL. It is totally reasonable to provide the same URL for
    both the permalink and permashortlink.

    :param string text: The full note text that may be ellipsized
    :param string permalink: URL of the original note, will only be added if
      the text is shortened (optional).
    :param string permashortlink: Short URL of the original note, if provided
      will be added in parentheses to the end of all notes. (optional)
    :param string permashortcitation: Citation to the original note, e.g.
      'ttk.me t4_f2', an alternative to permashortlink. If provided will be
      added in parentheses to the end of all notes. (optional)
    :param int target_length: The target overall length (default = 280)
    :param int link_length: The t.co length for a URL (default = 23)
    :param string format: one of the FORMAT_ constants that determines
      whether to format the text like a note or an article (default = FORMAT_NOTE)

    :return string: the final composed text
    """
    tokens = tokenize(text)

    citation_tokens = []
    if FORMAT_ARTICLE in format and permalink:
        citation_tokens.append(Token('text', ': ', True))
        citation_tokens.append(Token('link', permalink, True))
    elif permashortlink:
        citation_tokens.append(Token('text', ' (', True))
        citation_tokens.append(Token('link', permashortlink, True))
        citation_tokens.append(Token('text', ')', True))
    elif permashortcitation:
        citation_tokens.append(
            Token('text', u' ({0})'.format(permashortcitation), True))

    if 'media' in format:
        print('Brevity: "media" formatting has been removed; Media attachments no longer count against Twitter\'s character limit (https://dev.twitter.com/overview/api/upcoming-changes-to-tweets)', file=sys.stderr)

    base_length = total_length(tokens, link_length)
    citation_length = total_length(citation_tokens, link_length)

    if base_length + citation_length <= target_length:
        tokens += citation_tokens

    else:
        # add permalink
        if permalink:
            tokens.append(Token('text', u'… ', True))
            tokens.append(Token('link', permalink, True))
        else:
            tokens.append(Token('text', u'…', True))

        # drop or shorten tokens, starting from the end
        for ii in xrange(len(tokens) - 1, -1, -1):
            token = tokens[ii]
            if token.required:
                continue

            over = total_length(tokens, link_length) - target_length
            if over <= 0:
                # strip trailing whitespace and punctuation on the last token
                if token.tag == 'text':
                    token.content = token.content.rstrip(DELIMITERS)
                break

            if token.tag == 'link':
                del tokens[ii]
            elif token.tag == 'text':
                toklen = token_length(token, link_length)
                if over >= toklen:
                    del tokens[ii]
                else:
                    token.content = truncate_to_nearest_word(
                        token.content, toklen - over)

    return ''.join(t.content for t in tokens)


def truncate_to_nearest_word(text, length):
    # try stripping trailing whitespace first
    text = text.rstrip()
    if str_length(text) <= length:
        return text
    # walk backwards until we find a delimiter
    for j in xrange(len(text) - 1, -1, -1):
        if text[j] in DELIMITERS:
            trunc = text[:j].rstrip(DELIMITERS)
            if str_length(trunc) <= length:
                return trunc
    # walk backwards ignoring delimiters
    for j in xrange(len(text) - 1, -1, -1):
        trunc = text[:j]
        if str_length(trunc) <= length:
            return trunc
    warnings.warn('Failed to truncate text "{}" to {} characters. This indicates a logical error'.format(text, length))
    return ''


def char_length(char):
    point = ord(char)
    weight = WEIGHTS['defaultWeight']
    for range in WEIGHTS['ranges']:
        if point >= range['start'] and point <= range['end']:
            weight = range['weight']
    return weight // WEIGHTS['scale']


def str_length(s):
    sum = 0
    skip_next = False

    print(type(s), s)

    for c in s:
        if skip_next:
            skip_next = False
            print('skipping', c)
        elif ord(c) == 0x200d:
            # ignore character after a ZWJ
            skip_next = True
            print('zwj', ord(c))
        elif ord(c) >= 0xfe00 and ord(c) <= 0xfe0f:
            # ignore variation selectors
            print('variation selector:', ord(c))
            pass
        else:
            print('char:', c, ord(c), char_length(c))
            sum += char_length(c)

    return sum


def token_length(token, link_length):
    if token.tag == 'link':
        return link_length
    return str_length(token.content)


def total_length(tokens, link_length):
    return sum(token_length(t, link_length) for t in tokens)
