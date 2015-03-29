Brevity
=======

|Build Status|

*Brevity is the soul of tweet*

A small utility to shorten https://indiewebcamp.com/note posts to an
acceptable tweet-length summary. Appends an optional permalink or
citation.

Usage
-----

The primary method ``brevity.shorten`` takes a *plain text* string of
arbitrary length returns a shortened string that meets twitter's length
requirements (accounting for t.co URL shortening).

.. code:: python

    >>> import brevity
    >>> brevity.shorten("This is the text of a fairly long tweet that will need to be shortened before we can post it to twitter. Since it is longer than 140 characters, it will also include an ellipsis and link to the original note.", permalink="http://example.com/2015/03/fairly-long-note")
    'This is the text of a fairly long tweet that will need to be shortened before we can post it to twitter. Since it is… http://example.com/2015/03/fairly-long-note'

The permalink, permashortlink, and permashortcitation parameters are all
optional and all have slightly different behavior. Permalinks will
*only* be added if the main text needs to be shortened, with the
intention that followers can click the link for the full note contents.

To identify *all* tweets as `POSSE <https://indiewebcamp.com/POSSE>`__
copies, you may additionally provide a
`permashortlink <https://indiewebcamp.com/permashortlink>`__ or
`permashortcitation <https://indiewebcamp.com/permashortcitation>`__. If
a note is short enough to post to twitter without truncation, the
PSL/PSC will be appended to the note text in parentheses.

.. code:: python

    >>> brevity.shorten("This note is pithy and to the point", permalink="http://example.com/2015/03/to-the-point", permashortlink="http://exm.pl/y1x3")
    'This note is pithy and to the point (http://exm.pl/y1x3)'
    >>> brevity.shorten("This note is pithy and to the point", permalink="http://example.com/2015/03/to-the-point", permashortcitation="exm.pl y1x3")
    'This note is pithy and to the point (exm.pl y1x3)'

If you do not have a URL shortener, but still want to tag all tweets
with their permalinks, it is perfectly fine to use the same url for your
permalink and permashortlink. It will be appended after an ellipsis for
long notes, or in parentheses for short ones.

Note that to be used in a permashortcitation, the bare domain must not
be autolinked by Twitter (Otherwise, what should be 5-6 characters will
count for 22). This typically means it cannot be a .com, .net, or .org.

.. |Build Status| image:: https://travis-ci.org/kylewm/brevity.svg
   :target: https://travis-ci.org/kylewm/brevity
