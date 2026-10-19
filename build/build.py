#!/usr/bin/env python3
"""Generate the AI Evaluation Field Guide static pages.

Reads data/*.json and content/source/*, writes HTML into the site folder plus
js/data.js, js/search-index.js and feed.xml. Python 3 standard library only.

    python3 build/import_manuscript.py   # only after editing the manuscript
    python3 build/build.py
"""
import base64
import urllib.parse
import datetime
import hashlib
import html
import json
import pathlib
import re
import sys
import collections

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import bibliography  # noqa: E402  (source counts and the Bibliography, computed from data)

ROOT = pathlib.Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
SRC = ROOT / "content/source"


def load(name):
    return json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))


SITE = load("site.json")
LAWS = load("laws.json")
EDIT = load("editorial.json")
ROOM = load("room.json")
NAMING = load("naming.json")
LIMITS = load("limits.json")
GLOSS = load("glossary.json")
CHANGELOG = load("changelog.json")["entries"]

CATS = [
    {"id": "I", "name": "What you're measuring", "short": "Measuring", "n": 1},
    {"id": "II", "name": "The test itself", "short": "The test", "n": 2},
    {"id": "III", "name": "Running the eval", "short": "Running", "n": 3},
    {"id": "IV", "name": "Reading the results", "short": "Results", "n": 4},
    {"id": "V", "name": "Beyond the benchmark", "short": "Beyond", "n": 5},
]
for _c in CATS:
    _c["thread"] = EDIT["categories"][_c["id"]]["thread"]
CAT = {c["id"]: c for c in CATS}
# One list drives the header nav, the mobile menu and the footer. Groups are (label, [(label, href), ...]).
# The current page is marked in write(), from its file name, so pages do not need to say where they sit.
NAV = [
    ("Patterns", "index.html"),
    ("Use it now", "use-it-now.html"),
    ("Tools", [
        ("Find your patterns", "situation-finder.html"),
        ("Claim checker", "claim-checker.html"),
        ("Design Rubric", "design-rubric.html"),
        ("Readiness Review", "readiness-review.html"),
        ("Sample size", "sample-size.html"),
        ("Case studies", "case-studies.html"),
        ("Templates", "templates.html"),
    ]),
    ("Guide", "guide.html"),
    ("About", "about.html"),
]
# Pages that belong to a nav item without being in the nav themselves (marked as the section, not the page).
NAV_SECTION = {
    "brief.html": "index.html",
    "checklist.html": "index.html",
    "changelog.html": "about.html",
    "privacy.html": "about.html",
}
# The guide: four chapters in reading order (the walkthrough first), then reference pages. The question lists (INTENT_PAGES) are
# the "Playbooks by situation" group. guide.html is the hub; the overview essay lives at overview.html.
GUIDE_CHAPTERS = [
    ("walkthrough.html", "Walkthrough", "Three real cases read slowly in three steps: choose the claim, test it against the patterns, decide what you can and cannot conclude."),
    ("overview.html", "Overview", "What AI evaluation is, why it is hard, and how to use the patterns."),
    ("playbook.html", "Playbook", "Ten questions for reading any AI claim, a sequence for building your own eval, red flags, and an eval card template."),
    ("being-pragmatic.html", "Being Pragmatic", "How to do this inside a real team, with deadlines, a small budget, and a model that changed last Tuesday."),
]
GUIDE_REFERENCE = [
    ("glossary.html", "Glossary", "Definitions of the terms used across the patterns."),
    ("bibliography.html", "Bibliography", "Every source cited on this site, and where each is used."),
    ("methodology.html", "Methodology", "How the patterns were chosen, what counts as a source, and what the guide does not claim."),
]
FONTS = (
    "https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500"
    "&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400"
    "&family=Public+Sans:wght@400;500;600&display=swap"
)


# ---------------------------------------------------------------- text helpers
def esc(s):
    return html.escape(s, quote=True)


def typo(s):
    s = re.sub(r"(\w)'(\w)", "\\1\u2019\\2", s)
    s = re.sub(r'(^|[\s(\[\u2014-])"', "\\1\u201c", s)
    s = s.replace('"', "\u201d")
    s = re.sub(r"(^|[\s(\[\u2014-])'", "\\1\u2018", s)
    return s.replace("'", "\u2019")


def unescape_md(s):
    return re.sub(r"\\([^A-Za-z0-9\s*_])", r"\1", s)


def inline(s):
    """Inline markdown (bold, italic, links) to HTML. Text is smart-quoted and escaped."""
    links = []

    def grab(m):
        links.append((m.group(1), re.sub(r"\\(.)", r"\1", m.group(2))))
        return "\x03%d\x03" % (len(links) - 1)

    s = re.sub(r"\[((?:\\.|[^\]\\])+)\]\(((?:\\.|[^)\\])+)\)", grab, s)
    s = unescape_md(s)
    s = s.replace("\\*", "\x01").replace("\\_", "\x02")
    s = esc(typo(s))
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    s = s.replace("\x01", "*").replace("\x02", "_")

    def put(m):
        text, url = links[int(m.group(1))]
        return '<a href="%s" rel="noopener">%s</a>' % (esc(url), esc(typo(text)))

    return re.sub("\x03(\\d+)\x03", put, s)


def plain(s):
    s = unescape_md(s).replace("\\*", "*").replace("\\_", "_")
    s = re.sub(r"\[((?:[^\]])+)\]\([^)]*\)", r"\1", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"(?<![\w*])\*(.+?)\*(?![\w*])", r"\1", s)
    return s.replace("\u00a0", " ")


def txt(s):
    """Plain text from importer strings that may keep \\* or \\_ escapes."""
    return s.replace("\\*", "*").replace("\\_", "_")


def slugify(s):
    s = re.sub(r"[^a-z0-9]+", "-", plain(s).lower().replace("'", ""))
    return s.strip("-")


def fmt_date(iso, short=False):
    d = datetime.date.fromisoformat(iso)
    return "%d %s %d" % (d.day, d.strftime("%b"), d.year) if not short else "%d %s" % (d.day, d.strftime("%b"))


# ---------------------------------------------------------------- data prep
def sentences(text):
    """Split into sentences without breaking after 'et al.' or inside '(2016)'."""
    return re.split(r'(?<!al\.)(?<=[.?!])\s+(?=[A-Z\u201c"])', text)


def prep_laws():
    glossary_by_law = collections.defaultdict(list)
    for g in GLOSS:
        for name in g["see"]:
            glossary_by_law[name].append(g)
    keysets = []
    for law in LAWS:
        keysets.append({re.sub(r"[^a-z0-9]", "", s["title"].lower()) for s in law["sources"]})
    for i, law in enumerate(LAWS):
        ed = EDIT["laws"][law["slug"]]
        law["roles"] = ed["roles"]
        law["plainTerms"] = ed["plainTerms"]
        law["bottomLine"] = ed["bottomLine"]
        law["bottomLineCaveat"] = ed["bottomLineCaveat"]
        law["questions"] = ed["questions"]
        law["alsoKnownAs"] = ed.get("alsoKnownAs", [])
        law["workedExample"] = ed.get("workedExample")
        d = SITE["lawDefaults"]
        law["published"] = ed.get("published", d["published"])
        law["revised"] = ed.get("revised")
        law["version"] = ed.get("version", d["version"])
        law["evidenceChecked"] = ed.get("evidenceChecked", d["evidenceChecked"])
        law["history"] = ed.get("history") or [{"v": law["version"], "d": law["published"], "t": "Published."}]
        law["terms"] = glossary_by_law.get(law["name"], [])
        scores = []
        for j, other in enumerate(LAWS):
            if j == i:
                continue
            shared = len(keysets[i] & keysets[j])
            if shared:
                same_cat = 1 if other["category"] == law["category"] else 0
                scores.append((-shared, -same_cat, abs(j - i), j))
        law["shared"] = [[LAWS[j]["no"], n] for n, j in sorted(((len(keysets[i] & keysets[j]), j) for j in range(len(LAWS)) if j != i and keysets[i] & keysets[j]), key=lambda t: (-t[0], t[1]))]
        item, idxs = EDIT["briefEvidence"][law["slug"]]
        ev_sentences = sentences(plain(law["evidence"][item]["text"]))
        law["evidenceLine"] = typo(" ".join(ev_sentences[k] for k in idxs))
        law["doIt"] = typo(plain(law["useIt"][0]))
        scores.sort()
        related = [LAWS[s[3]]["slug"] for s in scores[:3]]
        fill = sorted((j for j in range(len(LAWS)) if j != i and LAWS[j]["slug"] not in related), key=lambda j: (LAWS[j]["category"] != law["category"], abs(j - i)))
        law["related"] = (related + [LAWS[j]["slug"] for j in fill])[:3]
    by_slug = {l["slug"]: l for l in LAWS}
    return by_slug


BY_SLUG = prep_laws()
BY_SLUG_NAMES = {l["name"] for l in LAWS}
NAMES = sorted([(l["name"], l["slug"]) for l in LAWS], key=lambda t: -len(t[0]))
PAGE_LINKS = {"Overview": "overview.html", "Being Pragmatic": "being-pragmatic.html", "Playbook": "playbook.html", "Glossary": "glossary.html"}


def link_laws(h, prefix=""):
    """Link pattern names and guide page names found in text nodes (outside existing anchors)."""
    parts = re.split(r"(<[^>]+>)", h)
    out, in_a = [], 0
    targets = [(typo(n), "patterns/%s.html" % s) for n, s in NAMES] + [(typo(n), href) for n, href in PAGE_LINKS.items() if n in ("Being Pragmatic", "Playbook")]
    targets.sort(key=lambda t: -len(t[0]))
    pattern = re.compile("|".join(re.escape(n) for n, _ in targets))
    lookup = dict(targets)
    for part in parts:
        if part.startswith("<"):
            if part.startswith("<a "):
                in_a += 1
            elif part.startswith("</a"):
                in_a -= 1
            out.append(part)
        elif in_a:
            out.append(part)
        else:
            out.append(pattern.sub(lambda m: '<a href="%s%s">%s</a>' % (prefix, lookup[m.group(0)], m.group(0)), part))
    return "".join(out)


def law_url(slug, prefix=""):
    return "%spatterns/%s.html" % (prefix, slug)


# ---------------------------------------------------------------- markdown blocks
def md_blocks(lines, prefix="", h2="###"):
    out, i = [], 0
    h3 = h2 + "#"
    lines = [l.replace("\u00a0", " ") for l in lines]

    def is_block_start(ln):
        return ln.startswith("#") or ln.startswith("|") or ln.startswith("- ") or re.match(r"^\d+\\?\.\s", ln) or ln.startswith("> ")

    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1
        elif ln.startswith(h3 + " "):
            text = unescape_md(ln[len(h3) + 1 :])
            out.append('<h3 id="%s">%s</h3>' % (slugify(text), inline(text)))
            i += 1
        elif ln.startswith(h2 + " "):
            text = unescape_md(ln[len(h2) + 1 :])
            out.append('<h2 id="%s">%s</h2>' % (slugify(text), inline(text)))
            i += 1
        elif ln.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.match(r"^:?-+:?$", c) for c in cells):
                    rows.append(cells)
                i += 1
            head, body = rows[0], rows[1:]
            t = "<div class=\"table-wrap\"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>" % (
                "".join("<th scope=\"col\">%s</th>" % link_laws(inline(c), prefix) for c in head),
                "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % link_laws(inline(c), prefix) for c in r) for r in body),
            )
            out.append(t)
        elif ln.startswith("- ") or re.match(r"^\d+\\?\.\s", ln):
            ordered = not ln.startswith("- ")
            items = []
            while i < len(lines) and (lines[i].startswith("- ") or re.match(r"^\d+\\?\.\s", lines[i]) or (lines[i].startswith("  ") and lines[i].strip())):
                cur = lines[i]
                if cur.startswith("  "):
                    items[-1] += " " + cur.strip()
                else:
                    items.append(re.sub(r"^(- |\d+\\?\.\s)", "", cur).rstrip())
                i += 1
            tag = "ol" if ordered else "ul"
            out.append("<%s>%s</%s>" % (tag, "".join("<li>%s</li>" % link_laws(inline(x), prefix) for x in items), tag))
        elif ln.startswith("> "):
            out.append("<blockquote>%s</blockquote>" % inline(ln[2:]))
            i += 1
        else:
            buf = []
            while i < len(lines) and lines[i].strip() and not is_block_start(lines[i]):
                buf.append(lines[i].strip())
                i += 1
            if not buf:
                buf = [lines[i].strip()]
                i += 1
            out.append("<p>%s</p>" % link_laws(inline(" ".join(buf)), prefix))
    return "\n".join(out)


MANUSCRIPT = (SRC / "ai-evaluation-field-guide-full.md").read_text(encoding="utf-8").split("\n")


def manuscript_region(start, end):
    a = next(i for i, l in enumerate(MANUSCRIPT) if l.strip() == start)
    b = next((i for i, l in enumerate(MANUSCRIPT) if i > a and l.strip() == end), len(MANUSCRIPT))
    return MANUSCRIPT[a + 1 : b]


# ---------------------------------------------------------------- layout
def analytics_inline_js():
    # Consent defaults to denied in the EEA, UK and Switzerland (no banner, so analytics cookies are off there).
    return (
        "window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}"
        "gtag('consent','default',{ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied',analytics_storage:'denied',"
        "region:['AT','BE','BG','HR','CY','CZ','DK','EE','FI','FR','DE','GR','HU','IE','IT','LV','LT','LU','MT','NL','PL','PT','RO','SK','SI','ES','SE','IS','LI','NO','GB','CH']});"
        "gtag('js',new Date());gtag('config','%s');" % SITE["gaId"]
    )


TITLE_TAGS = {
    "Guide": "AI evaluation guide: what to read first, and what next",
    "A claim, read slowly": "A claim, read slowly: three AI evaluation cases",
    "Glossary": "AI evaluation glossary: key terms explained",
    "Playbook": "Playbook for reading AI claims and building evals",
    "Being Pragmatic": "AI evaluation on a real team: being pragmatic",
    "Claim checker": "AI claim checker: which patterns apply to a claim",
    "Find your patterns": "Find the AI evaluation patterns that fit your situation",
    "Use it now": "Questions to ask when someone shares an AI result",
    "AI Design Evaluation Rubric": "AI design evaluation rubric: 18 checks",
    "AI Readiness Review": "AI readiness review: a 27-criterion launch checklist",
    "Checklist builder": "Printable AI evaluation checklist builder",
}


def nav_html(p):
    """Primary nav from NAV. Tools is a <details> disclosure, so it opens without JavaScript."""
    out = ""
    for label, target in NAV:
        if isinstance(target, list):
            menu = "".join('<a href="%s%s">%s</a>' % (p, h, l) for l, h in target)
            out += '<details class="nav-group"><summary>%s</summary><div class="nav-group__menu">%s</div></details>' % (label, menu)
        else:
            out += '<a href="%s%s">%s</a>' % (p, target, label)
    return out


def footer_nav_html(p):
    """The same list, flattened, so a visitor without JavaScript can reach every page from the footer."""
    out = []
    for label, target in NAV:
        for l, h in (target if isinstance(target, list) else [(label, target)]):
            out.append('<a href="%s%s">%s</a>' % (p, h, l))
    return " \u00b7 ".join(out)


def nav_hrefs():
    return [h for _, t in NAV for h in ([x[1] for x in t] if isinstance(t, list) else [t])]


def guide_files():
    return {f for f, _, _ in GUIDE_CHAPTERS + GUIDE_REFERENCE} | {pg["file"] for pg in INTENT_PAGES}


def mark_nav(rel, content):
    """Add aria-current to this page's nav link ("page"), or to the nav item it belongs to ("true")."""
    exact = rel in nav_hrefs()
    if exact:
        target = rel
    elif rel.startswith("patterns/"):
        target = "index.html"
    elif rel in NAV_SECTION:
        target = NAV_SECTION[rel]
    elif rel in guide_files():
        target = "guide.html"
    else:
        return content
    m = re.search(r'<nav class="site-nav".*?</nav>', content, re.S)
    if not m:
        return content
    p = "../" * rel.count("/")
    needle = '<a href="%s%s"' % (p, target)
    block = m.group(0).replace(needle, needle + ' aria-current="%s"' % ("page" if exact else "true"), 1)
    for label, group in NAV:
        if isinstance(group, list) and target in [h for _, h in group]:
            block = block.replace("<summary>%s</summary>" % label, '<summary aria-current="true">%s</summary>' % label, 1)
    return content[: m.start()] + block + content[m.end() :]


def fit_desc(desc, limit=155):
    """Meta descriptions truncate near 155-160 characters in search results: keep whole sentences that fit, else cut at a word."""
    desc = re.sub(r"\s+", " ", desc).strip()
    if len(desc) <= limit:
        return desc
    out = ""
    for sent in sentences(desc):
        cand = (out + " " + sent).strip()
        if len(cand) > limit:
            break
        out = cand
    if len(out) >= 90:
        return out
    cut = desc[: limit - 1].rsplit(" ", 1)[0].rstrip(",;:")
    return cut + "\u2026"


def layout(title, desc, body, depth=0, current=None, scripts=(), data=False, skip="Skip to content", page_class="", head_extra="", og_image=None):
    p = "../" * depth
    desc = fit_desc(desc)
    if title == SITE["title"]:
        full_title = "%s: %d sourced principles for judging AI claims" % (SITE["title"], len(LAWS))
    else:
        tag = TITLE_TAGS.get(title) or ("%s in AI evaluation" % title if title in BY_SLUG_NAMES else title)
        full_title = "%s \u00b7 %s" % (tag, SITE["title"])
        if len(full_title) > 62:
            full_title = tag
    nav = nav_html(p)
    footer_nav = footer_nav_html(p)
    scripts_html = ""
    if data:
        scripts_html += '<script src="%sjs/data.js"></script>\n' % p
    scripts_html += '<script src="%sjs/collection.js" defer></script>\n' % p
    scripts_html += '<script src="%sjs/site.js" defer></script>\n' % p
    for s in scripts:
        scripts_html += '<script src="%sjs/%s" defer></script>\n' % (p, s)
    analytics = ""
    if SITE.get("gaId"):
        analytics = (
            '<script async src="https://www.googletagmanager.com/gtag/js?id=%s"></script>\n<script>%s</script>\n'
            % (SITE["gaId"], analytics_inline_js())
        )
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%(title)s</title>
<meta name="description" content="%(desc)s">
<meta property="og:title" content="%(title)s">
<meta property="og:description" content="%(desc)s">
<meta property="og:type" content="website">
<meta property="og:site_name" content="%(site)s">
<meta property="og:image" content="%(og)s">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="%(title)s">
<meta name="twitter:description" content="%(desc)s">
<meta name="twitter:image" content="%(og)s">
<link rel="icon" href="data:image/svg+xml,%%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%%3E%%3Crect width='32' height='32' fill='%%239b2f1f'/%%3E%%3Ctext x='16' y='23' font-size='20' text-anchor='middle' fill='%%23faf7f1' font-family='Georgia,serif'%%3E\u00a7%%3C/text%%3E%%3C/svg%%3E">
<link rel="alternate" type="application/rss+xml" title="%(site)s changelog" href="%(p)sfeed.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<script src="%(p)sjs/boot.js"></script>
<link rel="stylesheet" href="%(fonts)s">
<link rel="stylesheet" href="%(p)scss/tokens.css">
<link rel="stylesheet" href="%(p)scss/styles.css">
%(head_extra)s%(analytics)s</head>
<body class="%(page_class)s" data-root="%(p)s">
<a class="skip-link" href="#main">%(skip)s</a>
<header class="site-header">
  <a class="wordmark" href="%(p)sindex.html"><span class="wordmark__mark" aria-hidden="true">\u00a7</span><span class="wordmark__text">AI Evaluation Field Guide</span></a>
  <nav class="site-nav" id="site-nav" aria-label="Primary">%(nav)s</nav>
  <div class="header-actions">
    <button class="search-btn" type="button" data-search-open aria-haspopup="dialog"><svg aria-hidden="true" focusable="false" width="15" height="15" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6"><circle cx="6.5" cy="6.5" r="4.75"/><path d="M10 10l4.5 4.5" stroke-linecap="round"/></svg><span class="search-btn__text">Search</span></button>
    <button class="menu-btn" type="button" data-menu-toggle aria-expanded="false" aria-controls="site-nav">Menu</button>
  </div>
