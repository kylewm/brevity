# coding=utf-8
from __future__ import unicode_literals, print_function
import re
import sys

if sys.version < '3':
    pass
else:
    xrange = range

TLDS = ["aaa", "aarp", "abb", "abbott", "abogado", "ac", "academy", "accenture", "accountant", "accountants", "aco", "active", "actor", "ad", "adac", "ads", "adult", "ae", "aeg", "aero", "af", "afl", "ag", "agency", "ai", "aig", "airforce", "airtel", "al", "alibaba", "alipay", "allfinanz", "alsace", "am", "amica", "amsterdam", "analytics", "android", "ao", "apartments", "app", "apple", "aq", "aquarelle", "ar", "aramco", "archi", "army", "arpa", "arte", "as", "asia", "associates", "at", "attorney", "au", "auction", "audi", "audio", "author", "auto", "autos", "aw", "ax", "axa", "az", "azure", "ba", "baidu", "band", "bank", "bar", "barcelona", "barclaycard", "barclays", "bargains", "bauhaus", "bayern", "bb", "bbc", "bbva", "bcn", "bd", "be", "beats", "beer", "bentley", "berlin", "best", "bet", "bf", "bg", "bh", "bharti", "bi", "bible", "bid", "bike", "bing", "bingo", "bio", "biz", "bj", "black", "blackfriday", "bloomberg", "blue", "bm", "bms", "bmw", "bn", "bnl", "bnpparibas", "bo", "boats", "boehringer", "bom", "bond", "boo", "book", "boots", "bosch", "bostik", "bot", "boutique", "br", "bradesco", "bridgestone", "broadway", "broker", "brother", "brussels", "bs", "bt", "budapest", "bugatti", "build", "builders", "business", "buy", "buzz", "bv", "bw", "by", "bz", "bzh", "ca", "cab", "cafe", "cal", "call", "camera", "camp", "cancerresearch", "canon", "capetown", "capital", "car", "caravan", "cards", "care", "career", "careers", "cars", "cartier", "casa", "cash", "casino", "cat", "catering", "cba", "cbn", "cc", "cd", "ceb", "center", "ceo", "cern", "cf", "cfa", "cfd", "cg", "ch", "chanel", "channel", "chat", "cheap", "chloe", "christmas", "chrome", "church", "ci", "cipriani", "circle", "cisco", "citic", "city", "cityeats", "ck", "cl", "claims", "cleaning", "click", "clinic", "clinique", "clothing", "cloud", "club", "clubmed", "cm", "cn", "co", "coach", "codes", "coffee", "college", "cologne", "com", "commbank", "community", "company", "compare", "computer", "comsec", "condos", "construction", "consulting", "contact", "contractors", "cooking", "cool", "coop", "corsica", "country", "coupons", "courses", "cr", "credit", "creditcard", "creditunion", "cricket", "crown", "crs", "cruises", "csc", "cu", "cuisinella", "cv", "cw", "cx", "cy", "cymru", "cyou", "cz", "dabur", "dad", "dance", "date", "dating", "datsun", "day", "dclk", "de", "dealer", "deals", "degree", "delivery", "dell", "delta", "democrat", "dental", "dentist", "desi", "design", "dev", "diamonds", "diet", "digital", "direct", "directory", "discount", "dj", "dk", "dm", "dnp", "do", "docs", "dog", "doha", "domains", "doosan", "download", "drive", "dubai", "durban", "dvag", "dz", "earth", "eat", "ec", "edeka", "edu", "education", "ee", "eg", "email", "emerck", "energy", "engineer", "engineering", "enterprises", "epson", "equipment", "er", "erni", "es", "esq", "estate", "et", "eu", "eurovision", "eus", "events", "everbank", "exchange", "expert", "exposed", "express", "fage", "fail", "fairwinds", "faith", "family", "fan", "fans", "farm", "fashion", "fast", "feedback", "ferrero", "fi", "film", "final", "finance", "financial", "firestone", "firmdale", "fish", "fishing", "fit", "fitness", "fj", "fk", "flights", "florist", "flowers", "flsmidth", "fly", "fm", "fo", "foo", "football", "ford", "forex", "forsale", "forum", "foundation", "fox", "fr", "fresenius", "frl", "frogans", "fund", "furniture", "futbol", "fyi", "ga", "gal", "gallery", "game", "garden", "gb", "gbiz", "gd", "gdn", "ge", "gea", "gent", "genting", "gf", "gg", "ggee", "gh", "gi", "gift", "gifts", "gives", "giving", "gl", "glass", "gle", "global", "globo", "gm", "gmail", "gmo", "gmx", "gn", "gold", "goldpoint", "golf", "goo", "goog", "google", "gop", "got", "gov", "gp", "gq", "gr", "grainger", "graphics", "gratis", "green", "gripe", "group", "gs", "gt", "gu", "gucci", "guge", "guide", "guitars", "guru", "gw", "gy", "hamburg", "hangout", "haus", "health", "healthcare", "help", "helsinki", "here", "hermes", "hiphop", "hitachi", "hiv", "hk", "hm", "hn", "hockey", "holdings", "holiday", "homedepot", "homes", "honda", "horse", "host", "hosting", "hoteles", "hotmail", "house", "how", "hr", "hsbc", "ht", "hu", "hyundai", "ibm", "icbc", "ice", "icu", "id", "ie", "ifm", "iinet", "il", "im", "immo", "immobilien", "in", "industries", "infiniti", "info", "ing", "ink", "institute", "insurance", "insure", "int", "international", "investments", "io", "ipiranga", "iq", "ir", "irish", "is", "iselect", "ist", "istanbul", "it", "itau", "iwc", "jaguar", "java", "jcb", "je", "jetzt", "jewelry", "jlc", "jll", "jm", "jmp", "jo", "jobs", "joburg", "jot", "joy", "jp", "jprs", "juegos", "kaufen", "kddi", "ke", "kfh", "kg", "kh", "ki", "kia", "kim", "kinder", "kitchen", "kiwi", "km", "kn", "koeln", "komatsu", "kp", "kpn", "kr", "krd", "kred", "kw", "ky", "kyoto", "kz", "la", "lacaixa", "lamborghini", "lamer", "lancaster", "land", "landrover", "lanxess", "lasalle", "lat", "latrobe", "law", "lawyer", "lb", "lc", "lds", "lease", "leclerc", "legal", "lexus", "lgbt", "li", "liaison", "lidl", "life", "lifeinsurance", "lifestyle", "lighting", "like", "limited", "limo", "lincoln", "linde", "link", "live", "living", "lixil", "lk", "loan", "loans", "lol", "london", "lotte", "lotto", "love", "lr", "ls", "lt", "ltd", "ltda", "lu", "lupin", "luxe", "luxury", "lv", "ly", "ma", "madrid", "maif", "maison", "makeup", "man", "management", "mango", "market", "marketing", "markets", "marriott", "mba", "mc", "md", "me", "med", "media", "meet", "melbourne", "meme", "memorial", "men", "menu", "meo", "mg", "mh", "miami", "microsoft", "mil", "mini", "mk", "ml", "mm", "mma", "mn", "mo", "mobi", "mobily", "moda", "moe", "moi", "mom", "monash", "money", "montblanc", "mormon", "mortgage", "moscow", "motorcycles", "mov", "movie", "movistar", "mp", "mq", "mr", "ms", "mt", "mtn", "mtpc", "mtr", "mu", "museum", "mutuelle", "mv", "mw", "mx", "my", "mz", "na", "nadex", "nagoya", "name", "navy", "nc", "ne", "nec", "net", "netbank", "network", "neustar", "new", "news", "nexus", "nf", "ng", "ngo", "nhk", "ni", "nico", "ninja", "nissan", "nl", "no", "nokia", "norton", "nowruz", "np", "nr", "nra", "nrw", "ntt", "nu", "nyc", "nz", "obi", "office", "okinawa", "om", "omega", "one", "ong", "onl", "online", "ooo", "oracle", "orange", "org", "organic", "origins", "osaka", "otsuka", "ovh", "pa", "page", "pamperedchef", "panerai", "paris", "pars", "partners", "parts", "party", "pe", "pet", "pf", "pg", "ph", "pharmacy", "philips", "photo", "photography", "photos", "physio", "piaget", "pics", "pictet", "pictures", "pid", "pin", "ping", "pink", "pizza", "pk", "pl", "place", "play", "playstation", "plumbing", "plus", "pm", "pn", "pohl", "poker", "porn", "post", "pr", "praxi", "press", "pro", "prod", "productions", "prof", "promo", "properties", "property", "protection", "ps", "pt", "pub", "pw", "py", "qa", "qpon", "quebec", "racing", "re", "read", "realtor", "realty", "recipes", "red", "redstone", "redumbrella", "rehab", "reise", "reisen", "reit", "ren", "rent", "rentals", "repair", "report", "republican", "rest", "restaurant", "review", "reviews", "rexroth", "rich", "ricoh", "rio", "rip", "ro", "rocher", "rocks", "rodeo", "room", "rs", "rsvp", "ru", "ruhr", "run", "rw", "rwe", "ryukyu", "sa", "saarland", "safe", "safety", "sakura", "sale", "salon", "samsung", "sandvik", "sandvikcoromant", "sanofi", "sap", "sapo", "sarl", "sas", "saxo", "sb", "sbs", "sc", "sca", "scb", "schaeffler", "schmidt", "scholarships", "school", "schule", "schwarz", "science", "scor", "scot", "sd", "se", "seat", "security", "seek", "select", "sener", "services", "seven", "sew", "sex", "sexy", "sfr", "sg", "sh", "sharp", "shell", "shia", "shiksha", "shoes", "show", "shriram", "si", "singles", "site", "sj", "sk", "ski", "skin", "sky", "skype", "sl", "sm", "smile", "sn", "sncf", "so", "soccer", "social", "softbank", "software", "sohu", "solar", "solutions", "sony", "soy", "space", "spiegel", "spreadbetting", "sr", "srl", "st", "stada", "star", "starhub", "statefarm", "statoil", "stc", "stcgroup", "stockholm", "storage", "studio", "study", "style", "su", "sucks", "supplies", "supply", "support", "surf", "surgery", "suzuki", "sv", "swatch", "swiss", "sx", "sy", "sydney", "symantec", "systems", "sz", "tab", "taipei", "taobao", "tatamotors", "tatar", "tattoo", "tax", "taxi", "tc", "tci", "td", "team", "tech", "technology", "tel", "telefonica", "temasek", "tennis", "tf", "tg", "th", "thd", "theater", "theatre", "tickets", "tienda", "tiffany", "tips", "tires", "tirol", "tj", "tk", "tl", "tm", "tmall", "tn", "to", "today", "tokyo", "tools", "top", "toray", "toshiba", "tours", "town", "toyota", "toys", "tr", "trade", "trading", "training", "travel", "travelers", "travelersinsurance", "trust", "trv", "tt", "tube", "tui", "tushu", "tv", "tw", "tz", "ua", "ubs", "ug", "uk", "university", "uno", "uol", "us", "uy", "uz", "va", "vacations", "vana", "vc", "ve", "vegas", "ventures", "verisign", "versicherung", "vet", "vg", "vi", "viajes", "video", "villas", "vin", "vip", "virgin", "vision", "vista", "vistaprint", "viva", "vlaanderen", "vn", "vodka", "volkswagen", "vote", "voting", "voto", "voyage", "vu", "wales", "walter", "wang", "wanggou", "watch", "watches", "weather", "webcam", "weber", "website", "wed", "wedding", "weir", "wf", "whoswho", "wien", "wiki", "williamhill", "win", "windows", "wine", "wme", "work", "works", "world", "ws", "wtc", "wtf", "xbox", "xerox", "xin", "xn--11b4c3d", "xn--1qqw23a", "xn--30rr7y", "xn--3bst00m", "xn--3ds443g", "xn--3e0b707e", "xn--3pxu8k", "xn--42c2d9a", "xn--45brj9c", "xn--45q11c", "xn--4gbrim", "xn--55qw42g", "xn--55qx5d", "xn--6frz82g", "xn--6qq986b3xl", "xn--80adxhks", "xn--80ao21a", "xn--80asehdb", "xn--80aswg", "xn--90a3ac", "xn--90ais", "xn--9dbq2a", "xn--9et52u", "xn--b4w605ferd", "xn--c1avg", "xn--c2br7g", "xn--cg4bki", "xn--clchc0ea0b2g2a9gcd", "xn--czr694b", "xn--czrs0t", "xn--czru2d", "xn--d1acj3b", "xn--d1alf", "xn--eckvdtc9d", "xn--efvy88h", "xn--estv75g", "xn--fhbei", "xn--fiq228c5hs", "xn--fiq64b", "xn--fiqs8s", "xn--fiqz9s", "xn--fjq720a", "xn--flw351e", "xn--fpcrj9c3d", "xn--fzc2c9e2c", "xn--g2xx48c", "xn--gecrj9c", "xn--h2brj9c", "xn--hxt814e", "xn--i1b6b1a6a2e", "xn--imr513n", "xn--io0a7i", "xn--j1aef", "xn--j1amh", "xn--j6w193g", "xn--jlq61u9w7b", "xn--kcrx77d1x4a", "xn--kprw13d", "xn--kpry57d", "xn--kpu716f", "xn--kput3i", "xn--l1acc", "xn--lgbbat1ad8j", "xn--mgb9awbf", "xn--mgba3a3ejt", "xn--mgba3a4f16a", "xn--mgbaam7a8h", "xn--mgbab2bd", "xn--mgbayh7gpa", "xn--mgbb9fbpob", "xn--mgbbh1a71e", "xn--mgbc0a9azcg", "xn--mgberp4a5d4ar", "xn--mgbpl2fh", "xn--mgbt3dhd", "xn--mgbtx2b", "xn--mgbx4cd0ab", "xn--mk1bu44c", "xn--mxtq1m", "xn--ngbc5azd", "xn--ngbe9e0a", "xn--node", "xn--nqv7f", "xn--nqv7fs00ema", "xn--nyqy26a", "xn--o3cw4h", "xn--ogbpf8fl", "xn--p1acf", "xn--p1ai", "xn--pbt977c", "xn--pgbs0dh", "xn--pssy2u", "xn--q9jyb4c", "xn--qcka1pmc", "xn--qxam", "xn--rhqv96g", "xn--s9brj9c", "xn--ses554g", "xn--t60b56a", "xn--tckwe", "xn--unup4y", "xn--vermgensberater-ctb", "xn--vermgensberatung-pwb", "xn--vhquv", "xn--vuq861b", "xn--wgbh1c", "xn--wgbl6a", "xn--xhq521b", "xn--xkc2al3hye2a", "xn--xkc2dl3a5ee0h", "xn--y9a3aq", "xn--yfro4i67o", "xn--ygbi2ammx", "xn--zfr164b", "xperia", "xxx", "xyz", "yachts", "yamaxun", "yandex", "ye", "yodobashi", "yoga", "yokohama", "youtube", "yt", "za", "zara", "zero", "zip", "zm", "zone", "zuerich", "zw"]

