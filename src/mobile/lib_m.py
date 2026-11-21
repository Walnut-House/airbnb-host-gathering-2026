"""lib_m — phone edition of the 상세판/요약판 decks: 1080 px wide, height fitted to the content. Spec: ../MOBILE.md

Every component takes a y (top of its block) and RETURNS the y just below it, so a slide is
written top to bottom:   y = header(d, K, title, sub);  y = section(d, y, "…");  y = numlist(d, y, [...])
Text is pre-wrapped here with real font metrics (fontmetrics.py), so every block's height is known
before rendering; build() then sizes the canvas to the content (min 1350 = 4:5, no max) and anchors the
footer to the bottom. One landscape slide = one mobile slide, same file name.
"""
import json, subprocess, sys, os, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fontmetrics as FM

T = os.path.expanduser("~/Library/Application Support/Tesseract/bin/tsrct")
FONT = "/System/Library/Fonts/AppleSDGothicNeo.ttc"

# ---------- canvas & grid ----------
W = 1080                    # width is fixed; height is computed per slide in build()
MIN_H = 1350                # minimum height (4:5) so short slides aren't stubby; no maximum
H = 99999                   # "taller than any slide" (used for the background before sizing)
X = 72                      # side margin (both sides)
CW = W - 2 * X              # 936 content width
IND = 60                    # number/dot column -> text indent inside lists & timelines
FOOT_GAP = 72               # last content line -> footer text top
FOOT_SLOT = 38              # footer line slot
BOTTOM_MARGIN = 64          # footer slot -> canvas bottom
NOFOOT_MARGIN = 96          # content -> canvas bottom on a slide without footer (cover)

# ---------- colours (identical to landscape lib.py) ----------
BG = (0.972, 0.965, 0.950); INK = (0.11, 0.11, 0.12); SEC = (0.36, 0.35, 0.34); MUT = (0.42, 0.41, 0.40)
LINE = (0.86, 0.85, 0.83); CARD = (1, 1, 1); ACC = (0.80, 0.24, 0.25); ACC_SOFT = (0.97, 0.90, 0.89)
GREY_BAR = (0.70, 0.68, 0.65)

# ---------- type scale: name -> (size, style, line-slot height, colour) ----------
TS = {
    "kicker":  (30, "SemiBold", 44, ACC),
    "title":   (64, "Bold",     80, INK),
    "sub":     (34, "Regular",  50, SEC),
    "head":    (42, "SemiBold", 58, INK),   # section / column head (one step above item titles)
    "body":    (38, "Regular",  56, INK),   # main text, list item (1-line items)
    "item":    (38, "Medium",   56, INK),   # list item title when it has a detail line
    "label":   (38, "SemiBold", 56, INK),   # card/table row label
    "detail":  (36, "Regular",  52, SEC),   # second line of an item, step body, card use-line (grey)
    "note":    (34, "Regular",  48, SEC),   # caveat / note, table legend
    "take":    (36, "SemiBold", 54, INK),   # takeaway line
    "num":     (40, "Bold",     56, INK),   # numbers inside rows/tables
    "card":    (36, "Regular",  52, INK),   # card body lines, bar labels, inline step bodies
    "foot":    (28, "Regular",  38, MUT),
}
HERO, GRID = 120, 96        # big-number sizes (bigstat)
GAP_S, GAP_M, GAP_L = 20, 40, 64   # gaps: within block / between blocks / between sections
BAR_MIN = 48                # shortest visible bar, so a tiny value never reads as a square/checkbox
SPINE = (0.76, 0.74, 0.71)          # timeline connector (a little darker than LINE)
FOOTER = "호스트, 우리가 만나다 · 2026 대한공유숙박호스트협회 연말 게더링"


class Doc:
    def __init__(s, name=""):
        s.layers = []; s.n = 0; s.name = name; s.warn = []; s.bottom = 0
        s.page = None         # landscape page number (run() reads it from the landscape deck); None = no footer
        s.height = None       # set by build()
        s.ind = IND           # number column -> text indent for every list on this slide (build() widens it
                              # for 2-digit / range numbers so all lists on a slide share one indent)
        s.num_w = 0           # widest list number drawn (measured in build's first pass)
        s.after_header = None # y returned by header(): a list starting there reuses the header rule
        s.content_top = None
        s._stat = None        # last bigstat drawn alone in its row (for automatic 2-up pairing)

    def _id(s): s.n += 1; return s.n

    def rect(s, x, y, w, h, c, r=0, stroke=None, flow=True):
        L = {"type": "Rect", "id": s._id(), "name": f"rect{s.n}", "blendMode": "normal",
             "activeRange": {"start": 0, "duration": 3000},
             "transform": {"anchorPoint": [0, 0], "position": [x, y], "scale": [100, 100], "rotation": 0, "opacity": 100},
             "rect": {"size": [w, h], "fillColor": [*c, 1], "roundness": r}}
        if stroke: L["rect"].update(strokeEnabled=True, strokeColor=[*stroke, 1], strokeWidth=2)
        L["_flow"] = flow
        s.layers.append(L)
        if flow and h < 5000 and y >= 0: s.bottom = max(s.bottom, y + h)

    def text(s, x, y, w, h, t, size, style="Regular", c=INK, just="left", lead=None, track=0, flow=True):
        """Raw box text, top-aligned. Prefer tx() which wraps and measures."""
        d = {"text": t, "fontFamily": "Apple SD Gothic Neo", "fontStyle": style, "fontSize": size, "fillColor": [*c, 1],
             "strokeWidth": 0, "justification": just, "boxText": True, "boxSize": [w, h], "boxPosition": [0, 0],
             "tracking": track, "verticalAlign": "top"}
        if lead: d["leading"] = lead
        s.layers.append({"type": "Text", "id": s._id(), "name": t.replace("\n", " ")[:24], "blendMode": "normal",
                         "activeRange": {"start": 0, "duration": 3000}, "_flow": flow,
                         "transform": {"anchorPoint": [0, 0], "position": [x, y], "scale": [100, 100], "rotation": 0, "opacity": 100},
                         "sourceText": d})