</header>
%(body)s
<footer class="site-footer">
  <nav class="site-footer__nav" aria-label="Footer">%(footer_nav)s</nav>
  <p>Independent reference. No vendor funding. <a href="%(p)sabout.html#editorial-policy">Editorial policy</a></p>
  <p>CC BY 4.0 \u00b7 <a href="%(p)smethodology.html">Methodology</a> \u00b7 <a href="%(p)sprivacy.html">Privacy</a> \u00b7 <a href="%(p)schangelog.html">Changelog</a> \u00b7 <a href="%(p)sfeed.xml">RSS</a> \u00b7 Last updated %(updated)s</p>
</footer>
%(scripts)s</body>
</html>
""" % {
        "analytics": analytics,
        "og": SITE["baseUrl"] + "/" + (og_image or "img/og.png"),
        "title": esc(full_title),
        "desc": esc(desc),
        "site": esc(SITE["title"]),
        "p": p,
        "fonts": FONTS,
        "nav": nav,
        "footer_nav": footer_nav,
        "body": body,
        "skip": esc(skip),
        "updated": fmt_date(SITE["updated"]),
        "scripts": scripts_html,
        "page_class": page_class,
        "head_extra": head_extra,
    }


def write(rel, content):
    if rel.endswith(".html"):
        url = SITE["baseUrl"] + "/" + ("" if rel == "index.html" else rel[: -len(".html")])
        tags = '<link rel="canonical" href="%s">\n<meta property="og:url" content="%s">\n' % (url, url)
        if rel == "index.html":
            tags += '<script type="application/ld+json">%s</script>\n' % json.dumps({"@context": "https://schema.org", "@type": "WebSite", "name": SITE["title"], "url": SITE["baseUrl"], "description": "26 short, sourced patterns for judging whether an AI system actually holds up.", "inLanguage": "en", "author": {"@type": "Person", "name": "Joseph Alfonso", "url": "https://josephalfonso.com"}}, ensure_ascii=False)
        content = content.replace("</head>", tags + "</head>", 1)
        content = mark_nav(rel, content)
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def roman_label(cat_id):
    return cat_id + "."


# ---------------------------------------------------------------- index
def pick_button(law, cls="pick", off="Add", on="Added"):
    name = esc(typo(law["name"]))
    return (
        '<button class="%s" type="button" data-pick="%d" data-name="%s" data-label-off="%s" data-label-on="%s" aria-pressed="false">'
        '<span class="pick__mark" aria-hidden="true">+</span><span class="pick__text">%s</span><span class="visually-hidden"> (%s)</span></button>' % (cls, int(law["no"]), name, off, on, off, name)
    )


def law_card(law, prefix=""):
    cat = CAT[law["category"]]
    return (
        '<li class="law-item"><a class="law-card cat-%d" href="%s" data-no="%s" data-roles="%s" data-published="%s" data-revised="%s">'
        '<span class="law-card__row"><span class="law-card__no">No. %s</span><span class="badge" data-badge hidden></span>'
        '%s<span class="tag">%s</span></span>'
        '<span class="law-card__title">%s</span>'
        '<span class="law-card__quote">\u201c%s\u201d</span>'
        '<span class="law-card__cta">Read the pattern \u2192</span></a>%s</li>'
        % (
            cat["n"],
            law_url(law["slug"], prefix),
            law["no"],
            esc(" ".join(r.lower() for r in law["roles"])),
            law["published"],
            law["revised"] or "",
            law["no"],
            evidence_card_tag(law),
            esc(cat["short"]),
            esc(typo(law["name"])),
            esc(typo(law["aphorism"])),
            pick_button(law),
        )
    )


NEWS = SITE.get("newsletter") or {}


def newsletter_action():
    """The signup endpoint from data/site.json, or "" when the signup is not set up."""
    action = (NEWS.get("action") or "").strip()
    if action and not action.startswith("https://"):
        raise SystemExit("data/site.json: newsletter.action must be an https:// URL (or empty)")
    return action


def follow_box(heading="h2"):
    """"Follow along" box. A plain POST form when a signup endpoint is configured, otherwise a pointer to the RSS feed."""
    action = newsletter_action()
    if action:
        hidden = "".join('<input type="hidden" name="%s" value="%s">' % (esc(k), esc(v)) for k, v in (NEWS.get("hidden") or {}).items())
        return (
            '<section class="follow" id="follow" aria-labelledby="follow-h">'
            '<%(h)s id="follow-h">Follow along</%(h)s>'
            '<form class="follow__form" method="post" action="%(action)s">'
            '<label for="follow-email">%(label)s</label>'
            '<div class="follow__row"><input id="follow-email" type="email" name="%(field)s" autocomplete="email" required>'
            '<button class="btn btn--ink" type="submit">Subscribe</button></div>%(hidden)s'
            '</form><p class="follow__note">%(privacy)s <a href="privacy.html">Privacy</a></p>'
            '<p class="follow__note">Prefer a feed reader? <a href="feed.xml">Use the RSS feed</a>.</p></section>'
        ) % {"h": heading, "action": esc(action), "label": esc(typo(NEWS["label"])), "field": esc(NEWS.get("field") or "email"), "hidden": hidden, "privacy": esc(typo(NEWS["privacy"]))}
    return (
        '<section class="follow" id="follow" aria-labelledby="follow-h">'
        '<%(h)s id="follow-h">Follow along</%(h)s>'
        '<p>Patterns are added and revised as the research changes, and every change is logged. '
        'Subscribe to the <a href="feed.xml">RSS feed</a> to get each update in a feed reader, or read the <a href="changelog.html">changelog</a>.</p></section>'
    ) % {"h": heading}


def start_here():
    cards = ""
    for r in SITE["startHere"]:
        reads = "".join(
            '<li><a href="%s"><span class="start__name">%s</span><span class="start__quote">“%s”</span></a></li>'
            % (law_url(sl), esc(typo(BY_SLUG[sl]["name"])), esc(typo(BY_SLUG[sl]["aphorism"])))
            for sl in r["patterns"]
        )
        cards += (
            '<li class="start__card"><h3 class="start__role">%(label)s</h3><p class="start__who">%(who)s</p>'
            '<p class="start__step"><span class="start__n" aria-hidden="true">1</span>Read these three patterns</p><ul class="start__reads">%(reads)s</ul>'
            '<p class="start__step"><span class="start__n" aria-hidden="true">2</span>Then use one tool</p>'
            '<p class="start__tool"><a class="btn btn--accent btn--sm" href="%(thref)s">%(tlabel)s</a> <span>%(twhy)s</span></p>'
            '<p class="start__more">Ready-made questions: <a href="%(lhref)s">%(llabel)s</a><br>'
            '<a href="index.html?role=%(role)s#patterns" data-role-link="%(role)s">All patterns for %(lower)s</a></p></li>'
        ) % {
            "label": esc(r["label"]), "who": esc(typo(r["who"])), "reads": reads, "role": r["role"], "lower": esc(r["label"].lower()),
            "thref": r["tool"]["href"], "tlabel": esc(r["tool"]["label"]), "twhy": esc(typo(r["tool"]["why"])),
            "lhref": r["list"]["href"], "llabel": esc(r["list"]["label"]),
        }
    return (
        '<section class="start" id="start-here" aria-labelledby="start-h">'
        '<div class="start__head"><h2 id="start-h">Start here</h2>'
        '<p>Pick the role closest to yours. Read three patterns, then use one tool on the claim or system in front of you.</p>'
        '<p class="start__walk">Want to see it done? <a href="walkthrough.html">Read a claim slowly</a>.</p></div>'
        '<ul class="start__grid">%s</ul></section>' % cards
    )


def build_index():
    total = len(LAWS)
    sections, chips = [], []
    for c in CATS:
        laws = [l for l in LAWS if l["category"] == c["id"]]
        cards = "".join(law_card(l) for l in laws)
        sections.append(
            '<section class="category cat-%d" id="cat-%s" aria-labelledby="cat-%s-h">'
            '<div class="category__head"><span class="category__num">%s</span><h3 id="cat-%s-h">%s</h3>'
            '<span class="category__count" data-count data-total="%d">%d of %d published</span></div>'
            '<ul class="card-grid">%s</ul></section>' % (c["n"], c["id"], c["id"], roman_label(c["id"]), c["id"], esc(typo(c["name"])), len(laws), len(laws), len(laws), cards)
        )
        chips.append('<a class="chip cat-%d" href="#cat-%s"><span class="chip__sq" aria-hidden="true"></span>%s</a>' % (c["n"], c["id"], c["id"]))
    lists = "".join('<a class="btn btn--outline btn--sm" href="%s">%s</a>' % (pg["file"], esc(pg["cta"])) for pg in INTENT_PAGES)

    # One copy of the pattern list. "By category" is the same markup laid out as columns (CSS keys off data-view),
    # so the page holds 26 patterns once. Without JavaScript the list is the category-by-category grid.
    body = """<main id="main" data-page="index" data-view="grid" data-total="%(total)d" data-updated="%(updated)s">
  <section class="hero">
    <div class="hero__text">
      <h1>Principles for judging whether an AI system <em>actually</em> holds up.</h1>
      <p class="hero__sub">%(total)d short, sourced patterns for people who build, buy, or design with AI. <a href="guide.html">How to use this guide</a></p>
      <div class="hero__actions">
        <a class="btn btn--accent" href="#start-here">Start here</a>
        <span class="hero__or">Need questions for a specific moment?</span>
        <span class="hero__lists">%(lists)s</span>
      </div>
    </div>
    <p class="hero__meta">Updated %(updated_h)s<br><a href="feed.xml">RSS</a> · <a href="changelog.html">Changelog</a></p>
  </section>
  %(start)s
  <section class="patterns" id="patterns" aria-labelledby="patterns-h">
    <div class="patterns__head">
      <h2 id="patterns-h">All %(total)d patterns</h2>
      <p class="patterns__why"><strong>Why these %(total)d?</strong> They are an editorial selection, not a systematic review: recurring ways AI evaluation goes wrong that have published research behind them. Another reasonable list would differ. Each page says whether its name is an established term or this site’s own. <a href="methodology.html#selection">How they were chosen and checked</a>.</p>
    </div>
    <div class="since" data-since hidden>
      <span class="since__badge" data-since-badge></span>
      <span data-since-text></span>
      <a href="changelog.html">See what changed</a>
      <button class="since__dismiss" type="button" data-since-dismiss>Dismiss</button>
    </div>
    <div class="toolbar">
      <div class="toolbar__js" data-js-only hidden>
        <div class="seg seg--ink" role="group" aria-label="View">
          <button type="button" data-view-btn="grid" aria-pressed="true">Grid</button>
          <button type="button" data-view-btn="category" aria-pressed="false">By category</button>
        </div>
        <div class="seg seg--rule" role="group" aria-label="Filter by role">
          <button type="button" data-role-btn="all" aria-pressed="true">All roles</button>
          <button type="button" data-role-btn="building" aria-pressed="false">Building</button>
          <button type="button" data-role-btn="buying" aria-pressed="false">Buying</button>
          <button type="button" data-role-btn="designing" aria-pressed="false">Designing</button>
        </div>
        <a class="btn btn--outline btn--sm toolbar__brief" href="brief.html" data-collection-link="brief.html">Quick brief<span data-collection-badge hidden> (<span data-collection-count>0</span>)</span></a>
      </div>
      <div class="toolbar__jump" data-jump><span class="toolbar__label">Jump to</span>%(chips)s</div>
      <p class="visually-hidden" role="status" aria-live="polite" data-status></p>
    </div>
    <div class="patterns__list">%(sections)s</div>
  </section>
  %(follow)s
</main>
<div class="tray no-print" data-tray hidden role="region" aria-label="My patterns">
  <p class="tray__count"><strong data-collection-count>0</strong> <span data-tray-word>patterns</span> in My patterns</p>
  <div class="tray__actions">
    <a class="btn btn--accent btn--sm" href="brief.html" data-collection-link="brief.html">Quick brief</a>
    <a class="btn btn--outline btn--sm" href="checklist.html?preset=custom" data-collection-link="checklist.html?preset=custom">Checklist</a>
    <button class="btn btn--ghost btn--sm" type="button" data-tray-clear>Clear</button>
  </div>
</div>
""" % {
        "total": total,
        "updated": SITE["updated"],
        "updated_h": fmt_date(SITE["updated"]),
        "lists": lists,
        "start": start_here(),
        "chips": "".join(chips),
        "sections": "".join(sections),
        "follow": follow_box(),
    }
    write(
        "index.html",
        layout(
            SITE["title"],
            "%d short, sourced patterns for people who build, buy, or design with AI: principles for judging whether an AI system actually holds up." % len(LAWS),
            body,
            current="laws",
            scripts=("index.js",),
            skip="Skip to patterns",
        ),
    )


# ---------------------------------------------------------------- law pages
SECTION_TOC = [
    ("plain-terms", "In plain terms"),
    ("takeaways", "Takeaways"),
    ("what-it-means", "What it means"),
    ("the-evidence", "The evidence"),
    ("use-it", "Use it"),
    ("questions-to-ask", "Questions to ask"),
    ("limits", "Where this doesn\u2019t apply"),
    ("origins", "Origins"),
    ("sources", "Sources"),
    ("cite-this-law", "Cite this pattern"),
    ("revision-history", "Revision history"),
]


EVIDENCE_LEVELS = {
    "well": {
        "label": "Well established",
        "dots": "●●●",
        "short": "Several peer-reviewed or classic sources, from different lead authors.",
    },
    "developing": {
        "label": "Developing",
        "dots": "●●○",
        "short": "A smaller or mixed base: some peer-reviewed support, with preprints, reports or a thin source list.",
    },
    "emerging": {
        "label": "Emerging",
        "dots": "●○○",
        "short": "A thin base: one peer-reviewed source or fewer, with the rest preprints or reports.",
    },
}


def evidence_base(law):
    """Evidence-base level for a pattern, computed from its source list only (thresholds in data/naming.json).

    It rates the sources cited on the page, not the wider literature. Reviewed and transparent: the same
    numbers are printed on the pattern page and explained on the About page.
    """
    crit = NAMING["evidenceCriteria"]
    wk, dv = crit["wellEstablished"], crit["developing"]
    srcs = law["sources"]
    n = len(srcs)
    peer = [s for s in srcs if not s["label"]]
    p = len(peer)
    leads = {re.sub(r"[^a-z]", "", txt(s["authors"]).split(",")[0].lower()) for s in peer}
    if n >= wk["minSources"] and p >= wk["minPeerReviewed"] and p / n >= wk["minPeerShare"] and len(leads) >= wk["minLeadAuthors"]:
        key = "well"
    elif n >= dv["minSources"] and p >= dv["minPeerReviewed"]:
        key = "developing"
    else:
        key = "emerging"
    why = "%d %s, %d peer-reviewed or classic" % (n, "source" if n == 1 else "sources", p)
    if p:
        why += " (from %d separate lead %s)" % (len(leads), "author" if len(leads) == 1 else "authors")
    return dict(EVIDENCE_LEVELS[key], key=key, why=why, n=n, peer=p, leads=len(leads))


def evidence_card_tag(law):
    ev = evidence_base(law)
    return '<span class="law-card__ev ev-%s" title="Evidence base: %s"><span aria-hidden="true">%s</span> <span class="visually-hidden">Evidence base: </span>%s</span>' % (ev["key"], ev["label"], ev["dots"], ev["label"])


def source_mix(law):
    c = collections.Counter(s["label"] or "peer" for s in law["sources"])
    parts = []
    if c["peer"]:
        parts.append("%d peer-reviewed or classic" % c["peer"])
    known = [(k, one, many) for k, (one, many) in bibliography.LABEL_PLURAL.items()]
    for key in sorted(set(c) - {"peer"} - {k for k, _, _ in known}):
        known.append((key, key.lower(), key.lower() + "s"))
    for key, one, many in known:
        if c[key]:
            parts.append("%d %s" % (c[key], one if c[key] == 1 else many))
    return ", ".join(parts)


def apa(law):
    d = datetime.date.fromisoformat(law["published"])
    return "AI Evaluation Field Guide. (%d, %s %d). %s (%s). %s/patterns/%s" % (d.year, d.strftime("%B"), d.day, law["name"], law["version"], SITE["baseUrl"], law["slug"])


def bibtex(law):
    d = datetime.date.fromisoformat(law["published"])
    return (
        "@misc{efg-%s,\n  title        = {%s},\n  author       = {{AI Evaluation Field Guide}},\n  year         = {%d},\n  month        = %s,\n"
        "  note         = {Version %s},\n  howpublished = {\\url{%s/patterns/%s}}\n}"
        % (law["slug"], law["name"], d.year, d.strftime("%b").lower(), law["version"].lstrip("v"), SITE["baseUrl"], law["slug"])
    )


ISSUES = "https://github.com/joealfonso/AI-Eval-Field-Guide/issues/new"


def report_url(law):
    title = "Correction: %s" % law["name"]
    body = "Pattern page: %s/patterns/%s\n\nWhat looks wrong, or what source should be added:\n\n" % (SITE["baseUrl"], law["slug"])
    return "%s?title=%s&body=%s" % (ISSUES, urllib.parse.quote(title), urllib.parse.quote(body))


def law_jsonld(law):
    data = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": law["name"],
        "description": "%s %s" % (law["aphorism"], law["bottomLine"]),
        "url": "%s/patterns/%s" % (SITE["baseUrl"], law["slug"]),
        "datePublished": law["published"],
        "dateModified": law.get("revised") or law["published"],
        "version": law["version"],
        "inLanguage": "en",
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "author": {"@type": "Person", "name": "Joseph Alfonso", "url": "https://josephalfonso.com"},
        "publisher": {"@type": "Organization", "name": SITE["title"], "url": SITE["baseUrl"]},
        "isPartOf": {"@type": "WebSite", "name": SITE["title"], "url": SITE["baseUrl"]},
        "citation": ["%s (%s). %s." % (txt(x["authors"]), x["year"], txt(x["title"])) for x in law["sources"]],
    }
    return '<script type="application/ld+json">%s</script>\n' % json.dumps(data, ensure_ascii=False).replace("</", "<\\/")


def case_line(law):
    """"See it in a real case" line linking to the matching entries on the case-studies page (ids from build_cases)."""
    cases = [c for c in load("cases.json")["cases"] if law["slug"] in c["patterns"]]
    if not cases:
        return ""
    links = "; ".join('<a href="../case-studies.html#%s">%s</a>' % (c["id"], esc(typo(c["title"]))) for c in cases)
    return '<p class="law__case">See it in a real case: %s</p>' % links


def bottom_line_box(law):
    """The quotable one-sentence takeaway with its main caveat directly beneath it."""
    return (
        '<section class="bottomline" aria-labelledby="bottom-line">'
        '<h2 class="bottomline__label" id="bottom-line">The bottom line</h2>'
        '<p class="bottomline__text">%s</p>'
        '<p class="bottomline__caveat"><span class="bottomline__k">Keep in mind:</span> %s</p></section>'
        % (esc(typo(law["bottomLine"])), esc(typo(law["bottomLineCaveat"])))
    )


def build_law(i, law):
    cat = CAT[law["category"]]
    cat_laws = [l for l in LAWS if l["category"] == law["category"]]
    pos = cat_laws.index(law) + 1
    nxt = LAWS[i + 1] if i + 1 < len(LAWS) else None
    url = "%s/patterns/%s" % (SITE["baseUrl"], law["slug"])
    cat_href = "../index.html#cat-%s" % cat["id"]

    toc = "".join(
        '<li><a href="#%s" data-toc="%s"><span class="toc__n">%02d</span><span>%s</span></a></li>' % (sid, sid, n + 1, label)
        for n, (sid, label) in enumerate(SECTION_TOC)
    )
    related = "".join(
        '<li><a href="%s.html"><span class="related__n">%s</span> <span class="related__t">%s</span></a></li>' % (s, BY_SLUG[s]["no"], esc(typo(BY_SLUG[s]["name"])))
        for s in law["related"]
    )

    def h2(sid, text, extra=""):
        return '<div class="sec-head"><h2 id="%s">%s <a class="permalink" href="#%s" aria-label="Link to %s">#</a></h2>%s</div>' % (sid, text, sid, esc(text), extra)

    takeaways = "".join("<li>%s</li>" % inline(t) for t in law["takeaways"])
    means = "".join("<p>%s</p>" % inline(p) for p in law["whatItMeans"])
    evidence = "".join("<p>%s%s</p>" % ("<strong>%s</strong> " % inline(e["lead"]) if e["lead"] else "", inline(e["text"])) for e in law["evidence"])
    use_it = "".join("<li>%s</li>" % inline(t) for t in law["useIt"])
    limits = "<p>%s</p>" % esc(typo(LIMITS[law["slug"]]))
    questions = "".join(
        '<li><label class="qrow"><input type="checkbox"><span class="qrow__box" aria-hidden="true"></span><span>%s</span></label></li>' % esc(typo(q)) for q in law["questions"]
    )
    origins = "".join("<p>%s</p>" % inline(p) for p in law["origins"])
    sources = ""
    for n, s in enumerate(law["sources"], 1):
        label = ' <span class="src__label">%s</span>' % esc(s["label"]) if s["label"] else ""
        open_link = '<a class="src__open" href="%s" target="_blank" rel="noopener">Open \u2197<span class="visually-hidden"> (opens in a new tab)</span></a>' % esc(s["url"]) if s["url"] else '<span class="src__open src__open--none">No link</span>'
        sources += (
            '<li id="src-%d"><span class="src__n">[%d]</span><div class="src__body"><cite>%s (%s). <em>%s</em>.</cite>'
            '<span class="src__venue">%s%s</span></div>%s</li>'
            % (n, n, esc(typo(txt(s["authors"]))), s["year"], esc(typo(txt(s["title"]))), esc(typo(txt(s["venue"]))), label, open_link)
        )
    history = "".join('<li><span class="rev__v">%s</span><span class="rev__d">%s</span><span class="rev__t">%s</span></li>' % (esc(h["v"]), fmt_date(h["d"]), esc(h["t"])) for h in law["history"])

    cite_apa, cite_bib = apa(law), bibtex(law)
    cite = """<div class="cite" data-cite>
  <div class="cite__tabs">
    <div class="cite__tablist" role="tablist" aria-label="Citation format">
      <button type="button" role="tab" id="tab-apa" aria-selected="true" aria-controls="panel-apa" data-tab="apa">APA</button>
      <button type="button" role="tab" id="tab-bibtex" aria-selected="false" aria-controls="panel-bibtex" tabindex="-1" data-tab="bibtex">BibTeX</button>
      <button type="button" role="tab" id="tab-link" aria-selected="false" aria-controls="panel-link" tabindex="-1" data-tab="link">Permalink</button>
    </div>
    <button class="btn btn--ink cite__copy" type="button" data-copy>Copy</button>
  </div>
  <div role="tabpanel" id="panel-apa" aria-labelledby="tab-apa" data-panel="apa"><pre><code>%s</code></pre></div>
  <div role="tabpanel" id="panel-bibtex" aria-labelledby="tab-bibtex" data-panel="bibtex" hidden><pre><code>%s</code></pre></div>
  <div role="tabpanel" id="panel-link" aria-labelledby="tab-link" data-panel="link" hidden><pre><code>%s</code></pre></div>
