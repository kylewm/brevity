# coding=utf-8
from __future__ import unicode_literals, print_function
import re
import sys

if sys.version < '3':
    pass
else:
    xrange = range

LINKIFY_RE = re.compile(r"""
(?:(?:http|https|file|irc):/{1,3})?       # optional scheme
(?:[a-z0-9\-]+\.)+[a-z]{2,}(?::\d{2,6})?  # host and optional port
(?:(?:/[\w/.\-_~.;:%?!@$#&()=+]*)|\b)     # path and query
""", re.VERBOSE | re.UNICODE | re.IGNORECASE)

DOMAIN_RE = re.compile("""
(?:(?:http|https|file|irc):/{1,3})?       # optional scheme
((?:[a-z0-9\-]+\.)+)([a-z]{2,})           # name and tld
""", re.VERBOSE | re.UNICODE | re.IGNORECASE)


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
    def has_valid_tld(link):
        m = DOMAIN_RE.match(link)
        return m and m.group(2).lower() in TLDS

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
                or not has_valid_tld(link)
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
            result.append('<a class="auto-link" href="{}">{}</a>'.format(
                add_scheme(token.content), token.content))
        else:
            result.append(token.content)
    return ''.join(result)


def shorten(text, permalink=None, permashortlink=None, permashortcitation=None,
            target_length=140, http_link_length=22, https_link_length=23):
    """Prepare note text for publishing as a tweet. Ellipsize and add a
    permalink or citation.

    If the full text plus optional '(permashortlink)' or
    '(permashortcitation)' can fit into the target length (defaults to
    140 characters), it will return the composed text.

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
    :param int http_link_length: The t.co length for an http URL (default = 22)
    :param int https_link_length: The t.co shortened length for an https URL
      (default = 23)

    :return string: the final composed text
    """
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
        citation_tokens.append(Token('text', ')', True))
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


