"""Read the machine brand audit's answers (the analysis plan, "Reading the answers"). Every reader returns (value, how); value is
None when the answer cannot be read, and `how` names the form that was matched.

    rating(text)            a whole number from 1 to 7
    percent(text)           a number from 0 to 100 (a range such as "3-5%" reads as its midpoint)
    yes_no(text)            "yes" or "no", from the first word of the first line
    country(text)           a country's canonical name, or None
    recognition(text)       {"yes": bool, "country": str or None, "fact": str}
    brand_list(text, known) [canonical brands in order], [unmatched names]
    one_brand(text, known)  a canonical brand, or None
    read(item, answer)      the reader of the item's measure
"""
import re
import unicodedata

_MD = re.compile(r"[*_`#>]+")
# "First line: yes" (Qwen 3.5 0.8B wrote the format's labels back; the analysis plan's amendment 4)
_LABEL = re.compile(r"^(?:first|second|third|1st|2nd|3rd)\s+line\s*[:\-–]\s*", re.I)


def final_text(answer):
    """The answer a model gave after its reasoning (the analysis plan's amendment 4). gpt-oss models answered on the computing cluster in their
    two channels ("analysis<reasoning>assistantfinal<answer>"); a model whose chat template opens a reasoning block can
    leave "</think>" or an unclosed "<think>" in the text. The rule is Study 2's final_answer (common/
    parse_answer.py, read only), so that the audit and the letters of the gap read answers the same way; the
    audit's own cases are in test_parse_audit.py."""
    import os
    import sys
    s2 = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "common"))
    if s2 not in sys.path:
        sys.path.insert(0, s2)
    from parse_answer import final_answer
    return final_answer(answer)


def _lines(text):
    return [_LABEL.sub("", l.strip()).strip() for l in _MD.sub("", text or "").replace("\r", "").split("\n")
            if _LABEL.sub("", l.strip()).strip()]


def _first(text):
    lines = _lines(text)
    return lines[0] if lines else ""


# the scale written back ("on a scale of 1 to 7", "1 (low) - 7 (high)", "6/7", "5 out of 7") is removed before reading
_ECHO = re.compile(r"\b1\s*(?:\([^)]*\))?\s*(?:-|–|to)\s*7\b(?:\s*\([^)]*\))?|(?:\bout of|/)\s*7\b", re.I)


def rating(text, lo=1, hi=7):
    text = _ECHO.sub(" ", text or "")
    first = _first(text)
    if not first:
        return None, "empty"
    for m in re.finditer(r"(?<![\d.])(\d+(?:\.\d+)?)(?![\d])", first):
        v = m.group(1)
        if "." in v:
            continue
        if lo <= int(v) <= hi:
            return int(v), "first-line"
        break
    found = {int(m.group(1)) for m in re.finditer(r"(?<![\d.])(\d+)(?![\d.])", _MD.sub("", text or ""))
             if lo <= int(m.group(1)) <= hi}
    if len(found) == 1:
        return found.pop(), "body"
    return None, "several" if found else "none"


_NUM = r"(\d+(?:\.\d+)?)"
_RANGE = re.compile(_NUM + r"\s*%?\s*(?:-|–|to)\s*" + _NUM)


def percent(text):
    first = _first(text)
    if not first:
        return None, "empty"
    for line, how in ((first, "first-line"),) + tuple((l, "body") for l in _lines(text)[1:]):
        r = _RANGE.search(line)
        n = re.search(_NUM, line)
        if r and n and r.start() == n.start():
            a, b = float(r.group(1)), float(r.group(2))
            if 0 <= a <= b <= 100:
                return (a + b) / 2, how + " range"
        if n:
            v = float(n.group(1))
            if 0 <= v <= 100:
                return v, how
            return None, "out of range"
    return None, "none"


def yes_no(text):
    first = _first(text).lower()
    m = re.match(r"[\W]*([a-z]+)", first)
    if not m:
        return None, "none"
    if m.group(1) == "yes":
        return "yes", "first-word"
    if m.group(1) == "no":
        return "no", "first-word"
    return None, "none"