</div>""" % (esc(cite_apa), esc(cite_bib), esc(url))

    plain_box = '<section class="plain" aria-labelledby="plain-terms"><h2 class="plain__label" id="plain-terms">In plain terms</h2><p>%s</p></section>' % esc(typo(law["plainTerms"]))

    if law["slug"] in NAMING["established"]:
        name_tag, name_note = "Established term", "This name is used in the research literature."
    elif law["slug"] in NAMING.get("coinedRecently", []):
        name_tag, name_note = "Recent term", "This name was coined in one recent paper and is not yet widely established."
    else:
        name_tag, name_note = "Named here", "The idea is established in the research. The name is this site\u2019s, chosen to make it easier to remember."
    ev = evidence_base(law)
    # One compact line (reviewed, sources, version) with the detail behind a disclosure, so the first
    # screen on a phone is the pattern itself. Sources and Cite stay as direct links.
    trust = (
        '<div class="trust">'
        '<p class="trust__line">Reviewed %s \u00b7 <a href="#sources">%d %s</a> \u00b7 %s \u00b7 <a href="#cite-this-law">Cite</a></p>'
        '<details class="trust__more"><summary>Details</summary><dl>'
        '<div><dt>Source types</dt><dd>%s</dd></div>'
        '<div><dt>Evidence base</dt><dd>%s. %s <a href="../about.html#evidence">How this is rated</a></dd></div>'
        '<div><dt>Name</dt><dd>%s: %s</dd></div>'
        '<div><dt>Version</dt><dd>%s, published %s</dd></div>'
        '</dl></details></div>'
        % (
            fmt_date(law["evidenceChecked"]), len(law["sources"]), "source" if len(law["sources"]) == 1 else "sources", esc(law["version"]),
            esc(source_mix(law)),
            ev["label"], esc(ev["why"]) + ".",
            name_tag, esc(name_note),
            esc(law["version"]), fmt_date(law["published"]),
        )
    ) + (
        # The single status statement on a pattern page. The full wording lives on About and Methodology.
        '<p class="law__status"><span class="etag etag--%s">Evidence base: %s</span><span class="ntag">%s</span>'
        '<span>Independent, not peer reviewed. <a href="../about.html#status">Status</a></span></p>'
        % (ev["key"], ev["label"], name_tag)
    )

    jump_main = [("questions-to-ask", "Questions to ask"), ("limits", "Where this doesn\u2019t apply"), ("sources", "Sources"), ("cite-this-law", "Cite")]
    jump = (
        '<nav class="jump" aria-label="Jump to a section"><ul>%s</ul>'
        '<details class="jump__all"><summary>All sections</summary><ol>%s</ol></details></nav>'
        % (
            "".join('<li><a href="#%s">%s</a></li>' % (sid, label) for sid, label in jump_main),
            "".join('<li><a href="#%s">%s</a></li>' % (sid, label) for sid, label in SECTION_TOC),
        )
    )

    # Shared text = bottom line + its "Keep in mind" caveat (the caveat travels with the claim); the link is added by js/law.js.
    share_text = "%s\nKeep in mind: %s" % (typo(law["bottomLine"]), typo(law["bottomLineCaveat"]))
    share = (
        '<div class="law__share"><button class="btn btn--outline btn--sm" type="button" data-share data-share-title="%s" data-share-text="%s" data-share-url="%s">Share this</button>'
        '<span class="law__share-status" role="status" aria-live="polite" data-share-status></span></div>'
        % (esc(typo(law["name"])), esc(share_text).replace("\n", "&#10;"), esc(url))
    )

    # right column
    aside = []
    if law["workedExample"]:
        aside.append(
            '<details class="aside-block" open><summary>Worked example</summary><p class="aside__serif">%s</p><p class="aside__note">%s</p></details>'
            % (esc(typo(law["workedExample"]["text"])), esc(typo(law["workedExample"]["note"])))
        )
    if law["terms"]:
        terms = "".join("<dt>%s</dt><dd>%s</dd>" % (esc(typo(t["term"])), inline(t["definition"])) for t in law["terms"][:4])
        aside.append('<details class="aside-block" open><summary>Terms used here</summary><dl class="terms">%s</dl></details>' % terms)
    if law["alsoKnownAs"]:
        aside.append('<details class="aside-block" open><summary>Related terms</summary><ul class="chips">%s</ul></details>' % "".join("<li>%s</li>" % esc(typo(a)) for a in law["alsoKnownAs"]))
    aside.append(
        '<details class="aside-block" open><summary>Take it with you</summary><ul class="takeaway">'
        '<li><a href="../brief.html?patterns=%s" data-collection-link="../brief.html" data-collection-extra="%s">Quick brief <span>Short overview</span></a></li>'
        '<li><a href="../checklist.html?preset=custom&amp;patterns=%s" data-collection-link="../checklist.html?preset=custom" data-collection-extra="%s">Printable checklist <span>Print \u00b7 PDF</span></a></li>'
        '<li><a href="#cite-this-law">Cite this pattern <span>APA \u00b7 BibTeX</span></a></li></ul></details>' % (law["no"], law["no"], law["no"], law["no"])
    )

    prev_box = '<a class="pn pn--prev" href="%s"><span class="pn__k">\u2190 Back to category</span><span class="pn__t">%s. %s</span></a>' % (cat_href, cat["id"], esc(typo(cat["name"])))
    if nxt:
        next_box = '<a class="pn pn--next" href="%s.html"><span class="pn__k">Next pattern \u2192</span><span class="pn__t">%s %s</span></a>' % (nxt["slug"], nxt["no"], esc(typo(nxt["name"])))
        crumb_next = '<a class="btn btn--outline btn--sm" href="%s.html">Next: %s %s \u2192</a>' % (nxt["slug"], nxt["no"], esc(typo(nxt["name"])))
        bar_next = '<a href="%s.html">Next: %s \u2192</a>' % (nxt["slug"], nxt["no"])
    else:
        next_box = '<a class="pn pn--next" href="../index.html"><span class="pn__k">All patterns \u2192</span><span class="pn__t">Back to the index</span></a>'
        crumb_next = '<a class="btn btn--outline btn--sm" href="../index.html">All patterns \u2192</a>'
        bar_next = '<a href="../index.html">All patterns \u2192</a>'

    body = """<div class="crumbs"><nav aria-label="Breadcrumb"><ol>
    <li><a href="../index.html">Patterns</a></li><li><a href="%(cat_href)s">%(cat_id)s. %(cat_name)s</a></li><li aria-current="page">No. %(no)s</li></ol></nav>
    <div class="crumbs__right"><span>%(pos)d of %(cat_total)d in this category</span>%(crumb_next)s</div></div>
<main id="main" class="law-layout cat-%(cat_n)d" data-page="law" data-no="%(no)s" data-slug="%(slug)s">
  <aside class="law-rail" aria-label="On this page">
    <details class="toc" open><summary>On this page <span aria-hidden="true" class="toc__plus"></span></summary><ol>%(toc)s</ol></details>
    <div class="related"><h2 class="rail-label">Related</h2><ul>%(related)s</ul></div>
  </aside>
  <article class="law">
    <div class="law__meta"><span class="law__no">No. %(no)s</span><a class="tag" href="%(cat_href)s">%(cat_short)s</a>%(pick)s<span class="law__for">For: %(roles)s</span></div>
    <h1 class="law__title">%(name)s</h1>
    <blockquote class="law__quote"><p>\u201c%(aphorism)s\u201d</p></blockquote>
    %(bottom)s
    %(case)s
    %(share)s
    %(trust)s
    %(plain)s
    %(jump)s
    <section class="sec" aria-labelledby="takeaways">%(h_take)s<ul class="dash">%(takeaways)s</ul></section>
    <section class="sec" aria-labelledby="what-it-means">%(h_means)s%(means)s</section>
    <section class="sec" aria-labelledby="the-evidence">%(h_evid)s%(evidence)s</section>
    <section class="sec" aria-labelledby="use-it">%(h_use)s<ol class="num">%(use_it)s</ol></section>
    <section class="sec" aria-labelledby="questions-to-ask">%(h_q)s<p class="sec__sub">For vendor reviews, model cards, and launch reviews.</p><ul class="qlist">%(questions)s</ul></section>
    <section class="sec" aria-labelledby="limits">%(h_lim)s%(limits)s</section>
    <section class="sec" aria-labelledby="origins">%(h_orig)s%(origins)s</section>
    <section class="sec" aria-labelledby="sources">%(h_src)s<ol class="sources">%(sources)s</ol></section>
    <section class="sec" aria-labelledby="cite-this-law">%(h_cite)s%(cite)s</section>
    <section class="sec" aria-labelledby="revision-history">%(h_rev)s<ul class="rev">%(history)s</ul><p class="rev__links"><a href="../changelog.html">Full changelog</a> \u00b7 Spot a mistake or a better source? <a href="%(report)s">Report it</a>. Corrections are logged in the changelog.</p></section>
    <nav class="pn-row" aria-label="Previous and next pattern">%(prev_box)s%(next_box)s</nav>
  </article>
  <aside class="law-aside" aria-label="Supporting material"><h2 class="aside-title">Supporting material</h2>%(aside)s</aside>
</main>
<div class="law-bar" aria-label="Pattern navigation"><a href="%(cat_href)s">\u2190 Category</a><a href="#cite-this-law">Cite</a>%(bar_next)s</div>
""" % {
        "cat_href": cat_href,
        "cat_id": cat["id"],
        "cat_name": esc(typo(cat["name"])),
        "cat_short": esc(cat["short"]),
        "cat_n": cat["n"],
        "no": law["no"],
        "pos": pos,
        "cat_total": len(cat_laws),
        "crumb_next": crumb_next,
        "toc": toc,
        "related": related,
        "share": share,
        "bottom": bottom_line_box(law),
        "case": case_line(law),
        "jump": jump,
        "pick": pick_button(law, "pick pick--inline", "Add to My patterns", "In My patterns"),
        "roles": " \u00b7 ".join(law["roles"]),
        "name": esc(typo(law["name"])),
        "aphorism": esc(typo(law["aphorism"])),
        "slug": law["slug"],
        "trust": trust,
        "plain": plain_box,
        "h_take": h2("takeaways", "Takeaways"),
        "takeaways": takeaways,
        "h_means": h2("what-it-means", "What it means"),
        "means": means,
        "h_evid": h2("the-evidence", "The evidence", '<span class="sec-head__note">reviewed %s</span>' % fmt_date(law["evidenceChecked"])),
        "evidence": evidence,
        "h_use": h2("use-it", "Use it"),
        "use_it": use_it,
        "h_q": h2("questions-to-ask", "Questions to ask", '<div class="sec-head__actions">%s<a class="btn btn--ink btn--sm" href="../checklist.html?preset=custom&amp;patterns=%s" data-collection-link="../checklist.html?preset=custom" data-collection-extra="%s">Print checklist</a></div>' % (pick_button(law, "pick pick--btn", "Add to My patterns", "In My patterns"), law["no"], law["no"])),
        "questions": questions,
        "report": esc(report_url(law)),
        "h_lim": h2("limits", "Where this doesn\u2019t apply"),
        "limits": limits,
        "h_orig": h2("origins", "Origins"),
        "origins": origins,
        "h_src": h2("sources", "Sources"),
        "sources": sources,
        "h_cite": h2("cite-this-law", "Cite this pattern"),
        "cite": cite,
        "h_rev": h2("revision-history", "Revision history"),
        "history": history,
        "prev_box": prev_box,
        "next_box": next_box,
        "aside": "".join(aside),
        "bar_next": bar_next,
    }
    # Per-pattern description: the bottom line with the pattern name when that fits one search-result line, else aphorism + plain terms.
    bl_desc = "%s: %s" % (law["name"], law["bottomLine"])
    desc = bl_desc if len(bl_desc) <= 155 else "%s %s" % (law["aphorism"], law["plainTerms"])
    page = layout(law["name"], desc, body, depth=1, current="laws", scripts=("law.js",), head_extra=law_jsonld(law), og_image="img/og/%s.png" % law["slug"])
    write("patterns/%s.html" % law["slug"], page)


# ---------------------------------------------------------------- tools data
def parse_rubric():
    groups, cur = [], None
    for ln in (SRC / "ai-design-evaluation-rubric.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"^## (.+?) \u2014 (.+?) \(\u2014\)$", ln)
        if m:
            cur = {"name": m.group(1), "tagline": m.group(2), "items": []}
            groups.append(cur)
        elif ln.startswith("- [\u2014] ") and cur is not None:
            cur["items"].append(ln[len("- [\u2014] ") :])
    initials = {"Agency": "A", "Transparency": "T", "Honesty": "H", "Equity": "E", "Real reduction": "R", "Failure design": "F"}
    for g in groups:
        g["code"] = initials[g["name"]]
        g["items"] = [{"id": "%s%d" % (g["code"], n), "text": t} for n, t in enumerate(g["items"], 1)]
    return groups


def load_airr():
    return json.loads((SRC / "ai-readiness-review.json").read_text(encoding="utf-8"))


RUBRIC = parse_rubric()
AIRR = load_airr()


def tool_page(title, desc, current, intro_html, sections_html, source_note):
    body = """<main id="main" class="page page--tool">
  <header class="page__head"><p class="eyebrow">Tool</p><h1>%s</h1>%s</header>
  %s
  <p class="page__note">%s</p>
