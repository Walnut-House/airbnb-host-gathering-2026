"""helpers for detail_d-* (numbered list with custom marks / title colour)."""
from lib_m import *

def mlist(d, y, items, hi=None, marks=None, tc=None, start=1, pad=22, x=X, w=CW):
    """numlist clone: marks[i] replaces the number (e.g. '—'), tc = title colour."""
    ix = x + d.ind; iw = w - d.ind
    y, top = list_top(d, y)
    for i, it in enumerate(items):
        if i or top: d.rect(x, y, w, 2, LINE)
        yy = y + 2 + pad
        t, det = (it if isinstance(it, tuple) else (it, None))
        kind = "item" if det else "body"
        num_mark(d, x, yy, marks[i] if marks else start + i, i == hi)
        yy = tx(d, ix, yy, iw, t, kind, c=tc)
        if det:
            dets = det if isinstance(det, list) else [det]
            yy += 2
            for dl in dets:
                if isinstance(dl, tuple): yy = tx(d, ix, yy + 4, iw, dl[0], "card")
                else: yy = tx(d, ix, yy, iw, dl, "detail")
        y = yy + pad
    d.rect(x, y, w, 2, LINE); y += 2; d.rule_end = y
    return y