# ---------- text wrapping with real metrics ----------
# Korean phrase-aware line breaker (cost-minimising, Knuth-Plass style over space-separated segments).
#  * breaks only at U+0020 spaces — never at U+00A0 (no-break space glues a phrase);
#  * a spaced " · " separator starts the next line ("· 폐기물"), never ends one; "—" ends its line;
#  * breaking before a short particle/auxiliary token (<= 2 Hangul syllables: 수, 것, 두면, 등에, 원, 개) …)
#    or after a 1-syllable word (그, 전, 약, 내) or between a number and its unit (10만 원, 수천 개, 다섯 가지)
#    or inside a short 「…」 / "…" / (…) span is (near-)forbidden — an extra line is cheaper;
#  * prefers breaks after a comma or around "—" / " · " when they fall in the last 40 % of the line;
#  * no orphan: the last line is never a single short word (< 30 % width) unless unavoidable;
#  * balance=True evens out the lines; balance="clause" (takeaways) fills lines and breaks at commas.
NBSP = " "
_LINE_COST = 1e6            # every extra line
_P_HARD = 3e6               # "forbidden unless unavoidable" (more than an extra line)
_P_SHORT2 = 6e3             # before a generic 2-syllable word (주민 / 동의) — avoid unless lines get very uneven
_P_ORPHAN = 2e6             # last line = one short word
_P_DOT = 1.5e4              # after a tight "·" inside a word list (얼리버드·장박·… / 신규 숙소)
_P_ITEM = 2e4               # at a space inside one item of a tight "·" list (…·신규 / 숙소·…)
_P_CHAR = 1e8               # inside an over-long token, between characters
_AUX2 = set("두면 두고 두기 둔다 등에 등을 등은 등이 등의 것은 것을 것이 것도 수도 수는 거나 거다 있다 있음 있어 없다 없음 "
            "않다 않음 말기 말고 말라 본다 보기 보고 된다 됐다 돼요 한다 했다 하기 하고 해요 해야 같은 위해 때는 때도 때만 "
            "정도 이상 이하 미만 이내 동안 전후 대비 만큼 뿐인 뿐이다 씩은".split())
_UNIT = ("원", "년", "개", "명", "곳", "번", "월", "일", "박", "분", "시간", "층", "평", "건", "회", "배", "쪽", "차", "살",
         "주", "가지", "단계", "만", "천", "억", "%", "달", "초", "세대", "가구", "호", "장", "권", "대", "채", "인", "축", "줄")
_NUMWORD = {"한", "두", "세", "네", "다섯", "여섯", "일곱", "여덟", "아홉", "열", "스무", "서른", "마흔", "몇", "수십", "수백",
            "수천", "수만", "수억", "약"}
_OPEN = {"「": "」", "『": "』", "(": ")", "“": "”", "‘": "’", "[": "]"}
_HANG = re.compile(r"[가-힣]")
_P_AUXV = 5e4               # verb + auxiliary verb (쓰지 / 말고, 되어 / 있으면, 해야 / 하는지, 풀어 / 드리겠다)
_AUXV = (("지", ("않", "못", "말")), ("고", ("있", "싶")), ("야", ("하", "한", "할", "했", "돼", "된", "될")),
         (("어", "아", "워", "해", "줘", "와", "봐", "려", "내", "써", "켜", "둬"),
          ("주", "줘", "준", "줄", "드리", "드릴", "드려", "두", "둔", "둬", "놓", "버리", "있", "보", "봐", "본", "볼")))

def _short_spans(par):
    """Char ranges (start, end) of 「…」 / "…" / (…) spans of <= 20 chars: no break inside."""
    spans, stack, dq = [], [], None
    for i, ch in enumerate(par):
        if ch in _OPEN: stack.append((ch, i))
        elif stack and ch == _OPEN[stack[-1][0]]:
            _, s = stack.pop(); spans.append((s, i))
        elif ch == '"':
            if dq is None: dq = i
            else: spans.append((dq, i)); dq = None
    return [(s, e) for s, e in spans if e - s - 1 <= 20]