COUNTRIES = {
    "United States": ["united states of america", "united states", "usa", "u s a", "u s", "us", "america",
                      "the united states"],
    "China": ["china", "people s republic of china", "prc", "mainland china"],
    "Hong Kong": ["hong kong"],
    "Taiwan": ["taiwan"],
    "Japan": ["japan"],
    "South Korea": ["south korea", "korea", "republic of korea"],
    "Germany": ["germany"],
    "United Kingdom": ["united kingdom", "uk", "u k", "england", "britain", "great britain", "scotland", "wales"],
    "France": ["france"], "Italy": ["italy"], "Switzerland": ["switzerland"],
    "Netherlands": ["netherlands", "the netherlands", "holland"], "Denmark": ["denmark"], "Sweden": ["sweden"],
    "Finland": ["finland"], "Norway": ["norway"], "Canada": ["canada"], "Australia": ["australia"], "India": ["india"],
    "Singapore": ["singapore"], "Ireland": ["ireland"], "Spain": ["spain"], "Austria": ["austria"],
    "Belgium": ["belgium"], "Israel": ["israel"], "Mexico": ["mexico"], "Brazil": ["brazil"],
    "New Zealand": ["new zealand"], "Poland": ["poland"], "Czech Republic": ["czech republic", "czechia"],
    "Portugal": ["portugal"], "Turkey": ["turkey", "turkiye"], "Vietnam": ["vietnam", "viet nam"],
    "Thailand": ["thailand"], "Malaysia": ["malaysia"], "Indonesia": ["indonesia"], "Philippines": ["philippines"],
    "Russia": ["russia"], "Ukraine": ["ukraine"], "Estonia": ["estonia"], "Iceland": ["iceland"],
    "Luxembourg": ["luxembourg"], "Greece": ["greece"], "South Africa": ["south africa"],
    "United Arab Emirates": ["united arab emirates", "uae"],
}
# every other country (the analysis plan's amendment 4: a model that names a country outside the list above was left unread)
for _c in ("Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda", "Argentina", "Armenia",
           "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belize", "Benin", "Bhutan",
           "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brunei", "Bulgaria", "Burkina Faso", "Burundi",
           "Cambodia", "Cameroon", "Cape Verde", "Central African Republic", "Chad", "Chile", "Colombia", "Comoros",
           "Costa Rica", "Croatia", "Cuba", "Cyprus", "Djibouti", "Dominica", "Dominican Republic", "Ecuador",
           "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Eswatini", "Ethiopia", "Fiji", "Gabon", "Gambia",
           "Georgia", "Ghana", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau", "Guyana", "Haiti", "Honduras",
           "Hungary", "Iran", "Iraq", "Ivory Coast", "Jamaica", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Kosovo",
           "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya", "Liechtenstein",
           "Lithuania", "Madagascar", "Malawi", "Maldives", "Mali", "Malta", "Marshall Islands", "Mauritania",
           "Mauritius", "Micronesia", "Moldova", "Monaco", "Mongolia", "Montenegro", "Morocco", "Mozambique",
           "Myanmar", "Namibia", "Nauru", "Nepal", "Nicaragua", "Niger", "Nigeria", "North Korea", "North Macedonia",
           "Oman", "Pakistan", "Palau", "Palestine", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Qatar",
           "Romania", "Rwanda", "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", "Samoa",
           "San Marino", "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone",
           "Slovakia", "Slovenia", "Solomon Islands", "Somalia", "South Sudan", "Sri Lanka", "Sudan", "Suriname",
           "Syria", "Tajikistan", "Tanzania", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia",
           "Turkmenistan", "Tuvalu", "Uganda", "Uruguay", "Uzbekistan", "Vanuatu", "Vatican City", "Venezuela",
           "Yemen", "Zambia", "Zimbabwe", "Puerto Rico", "Greenland", "Scotland"):
    if _c not in COUNTRIES and not any(_c.lower() in v for v in COUNTRIES.values()):
        COUNTRIES[_c] = [_c.lower()]
EUROPE = {"Germany", "United Kingdom", "France", "Italy", "Switzerland", "Netherlands", "Denmark", "Sweden", "Finland",
          "Norway", "Ireland", "Spain", "Austria", "Belgium", "Poland", "Czech Republic", "Portugal", "Estonia",
          "Iceland", "Luxembourg", "Greece", "Ukraine", "Russia"}


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    s = s.replace("&", " and ").replace("'", "").replace("’", "")
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