</main>""" % (esc(title), intro_html, sections_html, source_note)
    return layout(title, desc, body, current=current)


def build_rubric():
    secs = []
    for g in RUBRIC:
        items = "".join('<li id="%s"><span class="crit__id">%s</span><span class="crit__text">%s</span></li>' % (i["id"], i["id"], esc(typo(i["text"]))) for i in g["items"])
        secs.append(
            '<section class="tool-sec" aria-labelledby="g-%s"><h2 id="g-%s"><span class="tool-sec__code">%s</span>%s <span class="tool-sec__tag">\u2014 %s</span></h2><ol class="crit">%s</ol></section>'
            % (g["code"], g["code"], g["code"], esc(typo(g["name"])), esc(typo(g["tagline"])), items)
        )
    intro = (
        '<p class="page__lede">A quick scoring checklist for judging a single AI feature or design. Each of the six groups has three checks. '
        'Use it in a design critique or before a launch review, then follow the checks that fail back to the patterns.</p>'
    )
    note = "This page is a reference list of the checks: it does not calculate a score. It is a design-review aid, not a standard or a compliance test. Check numbers (A1, H2, and so on) are labels used on this site. They are unrelated to the Tier labels on the Readiness Review."
    write("design-rubric.html", tool_page("AI Design Evaluation Rubric", "An 18-check rubric for evaluating an AI feature across agency, transparency, honesty, equity, real reduction, and failure design.", "rubric", intro, "".join(secs), note))


REVIEW_SOURCES = {
    "HAX G1\u2013G18": "Microsoft\u2019s Guidelines for Human-AI Interaction (Amershi et al., CHI 2019): eighteen guidelines for how an AI feature should behave with the people using it.",
    "NIST AI 100-1": "NIST\u2019s Artificial Intelligence Risk Management Framework (AI RMF 1.0, NIST AI 100-1, January 2023), a U.S. voluntary framework for identifying and managing AI risk. NIST has said that AI RMF 1.0 is being revised.",
    "NIST AI 600-1": "NIST AI 600-1, Artificial Intelligence Risk Management Framework: Generative Artificial Intelligence Profile (July 2024), which applies the AI RMF to generative AI.",
    "PAIR Guidebook": "Google\u2019s People + AI Guidebook, design guidance for AI-powered products.",
    "AI Act Art. 13": "EU AI Act (Regulation (EU) 2024/1689), Article 13: transparency and provision of information to deployers. It sets a requirement for high-risk AI systems, about the instructions for use given to the organizations that deploy them. Criteria that cite it apply the same idea to what users are shown.",
    "AI Act Art. 14": "EU AI Act (Regulation (EU) 2024/1689), Article 14: human oversight. It sets a requirement for high-risk AI systems: suitable tools so that people can oversee the system, and the ability to disregard, override, reverse, or stop it. It does not require confirmation of every action.",
    "AI Act Art. 50": "EU AI Act (Regulation (EU) 2024/1689), Article 50: transparency obligations for providers and deployers of certain AI systems, including telling people when they are interacting directly with an AI system unless that is obvious. It is not limited to high-risk systems.",
    "ISO/IEC 42001": "ISO/IEC 42001:2023, Information technology \u2014 Artificial intelligence \u2014 Management system (edition 1, December 2023): requirements for establishing, implementing, maintaining, and improving an AI management system in an organization. It works at organization level; criteria that cite it draw on its management practices.",
    "WCAG 2.2": "W3C\u2019s Web Content Accessibility Guidelines (WCAG) 2.2, a W3C Recommendation (12 December 2024).",
    "W3C AI accessibility draft": "\u201cAccessibility of machine learning and generative AI\u201d, an Editor\u2019s Draft (28 March 2026 when checked) from the W3C Accessible Platform Architectures Working Group. It is a work in progress, not a standard, and is not endorsed by W3C or its members. Background reading, not a requirement.",
    "Parasuraman 1997": "Parasuraman and Riley (1997), \u201cHumans and automation: use, misuse, disuse, abuse\u201d, Human Factors: research on how people use, over-rely on, and neglect automation.",
    "Mosier 1996": "Mosier and Skitka (1996), \u201cHuman decision makers and automated decision aids: made for each other?\u201d, in Automation and Human Performance: research on automation bias in human decision-making.",
}


def src_id(ref):
    return "src-" + re.sub(r"[^a-z0-9]+", "-", ref.lower()).strip("-")


def build_review():
    dims = {d["code"]: d for d in AIRR["dimensions"]}
    screening = "".join('<li id="%s"><span class="crit__id">%s</span><span class="crit__text">%s</span></li>' % (s["id"], s["id"].upper(), esc(typo(s["question"]))) for s in AIRR["screening"])
    secs = ['<section class="tool-sec" aria-labelledby="screening"><h2 id="screening"><span class="tool-sec__code">1</span>Screening <span class="tool-sec__tag">\u2014 five questions asked before scoring</span></h2><ol class="crit">%s</ol></section>' % screening]
    for code in sorted(dims):
        crits = [c for c in AIRR["criteria"] if c["dimension"] == code]
        rows = ""
        for c in crits:
            gate = '<span class="gate">Gate \u00b7 Tier %d</span>' % c["gateTier"] if c["gateTier"] else ""
            refs = "".join('<li><a href="#%s">%s</a></li>' % (src_id(r), esc(r)) for r in c["references"])
            based = '<span class="crit__label" id="%s-src">Based on</span><ul class="refs" aria-labelledby="%s-src">%s</ul>' % (c["id"], c["id"], refs) if c["references"] else ""
            note_c = '<span class="crit__label">Note</span><span>%s</span>' % esc(typo(c["note"])) if c.get("note") else ""
            rows += '<li id="%s"><span class="crit__id">%s</span><span class="crit__text">%s<span class="crit__meta">%s%s%s</span></span></li>' % (c["id"], c["id"], esc(typo(c["criterion"])), gate, based, note_c)
        secs.append(
            '<section class="tool-sec" aria-labelledby="%s"><h2 id="%s"><span class="tool-sec__code">%s</span>%s</h2><ol class="crit">%s</ol></section>'
            % (code, code, code, esc(typo(dims[code]["title"])), rows)
        )
    intro = (
        '<p class="page__lede">A more rigorous instrument for launch review. Five screening questions come first, then 27 criteria across seven dimensions. '
        'Under each criterion, the labels marked "Based on" name the standards and guidelines it draws on; the key at the bottom of the page explains each one. Some criteria are marked as gates.</p>'
        '<p class="case__note"><strong>Scope.</strong> As of 19 October 2026. This is a design and launch-review checklist, not legal advice, a conformity assessment, or a compliance determination. '
        'The standards named under \u201cBased on\u201d are sources the criteria draw on; this page does not claim that meeting a criterion satisfies any of them. '
        'EU AI Act Articles 13 and 14 set requirements for high-risk AI systems only; Article 50 covers certain other systems, including ones that interact directly with people. '
        'As amended by Regulation (EU) 2026/1744 (in force 27 July 2026), the Commission\u2019s AI Act Service Desk lists the high-risk rules as applying from 2 December 2027 (Annex III systems) and 2 August 2028 (AI embedded in products covered by Annex I), and Article 50 from 2 August 2026. Check current application dates before relying on them.</p>'
    )
    note = (
        "This page lists the instrument (AIRR v%s). This page does not score a system or assign a tier; use it as a checklist. "
        "Tiers: Tier 1 to Tier 3 are this instrument\u2019s own risk tiers, running from lower to higher risk. They are not EU AI Act risk categories and are unrelated to the check labels on the Design Rubric. "
        "A Gate badge marks a criterion treated as a gate: it should be met before launch for a feature at that tier or higher. \u201cGate \u00b7 Tier 2\u201d applies at Tier 2 and Tier 3; \u201cGate \u00b7 Tier 3\u201d applies at Tier 3 only. "
        "Criteria with no badge are not gates. The page does not say how to place a feature in a tier; the five screening questions are the starting point for that judgment."
    ) % esc(AIRR["instrument"]["version"])
    used = []
    for c in AIRR["criteria"]:
        for r in c["references"]:
            if r not in used:
                used.append(r)
    key = "".join('<li id="%s"><strong>%s</strong> <span>%s</span></li>' % (src_id(r), esc(r), esc(REVIEW_SOURCES.get(r, ""))) for r in used)
    secs.append('<section class="tool-sec" aria-labelledby="sources"><h2 id="sources"><span class="tool-sec__code">Key</span>Sources <span class="tool-sec__tag">\u2014 what each \u201cBased on\u201d label refers to</span></h2><ul class="src-key">%s</ul></section>' % key)
    write("readiness-review.html", tool_page("AI Readiness Review", "A 27-criterion readiness review for AI features, with screening questions and references to the EU AI Act, NIST, ISO/IEC 42001, WCAG 2.2, and HAX/PAIR guidelines.", "review", intro, "".join(secs), note))


# ---------------------------------------------------------------- simple pages
def build_changelog():
    items = ""
    for e in sorted(CHANGELOG, key=lambda x: x["date"], reverse=True):
        links = " ".join('<a href="%s">%s</a>' % (esc(l["href"]), esc(l["label"])) for l in e.get("links", []))
        items += '<li><time datetime="%s">%s</time><p>%s %s</p></li>' % (e["date"], fmt_date(e["date"]), esc(typo(e["text"])), links)
    body = """<main id="main" class="page">
  <header class="page__head"><p class="eyebrow">Record</p><h1>Changelog</h1>
  <p class="page__lede">What changed on this site and when. Corrections and revisions to a pattern also appear in that pattern's revision history.</p></header>
  <ol class="changelog">%s</ol>
  <p class="page__note"><a href="feed.xml">RSS feed</a></p>
</main>""" % items
    write("changelog.html", layout("Changelog", "Every change to the AI Evaluation Field Guide: new patterns, tools, corrections, and source checks, with dates.", body, current="changelog"))


def NAME_TAG(slug):
    if slug in NAMING["established"]:
        return "Established term"
    if slug in NAMING.get("coinedRecently", []):
        return "Recent term"
    return "Named here"


def build_about():
    crit = NAMING["evidenceCriteria"]
    wk, dv = crit["wellEstablished"], crit["developing"]
    rows, counts = "", collections.Counter()
    for l in LAWS:
        ev = evidence_base(l)
        counts[ev["key"]] += 1
        rows += '<tr><td>%s</td><td><a href="patterns/%s.html">%s</a></td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            l["no"], l["slug"], esc(typo(l["name"])), ev["label"],
            NAME_TAG(l["slug"]), esc(ev["why"]),
        )
    evidence = '''  <section><h2 id="evidence">How strong is the evidence?</h2>
  <p>Each pattern page carries an <strong>Evidence base</strong> label. It describes the sources cited on that page. It does not rate the whole research literature on the topic, and it does not say a pattern is more or less important. It is computed from the source list by fixed rules, so anyone can check it.</p>
  <ul>
    <li><strong>Well established (%(c_well)d):</strong> at least %(w_n)d sources, at least %(w_p)d of them peer-reviewed or classic works making up at least %(w_share)d%% of the list, and those works have at least %(w_a)d different lead authors. Several independent studies point the same way.</li>
    <li><strong>Developing (%(c_dev)d):</strong> at least %(d_n)d sources, at least %(d_p)d of them peer-reviewed or classic, but short of the bar above. The list is smaller, or leans on preprints and reports.</li>
    <li><strong>Emerging (%(c_em)d):</strong> everything else. Typically one peer-reviewed source or fewer, with the rest preprints or reports. The idea may still be sound; the cited support is thin so far.</li>
  </ul>
  <p>\u201cPeer-reviewed or classic\u201d means any source not labeled a preprint, report, working paper, or book on the pattern page. \u201cLead author\u201d is the first author listed, used as a rough stand-in for a separate research group. The rules count sources. They cannot tell whether a study is good, and a pattern can rest on a few strong papers or a large pile of weak ones. Read the Evidence section and the sources themselves. The same limits apply to the labels: they are an editorial summary, not a measurement. The rules were written for this guide and are not a published standard.</p>
  <p>This is separate from the name. <strong>Established term</strong> means the name is used in the research literature. <strong>Recent term</strong> means the name was coined in one recent paper and is not yet widely established. <strong>Named here</strong> means the idea is established but the name is this guide\u2019s own. A pattern can be well established under a name used only here, and a pattern with a standard name can still have a thin evidence base. The table lists both for every pattern.</p>
  <div class="table-wrap"><table><thead><tr><th scope="col">No.</th><th scope="col">Pattern</th><th scope="col">Evidence base</th><th scope="col">Name</th><th scope="col">Basis</th></tr></thead><tbody>%(rows)s</tbody></table></div></section>
''' % {
        "c_well": counts["well"], "c_dev": counts["developing"], "c_em": counts["emerging"],
        "w_n": wk["minSources"], "w_p": wk["minPeerReviewed"], "w_share": round(wk["minPeerShare"] * 100), "w_a": wk["minLeadAuthors"],
        "d_n": dv["minSources"], "d_p": dv["minPeerReviewed"], "rows": rows,
    }
    status = '''  <section><h2 id="status">Status of this guide</h2>
  <p>This is an independent, self-published reference built from published research. It has not been through formal peer review. Every pattern links to its sources, so you can check the evidence for yourself.</p>
  <h3>Established terms, recent terms, and names from this guide</h3>
  <p>Not every pattern name is standard. The idea behind each pattern is established in the research, but for some the name is this guide’s own. Each pattern page, and the table below, uses one of three name labels.</p>
  <ul>
    <li><strong>Established term (%(n_est)d):</strong> the name is used in the research literature.</li>
    <li><strong>Recent term (%(n_recent)d):</strong> the name was coined in one recent paper and is not yet widely established, so cite that paper.</li>
    <li><strong>Named here (%(n_here)d):</strong> the idea is established but the name is this guide’s own. Please do not cite these names as established terms. Cite the sources linked on each page instead.</li>
  </ul>
  <p>Which is which, along with how strong each pattern’s evidence is, is in the <a href="#evidence">table below</a>.</p>
  <h3>Review</h3>
  <p>See the <a href="methodology.html">methodology</a> for how sources were chosen and checked. No outside reviewer has signed off on any pattern yet. The kind of reviewer who would help most is an evaluation researcher or statistician, someone who can check whether a pattern is stated as strongly as its sources allow and whether the statistics are right. If that is you, and you would read one or two patterns, or you see something wrong or a better source, please say so on the <a href="https://josephalfonso.com/pages/contact.html">contact page</a>. Corrections are recorded in the <a href="changelog.html">Changelog</a>.</p></section>
''' % {"n_est": len(NAMING["established"]), "n_here": len(NAMING["namedHere"]), "n_recent": len(NAMING.get("coinedRecently", []))}
    named_here = [l for l in LAWS if NAME_TAG(l["slug"]) == "Named here"]
    n_est = sum(1 for l in LAWS if NAME_TAG(l["slug"]) == "Established term")
    n_rec = sum(1 for l in LAWS if NAME_TAG(l["slug"]) == "Recent term")
    named_list = ", ".join('<a href="patterns/%s.html">%s</a>' % (l["slug"], esc(typo(l["name"]))) for l in named_here)
    recent_list = ", ".join('<a href="patterns/%s.html">%s</a>' % (l["slug"], esc(typo(l["name"]))) for l in LAWS if NAME_TAG(l["slug"]) == "Recent term")
    ck = EDIT["checklist"]
    roles = []
    for l in LAWS:
        for r in l["roles"]:
            if r not in roles:
                roles.append(r)
    own = {
        "n": len(LAWS), "n_parts": len(CATS), "n_est": n_est, "n_rec": n_rec, "n_here": len(named_here),
        "named": named_list, "recent": recent_list,
        "roles": join_and(roles),
        "phases": len(ck["phases"]), "stakes": len(ck["stakes"]),
        "n_tpl": len(TEMPLATES), "n_rubric": sum(len(g["items"]) for g in RUBRIC), "n_airr": len(AIRR["criteria"]),
        "n_tiers": 3, "n_stages": 5,
    }
    own_section = """  <section><h2 id="own-vs-research">What comes from the research, and what is this guide’s own</h2>
  <p>A pattern page mixes two kinds of content. This section draws the line, so you can tell what to check against a paper and what to treat as editorial judgment.</p>
  <h3>From the research</h3>
  <ul>
    <li>The findings and numbers on each of the %(n)d pattern pages. Each can be traced to a source listed on that page.</li>
    <li>The idea behind every pattern, including the %(n_here)d whose names are this guide’s own.</li>
    <li>The names labeled Established term (%(n_est)d), which the research literature uses, and Recent term (%(n_rec)d: %(recent)s), which was coined in one recent paper.</li>
    <li>Findings in the Overview, Being Pragmatic, Playbook, and Glossary that are attributed to a named source.</li>
  </ul>
  <h3>This guide’s own</h3>
  <ul>
    <li><strong>Which patterns are included.</strong> An editorial selection, not a systematic review. Another reasonable list would differ.</li>
    <li><strong>The grouping into %(n_parts)d parts</strong> and the order of the patterns.</li>
    <li><strong>The %(n_here)d names marked Named here:</strong> %(named)s.</li>
    <li><strong>The Evidence base labels and their rules.</strong> They are computed from each page’s source list by fixed rules, written for this guide; they are not a published standard or a measurement (see <a href="#evidence">How strong is the evidence?</a>).</li>
    <li><strong>Role tags</strong> (%(roles)s), the <strong>In plain terms</strong> summaries, and the <strong>questions to ask</strong> on each pattern page.</li>
    <li><strong>The matching rules</strong> in the claim checker and the situation finder. Both are published on their own pages.</li>
    <li><strong>The checklist’s phases and stakes levels:</strong> %(phases)d phases and %(stakes)d levels of stakes, and where each pattern’s question sits.</li>
    <li><strong>The models in the guide chapters,</strong> each marked in the text: the %(n_stages)d-stage maturity path, the %(n_tiers)d risk tiers and the minimum evidence for each, and the sequences in the Playbook.</li>
    <li><strong>Rules of thumb,</strong> marked as such where they appear, for example “three to five” prompt variants or runs and “a few dozen” outputs to read. They are starting points from this guide, not findings of the studies cited nearby.</li>
    <li><strong>The tools’ content:</strong> the %(n_tpl)d templates, the Design Rubric’s %(n_rubric)d checks, and the Readiness Review’s %(n_airr)d criteria, tiers, and gates, along with which standards each criterion is based on. The standards themselves are not this guide’s.</li>
  </ul>
  <p>When a sentence in the guide chapters is this guide’s own, it says so in the text. See “How to read the labels” at the top of the <a href="playbook.html">Playbook</a>.</p></section>
""" % own
    body = """<main id="main" class="page page--prose">
  <header class="page__head"><p class="eyebrow">About</p><h1>About this guide</h1>
  <p class="page__lede">An independent reference for people who build, buy, or design with AI. It collects the reliable ways AI evaluation goes wrong, with the research behind each one.</p></header>
  <section class="callout" aria-labelledby="trust"><h2 id="trust">What you can rely on</h2>
  <p>Every claim on a pattern page is traceable to a source listed on that page, and preprints, reports, working papers, and books are labeled as such. On 19 October 2026 I re-audited every claim on the pattern, guide, glossary, and bibliography pages against its primary source, with AI-assisted checking; the <a href="methodology.html#checking">methodology</a> says what that covered and what it could not. This guide is independent, with no vendor funding. It is self-published, has not been through formal peer review, and no outside reviewer has signed off on any pattern. If you find an error, tell me through the <a href="https://josephalfonso.com/pages/contact.html">contact page</a> or a pattern page\u2019s \u201cReport it\u201d link; every correction is recorded in the <a href="changelog.html">Changelog</a>.</p></section>
%(own)s  <section><h2 id="what-a-pattern-is">What a \u201cpattern\u201d means here</h2>
  <p>A pattern here is a reliable way evaluation goes wrong, with research behind it. It is not a law of physics. Some are established terms, like Goodhart\u2019s Law. Others are named here: the idea is well documented, and the name is this guide\u2019s own, chosen to make it easier to remember. Each page says which.</p></section>
  <section><h2 id="editorial-policy">Editorial policy</h2>
  <ul>
    <li>Every pattern links to its sources. Preprints, reports, regulations, working papers, and books are labeled as such. Every other source appeared in a peer-reviewed venue or is a long-established classic, apart from a few commentary pieces and older documents that the <a href=\"bibliography.html\">Bibliography</a> tags. The <a href=\"methodology.html\">methodology</a> explains how sources are counted and how the evidence was checked.</li>
    <li>Each pattern shows when its evidence was last checked and carries a version number and revision history.</li>
    <li>The <a href="changelog.html">Changelog</a> records what changed and when. Corrections are made in the open.</li>
    <li>Role tags, plain-terms summaries, checklist questions, and claim-checker rules are editorial work built from the patterns themselves. They are starting points, not authority (see <a href="#own-vs-research">what is this guide\u2019s own</a>).</li>
  </ul></section>
%(status)s%(evidence)s  <section><h2 id="who">Who maintains it</h2>
  <p>Hi, I\u2019m <a href="https://josephalfonso.com">Joseph Alfonso</a>, a UX design lead. I made this guide because I wanted to understand how AI really gets judged, and how those judgments go wrong. Writing it down was how I learned. I chose the patterns, built the guide and its tools, and maintain it.</p>
  <p>The evidence has been checked twice: a spot-check of specific figures in early October 2026, then a full re-audit of every claim against its primary source on 19 October 2026. The re-audit was my own, done with AI-assisted checking, not by an outside expert. The <a href="methodology.html#checking">methodology</a> says exactly what the checks covered and where a source could not be read in full. Where the evidence is mixed or limited, the page says so.</p>
  <p>I care about this because AI can feel like something that happens to us. I don\u2019t think it has to. The more we understand how it works and why it fails, the more we can use it on our own terms and ask better questions of the people selling it, building it, or telling us to trust it. I\u2019m still learning, and I\u2019ve tried to be honest about what I know and don\u2019t.</p>
  <p>No outside reviewer has signed off on any pattern yet. If you work in evaluation research or statistics and would review a pattern, or you find a mistake or a better source, please tell me through the <a href="https://josephalfonso.com/pages/contact.html">contact page</a>. I\u2019d be grateful, and I\u2019ll fix it. I hope this helps you the way making it helped me.</p></section>
  <section><h2 id="how-to-use">How to use it</h2>
  <p>Start with the <a href="guide.html">guide</a>, browse the <a href="index.html">patterns</a>, describe your circumstances to <a href="situation-finder.html">find your patterns</a>, or paste a claim into the <a href="claim-checker.html">claim checker</a> to see which patterns apply. Collect any patterns with the Add buttons to get a <a href="brief.html">quick brief</a>, or turn them into a printable sheet with the <a href="checklist.html">checklist builder</a>. For ready-made question lists, see <a href="questions-to-ask-ai-vendor.html">buying an AI model or vendor</a>, <a href="ai-launch-review-questions.html">a launch review</a>, and <a href="how-to-build-an-ai-evaluation.html">building an evaluation</a>.</p></section>
</main>""" % {"status": status, "evidence": evidence, "own": own_section}
    write("about.html", layout("About", "About the AI Evaluation Field Guide: what comes from the research and what is the guide\u2019s own, what a pattern means here, the editorial policy, and who maintains it.", body, current="about"))


def guide_nav(active):
    """Where this page sits in the guide: the reading order, the playbooks by situation, then reference."""
    def group(label, items):
        links = "".join('<li><a href="%s"%s>%s</a></li>' % (href, ' aria-current="page"' if href == active else "", text) for href, text in items)
        return '<div class="guide-nav__group"><p class="guide-nav__label">%s</p><ul>%s</ul></div>' % (label, links)

    chapters = [(f, "%d. %s" % (n, t)) for n, (f, t, _) in enumerate(GUIDE_CHAPTERS, 1)]
    playbooks = [(pg["file"], pg["short"]) for pg in INTENT_PAGES]
    reference = [(f, t) for f, t, _ in GUIDE_REFERENCE]
    home = '<a class="guide-nav__home" href="guide.html"%s>Guide</a>' % (' aria-current="page"' if active == "guide.html" else "")
    return '<nav class="guide-nav" aria-label="Guide sections">%s%s%s%s</nav>' % (home, group("Read in order", chapters), group("Playbooks by situation", playbooks), group("Reference", reference))


def chapter_eyebrow(fname):
    """"Guide · Chapter N", with N taken from the reading order so adding a chapter cannot leave a stale number."""
    return "Guide \u00b7 Chapter %d" % ([f for f, _, _ in GUIDE_CHAPTERS].index(fname) + 1)


def guide_pager(fname):
    """Previous and next links for the chapters, so the reading order can be followed page to page."""
    files = [f for f, _, _ in GUIDE_CHAPTERS]
    if fname not in files:
        return ""
    i = files.index(fname)
    if i:
        prev_ = '<a class="pn pn--prev" href="%s"><span class="pn__k">\u2190 Previous chapter</span><span class="pn__t">%s</span></a>' % (files[i - 1], GUIDE_CHAPTERS[i - 1][1])
    else:
        prev_ = '<a class="pn pn--prev" href="guide.html"><span class="pn__k">\u2190 Guide</span><span class="pn__t">Reading order</span></a>'
    if i + 1 < len(files):
        next_ = '<a class="pn pn--next" href="%s"><span class="pn__k">Next chapter \u2192</span><span class="pn__t">%s</span></a>' % (files[i + 1], GUIDE_CHAPTERS[i + 1][1])
    else:
        next_ = '<a class="pn pn--next" href="guide.html#playbooks"><span class="pn__k">Next \u2192</span><span class="pn__t">Playbooks by situation</span></a>'
    return '<nav class="pn-row" aria-label="Previous and next chapter">%s%s</nav>' % (prev_, next_)


def guide_page(fname, title, eyebrow, desc, lede, blocks_html, extra=""):
    body = """<main id="main" class="page page--prose">
  %s
  <header class="page__head"><p class="eyebrow">%s</p><h1>%s</h1>%s</header>
  %s%s%s