def _segments(par):
    """Split a paragraph into segments with the break opportunity BEFORE each one.
    Returns [(text, sep, kind, pos)]: sep = text joining it to the previous segment when not broken,
    kind = "" | "sep" (before " · ") | "dot" | "char", pos = char offset of the break in par."""
    toks, i, n = [], 0, len(par)
    while i < n:                                   # tokens split on runs of U+0020 (keep the run as sep)
        j = i
        while j < n and par[j] == " ": j += 1
        sep = par[i:j]; k = j
        while k < n and par[k] != " ": k += 1
        if k > j: toks.append([par[j:k], sep, "", j])
        elif sep and toks: toks[-1][0] += ""        # trailing spaces dropped
        i = k
    segs = []
    for t in toks:
        txt = t[0]
        if txt in ("—", "–") and segs:              # dash stays at the end of the previous line
            segs[-1][0] += t[1] + txt; continue
        if txt == "·" and segs:                     # spaced separator: starts the next line
            t[2] = "sep"; segs.append(t); continue
        if segs and segs[-1][0] == "·" and segs[-1][2] == "sep":   # "·" + next word = one segment
            segs[-1][0] += t[1] + txt; continue
        segs.append(t)
    if segs: segs[0][1] = ""
    return [tuple(s) + (s[0],) for s in segs]     # + the whole space-delimited word

def _split_long(seg, w, size, style, track):
    """An over-long segment: break after tight "·" first, then by character (never next to a NBSP)."""
    txt, sep, kind, pos, word = seg
    if "·" not in txt.strip("·") and FM.width(txt, size, style, track) <= w: return [seg]
    parts, buf, start = [], "", pos
    for ci, ch in enumerate(txt):
        buf += ch
        if ch == "·" and 0 < ci < len(txt) - 1 and txt[ci - 1] not in " " + NBSP and txt[ci + 1] not in " " + NBSP:
            parts.append(buf); buf = ""
    if buf: parts.append(buf)
    out, off = [], pos
    for pi, p in enumerate(parts):
        k = (sep, kind) if pi == 0 else ("", "dot")
        if FM.width(p, size, style, track) <= w: out.append((p, k[0], k[1], off, word))
        else:
            buf, first = "", True
            for ci, ch in enumerate(p):
                nxt = p[ci + 1] if ci + 1 < len(p) else ""
                if buf and FM.width(buf + ch, size, style, track) > w and ch != NBSP and buf[-1] != NBSP:
                    out.append((buf, *(k if first else ("", "char")), off, word)); first = False; off += len(buf); buf = ""
                buf += ch
            if buf: out.append((buf, *(k if first else ("", "char")), off, word))
        off += len(p)
    return out

def _hang(s): return len(_HANG.findall(s))

def _pen(a, b, kind, spans, pos, wa=None, wb=None):
    """Penalty for breaking between segment text a and segment b (b's break kind/offset)."""
    if kind == "dot": return _P_DOT
    if kind == "char": return _P_CHAR
    p = 0
    for s, e in spans:
        if s < pos <= e: p += _P_HARD; break
    if kind == "sep": return p                      # before " · ": a natural break
    la = a.split(NBSP)[-1]; ca = re.sub(r"[^\w]", "", la)
    cb_full = re.sub(r"[^\w]", "", b.split(NBSP)[0])
    if not (a.endswith(",") or a.endswith("—") or a.endswith("–")):
        if len(ca) <= 1: p += _P_HARD               # after a 1-syllable word (그 / 나라에, 약 / 8시간)
        num = re.search(r"\d[\d,.~]*(만|천|억|백)*$", ca) or ca in _NUMWORD
        if num and cb_full.startswith(_UNIT): p += _P_HARD    # number + unit
    wa, wb = wa or a, wb or b
    if "·" in wa.strip("·") and "·" in wb.strip("·") and not wa.endswith(("·", ",")):
        p += _P_ITEM                                # 주간·…·신규 / 숙소·환불: splits the item 「신규 숙소」
    if cb_full in _NUMWORD: return p                # a numeral is a fine line start (다섯 단계에)
    for ends, starts in _AUXV:
        if ca.endswith(ends) and cb_full.startswith(starts) and _hang(ca) >= 2: p += _P_AUXV; break
    clause_end = a.endswith((",", "—", "–", ")", "」", "』", '"', "”"))   # a new phrase starts after these
    if cb_full and not re.search(r"[0-9A-Za-z]", cb_full):
        h = _hang(cb_full)
        if h == len(cb_full) and h <= 1: p += _P_HARD
        elif h == len(cb_full) and h == 2 and not clause_end: p += _P_HARD if cb_full in _AUX2 else _P_SHORT2
        elif cb_full in _AUX2: p += _P_HARD
    return p