_SCHEME = r'(?:http|https|file|irc):/{1,3}'
_HOST = r'(?:[a-z0-9\-]+\.)+(?:' + '|'.join(TLDS) + r')(?::\d{2,6})?'
_PATH = r'/[\w/.\-_~.;:%?!@$#&()=+]*'

LINKIFY_RE = re.compile(r'(?:{scheme})?{host}(?:{path}|\b)'
                        .format(scheme=_SCHEME, host=_HOST, path=_PATH), 
                        re.VERBOSE | re.UNICODE | re.IGNORECASE)

FORMAT_NOTE = 'note'
FORMAT_ARTICLE = 'article'
FORMAT_MEDIA = 'media'
FORMAT_NOTE_WITH_MEDIA = FORMAT_NOTE + '+' + FORMAT_MEDIA
FORMAT_ARTICLE_WITH_MEDIA = FORMAT_ARTICLE + '+' + FORMAT_MEDIA


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
    """Split text into link and non-link text, a list of brevity.Tokens,
    tagged with 'text' or 'link' depending on how they should be
    interpreted.

    :param string text: text to tokenize
    :param boolean skip_bare_cc_tlds: whether to skip links of the form
        [domain].[2-letter TLD] with no schema and no path

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
                or next_text.lstrip().startswith('</a')
                # skip domains with 2-letter TLDs and no schema or path
                or (skip_bare_cc_tlds
                    and re.match(r'[a-z0-9\-]+\.[a-z]{2}$', link, flags=re.IGNORECASE))):
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


def shorten(text, permalink=None, permashortlink=None, permashortcitation=None,
            target_length=140, link_length=23, format=FORMAT_NOTE):
    """Prepare note text for publishing as a tweet. Ellipsize and add a
    permalink or citation.

    If the full text plus optional '(permashortlink)' or
    '(permashortcitation)' can fit into the target length (defaults to
    140 characters), it will return the composed text.

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
    :param int target_length: The target overall length (default = 140)
    :param int link_length: The t.co length for a URL (default = 23)
    :param string format: one of the FORMAT_ constants that determines
      whether to format the text like a note or an article (default = FORMAT_NOTE)

    :return string: the final composed text
    """
    def truncate_to_nearest_word(text, length):
        delimiters = ',.;: \t\r\n'
        # try stripping trailing whitespace first
        text = text.rstrip()
        if len(text) <= length:
            return text
        # walk backwards until we find a delimiter
        for j in xrange(length, -1, -1):
            if text[j] in delimiters:
                return text[:j].rstrip(delimiters)

    def token_length(token):
        if token.tag == 'link':
            return link_length
        return len(token.content)

    def total_length(tokens):
        return sum(token_length(t) for t in tokens)

    tokens = tokenize(text, skip_bare_cc_tlds=True)

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

    if FORMAT_MEDIA in format:
        target_length -= link_length + 1  # 23 chars + a space

    base_length = total_length(tokens)
    citation_length = total_length(citation_tokens)

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