</main>""" % (guide_nav(fname), esc(eyebrow), esc(title), lede, blocks_html, extra, guide_pager(fname))
    write(fname, layout(title, desc, body, current=None))


def build_guide_hub():
    """guide.html: the one place that says what to read first and what to read next."""
    def item(tag, href, title, desc, num=False):
        return '<li class="chapter"><span class="chapter__n%s" aria-hidden="true">%s</span><div><a class="chapter__title" href="%s">%s</a><p>%s</p></div></li>' % ("" if num else " chapter__n--tag", tag, href, esc(title), esc(typo(desc)))

    chapters = "".join(item(str(n), f, t, d, True) for n, (f, t, d) in enumerate(GUIDE_CHAPTERS, 1))
    playbooks = "".join(item(pg["role"], pg["file"], pg["cta"], pg["for"]) for pg in INTENT_PAGES)
    reference = "".join(item("ref", f, t, d) for f, t, d in GUIDE_REFERENCE)
    body = """<main id="main" class="page page--prose page--hub">
  <header class="page__head"><p class="eyebrow">Guide</p><h1>Guide to AI evaluation</h1>
  <p class="page__lede">The patterns are the core of this site. The guide is the order to read everything else in: four short chapters, starting with a worked example, then question lists for the moment you are in, then reference pages.</p></header>
  <p class="hub__quick">Short on time? Pick a role under <a href="index.html#start-here">Start here</a> on the home page, or go straight to <a href="use-it-now.html">Use it now</a> for questions you can ask today.</p>
  <section aria-labelledby="how"><h2 id="how">How this guide works</h2>
  <p>%(arc)s</p></section>
  <section aria-labelledby="order"><h2 id="order">Read in this order</h2>
  <ol class="chapters">%(chapters)s</ol></section>
  <section aria-labelledby="playbooks"><h2 id="playbooks">Playbooks by situation</h2>
  <p>Each one takes the patterns that matter most for a single situation and turns them into questions, with the evidence one click away. They apply the general <a href="playbook.html">Playbook</a> chapter and do not repeat it.</p>
  <ul class="chapters">%(playbooks)s</ul></section>
  <section aria-labelledby="reference"><h2 id="reference">Reference</h2>
  <ul class="chapters">%(reference)s</ul></section>
  <section aria-labelledby="apply"><h2 id="apply">Apply it to your own case</h2>
  <p>The <a href="situation-finder.html">situation finder</a> and <a href="claim-checker.html">claim checker</a> match your text to the patterns that apply. Collect patterns with the Add buttons for a <a href="brief.html">quick brief</a> or a printable <a href="checklist.html">checklist</a>. All the tools are under Tools in the menu.</p></section>
  %(follow)s
</main>""" % {"chapters": chapters, "playbooks": playbooks, "reference": reference, "follow": follow_box(),
        "arc": 'This guide is built around three moves. <strong>Choose a claim</strong>: write down exactly what is being claimed and what decision depends on it. <strong>Test it</strong>: find the patterns that apply and ask their questions, in order, of the evidence behind the claim. <strong>Decide</strong> what you can conclude and what you still cannot, and say both. The <a href="walkthrough.html">walkthrough</a> does all three slowly, on three real published cases.'}
    write("guide.html", layout("Guide", "Where to start with AI evaluation and what to read next: four chapters in order, question lists by situation, and reference pages.", body, current=None))


def glossary_jsonld():
    terms = [{"@type": "DefinedTerm", "name": g["term"], "description": plain(g["definition"]), "url": "%s/glossary#%s" % (SITE["baseUrl"], slugify(g["term"]))} for g in GLOSS]
    data = {"@context": "https://schema.org", "@type": "DefinedTermSet", "name": "AI evaluation glossary", "url": SITE["baseUrl"] + "/glossary", "hasDefinedTerm": terms}
    return '<script type="application/ld+json">%s</script>' % json.dumps(data, ensure_ascii=False).replace("</", "<\\/")


def build_guide_pages():
    overview = manuscript_region("## AI Evaluation, an Overview", "## The Patterns")
    build_guide_hub()
    guide_page(
        "overview.html",
        "AI Evaluation, an Overview",
        chapter_eyebrow("overview.html"),
        "What AI evaluation is, why it is hard, the three layers it works at, and how to use the 26 patterns to read an AI claim.",
        "",
        md_blocks(overview),
    )
    pragmatic = manuscript_region("## Being Pragmatic", "## Playbook")
    guide_page("being-pragmatic.html", "Being Pragmatic", chapter_eyebrow("being-pragmatic.html"), "How to do AI evaluation inside a real team with deadlines, limited budget, and a model that changed last Tuesday.", "", md_blocks(pragmatic))

    field = manuscript_region("## Playbook", "## Glossary")
    # split the eval card template out of the regular flow
    start = next(i for i, l in enumerate(field) if l.startswith("### 4"))
    end = next(i for i, l in enumerate(field) if i > start and l.startswith("### References"))
    card_lines = [l for l in field[start + 1 : end]]
    card_rows = []
    seen_marker = False
    for l in card_lines:
        t = l.strip().replace("&nbsp;", "").strip()
        if t == "EVAL CARD":
            seen_marker = True
            continue
        if not seen_marker:
            continue
        if l.strip() == "&nbsp;":
            card_rows.append('<hr class="evalcard__sep">')
        elif t:
            card_rows.append('<p class="evalcard__row">%s</p>' % inline(t))
    card = '<div class="evalcard" role="group" aria-label="Eval card template"><p class="evalcard__title">Eval card</p>%s</div>' % "".join(card_rows)
    before = md_blocks(field[:start])
    after = md_blocks(field[end:])
    playbooks = ", ".join('<a href="%s">%s</a>' % (pg["file"], esc(pg["short"].lower())) for pg in INTENT_PAGES)
    pb_lede = '<p class="page__lede">The general sequence. For the same questions applied to one situation, use the playbooks for %s.</p>' % playbooks
    guide_page("playbook.html", "Playbook", chapter_eyebrow("playbook.html"), "Questions for reading an AI claim, a sequence for building your own eval, red flags, and an eval card template.", pb_lede, before + '<h2 id="4-eval-card-template">4. Eval card template</h2><p>Copy this into any eval you run. It borrows from model cards (Mitchell et al., 2019). The fields are this guide\u2019s own model, not a standard.</p>' + card + after)

    gl = "".join('<div class="gloss__row"><dt id="%s">%s</dt><dd>%s%s</dd></div>' % (
        slugify(g["term"]), esc(typo(g["term"])), inline(g["definition"]),
        (" See " + ", ".join(link_laws(inline(n)) for n in g["see"]) + ".") if g["see"] else "") for g in GLOSS)
    guide_page("glossary.html", "Glossary", "Guide \u00b7 Reference", "Plain-language definitions of the terms used across the patterns, such as contamination, construct validity, and judge bias.", "", '<dl class="gloss">%s</dl>' % gl + glossary_jsonld())

    model = bibliography.build_model(LAWS)
    for where, src, prim in model["mismatches"]:
        print("warning: one work is listed with different details in %s and elsewhere: %s (%s)" % (where, src["title"][:60], src["year"]))
    names = {l["slug"]: l["name"] for l in LAWS}

    def bib_ref(src, tag=None):
        venue = txt(src["venue"]).rstrip(".")
        title = esc(typo(txt(src["title"])))
        if src["url"]:
            title = '<a href="%s" rel="noopener">%s</a>' % (esc(src["url"]), title)
        out = "%s (%s). %s%s" % (esc(typo(txt(src["authors"]))), src["year"], title, "" if txt(src["title"]).rstrip().endswith(("?", "!")) else ".")
        if venue:
            out += " %s." % esc(typo(venue))
        if tag:
            out += " <em>(%s)</em>" % esc(tag)
        return out

    items = ""
    for e in model["entries"]:
        p = e["primary"]
        cited = ['<a href="patterns/%s.html">%s</a>' % (slug, esc(typo(names[slug]))) for slug in e["patterns"]]
        cited += ['<a href="%s">%s</a>' % (PAGE_LINKS[n], n) for n in e["pages"]]
        ref = bib_ref(p, p["label"] or (e["kind"]["tag"] if e["kind"] else None))
        for alt in e["alsoAs"]:
            ref += "<br><em>Also circulated as:</em> " + bib_ref(alt, alt["label"])
        items += '<li class="bib__item"><span>%s</span><span class="bib__cited">Cited in: %s</span></li>' % (ref, ", ".join(cited))
    guide_page("bibliography.html", "Bibliography", "Guide \u00b7 Reference", "Every source cited across the 26 patterns, with its type (peer-reviewed, preprint, report, book) and where it is used on this site.", '<p class="page__lede">%s</p>' % esc(typo(bibliography.intro_text(model))), '<ul class="bib">%s</ul>' % items)


# ---------------------------------------------------------------- situation finder
def build_situation_finder():
    sf = EDIT["situationFinder"]
    sigs = sf["situations"]
    chips = "".join('<button type="button" class="chip-toggle" data-type="%s" aria-pressed="false">%s</button>' % (t["id"], esc(t["label"])) for t in sigs)
    rules = ""
    for t in sigs:
        rows = "".join("<li><a href=\"%s\">%s</a> <span class=\"rules__fit\">%s</span> %s</li>" % (law_url(r["slug"]), esc(typo(BY_SLUG[r["slug"]]["name"])), {"strong": "strong match", "likely": "likely", "worth": "worth checking"}[r["fit"]], esc(typo(r["why"]))) for r in t["laws"])
        rules += "<h3>%s</h3><ul>%s</ul>" % (esc(t["label"]), rows)
    body = """<main id="main" class="page page--claim" data-page="situation">
  <div class="claim">
    <section class="claim__input" aria-labelledby="sit-h">
      <p class="eyebrow eyebrow--muted">Tool</p>
      <h1 id="sit-h">Find your patterns</h1>
      <p class="page__lede">Describe where you are with an AI system: what you are building or buying, how you test it, who it affects. You get the patterns worth checking first, why each applies, and a question to ask.</p>
      <label class="field-label" for="sit-text">Your situation</label>
      <textarea id="sit-text" class="claim__text" rows="6" placeholder="%s"></textarea>
      <p class="field-label field-label--row" id="sit-type-label">What we picked up <span class="muted-inline" data-detect-note>Detected from your description, edit if wrong</span></p>
      <div class="chip-toggles" role="group" aria-labelledby="sit-type-label">%s</div>
      <div class="claim__buttons"><button class="btn btn--accent" type="button" data-find>Find my patterns</button><button class="btn btn--outline" type="button" data-export disabled>Export questions</button><button class="btn btn--ghost" type="button" data-example>Try an example</button></div>
      <p class="claim__note">Runs in your browser; nothing you type is sent anywhere. Matching is rule-based. <a href="#how-matching-works">How matching works</a></p>
    </section>
    <section class="claim__results" aria-live="polite" aria-labelledby="sit-results-h" data-results>
      <h2 id="sit-results-h" class="visually-hidden">Results</h2>
      <p class="claim__empty">Results appear here. Describe your situation, or choose what applies, then choose Find my patterns.</p>
    </section>
  </div>
  <section class="claim__rules" id="how-matching-works"><h2>How matching works</h2>
    <p>Your description is scanned for situations a careful reader would recognize, such as buying a model, using an AI grader, or launching to real users. You can add or remove any of them. Each situation maps to the patterns that matter most for it, using the manuscript\u2019s Playbook and Being Pragmatic. Patterns are ranked by how many of your situations point to them and how strongly: the top five are where to start, the next six are likely to matter, and the rest are worth a look. This is a reading aid, not an assessment of your system.</p>
    <details><summary>Show the rules</summary>%s</details>
  </section>
</main>""" % (esc(sf["example"]), chips, rules)
    write("situation-finder.html", layout("Find your patterns", "Describe your situation with an AI system and see which patterns to check first, why each applies, and what to ask.", body, current="situation", data=True, scripts=("situation.js",)))


# ---------------------------------------------------------------- claim checker, checklist
def build_room():
    cards = ""
    for m in ROOM["moments"]:
        qs = "".join('<li><button type="button" class="room__q" data-copy="%s" aria-label="Copy question: %s"><span>%s</span><span class="room__copy" aria-hidden="true">Copy</span></button></li>' % (esc(typo(q)), esc(typo(q)), esc(typo(q))) for q in m["questions"])
        laws = ", ".join('<a href="%s">%s</a>' % (law_url(sl), esc(typo(BY_SLUG[sl]["name"]))) for sl in m["laws"])
        weak = ""
        if m.get("weak"):
            weak = '\n  <p class="room__weak"><strong>A weak answer:</strong> %s</p>\n  <p class="room__why"><strong>Why it\u2019s weak:</strong> %s</p>' % (esc(typo(m["weak"])), esc(typo(m["whyWeak"])))
        cards += """<section class="room__card" id="%s" aria-labelledby="%s-h">
  <p class="room__label">When you hear</p>
  <h2 id="%s-h" class="room__heard">%s</h2>
  <ul class="room__qs">%s</ul>
  <p class="room__good"><strong>A good answer:</strong> %s</p>%s
  <p class="room__laws">Why: %s</p>
</section>""" % (m["id"], m["id"], m["id"], esc(typo(m["heard"])), qs, esc(typo(m["good"])), weak, laws)
    body = """<main id="main" class="page page--room" data-page="room">
  <header class="page__head"><p class="eyebrow eyebrow--muted">Tool</p><h1>Use it now</h1>
  <p class="page__lede">%s</p></header>
  <div class="room__grid">%s</div>
  <p class="room__editorial">%s</p>
  <p class="room__foot">Want the full reasoning? Each pattern page has the evidence and sources. Reviewing a specific claim? Try the <a href="claim-checker.html">claim checker</a>. Longer lists: <a href="questions-to-ask-ai-vendor.html">buying an AI model or vendor</a>, <a href="ai-launch-review-questions.html">a launch review</a>, <a href="how-to-build-an-ai-evaluation.html">building an evaluation</a>. Templates you can copy: <a href="templates.html">vendor questionnaire, eval plan, results report</a>. Real examples: <a href="case-studies.html">case studies</a>. How many items is enough: <a href="sample-size.html">sample size and error bars</a>.</p>
  <p class="room__status" role="status" aria-live="polite" data-room-status></p>
</main>""" % (esc(typo(ROOM["intro"])), cards, esc(typo(ROOM["weakNote"])))
    write("use-it-now.html", layout("Use it now", "Friendly questions you can use today when someone shares an AI result at work, with what a good answer sounds like.", body, current="room", data=True, scripts=("room.js",)))


def build_claim_checker():
    types = EDIT["claimChecker"]["types"]
    chips = "".join('<button type="button" class="chip-toggle" data-type="%s" aria-pressed="false">%s</button>' % (t["id"], esc(t["label"])) for t in types)
    rules = ""
    for t in types:
        rows = "".join("<li><a href=\"%s\">%s</a> <span class=\"rules__fit\">%s</span> %s</li>" % (law_url(r["slug"]), esc(typo(BY_SLUG[r["slug"]]["name"])), {"strong": "strong match", "likely": "likely", "worth": "worth checking"}[r["fit"]], esc(typo(r["why"]))) for r in t["laws"])
        rules += "<h3>%s</h3><ul>%s</ul>" % (esc(t["label"]), rows)
    body = """<main id="main" class="page page--claim" data-page="claim">
  <div class="claim">
    <section class="claim__input" aria-labelledby="claim-h">
      <p class="eyebrow eyebrow--muted">Tool</p>
      <h1 id="claim-h">Check a claim</h1>
      <p class="page__lede">Paste a claim about an AI system. You get the patterns worth checking, why, and a question to ask for each. Not checking a claim? <a href="situation-finder.html">Describe your situation</a> instead.</p>
      <label class="field-label" for="claim-text">The claim</label>
      <textarea id="claim-text" class="claim__text" rows="5" placeholder="Our assistant scores 94%% on MMLU-Pro and beats leading models on our internal benchmark."></textarea>
      <p class="field-label field-label--row" id="type-label">What kind of claim? <span class="muted-inline" data-detect-note>Choose one, or paste a claim and we will suggest some</span></p>
      <div class="chip-toggles" role="group" aria-labelledby="type-label">%s</div>
      <div class="claim__buttons"><button class="btn btn--accent" type="button" data-find>Find patterns that apply</button><button class="btn btn--outline" type="button" data-export disabled>Export questions</button><button class="btn btn--ghost" type="button" data-example>Try an example</button></div>
      <p class="claim__note">A keyword matcher, not an assessment. It looks for words in the claim and lists the patterns usually worth checking for that kind of claim. It cannot tell you whether the claim is true. <a href="#how-matching-works">How matching works</a></p>
    </section>
    <section class="claim__results" aria-live="polite" aria-labelledby="results-h" data-results>
      <h2 id="results-h" class="visually-hidden">Results</h2>
      <p class="claim__empty">Results appear here. Paste a claim and choose Find patterns that apply.</p>
    </section>
  </div>
  <section class="claim__rules" id="how-matching-works"><h2>How matching works</h2>
    <p>Each claim type maps to the patterns a careful reader would check first, using the manuscript\u2019s Playbook and red-flag table. A few phrases (such as \u201cinternal benchmark\u201d or \u201csuperhuman\u201d) add matches of their own. A pattern that matches more than one type moves up a step. The strongest matches are shown first, and lower-fit ones sit behind a button so they do not crowd the rest. If no claim type is detected, you are told so rather than shown a list. This is a keyword matcher, a reading aid and not an assessment of the claim.</p>
    <details><summary>Show the rules</summary>%s</details>
  </section>
</main>""" % (chips, rules)
    write("claim-checker.html", layout("Claim checker", "Paste a claim about an AI system and see which patterns apply, why, and what to ask.", body, current="claim", data=True, scripts=("claim-match.js", "claim-checker.js")))


def build_brief():
    body = """<main id="main" class="page page--brief" data-page="brief">
  <header class="page__head"><p class="eyebrow eyebrow--muted">Learn</p><h1>Quick brief</h1>
  <p class="page__lede">Pick any patterns and get a short overview you can read in a few minutes. It links to the full pattern pages and their sources.</p></header>
  <details class="brief__picker no-print" data-brief-picker><summary data-picker-summary>Choose patterns</summary>
    <div class="brief__presets" data-brief-presets></div>
    <div class="picker" data-brief-grid></div></details>
  <div class="brief__out" data-brief-out></div>
  <noscript><p class="page__note">The quick brief needs JavaScript. You can read each pattern on the <a href="index.html">patterns page</a> instead.</p></noscript>
  <p class="page__note">Assembled in your browser from each pattern\u2019s own text. Read the full pattern and its sources before you rely on one.</p>