def _layout(segs, w, size, style, track, mode, spans):
    n = len(segs)
    S, bounds = "", []
    for i, (t, sep, _, _, _) in enumerate(segs):
        if i: S += sep
        bounds.append((len(S), len(S) + len(t))); S += t
    cum = [0.0]
    for ch in S: cum.append(cum[-1] + FM.width(ch, size, style, track))
    def wd(i, j): return cum[bounds[j - 1][1]] - cum[bounds[i][0]]
    pens = [0] * (n + 1)
    for k in range(1, n):
        pens[k] = _pen(segs[k - 1][0], segs[k][0], segs[k][2], spans, segs[k][3], segs[k - 1][4], segs[k][4])
    best = [0.0] + [float("inf")] * n; prev = [0] * (n + 1)
    for j in range(1, n + 1):
        last = (j == n)
        for i in range(j - 1, -1, -1):
            L = wd(i, j)
            if L > w and j - i > 1: break
            slack = max(0.0, (w - L) / w)
            if mode is True: bad = slack * slack * 1e4 if not (last and i == 0) else 0
            else: bad = 0 if last else slack * slack * 1e4
            c = best[i] + _LINE_COST + bad + (pens[j] if not last else 0)
            if not last:                       # preferred break: comma / dash / before " · " late in the line
                a = segs[j - 1][0]
                if a.endswith(",") or a.endswith("—") or a.endswith("–") or segs[j][2] == "sep":
                    if mode == "clause":
                        if L >= 0.45 * w: c -= 2e4
                    elif L >= 0.6 * w: c -= 4e3
                    elif L >= 0.3 * w: c -= 3e3
            if not last and j - i == 1 and L < 0.35 * w and " " not in segs[i][0]:
                c += _P_ORPHAN / 2                 # a lone short word on a first/middle line
            if last and i > 0:
                if j - i == 1 and L < 0.35 * w: c += _P_ORPHAN
                elif mode == "clause" and L < 0.3 * w: c += 5e3
            if c < best[j]: best[j] = c; prev[j] = i
    cuts, j = [], n
    while j > 0: cuts.append((prev[j], j)); j = prev[j]
    lines = []
    for i, j in reversed(cuts): lines.append(S[bounds[i][0]:bounds[j - 1][1]])
    return lines

def wrap(text, w, size, style="Regular", track=0, balance=True, max_lines=None):
    """Return list of lines. '\\n' forces a break. balance=True evens out the lines of each paragraph,
    "clause" fills lines and breaks at commas (takeaways), False fills lines. max_lines: if the
    phrase rules push a paragraph past it, rewrap preferring fewer lines over the phrase rules."""
    global _LINE_COST
    w = w * 0.985
    out = []
    for par in text.split("\n"):
        segs = _segments(par)
        if not segs: out.append(""); continue
        segs = [s for sg in segs for s in _split_long(sg, w, size, style, track)]
        spans = _short_spans(par)
        lines = _layout(segs, w, size, style, track, balance, spans)
        if max_lines and len(lines) > max_lines:
            old = _LINE_COST; _LINE_COST = 1e9
            try: lines = _layout(segs, w, size, style, track, balance, spans)
            finally: _LINE_COST = old
        out += lines
    return out

_MARK = re.compile(r"^([①-⑳❶-❿]|\d{1,2}[.)]|[•·\-–]) ")

def tx(d, x, y, w, text, kind="body", size=None, style=None, c=None, lead=None, just="left", track=0,
       balance=True, max_lines=None):
    """Wrapped text block. Occupies n*lead px from y (each line optically centred in its slot).
    A paragraph starting with a mark (①, "1)", "•") gets a hanging indent: wrapped lines sit under
    its text, not under the mark. Returns y below the block."""
    s0, st0, l0, c0 = TS[kind]
    size = size or s0; style = style or st0; lead = lead or (l0 if size == s0 else round(size * 1.45)); c = c or c0
    pars = text.split("\n")
    if just == "left" and any(_MARK.match(p) for p in pars):
        if len(pars) > 1:                           # mixed block: lay out paragraph by paragraph
            for p in pars: y = tx(d, x, y, w, p, kind, size, style, c, lead, just, track, balance)
            return y
        m = _MARK.match(text); mark = m.group(1); mw = FM.width(mark + " ", size, style, track)
        if FM.width(text, size, style, track) > w * 0.985:   # wraps → hang the body under its own text
            off = lead / 2 - 0.58 * size
            d.text(x, y + off, mw + 8, lead + size, mark, size, style, c, lead=lead, track=track)
            return tx(d, x + mw, y, w - mw, text[m.end():], kind, size, style, c, lead, just, track, balance, max_lines)
    lines = wrap(text, w, size, style, track, balance, max_lines)
    _check_lines(d, lines, text, w, size, style, track)
    if max_lines and len(lines) > max_lines:
        d.warn.append(f"{kind} has {len(lines)} lines (max {max_lines}): {text[:30]!r}")
    n = len(lines)
    off = lead / 2 - 0.58 * size          # optical centring of Hangul glyphs in the slot
    d.text(x, y + off, w, n * lead + size, "\n".join(lines), size, style, c, just=just, lead=lead, track=track)
    d.bottom = max(d.bottom, y + n * lead)
    return y + n * lead

