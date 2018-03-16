# Brevity

[![Build Status](https://travis-ci.org/kylewm/brevity.svg)](https://travis-ci.org/kylewm/brevity)

*Brevity is the soul of tweet*

A small utility to shorten [posts](https://indiewebcamp.com/note) to a
tweet-length summary. Appends an optional permalink or citation. Also
supports autolinking.

Brevity checks URLs against the full list of ICANN TLDs, to avoid
linking things that look like web addresses but aren't.

## Ports

- PHP: https://github.com/kylewm/brevity-php
- Javascript: https://github.com/kylewm/brevity-js

## Usage

### Shorten

The primary method `brevity.shorten` takes a *plain text* string of
arbitrary length returns a shortened string that meets twitter's length
requirements (accounting for t.co URL shortening).

```python
>>> import brevity
>>> brevity.shorten("This is the text of a fairly long tweet that will need to be shortened before we can post it to twitter. Since it is longer than 280 characters, it will also include an ellipsis and link to the original note. 123567890 123567890 123567890 123567890 123567890 123567890 123567890 123567890", permalink="http://example.com/2015/03/fairly-long-note")
'This is the text of a fairly long tweet that will need to be shortened before we can post it to twitter. Since it is longer than 280 characters, it will also include an ellipsis and link to the original note. 123567890 123567890 123567890 123567890… http://example.com/2015/03/fairly-long-note'
```

The permalink, permashortlink, and permashortcitation parameters are all
optional and all have slightly different behavior. Permalinks will
*only* be added if the main text needs to be shortened, with the
intention that followers can click the link for the full note contents.

To identify *all* tweets as [POSSE](https://indiewebcamp.com/POSSE)
copies, you may additionally provide a
[permashortlink](https://indiewebcamp.com/permashortlink) or
[permashortcitation](https://indiewebcamp.com/permashortcitation). If a
note is short enough to post to twitter without truncation, the PSL/PSC
will be appended to the note text in parentheses.

```python
>>> brevity.shorten("This note is pithy and to the point", permalink="http://example.com/2015/03/to-the-point", permashortlink="http://exm.pl/y1x3")
'This note is pithy and to the point (http://exm.pl/y1x3)'
>>> brevity.shorten("This note is pithy and to the point", permalink="http://example.com/2015/03/to-the-point", permashortcitation="exm.pl y1x3")
'This note is pithy and to the point (exm.pl y1x3)'
```

If you do not have a URL shortener, but still want to tag all tweets
with their permalinks, it is perfectly fine to use the same url for your
permalink and permashortlink. It will be appended after an ellipsis for
long notes, or in parentheses for short ones.

Note that to be used in a permashortcitation, the bare domain must not
be autolinked by Twitter (Otherwise, what should be 5-6 characters will
count for 22). This typically means it cannot be a .com, .net, or .org.

Setting the optional parameter `format='article'` implies that
text is the title of a longer article (that can be found at
`permalink`). The composed text will be `Article Title: permalink` and
the permalink will be included regardless of the length of the title.
The values of `permashortlink` and `permashortcitation` are ignored.

### Autolink

The method `brevity.autolink`, based heavily on
[CASSIS auto_link](https://github.com/tantek/cassis/), takes a text
string, that may contain some HTML, and surrounds web addresses with
well-formed &lt;a> tags.

```python
>>> import brevity
>>> brevity.autolink('this links to nebenan.hamburg')
'this links to <a class="auto-link" href="http://nebenan.hamburg">nebenan.hamburg</a>'
```

Like the CASSIS method it is based on, autolink is idempotent --
applying it to its own output will not change the result. In practice,
this means &lt;a> tags in existing HTML will not be affected.

## Acknowledgments

Brevity's URL-recognition is based very heavily on
[Tantek Çelik's](http://tantek.com) excellent
[CASSIS](http://cassisjs.org).

## Changes
- 0.2.17 - 2018-03-15: Twitter's API no longer has a special carve-out for
  ccTLDs; they count as 23 characters like every other URL. Simplified the
  logic and updated the tests to match
- 0.2.16 - Fix character-counting bug that caused index out of range error.
- 0.2.15 - Implement Twitter's new
  [weighted character counting][tw-text] [introduced on 2017-11-07][280].
- 0.2.14 - 2017-04-23: Fix crash when given very long tokens
- 0.2.13 - 2017-04-23: Account for leading special characters like /, @, and $
- 0.2.12 - 2017-01-03: Update list of TLDs
- 0.2.11 - 2016-09-25: Remove special formatting for media attachments
  since Twitter no longer counts them against us!
- 0.2.10 - 2016-09-05: Rearrange link regex so that TLDs
  are validated by the regex instead of after the fact. Makes
  the shortener behave more like Twitter's.
- 0.2.9 - 2016-05-26: Bugfix: when trimming trailing characters
  from a URL, fixes an issue where characters after the first
  would be included several times.
- 0.2.8 - 2016-04-19: Add support for article+media where text
  represents the title of an article and includes an image.
- 0.2.7 - 2016-02-14: Bugfix: make sure check for ccTLDs is
  case-insensitive, so that we know Twitter won't autolink e.g.,
  Gogs.io
- 0.2.6 - 2016-02-01: Change shorten() parameter format_as_title to
  format, and allow different format styles, including note with media
  (to account for extra characters used by Twitter for an attachment)
- 0.2.5 - 2016-01-28: Added ports to to php and js
- 0.2.4 - 2016-01-28: Changed license from BSD to CC0. Extract test
  cases into reusable tests.json file. Fix bug where permalink
  citations were counted as text rather than links.
- 0.2.3 - 2015-11-19: when truncating to the nearest word, strip
  trailing delimiters, so there's no punctuation before the ellipsis
- 0.2.2 - 2015-11-19: add `format_as_title` parameter to shorten
  to support formatting article titles instead of note posts
- 0.2.1 - 2015-10-25: all links default to 23 characters now that
  [Twitter serves all t.co links over https][t.co-https]
- 0.2.0 - 2015-09-20: added autolink function
- 0.1.6 - 2015-06-05: move data text file into brevity.py for easier
  distribution/reuse.
- 0.1.5 - 2015-06-05: match all TLDs recognized by IANA; ignore
  things that look like domains but aren't.
- 0.1.4 - 2015-04-22: match URLs that include exclamation points.
- 0.1.3 - 2015-03-29: improved description in pypi.
- 0.1.0 - 2015-02-15: initial check-in.


[t.co-https]: https://twittercommunity.com/t/moving-t-co-to-https-only-for-new-links/52380
[tw-text]: https://developer.twitter.com/en/docs/developer-utilities/twitter-text
[280]: https://twittercommunity.com/t/updating-the-character-limit-and-the-twitter-text-library/96425
