# -*- coding: utf-8 -*-
"""Build data.json for the internship site from meta.py + summaries + synthesized content."""
import json, re, os, html
import markdown

from pathlib import Path as _P
BASE = str(_P(__file__).resolve().parent)
SUMM = str(_P(BASE) / "summaries")
if not os.path.isdir(SUMM):
    raise SystemExit(f"summaries directory not found: {SUMM}")
exec(open(f"{BASE}/meta.py", encoding="utf-8").read())

REF = {
 "tene2011": "טנא 2011", "kochavi2018": "כוכבי 2018", "peraui2013": "פראוי 2013",
 "greenwald2009": "גרינולד ומטיחס 2009", "tauber": "טאובר", "sapiryogev": "ספיר-יוגב 2016",
 "gantz2016": "גנץ 2016", "playbook": "הספר הראשון על טיפול במשחק", "miller": "הפגישה הראשונה (Miller)",
 "italy2019": "איטלי 2019", "dorhaim2018": "דור-חיים 2018", "englert": "אנגלרט",
 "alon2023": "אלון ועמיתיו 2023", "tene_sped": "טנא, מעבר לחנ\"מ", "ravid2024": "ראביד-חיון ובן ריי 2024",
 "ostrovil1987": "אוסטרוויל 1987", "barakstein2014": "ברק שטיין 2014", "gantz2021": "גנץ 2021",
 "greenwald2012": "גרינולד 2012", "aron": "ארון", "bahat": "בהט", "kellner2000": "קלנר 2000",
 "dorhaim2013": "דור-חיים 2013", "gaon2021": "גאון-הרשקו 2021", "yablon2017": "יבלון 2017",
 "luria2011": "לוריא ועמיתיו 2011", "nutkevitch2003": "נוטקביץ' 2003", "sharel2014": "שראל 2014",
 "mop2020": "בית ספר כארגון מורכב מסתגל", "turi_contract": "תורי-מגדסי, חוזה עם המנהל",
 "turi_unconscious": "תורי-מגדסי, הלא מודע", "forest2014": "לראות את היער 2014",
 "reflection": "מסמך הרפלקציה על הכלה", "tlv_smallclasses": "הכיתות הקטנות 2010",
 "sped_multi": "עבודה רב-מקצועית בחנ\"מ", "manor2004": "מנור-בנימיני 2004",
 "benrey2016": "בן ריי וכנפי בליי 2016", "binyamini1984": "בנימיני 1984", "rodded2017": "רודד ועמיתיו 2017",
 "kachergin2012": "קצ'רגין 2012", "yablon2019": "יבלון 2019", "bion": "היכרות עם ביון",
 "theorists": "קוהוט, ויניקוט, בולבי", "mor2006": "מור 2006", "nutkevitch2025": "Nutkevitch 2025",
 "menzies": "Menzies Lyth 1960", "armstrong": "Armstrong", "fuchs": "המפה של פוקס",
 "rubric": "המחוון המערכתי", "psa_map": "מפת המושגים הפסיכואנליטית-מערכתית",
 "cohen_parenting": "כהן, טיפול בהורות", "corona2020": "מצפן הקורונה 2020",
 "outline_elem": "ליבת העבודה ביסודי", "outline_sec": "ליבת העבודה בעל-יסודי", "outline_gan": "מודל העבודה בגנים",
}
ids = {i["id"] for i in ITEMS}
assert set(REF) == ids, (set(REF) ^ ids)

LIST_RE = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+")

def normalize_md(text):
    """Make agent-written markdown safe for python-markdown: 4-space nesting (from an indent stack),
    blank lines before lists/tables."""
    out = []
    prev = ""
    stack = []  # indents of the list levels currently open
    for line in text.split("\n"):
        m = LIST_RE.match(line)
        if m:
            ind = len(m.group(1).expandtabs(4))
            while stack and ind < stack[-1]:
                stack.pop()
            if not stack or ind > stack[-1]:
                stack.append(ind)
            level = len(stack) - 1
            line = "    " * level + line.lstrip()
            prev_is_list = bool(LIST_RE.match(prev)) or (prev.startswith("    ") and prev.strip())
            if prev.strip() and not prev_is_list and level == 0:
                out.append("")
            pm = LIST_RE.match(prev)
            if pm and len(pm.group(1)) == len("    " * level) and (pm.group(2)[0].isdigit() != m.group(2)[0].isdigit()):
                out.append("")  # list type switches (1. -> -): start a new list
        elif line.lstrip().startswith("|"):
            stack = []
            line = line.strip()
            if prev.strip() and not prev.strip().startswith("|"):
                out.append("")
        else:
            if line.strip() and not line[0].isspace():
                stack = []
            elif line.strip() and stack:
                # continuation text of a list item: indent to its level's content column
                line = "    " * len(stack) + line.lstrip()
            if line.strip() and prev.strip().startswith("|") and not line.strip().startswith("|"):
                out.append("")
        out.append(line)
        prev = line
    return "\n".join(out)

