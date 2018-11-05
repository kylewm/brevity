# coding=utf-8
from __future__ import unicode_literals, print_function
from .tokenize import tokenize

def autolink(text):
    """Add <a> tags around web addresses in an HTML or plain text
    document. URLs inside pre-existing HTML elements will be left alone.

    :param string text: the text document with addresses to mark up
    :return string: the text with addresses replaced by <a> elements
    """
    def add_scheme(url):
        if (url.startswith('//') or url.startswith('http://')
                or url.startswith('https://') or url.startswith('mailto://')
                or url.startswith('irc://')):
            return url
        if url.startswith('Http://') or url.startswith('Https://'):
            return 'h' + url[1:]
        return 'http://' + url

    result = []
    for token in tokenize(text):
        if token.tag == 'link':
            result.append('<a class="auto-link" href="{0}">{1}</a>'.format(
                add_scheme(token.content), token.content))
        else:
            result.append(token.content)
    return ''.join(result)