def _check_lines(d, lines, text, w, size, style, track):
    """WARNs: a line ending with '·', a line starting with whitespace (incl. NBSP), and an orphan —
    a single short word (< 30 % of the width) alone on a line of a wrapped paragraph."""
    pars = text.split("\n")
    for ln in lines:
        if re.search(r"\s·$", ln.rstrip()): d.warn.append(f"line ends with ' ·': {ln!r}")
        if ln[:1].isspace() or ln[:1] == NBSP: d.warn.append(f"line starts with whitespace: {ln!r}")
    # orphan check per paragraph: a paragraph of >1 line whose some line is one short word
    i = 0
    for par in pars:
        segs = _segments(par)
        if not segs: i += 1; continue
        # count lines belonging to this paragraph by consuming text
        j, acc = i, ""
        target = re.sub(r"\s", "", par)
        while j < len(lines) and len(re.sub(r"\s", "", acc)) < len(target):
            acc += lines[j]; j += 1
        plines = lines[i:j]; i = j
        if len(plines) > 1:
            for ln in plines:
                if " " not in ln.strip() and FM.width(ln, size, style, track) < 0.3 * w:
                    d.warn.append(f"orphan line {ln!r} in {par[:24]!r}")

def nlines(text, w, kind="body"):
    s, st, _, _ = TS[kind]; return len(wrap(text, w, s, st))

def rule(d, y, x=X, w=CW, c=LINE):
    d.rect(x, y, w, 2, c); return y + 2


# ---------- page frame ----------
def footer(d, H_):
    """Footer anchored to the computed canvas height: deck line left, landscape page right ("45쪽")."""
    if d.page is None: return
    y = H_ - BOTTOM_MARGIN - FOOT_SLOT
    d.text(X, y, CW - 200, 40, FOOTER, 28, "Regular", MUT, lead=FOOT_SLOT, flow=False)
    d.text(W - X - 200, y, 200, 40, f"{d.page}쪽", 28, "Regular", MUT, just="right", lead=FOOT_SLOT, flow=False)

def header(d, kicker, title, sub=None, page=None):
    """Kicker, title (<=3 lines), optional subtitle, hairline. The footer page comes from run()
    (landscape lookup); pass page=N only if the landscape JSON is missing. Returns content top y."""
    if page is not None: d.page = page
    s_, st_, l_, c_ = TS["kicker"]
    d.text(X, 96 + l_ / 2 - 0.58 * s_, CW, l_, kicker, s_, st_, c_, lead=l_); y = 96 + l_
    y = tx(d, X, y + 12, CW, title, "title", max_lines=3)
    if sub: y = tx(d, X, y + 10, CW, sub, "sub", max_lines=3)
    y += 32
    d.rect(X, y, CW, 2, LINE)
    d.content_top = y + 2
    d.after_header = y + 2 + 44
    return y + 2 + 44

def section(d, y, title, gap=GAP_L, first=False, rule=False):
    """Section/column head (42 SemiBold INK). first=True for the first block under the header.
    rule=True draws a hairline above the head (use where the landscape slide had a band rule
    between the two blocks); skipped automatically if the previous block already ended on a rule."""
    if not first:
        if rule and getattr(d, "rule_end", None) != y:
            y += gap // 2; d.rect(X, y, CW, 2, LINE); y += 2 + gap // 2
        else:
            y += gap
    return tx(d, X, y, CW, title, "head") + 18


# ---------- lists ----------
def list_top(d, y):
    """A ruled list/cards block that starts straight under the header (no section head) reuses the
    header hairline as its top rule: returns (y, draw_top_rule)."""
    if d.after_header is not None and y == d.after_header and d.content_top is not None:
        return d.content_top - 2, False
    return y, True

def num_mark(d, x, y, label, red=False):
    """List number (38 SemiBold SEC, ACC if it is the slide's one red) in the number column at x, row top y.
    Records its width so build() can size the slide's shared indent (d.ind) for 2-digit numbers."""
    s, st, lead, _ = TS["label"]
    label = str(label)
    d.num_w = max(d.num_w, FM.width(label, s, "SemiBold"))
    d.text(x, y + lead / 2 - 0.58 * s, max(d.ind, IND), lead, label, s, "SemiBold", ACC if red else SEC, lead=lead)