_C_ALIASES = sorted(((norm(a), c) for c, al in COUNTRIES.items() for a in al), key=lambda x: -len(x[0]))


def country(text):
    t = " " + norm(text) + " "
    best = None
    for a, c in _C_ALIASES:
        i = t.find(" " + a + " ")
        if i >= 0 and (best is None or i < best[0]):
            best = (i, c)
    if best:
        return best[1], "matched"
    return None, "none"


def recognition(text):
    yn, how = yes_no(text)
    if yn is None:
        return None, how
    lines = _lines(text)
    out = {"yes": yn == "yes", "country": None, "fact": ""}
    if yn == "yes":
        rest = lines[1:]
        if not rest:   # "Yes, China, ..." on one line
            rest = [re.sub(r"^\W*yes\W*", "", lines[0], flags=re.I)]
        if rest:
            out["country"] = country(rest[0])[0]
            out["fact"] = " ".join(rest[1:])
    return out, how


# Names that point to a brand of the tables or of the reference set; a product line points to its maker.
ALIASES = {
    "hewlett packard": "HP", "hp inc": "HP", "macbook": "Apple", "iphone": "Apple", "ipad": "Apple", "airpods": "Apple",
    "apple watch": "Apple", "galaxy": "Samsung", "pixel": "Google", "google pixel": "Google", "nest": "Google",
    "roomba": "iRobot", "kindle": "Amazon", "fire hd": "Amazon", "fire max": "Amazon", "amazon fire": "Amazon",
    "thinkpad": "Lenovo",
    "ideapad": "Lenovo", "legion": "Lenovo", "xps": "Dell", "inspiron": "Dell", "alienware": "Dell", "pavilion": "HP",
    "spectre": "HP", "envy": "HP", "omen": "HP", "rog": "ASUS", "zenbook": "ASUS", "vivobook": "ASUS",
    "predator": "Acer", "aspire": "Acer", "bravia": "Sony", "quietcomfort": "Bose", "beats by dre": "Beats",
    "beats by dr dre": "Beats", "wd": "Western Digital", "wd black": "Western Digital", "ue": "Ultimate Ears",
    "tnf": "The North Face", "north face": "The North Face", "oral b": "Oral-B", "delonghi": "De'Longhi",
    "de longhi": "De'Longhi", "mr coffee": "Mr. Coffee", "hoka one one": "HOKA", "sonicare": "Philips",
    "philips sonicare": "Philips", "anker soundcore": "Soundcore", "soundcore by anker": "Soundcore",
    "anker eufy": "eufy", "eufy by anker": "eufy", "tp link": "TP-Link", "tplink": "TP-Link", "orbi": "Netgear",
    "netgear orbi": "Netgear", "fuji": "Fujifilm", "hydroflask": "Hydro Flask", "kitchen aid": "KitchenAid",
    "camel bak": "CamelBak", "om digital solutions": "OM System", "om digital": "OM System", "jbl by harman": "JBL",
    "lg electronics": "LG", "samsung electronics": "Samsung", "sony electronics": "Sony",
    "audio technica": "Audio-Technica", "beyer dynamic": "Beyerdynamic", "new balance": "New Balance",
    "silicon power": "Silicon Power", "thermo flask": "ThermoFlask",
}


def make_matcher(known):
    """known: brand names that count in this category (tables' brands, the reference brands). Returns match(name),
    which gives the canonical brand or None: an exact name or alias first, then the longest known name or alias that
    begins the name ("Dell XPS 13" -> Dell, "Samsung Galaxy Book" -> Samsung)."""
    keys = {norm(b): b for b in known}
    for a, b in ALIASES.items():
        if b in known:
            keys[norm(a)] = b
    order = sorted(keys, key=len, reverse=True)

    def match(name):
        n = norm(name)
        if not n:
            return None
        if n in keys:
            return keys[n]
        for k in order:
            if n.startswith(k + " "):
                return keys[k]
        return None
    return match


_BULLET = re.compile(r"^\s*(?:\d+\s*[.)\]:-]\s*|[-•·▪◦]\s*)")
_CUT = re.compile(r"\s+[-–—:]\s+|\s*[(\[:]|\s+[-–—]\s*$")