MD = markdown.Markdown(extensions=["tables", "sane_lists"])

def md(text):
    MD.reset()
    h = MD.convert(normalize_md(text.strip()))
    # wrap tables for horizontal scroll on phones
    h = h.replace("<table>", '<div class="tablewrap"><table>').replace("</table>", "</table></div>")
    return h

def refs_to_links(h):
    def rep(m):
        i = m.group(1)
        if i not in REF:
            return m.group(0)
        return f'<a class="ref" href="#i-{i}" data-ref="{i}">{html.escape(REF[i])}</a>'
    h = re.sub(r"\[\[([a-z0-9_]+)\]\]", rep, h)
    return re.sub(r'(</a>)\s+(<a class="ref")', r'\1, \2', h)

def plain(h):
    t = re.sub(r"<[^>]+>", "", h)
    return html.unescape(re.sub(r"\s+", " ", t)).strip()

SEC_KEYS = {
    "תקציר": "abstract", "רעיונות מרכזיים": "ideas", "מושגי מפתח": "concepts",
    "מודלים, שלבים, טבלאות ורשימות": "models", "יישום למתמחה": "practice",
    "שאלות לחשיבה/הדרכה": "questions", "ציטוטים בולטים": "quotes", "הערות": "notes",
    "תוכן עניינים": "toc",
}

def parse_summary(path):
    txt = open(path, encoding="utf-8").read().replace("\r", "")
    lines = txt.split("\n")
    title = lines[0].lstrip("# ").strip()
    body = "\n".join(lines[1:])
    parts = re.split(r"^## ", body, flags=re.M)
    meta_md = parts[0]
    secs = {}
    for p in parts[1:]:
        head, _, rest = p.partition("\n")
        head = re.sub(r"\s*\(.*$", "", head).strip()
        key = SEC_KEYS.get(head)
        if not key:
            raise ValueError(f"unknown section {head!r} in {path}")
        secs[key] = md(rest)
    meta = {}
    for m in re.finditer(r"^- \*\*([^*]+)\*\*:?\s*(.*)$", meta_md, flags=re.M):
        meta[m.group(1).strip().rstrip(":")] = m.group(2).strip()
    secs.pop("notes", None)
    return dict(srcTitle=title, secs=secs,
                level=plain(md(meta.get("רמה מומלצת", ""))), stype=plain(md(meta.get("סוג", ""))))

FILES = json.load(open(f"{BASE}/files_manifest.json", encoding="utf-8"))
URL_LABELS = json.load(open(f"{BASE}/url_labels.json", encoding="utf-8"))
items = []
for it in ITEMS:
    d = {k: it.get(k) for k in ("id", "title", "authors", "year", "cite", "url", "kind", "desc")}
    if it.get("url"):
        d["urlLabel"] = it.get("urlLabel") or URL_LABELS.get(it["id"]) or ("המאמר באתר פסיכולוגיה עברית" if "hebpsy.net" in it["url"] else "קישור למקור")
    if it["id"] in FILES:
        d["file"] = FILES[it["id"]]
    d["placements"] = [list(p) for p in it["placements"]]
    d["extra"] = bool(it.get("extra"))
    d["ref"] = REF[it["id"]]
    d["inFolder"] = bool(it["file"])
    if it["file"]:
        s = parse_summary(f"{SUMM}/{it['file']}.md")
        d.update(s)
        ab = plain(s["secs"]["abstract"])
        d["tldr"] = ab if len(ab) < 260 else ab[:250].rsplit(" ", 1)[0] + "…"
        d["search"] = plain(" ".join(s["secs"].get(k, "") for k in ("abstract", "ideas", "concepts")))
    else:
        d["tldr"] = it.get("desc", "")
        d["search"] = it.get("desc", "")
    items.append(d)

