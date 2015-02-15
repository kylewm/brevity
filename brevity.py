# coding=utf-8
import re
import sys

if sys.version < '3':
    pass
else:
    xrange = range


LINKIFY_RE = re.compile(r"""
(?:(?:http|https|file|irc):/{1,3})?       # optional scheme
(?:[a-z0-9\-]+\.)+[a-z]{2,4}(?::\d{2,6})? # host and optional port
(?:(?:/[\w/.\-_~.;:%?@$#&()=+]*)|\b)      # path and query
""", re.VERBOSE | re.UNICODE)


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


def tokenize(text, skip_bare_cc_tlds=False):
    """Split text into link and non-link text, returning two lists
    roughly equivalent to the output of re.findall and re.split (with
    some post-processing)

    Args:
      text: string to linkify
      skip_bare_cc_tlds: boolean, whether to skip links of the form
        [domain].[2-letter TLD] with no schema and no path

    Returns: a list of brevity.Tokens
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
                or next_text.lstrip().startswith('</a')
                # skip domains with 2-letter TLDs and no schema or path
                or (skip_bare_cc_tlds
                    and re.match(r'[a-z0-9\-]+\.[a-z]{2}$', link))):
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


def shorten(text, permalink=None, permashortlink=None, permashortcitation=None,
            target_length=140, http_link_length=22, https_link_length=23):
    def truncate_to_nearest_word(text, length):
      # try stripping trailing whitespace first
      text = text.rstrip()
      if len(text) <= length:
        return text
      # walk backwards until we find a delimiter
      for j in xrange(length, -1, -1):
        if text[j] in ',.;: \t\r\n':
          return text[:j]

    def token_length(token):
        if token.tag == 'link':
            if token.content.startswith('https'):
                return https_link_length
            return http_link_length
        return len(token.content)

    def total_length(tokens):
        return sum(token_length(t) for t in tokens)

    tokens = tokenize(text, skip_bare_cc_tlds=True)

    citation_tokens = []
    if permashortlink:
        citation_tokens.append(Token('text', ' (', True))
        citation_tokens.append(Token('link', permashortlink, True))
        citation_tokens.append(Token('text', ' )', True))
    elif permashortcitation:
        citation_tokens.append(
            Token('text', u' ({})'.format(permashortcitation), True))

    base_length = total_length(tokens)
    citation_length = total_length(citation_tokens)

    if base_length + citation_length <= target_length:
        tokens += citation_tokens

    else:
        # add permalink
        if permalink:
            tokens.append(Token('text', u'… ', True))
            tokens.append(Token('link', permalink, True))

        # drop or shorten tokens, starting from the end
        for ii in xrange(len(tokens) - 1, -1, -1):
            token = tokens[ii]
            if token.required:
                continue

            over = total_length(tokens) - target_length
            if over <= 0:
                break

            if token.tag == 'link':
                del tokens[ii]
            elif token.tag == 'text':
                toklen = token_length(token)
                if over >= toklen:
                    del tokens[ii]
                else:
                    token.content = truncate_to_nearest_word(
                        token.content, toklen - over)

    return ''.join(t.content for t in tokens)