def clean_name(line):
    s = _BULLET.sub("", _MD.sub("", line)).strip()
    s = _CUT.split(s, maxsplit=1)[0].strip()
    return s.strip(" .,;")


def brand_list(text, known):
    match = make_matcher(known)
    found, other = [], []
    for line in _lines(text):
        name = clean_name(line)
        if not name:
            continue
        b = match(name)
        if b:
            if b not in found:
                found.append(b)
        else:
            other.append(name)
    return (found, other), ("listed" if found else "none")


def one_brand(text, known):
    match = make_matcher(known)
    first = clean_name(_first(text))
    b = match(first)
    if b:
        return b, "first-line"
    return None, ("other: " + first[:60]) if first else "empty"


# In free answers, brand names that are also common words are read by stricter rules: a word in CASED counts only with
# its capital letter; "Nothing" and "Amazon" count only with one of their products ("on Amazon" names a shop).
CASED = {"Beats", "Shark", "Ninja", "Quip", "Stanley", "Yeti", "Brooks", "Insignia", "Flair", "Varia", "Apple"}
SPECIAL = {"Nothing": re.compile(r"\bNothing\s+(?:Phone|Ear)\b|\bCMF by Nothing\b"),
           "Amazon": re.compile(r"\bAmazon\s+(?:Fire|Kindle)\b|\bFire\s+(?:HD|Max|7|8|10)\b|\bKindle\b"),
           "S'well": re.compile(r"\bS['’]?well\b")}
# product lines whose names are also ordinary words or short letters count in a free answer only as written here
CASED_ALIASES = {"galaxy": "Galaxy", "pixel": "Pixel", "nest": "Nest", "legion": "Legion", "pavilion": "Pavilion",
                 "spectre": "Spectre", "envy": "Envy", "omen": "OMEN", "rog": "ROG", "predator": "Predator",
                 "aspire": "Aspire", "fuji": "Fuji", "ue": "UE", "wd": "WD", "tnf": "TNF", "xps": "XPS", "orbi": "Orbi",
                 "kindle": "Kindle"}


def mentions(text, known):
    """The brands of `known` that a free answer names, in the order of their first mention (a product line counts for
    its maker: "iPhone 15" for Apple), each matched only as a whole word. Returns ([brands], how); the position is
    the character offset of the first mention in the answer with markdown removed."""
    raw = _MD.sub("", text or "")
    first = {}

    def hit(b, i):
        if b not in first or i < first[b]:
            first[b] = i
    lowered = raw.lower()
    for b in known:
        if b in SPECIAL:
            m = SPECIAL[b].search(raw)
            if m:
                hit(b, m.start())
            continue
        names = [a for a, c in ALIASES.items() if c == b]
        if b in CASED:     # the brand's own name with its capital letter; its product lines as below
            m = re.search(r"\b" + re.escape(b) + r"\b", raw)
            if m:
                hit(b, m.start())
        else:
            names = [b] + names
        for n in names:
            if n in CASED_ALIASES:
                m = re.search(r"\b" + re.escape(CASED_ALIASES[n]) + r"\b", raw, re.I if n == "omen" else 0)
                if m and (n != "omen" or m.group(0) in ("OMEN", "Omen")):
                    hit(b, m.start())
                continue
            pat = r"(?<![a-z0-9])" + r"[\s\-'’.]*".join(re.escape(w) for w in norm(n).split()) + r"(?![a-z0-9])"
            m = re.search(pat, lowered)
            if m:
                hit(b, m.start())
    found = sorted(first, key=first.get)
    return found, ("named" if found else "none")


def read(item, answer, known=()):
    m = item["measure"]
    if m == "consideration":
        return mentions(answer, known)
    if m in ("typicality", "rating", "credibility") or (m == "quality" and item["attribute"] != "failure"):
        return rating(answer)
    if m == "quality":
        return percent(answer)
    if m == "recognition":
        return recognition(answer)
    if m == "country":
        return country(_first(answer))
    if m == "salience":
        return brand_list(answer, known)
    if m == "default":
        return one_brand(answer, known)
    if m == "description":
        t = " ".join(_lines(answer))
        return (t, "text") if t else (None, "empty")
    raise ValueError(f"no reader for measure {m}")