</main>"""
    write("brief.html", layout("Quick brief", "Pick any patterns and get a short overview you can read in a few minutes, built from each pattern's own text.", body, current="laws", data=True, scripts=("brief.js",)))


def build_checklist():
    cl = EDIT["checklist"]
    missing = [l["slug"] for l in LAWS if l["slug"] not in cl["phaseOf"]]
    if missing:
        raise SystemExit("data/editorial.json checklist.phaseOf is missing: %s" % ", ".join(missing))
    nums = {l["slug"]: l["no"] for l in LAWS}
    data = {
        "phases": [{"id": p["id"], "label": p["label"], "note": p["note"]} for p in cl["phases"]],
        "stakes": [{"id": s["id"], "label": s["label"], "perPattern": s["perPattern"], "mustAsk": s["mustAsk"], "note": s["note"]} for s in cl["stakes"]],
        "phaseOf": {nums[slug]: ph for slug, ph in cl["phaseOf"].items()},
    }
    write("js/checklist-data.js", "/* Generated by build/build.py. Do not edit. */\nwindow.LAICL = %s;\n" % json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    body = """<main id="main" class="page page--checklist" data-page="checklist">
  <div class="checklist-controls no-print">
    <p class="eyebrow eyebrow--muted">Tool</p>
    <h1>Build a printable checklist</h1>
    <p class="page__lede">Pick a starting set of patterns, choose how much is at stake, and print or save a one-sheet checklist. Questions are grouped by when you would ask them: before you buy, before you launch, and after launch.</p>
    <div class="seg seg--rule seg--wrap" role="group" aria-label="Preset" data-presets></div>
    <div class="checklist-stakes">
      <p class="field-label" id="stakes-label">How much is at stake?</p>
      <div class="seg seg--rule seg--wrap" role="group" aria-labelledby="stakes-label" data-stakes></div>
      <p class="muted-inline" data-stakes-note></p>
    </div>
    <details class="customise" data-customise><summary data-customise-summary>Customise patterns</summary><div class="customise__grid" data-law-grid></div></details>
    <button class="btn btn--ink btn--lg" type="button" data-print>Print / save PDF</button>
    <p class="muted-inline" data-empty hidden>Select at least one pattern to build a checklist.</p>
  </div>
  <section class="sheet" data-sheet aria-label="Checklist preview"></section>
  <noscript><p class="page__note">The checklist builder needs JavaScript. You can read the questions on each <a href="index.html">pattern page</a> instead.</p></noscript>
</main>"""
    write("checklist.html", layout("Checklist builder", "Build a printable checklist of questions to ask when evaluating an AI system, grouped by phase and scaled to the stakes.", body, current="laws", data=True, scripts=("checklist-data.js", "checklist.js")))


# ---------------------------------------------------------------- emitted data
def build_data_js():
    nums = {l["slug"]: l["no"] for l in LAWS}
    presets = {}
    for key, p in EDIT["presets"].items():
        if key.startswith("_"):
            continue
        presets[key] = {"label": p["label"], "laws": [l["no"] for l in LAWS] if p["laws"] == "all" else sorted(nums[s] for s in p["laws"])}
    brief_presets = [{"id": "tour", "label": EDIT["briefPresets"]["tour"]["label"], "laws": sorted(nums[x] for x in EDIT["briefPresets"]["tour"]["laws"])}]
    for key in ("buying", "building", "launch"):
        brief_presets.append({"id": key, "label": presets[key]["label"], "laws": presets[key]["laws"]})
    data = {
        "site": {"baseUrl": SITE["baseUrl"], "version": SITE["version"], "updated": SITE["updated"]},
        "categories": [{"id": c["id"], "name": c["name"], "n": c["n"], "thread": c["thread"]} for c in CATS],
        "laws": [
            {
                "no": l["no"], "slug": l["slug"], "name": l["name"], "aphorism": l["aphorism"], "cat": l["category"], "questions": l["questions"],
                "plain": typo(l["plainTerms"]), "evidence": l["evidenceLine"], "doIt": l["doIt"], "shared": l["shared"],
            }
            for l in LAWS
        ],
        "presets": presets,
        "briefPresets": brief_presets,
        "claim": {
            "types": [{"id": t["id"], "label": t["label"], "detect": t["detect"], "laws": [dict(r, no=nums[r["slug"]]) for r in t["laws"]]} for t in EDIT["claimChecker"]["types"]],
            "modifiers": [dict(m, no=nums[m["slug"]]) for m in EDIT["claimChecker"]["modifiers"]],
        },
        "situation": {
            "example": EDIT["situationFinder"]["example"],
            "types": [{"id": t["id"], "label": t["label"], "detect": t["detect"], "laws": [dict(r, no=nums[r["slug"]]) for r in t["laws"]]} for t in EDIT["situationFinder"]["situations"]],
        },
    }
    write("js/data.js", "/* Generated by build/build.py. Do not edit. */\nwindow.LAI = %s;\n" % json.dumps(data, ensure_ascii=False, separators=(",", ":")))


def page_search_entries():
    """Whole pages (guide, playbooks, tools) so search finds them by name."""
    pages = [("guide.html", "Guide to AI evaluation", "Where to start and what to read next.")]
    pages += [(f, t, d) for f, t, d in GUIDE_CHAPTERS + GUIDE_REFERENCE]
    pages += [(pg["file"], pg["title"], pg["for"]) for pg in INTENT_PAGES]
    pages += [
        ("use-it-now.html", "Use it now", "Questions to ask when someone shares an AI result."),
        ("claim-checker.html", "Claim checker", "Paste a claim and see which patterns apply."),
        ("situation-finder.html", "Find your patterns", "Describe your situation and see which patterns to check first."),
        ("brief.html", "Quick brief", "Pick patterns and get a short overview."),
        ("checklist.html", "Checklist builder", "Build a printable checklist of questions."),
    ]
    return [{"k": "Page", "n": "", "t": t, "s": d, "u": f} for f, t, d in pages]


def build_search_index():
    entries = []
    for l in LAWS:
        u = "patterns/%s.html" % l["slug"]
        entries.append({"k": "Pattern", "n": l["no"], "t": l["name"], "s": l["aphorism"], "u": u})
        sections = [
            ("takeaways", "Takeaways", plain(l["bottomLine"]) + " " + " ".join(plain(t) for t in l["takeaways"])),
            ("what-it-means", "What it means", " ".join(plain(t) for t in l["whatItMeans"])),
            ("the-evidence", "The evidence", " ".join(plain(e["lead"] + " " + e["text"]) for e in l["evidence"])),
            ("use-it", "Use it", " ".join(plain(t) for t in l["useIt"])),
            ("limits", "Where this doesn\u2019t apply", LIMITS[l["slug"]]),
            ("origins", "Origins", " ".join(plain(t) for t in l["origins"])),
        ]
        for sid, label, text in sections:
            entries.append({"k": "Section", "n": l["no"], "t": "%s \u203a %s" % (l["name"], label), "x": text, "u": "%s#%s" % (u, sid)})
    for g in RUBRIC:
        for it in g["items"]:
            entries.append({"k": "Rubric", "n": it["id"], "t": it["text"], "s": "%s \u00b7 %s" % (g["name"], g["tagline"]), "u": "design-rubric.html#%s" % it["id"]})
    dims = {d["code"]: d["title"] for d in AIRR["dimensions"]}
    for c in AIRR["criteria"]:
        entries.append({"k": "Review", "n": c["id"], "t": c["criterion"], "s": "%s \u00b7 %s" % (dims[c["dimension"]], ", ".join(c["references"])), "u": "readiness-review.html#%s" % c["id"]})
    entries.append({"k": "Section", "n": "Page", "t": "Sample size and error bars", "s": "Confidence intervals, margin of error, and how many test items you need to compare two AI systems.", "u": "sample-size.html"})
    entries.append({"k": "Section", "n": "Page", "t": "AI evaluation case studies", "s": "Documented cases mapped to the patterns, each with a primary source.", "u": "case-studies.html"})
    for c in load("cases.json")["cases"]:
        entries.append({"k": "Section", "n": "Case", "t": "Case: " + c["title"], "x": c["what"] + " " + c["check"], "u": "case-studies.html#%s" % c["id"]})
    entries.append({"k": "Section", "n": "Page", "t": "Templates for AI evaluation", "s": "Vendor questionnaire, eval plan one-pager, and results-reporting template.", "u": "templates.html"})
    for t in TEMPLATES:
        entries.append({"k": "Section", "n": "Template", "t": "Template: " + t["title"], "s": t["blurb"], "u": "templates.html#%s" % t["id"]})
    for e in CHANGELOG:
        entries.append({"k": "Changelog", "n": fmt_date(e["date"], short=True), "t": e["text"], "u": "changelog.html"})
    entries.extend(page_search_entries())
    write("js/search-index.js", "/* Generated by build/build.py. Do not edit. */\nwindow.LAI_SEARCH = %s;\n" % json.dumps(entries, ensure_ascii=False, separators=(",", ":")))


INTENT_PAGES = [
    {
        "file": "questions-to-ask-ai-vendor.html",
        "preset": "buying",
        "role": "buying",
        "short": "Buying a model or vendor",
        "cta": "Questions to ask an AI vendor",
        "for": "For choosing or signing off on an AI model, vendor or feature. Questions to put to the people selling it.",
        "see": 'To read a single claim quickly, see <a href="playbook.html#1-reading-an-ai-claim">Playbook: reading an AI claim</a>, or paste it into the <a href="claim-checker.html">claim checker</a>.',
        "title": "Questions to ask when buying an AI model or vendor",
        "desc": "Questions to put to an AI vendor or internal team before you rely on a model, each tied to a documented pattern in AI evaluation research.",
        "lede": "A vendor\u2019s numbers answer the questions the vendor chose to ask. These questions are drawn from the patterns on this site. Each one comes from a documented pattern in the research, with the evidence one click away.",
    },
    {
        "file": "ai-launch-review-questions.html",
        "preset": "launch",
        "role": "launch",
        "short": "Launch review",
        "cta": "AI launch review questions",
        "for": "For the last review before an AI feature ships. Questions about reliability, edge cases and real-world use.",
        "see": 'For the warning signs to look for, see <a href="playbook.html#3-red-flags">Playbook: red flags</a>. For a longer checklist, see the <a href="readiness-review.html">Readiness Review</a>.',
        "title": "Questions for an AI launch review",
        "desc": "Questions to ask before launching an AI feature, covering reliability, edge cases, real-world conditions, and how people will use it.",
        "lede": "A launch review is the last cheap moment to ask what the evaluation did not cover. These questions come from the patterns most relevant to shipping an AI feature, each with its evidence.",
    },
    {
        "file": "how-to-build-an-ai-evaluation.html",
        "preset": "building",
        "role": "building",
        "short": "Building an evaluation",
        "cta": "How to build an AI evaluation",
        "for": "For designing your own evaluation. Questions to check the design before you trust a score.",
        "see": 'For the step-by-step sequence, see <a href="playbook.html#2-building-your-own-eval">Playbook: building your own eval</a>. To record what you ran, copy the <a href="playbook.html#4-eval-card-template">eval card template</a>.',
        "title": "Questions to ask when building an AI evaluation",
        "desc": "What to ask while designing your own AI evaluation, from choosing the metric to reporting uncertainty, drawn from documented evaluation pitfalls.",
        "lede": "Most evaluation mistakes are made before the first score is computed. These questions, drawn from the patterns, help you check the design before you trust the result.",
    },
]


def build_intent_pages():
    for pg in INTENT_PAGES:
        slugs = EDIT["presets"][pg["preset"]]["laws"]
        secs = ""
        for sl in slugs:
            l = BY_SLUG[sl]
            qs = "".join("<li>%s</li>" % esc(typo(q)) for q in l["questions"])
            secs += '<section><h2 id="%s">%s</h2><p>%s</p><ul class="dash">%s</ul><p><a href="%s">Read the evidence: %s</a></p></section>' % (
                sl, esc(typo(l["name"])), esc(typo(l["plainTerms"])), qs, law_url(sl), esc(typo(l["name"])))
        others = ", ".join('<a href="%s">%s</a>' % (o["file"], esc(o["short"].lower())) for o in INTENT_PAGES if o is not pg)
        body = """<main id="main" class="page page--prose">
  %(nav)s
  <header class="page__head"><p class="eyebrow">Guide \u00b7 Playbook</p><h1>%(title)s</h1>
  <p class="page__lede">%(lede)s</p>
  <p class="page__see">%(see)s</p>
  <p><a class="btn btn--ink btn--sm" href="checklist.html?preset=%(preset)s">Print this as a one-page checklist</a></p></header>
  %(secs)s
  <p class="page__note">Other playbooks: %(others)s. Shorter, friendlier questions for common moments are in <a href="use-it-now.html">Use it now</a>. Back to the <a href="guide.html">guide</a>.</p>
</main>""" % {"nav": guide_nav(pg["file"]), "title": esc(pg["title"]), "lede": esc(typo(pg["lede"])), "see": pg["see"], "preset": pg["preset"], "secs": secs, "others": others}
        write(pg["file"], layout(pg["title"], pg["desc"], body, current=None))


# ---------------------------------------------------------------- practitioner pages: sample size, cases, templates
def practitioner_page(fname, title, desc, current, intro_html, sections_html, note, scripts=(), eyebrow="Tool"):
    body = """<main id="main" class="page page--prose page--practice">
  <header class="page__head"><p class="eyebrow">%s</p><h1>%s</h1>%s</header>
  %s
  <p class="page__note">%s</p>