# ---------- tools ----------
tools = []
t_txt = open(f"{BASE}/content/tools.md", encoding="utf-8").read()
for block in re.split(r"^## TOOL: ", t_txt, flags=re.M)[1:]:
    head, _, rest = block.partition("\n")
    tid, _, ttitle = head.partition("|")
    hdr, _, body = rest.partition("\n---\n")
    f = dict(re.findall(r"^(DOMAIN|SOURCES|WHEN):\s*(.*)$", hdr, flags=re.M))
    srcs = [s.strip() for s in f["SOURCES"].split(",") if s.strip()]
    for s in srcs:
        assert s in ids, (tid, s)
    tools.append(dict(id=tid.strip(), title=ttitle.strip(), domain=f["DOMAIN"].strip(), sources=srcs,
                      when=f["WHEN"].strip(), html=refs_to_links(md(body))))

# ---------- glossary ----------
gloss = []
g_txt = open(f"{BASE}/content/glossary.md", encoding="utf-8").read()
for block in re.split(r"^### ", g_txt, flags=re.M)[1:]:
    head, _, rest = block.partition("\n")
    he, _, en = head.partition("|")
    f = dict(re.findall(r"^(DOMAINS|SOURCES):\s*(.*)$", rest, flags=re.M))
    body = re.sub(r"^(DOMAINS|SOURCES):.*$", "", rest, flags=re.M).strip()
    srcs = [s.strip() for s in f.get("SOURCES", "").split(",") if s.strip()]
    bad = [x for x in srcs if x not in ids]
    assert not bad, (he, bad)
    gloss.append(dict(term=he.strip(), en=en.strip(), domains=[x.strip() for x in f.get("DOMAINS", "").split(",") if x.strip()],
                      sources=srcs, html=refs_to_links(md(body))))

# ---------- domains ----------
domains_text = {}
d_txt = open(f"{BASE}/content/domains.md", encoding="utf-8").read()
for block in re.split(r"^## DOMAIN: ", d_txt, flags=re.M)[1:]:
    head, _, rest = block.partition("\n")
    domains_text[head.strip()] = refs_to_links(md(rest))
for dd in DOMAINS:
    assert dd["id"] in domains_text, dd["id"]

data = dict(stages=STAGES, domains=DOMAINS, items=items, tools=tools, glossary=gloss,
            domainText=domains_text, resources=RESOURCES, openCells=[list(c) for c in OPEN_CELLS],
            outlines=OUTLINES, kitFile=FILES["kit"])
s = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
s = s.replace("<", "\\u003c")
open(f"{BASE}/data.json", "w", encoding="utf-8").write(s)
print("items", len(items), "tools", len(tools), "glossary", len(gloss), "bytes", len(s.encode()))
unresolved = re.findall(r"\[\[([a-z0-9_]+)\]\]", s)
assert not unresolved, ("unresolved refs", unresolved[:5])
broken_lists = re.findall(r"<li>[^<]*\\n\s*[-*+] ", s)
assert not broken_lists, ("lists rendered as text", len(broken_lists), broken_lists[:2])
print("checks: refs ok, lists ok")

# assemble the page: <build dir>/kit.html (artifact body) and ../index.html (standalone site)
_tpl = os.path.join(BASE, "template.html")
if os.path.exists(_tpl):
    body = open(_tpl, encoding="utf-8").read().replace("/*__DATA__*/", s)
    open(os.path.join(BASE, "kit.html"), "w", encoding="utf-8").write(body)
    skel = ('<!doctype html>\n<html lang="he" dir="rtl"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
            '<style>:root{color-scheme:light;padding-top:env(safe-area-inset-top);padding-bottom:env(safe-area-inset-bottom)}'
            'body{margin:0;font:14px system-ui}img{max-width:100%}[hidden]{display:none!important}</style></head><body>\n')
    open(os.path.join(BASE, "..", "index.html"), "w", encoding="utf-8").write(skel + body + "\n</body></html>\n")
    print("wrote kit.html and ../index.html")