# http://data.iana.org/TLD/tlds-alpha-by-domain.txt
TLD_STRING = """\
# Version 2015091901, Last Updated Sun Sep 20 07:07:01 2015 UTC
AAA
ABB
ABBOTT
ABOGADO
AC
ACADEMY
ACCENTURE
ACCOUNTANT
ACCOUNTANTS
ACO
ACTIVE
ACTOR
AD
ADS
ADULT
AE
AEG
AERO
AF
AFL
AG
AGENCY
AI
AIG
AIRFORCE
AIRTEL
AL
ALLFINANZ
ALSACE
AM
AMICA
AMSTERDAM
ANDROID
AO
APARTMENTS
APP
AQ
AQUARELLE
AR
ARCHI
ARMY
ARPA
AS
ASIA
ASSOCIATES
AT
ATTORNEY
AU
AUCTION
AUDIO
AUTO
AUTOS
AW
AX
AXA
AZ
AZURE
BA
BAND
BANK
BAR
BARCELONA
BARCLAYCARD
BARCLAYS
BARGAINS
BAUHAUS
BAYERN
BB
BBC
BBVA
BCN
BD
BE
BEER
BENTLEY
BERLIN
BEST
BET
BF
BG
BH
BHARTI
BI
BIBLE
BID
BIKE
BING
BINGO
BIO
BIZ
BJ
BLACK
BLACKFRIDAY
BLOOMBERG
BLUE
BM
BMW
BN
BNL
BNPPARIBAS
BO
BOATS
BOND
BOO
BOOTS
BOUTIQUE
BR
BRADESCO
BRIDGESTONE
BROKER
BROTHER
BRUSSELS
BS
BT
BUDAPEST
BUILD
BUILDERS
BUSINESS
BUZZ
BV
BW
BY
BZ
BZH
CA
CAB
CAFE
CAL
CAMERA
CAMP
CANCERRESEARCH
CANON
CAPETOWN
CAPITAL
CAR
CARAVAN
CARDS
CARE
CAREER
CAREERS
CARS
CARTIER
CASA
CASH
CASINO
CAT
CATERING
CBA
CBN
CC
CD
CEB
CENTER
CEO
CERN
CF
CFA
CFD
CG
CH
CHANEL
CHANNEL
CHAT
CHEAP
CHLOE
CHRISTMAS
CHROME
CHURCH
CI
CISCO
CITIC
CITY
CK
CL
CLAIMS
CLEANING
CLICK
CLINIC
CLOTHING
CLOUD
CLUB
CM
CN
CO
COACH
CODES
COFFEE
COLLEGE
COLOGNE
COM
COMMBANK
COMMUNITY
COMPANY
COMPUTER
CONDOS
CONSTRUCTION
CONSULTING
CONTRACTORS
COOKING
COOL
COOP
CORSICA
COUNTRY
COUPONS
COURSES
CR
CREDIT
CREDITCARD
CRICKET
CROWN
CRS
CRUISES
CSC
CU
CUISINELLA
CV
CW
CX
CY
CYMRU
CYOU
CZ
DABUR
DAD
DANCE
DATE
DATING
DATSUN
DAY
DCLK
DE
DEALS
DEGREE
DELIVERY
DELTA
DEMOCRAT
DENTAL
DENTIST
DESI
DESIGN
DEV
DIAMONDS
DIET
DIGITAL
DIRECT
DIRECTORY
DISCOUNT
DJ
DK
DM
DNP
DO
DOCS
DOG
DOHA
DOMAINS
DOOSAN
DOWNLOAD
DRIVE
DURBAN
DVAG
DZ
EARTH
EAT
EC
EDU
EDUCATION
EE
EG
EMAIL
EMERCK
ENERGY
ENGINEER
ENGINEERING
ENTERPRISES
EPSON
EQUIPMENT
ER
ERNI
ES
ESQ
ESTATE
ET
EU
EUROVISION
EUS
EVENTS
EVERBANK
EXCHANGE
EXPERT
EXPOSED
EXPRESS
FAGE
FAIL
FAITH
FAMILY
FAN
FANS
FARM
FASHION
FEEDBACK
FI
FILM
FINANCE
FINANCIAL
FIRMDALE
FISH
FISHING
FIT
FITNESS
FJ
FK
FLIGHTS
FLORIST
FLOWERS
FLSMIDTH
FLY
FM
FO
FOO
FOOTBALL
FOREX
FORSALE
FORUM
FOUNDATION
FR
FRL
FROGANS
FUND
FURNITURE
FUTBOL
FYI
GA
GAL
GALLERY
GAME
GARDEN
GB
GBIZ
GD
GDN
GE
GEA
GENT
GENTING
GF
GG
GGEE
GH
GI
GIFT
GIFTS
GIVES
GIVING
GL
GLASS
GLE
GLOBAL
GLOBO
GM
GMAIL
GMO
GMX
GN
GOLD
GOLDPOINT
GOLF
GOO
GOOG
GOOGLE
GOP
GOV
GP
GQ
GR
GRAPHICS
GRATIS
GREEN
GRIPE
GROUP
GS
GT
GU
GUGE
GUIDE
GUITARS
GURU
GW
GY
HAMBURG
HANGOUT
HAUS
HEALTHCARE
HELP
HERE
HERMES
HIPHOP
HITACHI
HIV
HK
HM
HN
HOCKEY
HOLDINGS
HOLIDAY
HOMEDEPOT
HOMES
HONDA
HORSE
HOST
HOSTING
HOTELES
HOTMAIL
HOUSE
HOW
HR
HSBC
HT
HU
IBM
ICBC
ICE
ICU
ID
IE
IFM
IINET
IL
IM
IMMO
IMMOBILIEN
IN
INDUSTRIES
INFINITI
INFO
ING
INK
INSTITUTE
INSURE
INT
INTERNATIONAL
INVESTMENTS
IO
IPIRANGA
IQ
IR
IRISH
IS
IST
ISTANBUL
IT
ITAU
IWC
JAVA
JCB
JE
JETZT
JEWELRY
JLC
JLL
JM
JO
JOBS
JOBURG
JP
JPRS
JUEGOS
KAUFEN
KDDI
KE
KG
KH
KI
KIM
KITCHEN
KIWI
KM
KN
KOELN
KOMATSU
KP
KR
KRD
KRED
KW
KY
KYOTO
KZ
LA
LACAIXA
LANCASTER
LAND
LASALLE
LAT
LATROBE
LAW
LAWYER
LB
LC
LDS
LEASE
LECLERC
LEGAL
LEXUS
LGBT
LI
LIAISON
LIDL
LIFE
LIGHTING
LIMITED
LIMO
LINDE
LINK
LIVE
LIXIL
LK
LOAN
LOANS
LOL
LONDON
LOTTE
LOTTO
LOVE
LR
LS
LT
LTDA
LU
LUPIN
LUXE
LUXURY
LV
LY
MA
MADRID
MAIF
MAISON
MAN
MANAGEMENT
MANGO
MARKET
MARKETING
MARKETS
MARRIOTT
MBA
MC
MD
ME
MEDIA
MEET
MELBOURNE
MEME
MEMORIAL
MEN
MENU
MG
MH
MIAMI
MICROSOFT
MIL
MINI
MK
ML
MM
MMA
MN
MO
MOBI
MODA
MOE
MOM
MONASH
MONEY
MONTBLANC
MORMON
MORTGAGE
MOSCOW
MOTORCYCLES
MOV
MOVIE
MOVISTAR
MP
MQ
MR
MS
MT
MTN
MTPC
MU
MUSEUM
MV
MW
MX
MY
MZ
NA
NADEX
NAGOYA
NAME
NAVY
NC
NE
NEC
NET
NETBANK
NETWORK
NEUSTAR
NEW
NEWS
NEXUS
NF
NG
NGO
NHK
NI
NICO
NINJA
NISSAN
NL
NO
NOKIA
NP
NR
NRA
NRW
NTT
NU
NYC
NZ
OFFICE
OKINAWA
OM
OMEGA
ONE
ONG
ONL
ONLINE
OOO
ORACLE
ORANGE
ORG
ORGANIC
OSAKA
OTSUKA
OVH
PA
PAGE
PANERAI
PARIS
PARTNERS
PARTS
PARTY
PE
PET
PF
PG
PH
PHARMACY
PHILIPS
PHOTO
PHOTOGRAPHY
PHOTOS
PHYSIO
PIAGET
PICS
PICTET
PICTURES
PINK
PIZZA
PK
PL
PLACE
PLAY
PLUMBING
PLUS
PM
PN
POHL
POKER
PORN
POST
PR
PRAXI
PRESS
PRO
PROD
PRODUCTIONS
PROF
PROPERTIES
PROPERTY
PROTECTION
PS
PT
PUB
PW
PY
QA
QPON
QUEBEC
RACING
RE
REALTOR
REALTY
RECIPES
RED
REDSTONE
REHAB
REISE
REISEN
REIT
REN
RENT
RENTALS
REPAIR
REPORT
REPUBLICAN
REST
RESTAURANT
REVIEW
REVIEWS
RICH
RICOH
RIO
RIP
RO
ROCKS
RODEO
RS
RSVP
RU
RUHR
RUN
RW
RYUKYU
SA
SAARLAND
SAKURA
SALE
SAMSUNG
SANDVIK
SANDVIKCOROMANT
SANOFI
SAP
SARL
SAXO
SB
SC
SCA
SCB
SCHMIDT
SCHOLARSHIPS
SCHOOL
SCHULE
SCHWARZ
SCIENCE
SCOR
SCOT
SD
SE
SEAT
SECURITY
SEEK
SENER
SERVICES
SEW
SEX
SEXY
SG
SH
SHIKSHA
SHOES
SHOW
SHRIRAM
SI
SINGLES
SITE
SJ
SK
SKI
SKY
SKYPE
SL
SM
SN
SNCF
SO
SOCCER
SOCIAL
SOFTWARE
SOHU
SOLAR
SOLUTIONS
SONY
SOY
SPACE
SPIEGEL
SPREADBETTING
SR
SRL
ST
STADA
STARHUB
STATOIL
STC
STCGROUP
STUDIO
STUDY
STYLE
SU
SUCKS
SUPPLIES
SUPPLY
SUPPORT
SURF
SURGERY
SUZUKI
SV
SWATCH
SWISS
SX
SY
SYDNEY
SYSTEMS
SZ
TAIPEI
TATAMOTORS
TATAR
TATTOO
TAX
TAXI
TC
TD
TEAM
TECH
TECHNOLOGY
TEL
TELEFONICA
TEMASEK
TENNIS
TF
TG
TH
THD
THEATER
THEATRE
TICKETS
TIENDA
TIPS
TIRES
TIROL
TJ
TK
TL
TM
TN
TO
TODAY
TOKYO
TOOLS
TOP
TORAY
TOSHIBA
TOURS
TOWN
TOYOTA
TOYS
TR
TRADE
TRADING
TRAINING
TRAVEL
TRUST
TT
TUI
TV
TW
TZ
UA
UBS
UG
UK
UNIVERSITY
UNO
UOL
US
UY
UZ
VA
VACATIONS
VC
VE
VEGAS
VENTURES
VERSICHERUNG
VET
VG
VI
VIAJES
VIDEO
VILLAS
VIN
VISION
VISTA
VISTAPRINT
VIVA
VLAANDEREN
VN
VODKA
VOTE
VOTING
VOTO
VOYAGE
VU
WALES
WALTER
WANG
WATCH
WEBCAM
WEBSITE
WED
WEDDING
WEIR
WF
WHOSWHO
WIEN
WIKI
WILLIAMHILL
WIN
WINDOWS
WINE
WME
WORK
WORKS
WORLD
WS
WTC
WTF
XBOX
XEROX
XIN
XN--11B4C3D
XN--1QQW23A
XN--30RR7Y
XN--3BST00M
XN--3DS443G
XN--3E0B707E
XN--3PXU8K
XN--42C2D9A
XN--45BRJ9C
XN--45Q11C
XN--4GBRIM
XN--55QW42G
XN--55QX5D
XN--6FRZ82G
XN--6QQ986B3XL
XN--80ADXHKS
XN--80AO21A
XN--80ASEHDB
XN--80ASWG
XN--90A3AC
XN--90AIS
XN--9DBQ2A
XN--9ET52U
XN--B4W605FERD
XN--C1AVG
XN--C2BR7G
XN--CG4BKI
XN--CLCHC0EA0B2G2A9GCD
XN--CZR694B
XN--CZRS0T
XN--CZRU2D
XN--D1ACJ3B
XN--D1ALF
XN--EFVY88H
XN--ESTV75G
XN--FHBEI
XN--FIQ228C5HS
XN--FIQ64B
XN--FIQS8S
XN--FIQZ9S
XN--FJQ720A
XN--FLW351E
XN--FPCRJ9C3D
XN--FZC2C9E2C
XN--GECRJ9C
XN--H2BRJ9C
XN--HXT814E
XN--I1B6B1A6A2E
XN--IMR513N
XN--IO0A7I
XN--J1AEF
XN--J1AMH
XN--J6W193G
XN--KCRX77D1X4A
XN--KPRW13D
XN--KPRY57D
XN--KPUT3I
XN--L1ACC
XN--LGBBAT1AD8J
XN--MGB9AWBF
XN--MGBA3A4F16A
XN--MGBAAM7A8H
XN--MGBAB2BD
XN--MGBAYH7GPA
XN--MGBBH1A71E
XN--MGBC0A9AZCG
XN--MGBERP4A5D4AR
XN--MGBPL2FH
XN--MGBX4CD0AB
XN--MK1BU44C
XN--MXTQ1M
XN--NGBC5AZD
XN--NODE
XN--NQV7F
XN--NQV7FS00EMA
XN--NYQY26A
XN--O3CW4H
XN--OGBPF8FL
XN--P1ACF
XN--P1AI
XN--PGBS0DH
XN--PSSY2U
XN--Q9JYB4C
XN--QCKA1PMC
XN--RHQV96G
XN--S9BRJ9C
XN--SES554G
XN--T60B56A
XN--TCKWE
XN--UNUP4Y
XN--VERMGENSBERATER-CTB
XN--VERMGENSBERATUNG-PWB
XN--VHQUV
XN--VUQ861B
XN--WGBH1C
XN--WGBL6A
XN--XHQ521B
XN--XKC2AL3HYE2A
XN--XKC2DL3A5EE0H
XN--Y9A3AQ
XN--YFRO4I67O
XN--YGBI2AMMX
XN--ZFR164B
XPERIA
XXX
XYZ
YACHTS
YANDEX
YE
YODOBASHI
YOGA
YOKOHAMA
YOUTUBE
YT
ZA
ZIP
ZM
ZONE
ZUERICH
ZW
"""

TLDS = set(line.lower() for line in TLD_STRING.split('\n')
           if line and not line.startswith('#'))