</main>""" % (esc(eyebrow), esc(title), intro_html, sections_html, note)
    write(fname, layout(title, desc, body, current=current, scripts=scripts))


def law_link(slug, prefix=""):
    return '<a href="%s">%s</a>' % (law_url(slug, prefix), esc(typo(BY_SLUG[slug]["name"])))


def calc_form(kind, title, hint, fields, button_note=""):
    """One calculator. fields: list of (name, label, default, attrs) or ('select', name, label, options, default)."""
    rows = ""
    for f in fields:
        if f[0] == "select":
            _, name, label, opts, default = f
            options = "".join('<option value="%s"%s>%s%%</option>' % (o, " selected" if o == default else "", o) for o in opts)
            rows += '<div class="calc__field"><label for="%s-%s">%s</label><select id="%s-%s" name="%s">%s</select></div>' % (kind, name, esc(label), kind, name, name, options)
        else:
            name, label, default, attrs = f
            rows += '<div class="calc__field"><label for="%s-%s">%s</label><input id="%s-%s" name="%s" type="number" inputmode="decimal" value="%s" %s></div>' % (kind, name, esc(label), kind, name, name, default, attrs)
    return (
        '<form class="calc" data-calc="%s" aria-labelledby="calc-%s-h"><h3 id="calc-%s-h">%s</h3><p class="calc__hint">%s</p>'
        '<div class="calc__fields">%s</div><div class="calc__out" data-out role="status" aria-live="polite"><p class="calc__noscript">The calculator needs JavaScript. The table and worked examples on this page work without it.</p></div></form>'
        % (kind, kind, kind, esc(title), esc(typo(hint)), rows)
    )


def build_sample_size():
    import math
    import sample_stats as S
    z = S.z_two_sided(0.95)
    zb = S.z_power(0.80)
    minus = "−"
    rows = ""
    for n in (50, 100, 200, 500, 1000, 5000):
        half50 = S.wilson_offsets(n // 2, n, z)[0] * 100
        below90, above90 = (x * 100 for x in S.wilson_offsets(round(0.9 * n), n, z))
        rows += "<tr><td>%s</td><td>±%.1f</td><td>%s%.1f / +%.1f</td></tr>" % (format(n, ","), half50, minus, below90, above90)
    table = (
        '<div class="table-wrap"><table><caption class="visually-hidden">Wilson 95% interval, in percentage points either side of the observed accuracy, by number of items</caption><thead><tr><th scope="col">Items (n)</th><th scope="col">Observed accuracy 50%: points either side</th><th scope="col">Observed accuracy 90%: points below / above</th></tr></thead><tbody>'
        + rows
        + '</tbody></table></div><p class="calc__hint">These are Wilson 95%% intervals, in percentage points. At 50%% the interval is symmetric and is the widest it gets, so the first column is the worst case. Near 0%% or 100%% it is not symmetric, so the second column gives the points below and above 90%%. For example, 45 correct out of 50 gives %.1f%% to %.1f%%, not a symmetric ± figure. The usual symmetric formula, 1.96 × √(p(1−p)/n), is too narrow there. Assumes independent items scored right or wrong, so the intervals cover which items were drawn and nothing else.</p>' % tuple(100 * x for x in S.wilson(0.9, 50, z))
    )
    lo, hi = S.wilson(0.8, 200, z)
    n97 = S.n_for_margin(0.5, 0.10, z)
    n385 = S.n_for_margin(0.5, 0.05, z)
    n1068 = S.n_for_margin(0.5, 0.03, z)
    ni = S.n_independent(0.80, 0.85)
    nicc = S.n_independent_cc(0.80, 0.85)
    np10 = S.n_paired(0.10, 0.05)
    np20 = S.n_paired(0.20, 0.05)
    ex10, ex20 = S.n_paired_exact(0.10, 0.05), S.n_paired_exact(0.20, 0.05)
    d_norm = S.max_disagreements_for_gap(200, 6, "normal", z)
    d_exact = S.max_disagreements_for_gap(200, 6, "exact", z)
    se_unpaired = math.sqrt(0.82 * 0.18 / 200 + 0.79 * 0.21 / 200)
    unpaired_half = z * se_unpaired * 100
    plo5, phi5, pn5lo, pn5hi = S.pilot_range(5, 50, 0.05, z, zb, z)
    plo10, phi10, pn10lo, pn10hi = S.pilot_range(10, 100, 0.05, z, zb, z)
    forms = "".join([
        calc_form("ci", "1. How precise is my score?", "Enter the number of items and the accuracy you observed. You get a Wilson interval at the confidence level you choose.",
                  [("n", "Number of items", 200, 'min="1" step="1"'), ("acc", "Observed accuracy (%)", 80, 'min="0" max="100" step="any"'), ("select", "conf", "Confidence", ("90", "95", "99"), "95")]),
        calc_form("margin", "2. How many items for a target margin of error?", "Planning figure for a score you have not collected yet. If you have no idea of the accuracy, use 50, which is the most cautious.",
                  [("acc", "Expected accuracy (%)", 50, 'min="1" max="99" step="any"'), ("e", "Margin of error (± points)", 5, 'min="0.1" max="49" step="any"'), ("select", "conf", "Confidence", ("90", "95", "99"), "95")]),
        calc_form("independent", "3a. Compare two systems on different items", "Use this when the two systems are scored on separate samples of items, for example two groups of real users.",
                  [("base", "Baseline accuracy (%)", 80, 'min="1" max="99" step="any"'), ("diff", "Difference to detect (points)", 5, 'min="-99" max="99" step="any"'), ("select", "conf", "Confidence", ("90", "95", "99"), "95"), ("select", "power", "Power", ("80", "90", "95"), "80")]),
        calc_form("paired", "3b. Compare two systems on the same items", "Use this when you run both systems on one test set. It depends on how often they disagree.",
                  [("diff", "Difference to detect (points)", 5, 'min="-99" max="99" step="any"'), ("dis", "Disagreement rate (% of items where exactly one is right)", 10, 'min="0.1" max="100" step="any"'), ("pilot", "Pilot size (items), optional", "", 'min="1" step="1"'), ("select", "conf", "Confidence", ("90", "95", "99"), "95"), ("select", "power", "Power", ("80", "90", "95"), "80")]),
        calc_form("pairedci", "4. Did system A really beat system B on the same items?", "After the run, count the items where only A was right and where only B was right. You get the difference and its confidence interval.",
                  [("n", "Number of items", 200, 'min="2" step="1"'), ("b", "Only A right", 30, 'min="0" step="1"'), ("c", "Only B right", 18, 'min="0" step="1"'), ("select", "conf", "Confidence", ("90", "95", "99"), "95")]),
    ])
    lede = (
        '<p class="page__lede">Every score on a test set is an estimate. How far it could move if you had drawn different items depends mostly on how many items you used. This page shows how to put numbers on that, and how many items you need before a comparison means anything.</p>'
    )
    sec = []
    sec.append(
        '<section><h2 id="short-version">The short version</h2><ul>'
        '<li>A score on %d items is a range, not a point. For %d items scored at 80%%, the Wilson 95%% interval runs from %.1f%% to %.1f%%.</li>'
        '<li>Halving the margin of error takes about four times as many items. As planning figures, ±10 points takes about %d items, ±5 about %d, and ±3 about %s (normal approximation, accuracy near 50%%, the cautious case).</li>'
        '<li>Telling two systems apart needs far more items than measuring one. Detecting 80%% against 85%% on two separate samples takes about %d items per system by the standard formula, or about %d with a continuity correction. On the same items, if the systems disagree on 10%% of them, about %d by the normal approximation; an exact test needs about %d.</li>'
        '<li>If the gap between two systems is within what the choice of items could produce, the test has not shown that they differ. See %s.</li>'
        '<li>A single run of a single prompt is also a sample. See %s and %s.</li></ul></section>'
        % (200, 200, lo * 100, hi * 100, n97, n385, format(n1068, ","), ni, nicc, np10, ex10, law_link("no-error-bars-no-result"), law_link("once-is-not-reliable"), law_link("prompt-sensitivity"))
    )
    sec.append('<section><h2 id="table">Interval by test-set size</h2>%s</section>' % table)
    sec.append('<section><h2 id="calculators">Calculators</h2><p>These run in your browser and send nothing anywhere. They give planning figures from standard formulas, listed under <a href="#sources">Sources</a>; read <a href="#assumptions">the assumptions</a> before relying on them.</p>%s</section>' % forms)
    sec.append(
        '<section><h2 id="worked">Worked examples</h2><ul>'
        '<li><strong>Is 82%% vs 79%% a win?</strong> On 200 items, a score of 80%% has a 95%% interval of %.1f%% to %.1f%%, roughly five to six points either side. If the two systems are scored on separate samples of 200 items, the 95%% interval for a 3-point gap is about ±%.1f points, so the gap is well within noise. Running both systems on the same items gives a sharper test, but a 3-point gap on 200 items is a net of 6 items, and it passes a 5%% test only if the systems disagree on few items: at most %d (%d%%) by the McNemar normal-approximation test, or at most %d (%d%%) by the exact McNemar test. If they disagree on more items than that, the gap is within what the choice of items could produce.</li>'
        '<li><strong>Same items, small disagreement.</strong> To detect a 5-point gap with 80%% power when the systems disagree on 10%% of items you need about %d items by the normal approximation, or about %d by an exact test. If they disagree on 20%% of items, about %d (exact: about %d). More disagreement means more noise in the comparison, so you need more items.</li>'
        '<li><strong>Different items.</strong> The same 5-point gap on two separate samples needs about %d items per system by the standard formula without a continuity correction, or about %d with it, because nothing is cancelled out by sharing items.</li>'
        '<li><strong>Do not know the disagreement rate?</strong> Run both systems on a pilot first and count the items where exactly one is right. A pilot of 50 to 100 items gives only a rough rate. If 5 of 50 items disagree (10%%), the 95%% Wilson range for the true rate is %.1f%% to %.1f%%, and the items needed for a 5-point gap run from about %d to about %d. With 10 of 100, the range is %.1f%% to %.1f%% and the items needed run from about %d to about %d. The disagreement rate cannot be below the gap itself, so where the Wilson range reaches below 5%%, as it does for 5 of 50, the low end is raised to 5%%. Plan with the upper end of the range if you want to be safe.</li></ul>'
        '<p>The main figures on this page are generated from <code>build/sample_stats.py</code> and checked by <code>build/test_sample_size.py</code> in the site repository. That test reads the built page and checks every number in the interval table, the short version, and these worked examples against separate calculations, including exact power for the sample-size figures. It does not check the wording of the assumptions below or the sources, and it checks formulas, not whether they suit your data.</p></section>'
        % (lo * 100, hi * 100, unpaired_half, d_norm, round(100 * d_norm / 200), d_exact, round(100 * d_exact / 200), np10, ex10, np20, ex20, ni, nicc,
           plo5 * 100, phi5 * 100, pn5lo, pn5hi, plo10 * 100, phi10 * 100, pn10lo, pn10hi)
    )
    sec.append(
        '<section><h2 id="assumptions">What the numbers assume, and where they fail</h2><ul>'
        '<li><strong>Independent items.</strong> The formulas treat each item as an independent draw. Items that come in groups (several questions about one document, or many prompts from one user) are correlated, and the true interval is wider. Miller (2024) gives a clustered standard error for this. With strong clustering, count the groups, not the items.</li>'
        '<li><strong>Items are a sample from what you care about.</strong> The interval only covers the luck of which items you drew. It says nothing about whether the test items resemble real use. See %s and %s.</li>'
        '<li><strong>Judge noise is extra.</strong> If an AI model grades the answers, its errors and preferences add to the uncertainty and can bias the score in one direction. The interval above does not include that. Check the grader against people (%s).</li>'
        '<li><strong>Model randomness is separate, and the intervals are over items.</strong> Running each item several times reduces noise from the model’s own variation, but not noise from which items you picked. The intervals on this page describe the choice of items; repeating runs on the same items does not make them narrower, and the run-to-run variation is an additional source of uncertainty. Both matter (%s).</li>'
        '<li><strong>Approximations.</strong> Wilson intervals have much better coverage than the usual symmetric formula at small n and for accuracy near 0%% or 100%%, though they are still approximate (Brown, Cai and DasGupta, 2001). The sample-size formulas are normal approximations, and an exact test can need more items. As a rough guide, not a sharp cut-off, treat the figures as rough below about 30 items, or with fewer than about 25 disagreements in a paired comparison, and consider an exact method.</li>'
        '<li><strong>Many comparisons.</strong> The calculators cover one comparison. If you test many variants against one test set and report the best, the best will look better than it is (%s). This page does not cover corrections for multiple comparisons.</li>'
        '<li><strong>Point of the plan.</strong> The sample size depends on the smallest difference that would change your decision. Decide that first and write it down (see the <a href="templates.html">eval plan template</a>).</li></ul></section>'
        % (law_link("distribution-shift"), law_link("the-construct-gap"), law_link("judge-bias"), law_link("once-is-not-reliable"), law_link("adaptive-overfitting"))
    )
    sec.append(
        '<section><h2 id="related">Related patterns</h2><ul>'
        '<li>%s: every score is an estimate; show the interval.</li>'
        '<li>%s: one run, or one prompt, is a single draw.</li>'
        '<li>%s: an average needs enough items in each slice to carry its own interval.</li></ul>'
        '<p>For real examples, see the <a href="case-studies.html">case studies</a>. For a reporting layout that includes intervals, see the <a href="templates.html">results template</a>.</p></section>'
        % (law_link("no-error-bars-no-result"), law_link("once-is-not-reliable"), law_link("the-averaging-trap"))
    )
    sources = [
        ("Wilson, E. B. (1927). Probable inference, the law of succession, and statistical inference. <em>Journal of the American Statistical Association</em>, 22(158), 209–212.", "https://doi.org/10.1080/01621459.1927.10502953", "The Wilson score interval."),
        ("Brown, L. D., Cai, T. T., &amp; DasGupta, A. (2001). Interval estimation for a binomial proportion. <em>Statistical Science</em>, 16(2), 101–133.", "https://doi.org/10.1214/ss/1009213286", "Compares intervals by coverage; recommends Wilson or Jeffreys for small samples and Agresti–Coull for larger ones."),
        ("Miller, E. (2024). Adding error bars to evals: A statistical approach to language model evaluations. arXiv:2411.00640.", "https://arxiv.org/abs/2411.00640", "Standard errors (including clustered), paired differences between models (eq. 7), and power analysis for evals (section 5)."),
        ("Fleiss, J. L., Levin, B., &amp; Paik, M. C. (2003). <em>Statistical Methods for Rates and Proportions</em>. Wiley.", "https://doi.org/10.1002/0471445428", "Sample size for comparing two independent proportions, with and without a continuity correction."),
        ("Connor, R. J. (1987). Sample size for testing differences in proportions for the paired-sample design. <em>Biometrics</em>, 43(1).", "https://doi.org/10.2307/2531961", "Sample size when both systems are scored on the same items (the McNemar setting)."),
    ]
    items = "".join('<li>%s <a href="%s" rel="noopener">%s</a><br><span class="calc__hint">%s</span></li>' % (s, u, u, esc(typo(d))) for s, u, d in sources)
    sec.append('<section><h2 id="sources">Sources</h2><ul class="plain-list">%s</ul><p>The formulas in the calculators are standard textbook results; this page applies them to eval data and does not add to them. The sample-size formulas in 3a and 3b are normal approximations. Figures for an exact test, and the pilot ranges, are computed on this site by enumerating the exact distributions and applying the Wilson interval; they are not from the sources above. Miller’s worked example for detecting a 3-point difference, under the assumptions in his paper, comes to roughly 1,000 questions.</p></section>' % items)
    note = "Planning aid, not a statistical consultation. For a high-stakes decision, have someone with statistics training check the design. The figures in the table and worked examples are checked by build/test_sample_size.py in the site repository."
    practitioner_page(
        "sample-size.html",
        "Sample size and error bars",
        "How many test items you need, with a confidence-interval calculator, an interval table, and sample sizes for comparing two AI systems.",
        "sample-size", lede, "".join(sec), note, scripts=("sample-size.js",),
    )


def build_cases():
    CASES = load("cases.json")
    secs = []
    for c in CASES["cases"]:
        tags = ", ".join(law_link(s) for s in c["patterns"])
        dispute = '<p>%s</p>' % esc(typo(c["dispute"])) if c.get("dispute") else ""
        also = ""
        if c.get("alsoRead"):
            also = '<p class="case__src"><span class="case__k">Also read</span> <a href="%s" rel="noopener">%s</a></p>' % (esc(c["alsoRead"]["url"]), esc(typo(c["alsoRead"]["label"])))
        secs.append(
            '<section class="case" id="%s" aria-labelledby="%s-h"><h2 id="%s-h">%s</h2>'
            '<p class="case__patterns"><span class="case__k">Patterns</span> %s</p>'
            '<h3>What the source reports</h3><p>%s</p>%s'
            '<h3>What this case does not show</h3><p>%s</p>'
            '<h3>The check that helps</h3><p>%s</p>'
            '<p class="case__src"><span class="case__k">Primary source</span> <a href="%s" rel="noopener">%s</a></p>%s</section>'
            % (c["id"], c["id"], c["id"], esc(typo(c["title"])), tags, esc(typo(c["what"])), dispute, esc(typo(c["limits"])), esc(typo(c["check"])), esc(c["source"]["url"]), esc(typo(c["source"]["label"])), also)
        )
    toc = "".join('<li><a href="#%s">%s</a></li>' % (c["id"], esc(typo(c["title"]))) for c in CASES["cases"])
    lede = '<p class="page__lede">%s</p>' % esc(typo(CASES["intro"]))
    intro = '%s<p class="case__note"><strong>Read this first.</strong> %s</p><nav aria-label="Cases"><ul class="case__toc">%s</ul></nav>' % (lede, esc(typo(CASES["note"])), toc)
    practitioner_page(
        "case-studies.html",
        "AI evaluation case studies",
        "Seven documented cases, each mapped to the evaluation patterns it shows, with the check that helps and a link to the primary source.",
        "cases", "", intro + "".join(secs) + '<p>To turn these into questions you can ask, see <a href="use-it-now.html">Use it now</a> and the <a href="templates.html">templates</a>. The numbers and wording above follow each source; for anything you plan to repeat, read the source.</p>',
        "Each case was checked against the abstract or full text of the linked source. Spot a mistake? Every pattern page has a Report it link, or use the contact page.",
        eyebrow="Evidence in practice",
    )


# The walkthrough re-tells three entries from data/cases.json (same facts, same numbers, nothing added), in
# three steps: choose the claim, test it, decide. [[slug]] becomes a link to that pattern page.
WALKTHROUGH = [
    {
        "id": "arena-private-variants",
        "anchor": "walk-leaderboard",
        "title": "A leaderboard rank",
        "told": [
            "You are told that a model ranks near the top of Chatbot Arena, a public leaderboard that ranks models by votes from users. Then you read Singh et al. (2025), who studied the platform. They report that some providers could test several model variants privately before release and choose which scores to publish. The most extreme case they identify is Meta, which they observed testing as many as 27 private variants in a single month before the Llama 4 release.",
        ],
        "choose": "The claim is that this model is better than its rivals, because of where it ranks. The decision that rides on it is which model to pick or recommend. The claim assumes the published score is a fair picture of the model, not the best of several tries.",
        "test": [
            "Start with [[goodharts-law]]. A rank stands in for quality, and the harder anyone pushes on a stand-in, the further it can drift. Ask what improved: the capability, or the fit to the test. In the paper’s controlled experiment, fine-tuning a model on Arena-style data raised its win rate against a baseline on an Arena-derived benchmark (ArenaHard) by up to 112% in relative terms, while performance on a broader benchmark (MMLU) slightly declined (step 3 gives LMArena’s response to this experiment).",
            "Then [[campbells-law]]. When a number drives buying and press, everyone has a reason to game it, often without anyone deciding to cheat. Ask how many variants were tried before the reported one, and whether a second measure that nobody optimized agrees.",
        ],
        "decide": "You can conclude that a rank alone does not say how many candidates it was selected from, and a published result should say. Treat it as one input. You still do not know whether any leaderboard result was wrong, whether any provider broke a rule, or how good any model is. LMArena, the platform, published a response on 9 May 2025 disputing parts of the paper. It says, for example, that the 112% experiment used a static benchmark rather than Chatbot Arena itself. This page does not settle the dispute; read both. Before you choose on rank, ask how many variants were tried before the reported one, and look for a second measure that nobody optimized.",
    },
    {
        "id": "epic-sepsis",
        "anchor": "walk-sepsis",
        "title": "A clinical model that “works”",
        "told": [
            "You are told that a sepsis prediction model in use at many US hospitals works. Then you read Wong et al. (2021), who externally validated the original version of the Epic Sepsis Model on 38,455 hospitalizations at Michigan Medicine between December 2018 and October 2019, where sepsis occurred in about 7%. They report a hospitalization-level AUC of 0.63, that the model did not identify about 67% of patients with sepsis, and that, at the alert threshold Michigan Medicine used (a score of 6 or higher), it generated alerts for about 18% of all hospitalized patients. They conclude that it has poor discrimination and calibration. The developer’s documentation reported an AUC of 0.76 to 0.83. The authors say the difference is likely due to how they treated the timing of sepsis predictions: when they also counted scores up to 3 hours after sepsis onset, which their main analysis excluded, the AUC rose to 0.80.",
        ],
        "choose": "The claim is that the model works, so a hospital can rely on its alerts. The decision that rides on it is whether to rely on it for your own patients. “Works” needs defining first: how well it separates patients who develop sepsis from those who do not, how many alerts it takes, and when a prediction counts, since the same model scored 0.63 or 0.80 depending on whether scores after onset were counted.",
        "test": [
            "Start with [[the-functionality-fallacy]]. Whether it works is the first question, not a settled one. Vendor-reported performance is a claim; independent validation is evidence. This is an independent validation, and it found 0.63 against the developer’s 0.76 to 0.83. Then ask why the numbers differ. The authors say it is likely how they treated timing, so before you compare any two figures, ask when a prediction counted and how sepsis was defined.",
            "Then [[the-lab-to-field-gap]], which asks what changes when a model is used in a real clinic. Here, count the alert burden as well as the hits: at the threshold Michigan Medicine used, the model alerted for about 18% of all hospitalized patients.",
        ],
        "decide": "You can conclude that this validation found poor discrimination and calibration for the original version, and that the definition of timing changed the headline number, so a figure without its definition is hard to compare. Epic released a revised version in 2022, and a 2026 multicenter study of the updated model (Wong et al., JAMA Network Open) reported encounter-level AUROC of 0.82 to 0.92 across four US health systems, with high variability between sites and a high alert burden. You still do not know how either version performs at your hospital. The next step is to ask the vendor how timing and sepsis were defined in its figures, then validate on your own data, with the metrics, timing rule, and alert threshold fixed in advance.",
    },
    {
        "id": "gsm1k",
        "anchor": "walk-benchmark",
        "title": "A benchmark score",
        "told": [
            "You are told that a model scores highly on GSM8K, a popular grade-school math benchmark. Then you read Zhang et al. (2024). Human annotators wrote GSM1k, a new set of grade-school math problems built to match GSM8K in style and difficulty. Some model families scored up to 8% lower on GSM1k than on GSM8K. Models that assigned higher probability to the GSM8K test items showed bigger gaps (Spearman rank correlation of 0.36), which the authors take to suggest partial memorization, though they note outliers and say contamination is likely not the full story. Many frontier models showed little or no gap, which the authors say could reflect better generalization or more careful data handling.",
        ],
        "choose": "The claim is that the score shows the model can do grade-school math. The decision that rides on it is whether to trust that score, or to choose the model because of it. The claim assumes the model had not already seen the test items.",
        "test": [
            "The pattern here is [[data-contamination]]: if the test was in the training data, the score measures memory, not skill. You usually cannot inspect a model’s training data, so the test has to be indirect. Compare scores on public items with scores on look-alike items that have never been posted online, as the GSM1k authors did, and ask whether the gap is larger for the models that are most familiar with the public items.",
        ],
        "decide": "You can conclude that a large gap is the warning sign, and that a small gap is some reassurance, not proof. Many frontier models showed little or no gap. You still do not know whether any one model memorized test items. This case does not show that public benchmarks are useless or that every model memorized test items, and the gaps apply to the models the authors tested. To find out for your own model, build a small private set of look-alike items that has never been posted online, score the model on both sets, and compare.",
    },
]


def build_walkthrough():
    CASES = load("cases.json")
    by_id = {c["id"]: c for c in CASES["cases"]}

    def prose(t):
        return re.sub(r"\[\[([a-z0-9-]+)\]\]", lambda m: law_link(m.group(1)), esc(typo(t)))

    def step(n, label, inner):
        return '<h3 class="walk__step"><span class="walk__n" aria-hidden="true">%d</span>%s</h3>%s' % (n, label, inner)

    secs = []
    for i, w in enumerate(WALKTHROUGH, 1):
        c = by_id[w["id"]]
        patterns = ", ".join(law_link(s) for s in c["patterns"])
        told = "".join('<p class="walk__told">%s</p>' % prose(t) for t in w["told"])
        secs.append(
            '<section class="walk" id="%(a)s" aria-labelledby="%(a)s-h"><p class="walk__case">Case %(i)d</p><h2 id="%(a)s-h">%(title)s</h2>'
            '%(told)s%(s1)s%(s2)s%(s3)s'
            '<p class="case__src"><span class="case__k">Patterns</span> %(patterns)s</p>'
            '<p class="case__src"><span class="case__k">Primary source</span> <a href="%(url)s" rel="noopener">%(label)s</a></p>'
            '<p class="case__src"><a href="case-studies.html#%(id)s">Full case-study entry</a></p></section>'
            % {
                "a": w["anchor"], "i": i, "title": esc(typo(w["title"])), "told": told,
                "s1": step(1, "Choose the claim", "<p>%s</p>" % prose(w["choose"])),
                "s2": step(2, "Test it", "".join("<p>%s</p>" % prose(t) for t in w["test"])),
                "s3": step(3, "Decide", "<p>%s</p>" % prose(w["decide"])),
                "patterns": patterns, "url": esc(c["source"]["url"]), "label": esc(typo(c["source"]["label"])), "id": c["id"],
            }
        )
    toc = "".join('<li><a href="#%s">%s</a></li>' % (w["anchor"], esc(typo(w["title"]))) for w in WALKTHROUGH)
    arc = (
        '<ol class="walk__arc">'
        '<li><strong>Choose the claim.</strong> Say exactly what is being claimed, and what decision rides on it.</li>'
        '<li><strong>Test it.</strong> Find the patterns that apply, in order, and ask what each one asks.</li>'
        '<li><strong>Decide.</strong> Say what you can conclude, and what you still would not know.</li></ol>'
    )
    lede = '<p class="page__lede">Choose a claim, test it, decide. This page does that three times, slowly, on real published cases: a leaderboard rank, a clinical model, and a benchmark score.</p>'
    intro = (
        arc
        + '<p class="case__note"><strong>Read this first.</strong> %s</p>' % esc(typo(CASES["note"]))
        + '<nav aria-label="Cases"><ul class="case__toc">%s</ul></nav>' % toc
        + '<p class="case__note">Each case here has a fuller entry on the <a href="case-studies.html">case studies page</a>, including what it does not show.</p>'
    )
    outro = (
        '<section class="walk walk--next" id="your-turn" aria-labelledby="your-turn-h"><h2 id="your-turn-h">Now try it on a claim you have</h2>'
        '<p>Write down the claim and the decision that depends on it. Then:</p>'
        '<ul><li>Paste the claim into the <a href="claim-checker.html">Claim checker</a> to see which patterns apply.</li>'
        '<li>Describe your situation in <a href="situation-finder.html">Find your patterns</a> to see which to check first.</li>'
        '<li>Fill in a <a href="templates.html">template</a> (the eval plan one-pager is the place to write down the decision) before you run anything.</li></ul>'
        '<p>The <a href="case-studies.html">case studies</a> page has more cases, each with its primary source. The numbers and wording above follow each source; for anything you plan to repeat, read the source.</p></section>'
    )
    body = """<main id="main" class="page page--prose page--walk">
  %s
  <header class="page__head"><p class="eyebrow">%s</p><h1>A claim, read slowly</h1>%s</header>
  %s%s%s%s