NUM_GAP = 36                # number right edge -> text, same for 1- and 2-digit numbers
def _ind_for(num_w):
    return max(IND, int(-(-(num_w + NUM_GAP) // 4) * 4))

def numlist(d, y, items, hi=None, start=1, x=X, w=CW, rules=True, nums=True, pad=22):
    """Numbered ruled list. items: str (1 line kind 'body'), or (title, detail) with detail str or
    list of str; a detail entry given as ("text","ink") renders as 36 INK (a key line under a grey label line).
    hi = index of the ONE red number (text stays INK). Returns y under the last rule."""
    ix = x + (d.ind if nums else 0); iw = w - (ix - x)
    top = True
    if rules: y, top = list_top(d, y)
    for i, it in enumerate(items):
        if rules and (i or top): d.rect(x, y, w, 2, LINE)
        yy = y + 2 + pad
        t, det = (it if isinstance(it, tuple) else (it, None))
        kind = "item" if det else "body"
        if nums: num_mark(d, x, yy, start + i, i == hi)
        yy = tx(d, ix, yy, iw, t, kind)
        if det:
            dets = det if isinstance(det, list) else [det]
            yy += 2
            for dl in dets:
                if isinstance(dl, tuple): yy = tx(d, ix, yy + 4, iw, dl[0], "card")
                else: yy = tx(d, ix, yy, iw, dl, "detail")
        y = yy + pad
    if rules: d.rect(x, y, w, 2, LINE); y += 2; d.rule_end = y
    return y

def vtimeline(d, y, steps, hi=None, x=X, w=CW, gap=36, inline=None):
    """Vertical timeline. steps: (label, body or None). Dot 24px on a vertical hairline, label
    '1 제목' 38 SemiBold, body 36 SEC under it. hi = index of the ONE outcome step (red dot).
    inline=N: compact form, body 36 SEC on the same line, starting N px right of the label column
    (use when every body is short — one line; 340 fits labels like "5 체크인 다음 날")."""
    s, st, lead, _ = TS["label"]
    dots = []
    for i, (lab, body) in enumerate(steps):
        dy = y + lead / 2 - 12
        dots.append(dy)
        if inline:
            yy = tx(d, x + IND, y, inline - 16, f"{i + 1} {lab}", "label")
            if body: yy = max(yy, tx(d, x + IND + inline, y, w - IND - inline, body, "card", c=SEC, lead=lead))
        else:
            yy = tx(d, x + IND, y, w - IND, f"{i + 1} {lab}", "label")
            if body: yy = tx(d, x + IND, yy + 4, w - IND, body, "detail")
        y = yy + gap
    for a, b in zip(dots, dots[1:]): d.rect(x + 11, a + 12, 2, b - a, SPINE)
    for i, dy in enumerate(dots): d.rect(x, dy, 24, 24, ACC if i == hi else INK, 12)
    return y - gap


# ---------- numbers ----------
STAT_HALF = 432             # (CW - 72) / 2: a big number this wide or narrower can sit 2 per row

def _bigstat(d, x, y, w, value, label, size, acc):
    if FM.width(value, size, "Bold", -10) > w: d.warn.append(f"bigstat {value!r} wider than {w}px at {size}")
    lead = round(size * 1.15)
    y = tx(d, x, y, w, value, "num", size=size, style="Bold", c=ACC if acc else INK, lead=lead, track=-10, balance=False)
    if label: y = tx(d, x, y + 6, w, label, "detail")
    return y

def _fits_half(value, label, size):
    return FM.width(value, size, "Bold", -10) <= STAT_HALF and (not label or
           len(wrap(label, STAT_HALF, *TS["detail"][:2])) <= 4)

def bigstat(d, x, y, w, value, label=None, size=HERO, acc=False):
    """Big number (HERO 120 / GRID 96), Bold, tracking -10, label 36 SEC under it. Numbers only.
    Two full-width bigstats in a row (nothing else drawn between, gap <= GAP_M + 8) that each fit 432 px
    are set side by side automatically (as in the landscape 2x2 grids); so is a full-width bigstat
    following the odd last item of a stats() grid."""
    p = d._stat
    if (p and x == X and w == CW and p["size"] == size and len(d.layers) == p["end"]
            and 0 <= y - p["bottom"] <= GAP_M + 8 and _fits_half(value, label, size)):
        cw = STAT_HALF
        d._stat = None
        if p["w"] != cw:                      # re-lay the previous full-width stat in the left half
            del d.layers[p["start"]:p["end"]]; d.bottom = p["bottom_before"]
            b1 = _bigstat(d, X, p["y"], cw, p["value"], p["label"], size, p["acc"])
        else: b1 = p["bottom"]
        b2 = _bigstat(d, X + CW - cw, p["y"], cw, value, label, size, acc)
        return max(b1, b2)
    start, bb = len(d.layers), d.bottom
    yb = _bigstat(d, x, y, w, value, label, size, acc)
    d._stat = None
    if x == X and w == CW and _fits_half(value, label, size):
        d._stat = dict(start=start, end=len(d.layers), y=y, bottom=yb, bottom_before=bb, w=w,
                       value=value, label=label, size=size, acc=acc)
    return yb

def stats(d, y, items, size=GRID, cols=2, gap=72):
    """Grid of big numbers. items: (value, label, acc). cols=2 default; cols=1 is overridden to 2 when
    every value fits 432 px (2 per row, 2x2 for 4, as in the landscape). Returns y."""
    if cols == 1 and len(items) > 1 and all(_fits_half(v, lab, size) for v, lab, _ in items): cols = 2
    cw = (CW - gap * (cols - 1)) / cols
    for r in range(0, len(items), cols):
        row = items[r:r + cols]; yb = y
        start, bb = len(d.layers), d.bottom
        for j, (v, lab, acc) in enumerate(row):
            yb = max(yb, _bigstat(d, X + j * (cw + gap), y, cw, v, lab, size, acc))
        d._stat = None
        if len(row) == 1 and cols == 2 and _fits_half(*row[0][:2], size):   # odd last item: a following
            v, lab, acc = row[0]                                         # bigstat may pair with it
            d._stat = dict(start=start, end=len(d.layers), y=y, bottom=yb, bottom_before=bb, w=cw,
                           value=v, label=lab, size=size, acc=acc)
        y = yb + GAP_M
    return y - GAP_M

def bars(d, y, rows, hi=None, maxv=None, label_w=None, x=X, w=CW, bar_h=44, gap=28):
    """Horizontal bars, full width. rows: (label, value, value_text).
    label_w=None -> label on its own line above each bar (bar from x); label_w=N -> label left (inline).
    Use the same maxv for all percentage bars on one slide. hi = the ONE red bar (and its value)."""
    maxv = maxv or max(r[1] for r in rows)
    vw = max(FM.width(r[2], 38, "Bold") for r in rows) + 20
    bx = x + (label_w or 0); span = x + w - vw - bx
    for i, (lab, v, vt) in enumerate(rows):
        col = ACC if i == hi else INK
        if label_w:
            tx(d, x, y + bar_h / 2 - 28, label_w - 16, lab, "card", lead=56)
        else:
            y = tx(d, x, y, w, lab, "card") + 6
        bw = max(BAR_MIN, span * v / maxv)
        d.rect(bx, y, bw, bar_h, ACC if i == hi else GREY_BAR)
        tx(d, bx + bw + 16, y + bar_h / 2 - 28, vw, vt, "num", size=38, c=col, balance=False)
        y += bar_h + gap
    return y - gap


# ---------- tables -> stacked cards ----------
def card(label, body=None, value=None, value_note=None, note=None, bar=None):
    """One table row as a stacked card. body: str, '\\n' = separate lines (36).
    value: number/amount shown right of the label (40 Bold). bar: 0..1 mini bar under the label."""
    return dict(label=label, body=body, value=value, value_note=value_note, note=note, bar=bar)

def cards(d, y, rows, hi=None, hi_value=True, pad=26, x=X, w=CW, label_w=None, keys=None):
    """Ruled stacked rows (portrait form of a table); one card per table row, fields in the landscape
    column order. Plain row: label (38 SemiBold) + value right-aligned (40 Bold) → body lines (36 INK)
    → note (34 SEC). Bar row (bar=0..1, for a table with a mini-bar column): label → bar (36 px, min BAR_MIN 48,
    GREY_BAR) with the value (38 Bold) at its end → body in grey (36 SEC).
    keys=("정책 · 전액 환불 마감 · 쓸 날짜",): the landscape column headers, in the landscape order, shown
    once as a legend row (34 SEC) above the first rule instead of repeating them in every row.
    hi = the ONE red row: its value/bar is red (or its label if it has no value)."""
    if keys:
        tx(d, x, y, w * 0.6 if len(keys) > 1 else w, keys[0], "note")
        if len(keys) > 1: tx(d, x + w * 0.4, y, w * 0.6, keys[1], "note", just="right")
        y += TS["note"][2] + 8
    top = True
    if not keys: y, top = list_top(d, y)
    rows = [r if isinstance(r, dict) else card(*r) for r in rows]
    span = None
    if any(r["bar"] is not None for r in rows):
        vmax = max(FM.width(r["value"] or "", 38, "Bold") for r in rows) + 20
        span = w - vmax
    for i, r in enumerate(rows):
        if i or top: d.rect(x, y, w, 2, LINE)
        yy = y + 2 + pad
        red = (i == hi)
        if r["bar"] is not None:
            yy = tx(d, x, yy, w, r["label"], "label", c=INK)
            bw = max(BAR_MIN, span * r["bar"])
            d.rect(x, yy + 10, bw, 36, ACC if red else GREY_BAR)
            if r["value"]: tx(d, x + bw + 16, yy + 28 - 28, span, r["value"], "num", size=38, c=ACC if red else INK, balance=False)
            yy += 58
            if r["body"]:
                for ln in r["body"].split("\n"): yy = tx(d, x, yy, w, ln, "detail")
        else:
            vw = (FM.width(r["value"], 40, "Bold") + 24) if r["value"] else 0
            lw = label_w or (w - vw)
            y1 = tx(d, x, yy, lw, r["label"], "label", c=ACC if (red and not r["value"]) else INK)
            if r["value"]:
                tx(d, x + w - vw, yy, vw, r["value"], "num", c=ACC if (red and hi_value) else INK, just="right", balance=False)
            yy = y1
            if r["value_note"]: yy = tx(d, x, yy, w, r["value_note"], "note", just="left")
            if r["body"]:
                yy += 6
                for ln in r["body"].split("\n"): yy = tx(d, x, yy, w, ln, "card")
        if r["note"]:
            yy += 4
            yy = tx(d, x, yy, w, r["note"], "note")
        y = yy + pad
    d.rect(x, y, w, 2, LINE)
    d.rule_end = y + 2
    return y + 2


# ---------- callouts ----------
def quote(d, y, text, caption=None, x=X, w=CW, padx=44, pady=40):
    """White card with hairline stroke for something to copy/say (e.g. an AI prompt). Text 38 Medium."""
    inner = w - 2 * padx
    h = nlines(text, inner, "item") * TS["item"][2] + (12 + nlines(caption, inner, "detail") * TS["detail"][2] if caption else 0) + 2 * pady
    d.rect(x, y, w, h, CARD, 16, stroke=LINE)
    yy = tx(d, x + padx, y + pady, inner, text, "item")
    if caption: tx(d, x + padx, yy + 12, inner, caption, "detail")
    return y + h

def takeaway(d, y, text, gap=GAP_L):
    """THE takeaway line (max one per slide): hairline, then 36 SemiBold INK, greedy wrap that moves a
    break back to a comma when possible (balance="clause"). If the block above already ended on a rule (numlist/cards), no second rule."""
    if getattr(d, "rule_end", None) == y:
        y += 12
        return tx(d, X, y + 24, CW, text, "take", balance="clause")
    y += gap
    d.rect(X, y, CW, 2, LINE)
    return tx(d, X, y + 28, CW, text, "take", balance="clause")

def note(d, y, text, gap=GAP_S):
    """Secondary note/caveat: 34 Regular SEC. Never bold, never red."""
    return tx(d, X, y + gap, CW, text, "note")


# ---------- build ----------
def _ceil8(v): return int(-(-v // 8) * 8)

def height_for(d):
    """Canvas height for the laid-out slide: content + footer block, multiple of 8, >= MIN_H."""
    tail = (FOOT_GAP + FOOT_SLOT + BOTTOM_MARGIN) if d.page is not None else NOFOOT_MARGIN
    return max(MIN_H, _ceil8(d.bottom + tail))

def build(name, fn, outdir, d=None):
    """Lay the slide out (fn), compute its height, then create/commit the project at that size and render."""
    d = d or Doc(name)
    probe = Doc(name); probe.page = d.page; fn(probe)          # pass 1: measure list numbers
    if probe.num_w: d.ind = _ind_for(probe.num_w)              # one shared indent for all lists
    fn(d)
    H_ = d.height = height_for(d)
    footer(d, H_)
    d.layers.insert(0, None); bg = Doc(); bg.rect(0, 0, W, H_, BG, flow=False); d.layers[0] = bg.layers[0]
    for i, L in enumerate(d.layers):          # unique ids after inserting the background
        L["id"] = i + 1; L.pop("_flow", None)
    os.makedirs(os.path.join(outdir, ".tesseract-work"), exist_ok=True)
    proj = os.path.join(outdir, f"{name}.tsrct"); work = os.path.join(outdir, ".tesseract-work", f"{name}.json")
    if not os.path.exists(proj):
        subprocess.run([T, "project", "create", "--project", proj], check=True, capture_output=True)
        subprocess.run([T, "project", "import-font", "--project", proj, "--file", FONT], check=True, capture_output=True)
    subprocess.run([T, "project", "checkout", "--project", proj, "--output", work], check=True, capture_output=True)
    doc = json.load(open(work))
    doc["dimensions"] = {"width": W, "height": H_}
    doc.pop("backgroundColor", None)
    doc["composition"]["layers"] = list(reversed(d.layers))   # first drawn = back
    json.dump(doc, open(work, "w"), ensure_ascii=False)
    r = subprocess.run([T, "project", "commit", "--project", proj, "--file", work], capture_output=True, text=True)
    if r.returncode: print(r.stdout, r.stderr); sys.exit(1)
    r = subprocess.run([T, "preview", "--project", proj, "--time", "1", "--output", os.path.join(outdir, f"{name}.png")],
                       capture_output=True, text=True)
    if r.returncode: print(r.stdout, r.stderr); sys.exit(1)
    print("ok", name, f"1080x{H_}")
    for w_ in d.warn: print("  WARN", name, w_)
    return d

def landscape_page(src_dir, stem):
    """Page number printed in the footer of the landscape slide <stem> (read from its checked-out JSON)."""
    p = os.path.join(src_dir, ".tesseract-work", f"{stem}.json")
    if not os.path.exists(p): return None
    for L in json.load(open(p))["composition"]["layers"]:
        if L.get("type") == "Text":
            x, y = L["transform"]["position"]
            t = L["sourceText"]["text"]
            if y >= 1000 and x > 1500 and t.strip().isdigit(): return int(t)
    return None

def run(slides, outdir, prefix="", src_dir=None):
    """slides: [(name, fn)] — name = the landscape file stem (one landscape slide = one mobile slide).
    outdir: e.g. slides-mobile/detail or slides-mobile/summary. prefix: optional file-name prefix.
    src_dir: the landscape deck dir; each slide's footer page is read from the landscape slide with the
    same name (no page there → no footer, e.g. the cover). CLI args filter by name (with or without prefix)."""
    allw = []
    for name, fn in slides:
        full = prefix + name
        if len(sys.argv) > 1 and name not in sys.argv[1:] and full not in sys.argv[1:]: continue
        d = Doc(full)
        if src_dir:
            d.page = landscape_page(src_dir, name)
            if not os.path.exists(os.path.join(src_dir, ".tesseract-work", f"{name}.json")):
                d.warn.append(f"no landscape slide named {name!r} in {src_dir} — use the landscape file stem")
        d = build(full, fn, outdir, d)
        allw += [(full, w_) for w_ in d.warn]
    if allw: print(f"{len(allw)} warning(s) — fix before handing over")
