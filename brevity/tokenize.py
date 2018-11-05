# coding=utf-8
from __future__ import unicode_literals, print_function

import re
import sys
if sys.version < '3':
    pass
else:
    xrange = range

from .definitions import TLDS

_SCHEME = r'(?:http|https|file|irc):/{1,3}'
_HOST = r'(?:[a-z0-9][a-z0-9\-]*\.)+(?:' + '|'.join(TLDS) + r')(?::\d{2,6})?'
_PATH = r'/[\w/.\-_~.;:%?!@$#&()=+]*'

LINKIFY_RE = re.compile(r'(?:{scheme})?{host}(?:{path}|\b)'
                        .format(scheme=_SCHEME, host=_HOST, path=_PATH),
                        re.VERBOSE | re.UNICODE | re.IGNORECASE)

class Token:
    def __init__(self, tag, content, required=False):
        self.tag = tag
        self.content = content
        self.required = required

    def __eq__(self, o):
        return self.tag == o.tag \
            and self.content == o.content \
            and self.required == o.required

    def __repr__(self):
        return u'Token(tag={}, content={}, required={})'.format(
            self.tag, self.content, self.required)


def tokenize(text):
    """Split text into link and non-link text, a list of brevity.Tokens,
    tagged with 'text' or 'link' depending on how they should be
    interpreted.

    :param string text: text to tokenize

    :return list: a list of brevity.Tokens
    """
    links = LINKIFY_RE.findall(text)
    splits = LINKIFY_RE.split(text)

    for ii in xrange(len(links)):
        # trim trailing punctuation from links
        link = links[ii]
        jj = len(link) - 1
        while (jj >= 0 and link[jj] in '.!?,;:)'
               # allow 1 () pair
               and (link[jj] != ')' or '(' not in link)):
            jj -= 1
            links[ii] = link[:jj + 1]
            splits[ii + 1] = link[jj + 1:] + splits[ii + 1]
            link = links[ii]

        # avoid double linking by looking at preceeding 2 chars
        prev_text = splits[ii]
        next_text = splits[ii + 1]
        if (prev_text.rstrip().endswith('="')
                or prev_text.rstrip().endswith("='")
                or prev_text.endswith('@') or next_text.startswith('@')
                or prev_text.endswith('$') or prev_text.endswith('/')
                or prev_text.endswith('.') or prev_text.endswith('#')
                or prev_text.endswith('_') or prev_text.endswith('-')
                or next_text.lstrip().startswith('</a')):
            # collapse link into before text
            splits[ii] = splits[ii] + links[ii]
            links[ii] = None
            continue

    # compile the tagged tokens
    result = []
    for ii in xrange(max(len(links), len(splits))):
        if ii < len(splits) and splits[ii]:
            if result and result[-1].tag == 'text':
                # collapse consecutive text tokens
                result[-1].content += splits[ii]
            else:
                result.append(Token('text', splits[ii]))
        if ii < len(links) and links[ii]:
            result.append(Token('link', links[ii]))

    return result