</main>""" % (guide_nav("walkthrough.html"), esc(chapter_eyebrow("walkthrough.html")), lede, intro, "".join(secs), outro, guide_pager("walkthrough.html"))
    write("walkthrough.html", layout(
        "A claim, read slowly",
        "Three real AI claims read slowly in three steps: choose the claim, test it against the patterns, then decide what you can and cannot conclude.",
        body, current=None))


TEMPLATES = [
    {
        "id": "vendor-questionnaire",
        "file": "ai-vendor-questionnaire.md",
        "title": "AI vendor questionnaire",
        "blurb": "Seventeen questions to send a vendor or internal team before you rely on an AI system, each with what a good answer and a red flag look like. Built from the questions on the pattern pages and the buying-a-model list.",
    },
    {
        "id": "eval-plan",
        "file": "eval-plan-one-pager.md",
        "title": "Eval plan one-pager",
        "blurb": "Fill this in before you run an evaluation: the decision, what is measured, data, locked test set, metrics, baselines, repeats, grader validation, stopping rules, and the owner.",
    },
    {
        "id": "results-report",
        "file": "results-reporting-template.md",
        "title": "Results-reporting template",
        "blurb": "A layout for reporting results: n, intervals, baselines, breakdowns, cost, and a section on what the evaluation cannot show.",
    },
]


def build_templates():
    secs = []
    for t in TEMPLATES:
        raw = (ROOT / "downloads" / t["file"]).read_text(encoding="utf-8")
        raw = re.sub(r"^<!--.*?-->\s*", "", raw, flags=re.S)
        lines = raw.split("\n")
        lines = [l for l in lines if not l.startswith("# ")]
        rendered = md_blocks(lines, h2="##")
        rendered = re.sub(r'<h([23]) id="([^"]+)">(.*?)</h\1>', lambda m: '<h%d id="%s-%s">%s</h%d>' % (int(m.group(1)) + 1, t["id"], m.group(2), m.group(3), int(m.group(1)) + 1), rendered)
        secs.append(
            '<section class="tpl" id="%s" aria-labelledby="%s-h"><h2 id="%s-h">%s</h2><p>%s</p>'
            '<p class="tpl__actions"><a class="btn btn--ink btn--sm" href="downloads/%s" download>Download (Markdown)</a></p>'
            '<details class="tpl__view" open><summary>View on this page</summary><div class="tpl__body">%s</div></details></section>'
            % (t["id"], t["id"], t["id"], esc(typo(t["title"])), esc(typo(t["blurb"])), t["file"], rendered)
        )
    lede = '<p class="page__lede">Three plain-text templates you can copy into a document, a ticket, or a repository. Each is on this page and also downloadable as a Markdown file.</p>'
    intro = lede + '<p>They are licensed <a href="https://creativecommons.org/licenses/by/4.0/" rel="noopener">CC BY 4.0</a>: copy, adapt, and share them with credit to the AI Evaluation Field Guide. They are starting points, not a standard, and filling one in does not by itself show that an evaluation is sound. Delete what does not fit and add what does.</p>'
    practitioner_page(
        "templates.html",
        "Templates for AI evaluation",
        "Downloadable templates: an AI vendor questionnaire with good answers and red flags, an eval plan one-pager, and a results-reporting template.",
        "templates", intro, "".join(secs),
        "Questions in the vendor questionnaire come from the pattern pages. Worked examples in the templates use invented numbers for layout only. See also the sample-size page and case studies.",
    )


def join_and(parts):
    return parts[0] if len(parts) == 1 else ", ".join(parts[:-1]) + ", and " + parts[-1]


def build_methodology():
    model = bibliography.build_model(LAWS)
    c = bibliography.counts(model)
    mix = esc(typo(join_and(bibliography.type_breakdown_text(c))))
    kinds = esc(typo(bibliography.kinds_sentence(c)))
    no_link = sum(1 for e in model["entries"] if not e["primary"]["url"])
    merged = esc(typo(join_and([bibliography.dedupe_note(e) for e in c["merged"]]))) if c["merged"] else ""
    sources_extra = (" Two versions of one study count as one work: %s%s" % (merged, "" if merged.endswith(".") else ".")) if merged else ""
    kinds_extra = (" A few unlabeled entries are not ordinary peer-reviewed papers, and the Bibliography tags them: %s." % kinds) if kinds else ""
    checked = fmt_date(SITE["lawDefaults"]["evidenceChecked"])
    body = """<main id="main" class="page page--prose">
  %(nav)s
  <header class="page__head"><p class="eyebrow">Guide</p><h1>Methodology</h1>
  <p class="page__lede">How the patterns were chosen, what counts as a source, how the evidence was checked, and what this guide does not claim to be.</p></header>
  <section><h2 id="selection">How patterns are chosen</h2>
  <p>The %(n_laws)d patterns are an editorial selection of recurring ways AI evaluation goes wrong, each with published research behind it. They are not the result of a systematic review, and another reasonable list would differ. Each pattern page says whether its name is an established term, a recent term, or named here (the idea is established, but the name is this guide\u2019s own), and gives an Evidence base of well established, developing, or emerging (see <a href="about.html#evidence">how the evidence base is described</a>).</p>
  <p>For what comes from the research and what is this guide\u2019s own, see <a href="about.html#own-vs-research">the line drawn on the About page</a>. The table of every pattern with its name label and Evidence base is in <a href="about.html#evidence">the same page</a>.</p></section>
  <section><h2 id="sources">What counts as a source</h2>
  <p>A <em>citation</em> is one source line on one pattern page, so a work cited by three patterns is three citations. A <em>work</em> is one distinct piece of research, counted once however many pages cite it.%(merged)s</p>
  <p>The %(n_laws)d pattern pages make %(n_cit)d citations to %(n_wp)d distinct works. The <a href="bibliography.html">Bibliography</a> lists %(n_tot)d works in all, which adds %(n_else)d that appear only in the Overview, Being Pragmatic, Playbook or Glossary. Counting each work once, of the %(n_tot)d, %(mix)s.%(kinds)s</p>
  <p>Preprints, reports, regulations, working papers, and books are labeled on the pattern page and in the Bibliography. The Evidence section reports what the authors found, and where results are mixed or limited the page says so, for example in <a href="patterns/adaptive-overfitting.html">Adaptive Overfitting</a> and <a href="patterns/data-contamination.html">Data Contamination</a>. Every pattern also has a \u201cWhere this doesn\u2019t apply\u201d section.</p></section>
  <section><h2 id="checking">How the evidence was checked</h2>
  <p>Each pattern shows when its evidence was last reviewed (currently %(checked)s). The evidence has been checked twice, and neither check is independent peer review.</p>
  <ul>
    <li><strong>Early October 2026: a spot-check.</strong> More than 40 specific figures and findings on the pattern pages were compared with the source\u2019s abstract or full text, covering at least one claim in 25 of the 26 patterns. It found no discrepancies, but it compared only numbers and headline findings, so it could not catch statements that went beyond their sources or left out a caveat.</li>
    <li><strong>19 October 2026: a full re-audit.</strong> Every claim on the pattern pages, the guide pages, the glossary, and the bibliography was checked against its primary source, including whether each statement was supported as strongly as it was worded. Every DOI was checked against Crossref and every arXiv entry against arXiv\u2019s records. This found five factual errors (a misquoted sentence, a wrong author name, a wrong statistical rule, two experiments reported as one, and a measure described as something it was not), plus several dozen statements that were stronger than their sources or missing a caveat. Those have been corrected, softened, or removed. Every source link was also tested: none returned a not-found error, although some publishers block automated checks. %(no_link)d sources are listed without a link.</li>
  </ul>
  <p>Limits of the re-audit. Some sources could not be read in full: paywalled journal articles, some conference papers in the ACM Digital Library, books, and recent legal texts were checked against abstracts, publisher records, or secondary descriptions, and the pages are worded to match what could be verified. Whether a preprint has since been published in a journal was not checked exhaustively. The re-audit was carried out by the site\u2019s author with AI-assisted checking, not by an outside expert, so errors may remain. If you find one, please report it.</p></section>
  <section><h2 id="tools">The tools</h2>
  <p>The claim checker, Find your patterns, the checklist, the quick brief, and Use it now are reading aids. The claim checker and Find your patterns match your text against published rules, which you can read on each page. They do not assess a system, and they run in your browser. The Design Rubric and Readiness Review are checklists. They do not calculate a score. The <a href="sample-size.html">sample-size calculators</a> apply standard formulas, listed on that page and checked by a test script in the site repository. The <a href="case-studies.html">case studies</a> summarize published studies and link to each primary source. The <a href="templates.html">templates</a> are editorial starting points.</p></section>
  <section><h2 id="not-covered">What this guide does not cover</h2>
  <p>These are gaps, not oversights. Each is a field of its own, and the guide treats it only briefly or not at all.</p>
  <ul>
    <li><strong>Statistics beyond the basics.</strong> The <a href="sample-size.html">sample-size page</a> covers confidence intervals and the number of items for one or two comparisons. It does not cover statistical power in complex designs, corrections for many comparisons, Bayesian methods, or items that come in correlated groups beyond a brief mention.</li>
    <li><strong>Calibration.</strong> Whether a system’s stated confidence matches how often it is right is not covered.</li>
    <li><strong>Agent and tool-use evaluation.</strong> Agents appear through a few benchmarks and studies, such as τ-bench. Designing evaluations for multi-step agents, tool use, and long-running tasks is not covered in depth.</li>
    <li><strong>Safety and red-team methods.</strong> <a href="patterns/presence-not-absence.html">Presence, Not Absence</a> explains why a failure to find a risk is weak evidence. How to run a red-team exercise, design adversarial tests, or assess dangerous capabilities is not covered.</li>
    <li><strong>Validating an AI grader.</strong> <a href="patterns/judge-bias.html">Judge Bias</a> says to check a grader against people on a sample. It does not cover agreement measures, rubric design for judges, or how many labels are enough.</li>
    <li><strong>Building evaluation sets at scale.</strong> Sampling, annotation pipelines, quality control, and keeping a set fresh over time are not covered.</li>
    <li><strong>Fairness auditing, privacy, security, and legal compliance.</strong> These are touched on by the Readiness Review, which points to standards, but they are not treated as evaluation methods here.</li>
    <li><strong>Evidence from the last few months.</strong> Each pattern shows when its evidence was last checked. Newer work may not be reflected yet.</li>
  </ul>
  <p>If you know a good source for any of these, please say so through the contact page.</p></section>
  <section><h2 id="not">What this guide is not</h2>
  <ul>
    <li>It is not a ranking or benchmark of any AI model or vendor.</li>
    <li>It is not legal, regulatory, or compliance advice, though the Readiness Review points to standards that are relevant.</li>
    <li>It is not peer reviewed, and no outside reviewer has signed off on any pattern yet.</li>
  </ul></section>
  <section><h2 id="changes">How it changes</h2>
  <p>Each pattern has a version number and a revision history, and site-wide changes are in the <a href="changelog.html">changelog</a>. Corrections are made in the open and logged there. If you find a mistake or a better source, every pattern page has a \u201cReport it\u201d link, or you can use the <a href="https://josephalfonso.com/pages/contact.html">contact page</a>.</p></section>
</main>""" % {"nav": guide_nav("methodology.html"), "n_laws": len(LAWS), "n_cit": c["citations"], "n_wp": c["works_on_patterns"], "n_tot": c["works_total"], "n_else": c["only_elsewhere"], "mix": mix, "kinds": kinds_extra, "merged": sources_extra, "checked": checked, "no_link": no_link}
    write("methodology.html", layout("Methodology", "How the patterns were chosen, what counts as a source, how the evidence was checked, and what this guide does not claim to be.", body, current=None))


def build_privacy():
    body = """<main id="main" class="page page--prose">
  <header class="page__head"><p class="eyebrow">Policy</p><h1>Privacy</h1>
  <p class="page__lede">There are no accounts and no ads, and nothing here is sold. This page lists what is collected and by whom.</p></header>
  <section class="callout" aria-labelledby="in-short"><h2 id="in-short">In short</h2>
  <ul>
    <li><strong>This site uses Google Analytics</strong> to count visits. Google receives your IP address, the page you view, and your browser and device details.</li>
    <li><strong>Google Fonts</strong> also receives your IP address and browser details when the fonts load.</li>
    <li><strong>My patterns is stored in your browser</strong> (local storage), on your device. The list itself is not sent anywhere, but when you open the brief or checklist your selection appears in the page address, which Google Analytics receives (see below).</li>
    <li>What you type into the claim checker, Find your patterns, the checklist, the quick brief, and Use it now stays in your browser.</li>
  </ul></section>
  <section><h2 id="analytics">Google Analytics</h2>
  <p>Every page loads Google Analytics (measurement ID %(ga)s) from Google\u2019s servers. Each page view sends Google the page address, the page you came from, your IP address, and your browser, device, and language details. Google uses the IP address to estimate roughly where visitors are. This site\u2019s code does not apply any extra IP-masking setting. It does not turn off Google\u2019s advertising-related storage outside the regions below, and it does not set user IDs or send anything you type. Depending on how the Google Analytics property is configured, which the page code does not control, Google may also record events such as outbound link clicks and scrolling.</p>
  <p>The page address includes any query string. On the quick brief, the checklist, and the patterns index, the address can contain the patterns you selected or a role filter (for example <code>?patterns=3,7</code>), so those selections are visible to Google Analytics along with the rest of the address.</p>
  <h3>Cookies and consent</h3>
  <p>Outside the regions below, Google Analytics sets its cookies when the page loads. There is no consent banner and no opt-in or opt-out control on this site.</p>
  <p>For visitors in the EU, the European Economic Area (including Iceland, Liechtenstein, and Norway), the UK, and Switzerland, the site tells Google Analytics to deny analytics and advertising storage by default, so Google Analytics does not set cookies there. The Google script still loads and may still receive cookieless signals about the visit, such as the page address and your IP address. Because there is no banner, visitors in those regions have no way to opt in.</p>
  <p>To block Google Analytics everywhere, use your browser\u2019s tracking protection or a content blocker, or Google\u2019s <a href="https://tools.google.com/dlpage/gaoptout" rel="noopener">Analytics opt-out browser add-on</a>. The site works without it.</p></section>
  <section><h2 id="fonts">Fonts</h2>
  <p>The fonts load from Google Fonts. Loading them sends your IP address and browser details to Google.</p>
  <h2 id="hosting">Hosting</h2>
  <p>As with any website, the server that delivers these pages receives your IP address and request details, and may keep standard server logs.</p></section>
  <section><h2 id="your-device">What stays on your device</h2>
  <p>The claim checker, Find your patterns, the checklist, the quick brief, and Use it now run in your browser. What you type into them is not sent anywhere. The Share and Copy buttons use only your device\u2019s clipboard or share menu.</p>
  <p>The site saves two things in your browser\u2019s local storage. Neither is sent to the site\u2019s server or to Google by this site\u2019s code.</p>
  <ul>
    <li><strong>My patterns:</strong> the numbers of the patterns you add with the Add buttons, so they are still there on your next visit and on the brief and checklist pages.</li>
    <li><strong>Last-seen date:</strong> the date of the latest update you had seen when you last opened the patterns index, so it can mark what is new since your last visit.</li>
  </ul>
  <p>Clearing your browser\u2019s site data removes both. Local storage stays on one browser and one device. It does not follow you to another.</p></section>
  <section><h2 id="contact">Questions</h2>
  <p>Use the <a href="https://josephalfonso.com/pages/contact.html">contact page</a>. Last updated %(updated)s.</p></section>
</main>""" % {"updated": fmt_date(SITE["updated"]), "ga": SITE["gaId"]}
    write("privacy.html", layout("Privacy", "What this site collects, who receives it, and what stays on your device.", body, current=None))


# Old URLs kept alive after renames or merges: (from, to). Add a line here when a page is merged away.
REDIRECTS = [
    ("/field-guide.html", "/playbook.html"),
    ("/field-guide", "/playbook"),
    ("/laws/*", "/patterns/:splat"),
    ("/laws", "/patterns"),
]


def build_security():
    # The signup form posts to an outside mail service only when data/site.json newsletter.action is set.
    # That one origin is then allowed in form-action; otherwise forms may only post to this site.
    action = newsletter_action()
    form_action = "'self'"
    news_comment = ""
    if action:
        u = urllib.parse.urlsplit(action)
        form_action += " %s://%s" % (u.scheme, u.netloc)
        news_comment = "# form-action also allows the newsletter signup endpoint set in data/site.json (newsletter.action).\n"
    csp = "; ".join([
        "default-src 'self'",
        "script-src 'self' 'sha256-%s' https://*.googletagmanager.com" % base64.b64encode(hashlib.sha256(analytics_inline_js().encode("utf-8")).digest()).decode(),
        "style-src 'self' https://fonts.googleapis.com",
        "font-src https://fonts.gstatic.com",
        "img-src 'self' data: https://*.google-analytics.com https://*.googletagmanager.com",
        "connect-src 'self' https://*.google-analytics.com https://*.analytics.google.com https://*.googletagmanager.com",
        "object-src 'none'",
        "base-uri 'self'",
        "form-action " + form_action,
        "frame-ancestors 'none'",
    ])
    headers = (
        "# Generated by build/build.py. Applied by Cloudflare Pages / Workers static assets.\n"
        "%s/*\n"
        "  Content-Security-Policy: %s\n"
        "  X-Frame-Options: DENY\n"
        "  Referrer-Policy: strict-origin-when-cross-origin\n"
        "  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=(), interest-cohort=()\n"
        "  Cross-Origin-Opener-Policy: same-origin\n" % (news_comment, csp)
    )
    write("_headers", headers)
    write("_redirects", "# Generated by build/build.py. Old URLs kept alive after renames.\n" + "".join("%s %s 301\n" % r for r in REDIRECTS))
    expires = (datetime.date.fromisoformat(SITE["updated"]) + datetime.timedelta(days=365)).isoformat()
    write(".well-known/security.txt", "Contact: https://josephalfonso.com/pages/contact.html\nExpires: %sT00:00:00.000Z\nPreferred-Languages: en\nCanonical: %s/.well-known/security.txt\n" % (expires, SITE["baseUrl"]))


def build_seo():
    urls = ["index.html"] + sorted(p.name for p in ROOT.glob("*.html") if p.name != "index.html") + ["patterns/%s.html" % l["slug"] for l in LAWS]
    def loc(rel):
        return SITE["baseUrl"] + "/" + ("" if rel == "index.html" else rel[: -len(".html")])
    entries = "".join("<url><loc>%s</loc><lastmod>%s</lastmod></url>\n" % (loc(u), SITE["updated"]) for u in urls)
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s</urlset>\n' % entries)
    write("robots.txt", "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE["baseUrl"])


def build_feed():
    items = ""
    for e in sorted(CHANGELOG, key=lambda x: x["date"], reverse=True):
        d = datetime.date.fromisoformat(e["date"])
        pub = d.strftime("%a, %d %b %Y 00:00:00 +0000")
        items += "<item><title>%s</title><link>%s/changelog</link><guid isPermaLink=\"false\">%s-%s</guid><pubDate>%s</pubDate><description>%s</description></item>\n" % (
            esc(e["text"]), SITE["baseUrl"], e["date"], hashlib.md5(e["text"].encode("utf-8")).hexdigest()[:8], pub, esc(e["text"]))
    feed = '<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>%s: changelog</title><link>%s/</link><description>What changed on %s.</description>\n%s</channel></rss>\n' % (
        esc(SITE["title"]), SITE["baseUrl"], esc(SITE["title"]), items)
    write("feed.xml", feed)


def main():
    build_index()
    for i, law in enumerate(LAWS):
        build_law(i, law)
    build_rubric()
    build_review()
    build_changelog()
    build_about()
    build_guide_pages()
    build_situation_finder()
    build_claim_checker()
    build_room()
    build_checklist()
    build_brief()
    build_data_js()
    build_search_index()
    build_feed()
    build_methodology()
    build_sample_size()
    build_cases()
    build_walkthrough()
    build_templates()
    build_intent_pages()
    build_privacy()
    build_seo()
    build_security()
    import test_claim_checker
    if test_claim_checker.main([], quiet=True):  # fail the build if the claim checker rules regress
        raise SystemExit("claim checker tests failed (python3 build/test_claim_checker.py for details)")
    print("built: %d patterns, %d pages" % (len(LAWS), len(list(ROOT.glob("*.html"))) + len(LAWS)))


if __name__ == "__main__":
    main()
