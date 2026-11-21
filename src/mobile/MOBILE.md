# Mobile (portrait) edition — spec for converting slides

Phone version of the 상세판 (`../slides-detail`) and 요약판 (`../slides-full`).
Same content, same look family (colours, Apple SD Gothic Neo, red kicker, footer), re-laid-out for a
portrait canvas 1080 px wide whose HEIGHT fits the content, so a phone reader scrolls and never zooms.

Library: `src/lib_m.py` (+ `src/fontmetrics.py`). Pilot / worked examples: `src/pilot.py` → `pilot/*.png|.tsrct`.
Read `../slides-detail/src/ROUND2.md` + `ROUND3.md` too: their wording/red/glossary rules still apply.

## 0. Core rules

- **One landscape slide = exactly one mobile slide.** Never split, never merge. File stem = the landscape
  stem (`1c-07-refund-by-date.png`), so files sort in landscape order.
- **Width 1080, height computed** (§2). No maximum height — a long slide is just a taller page.
- **Footer page label = landscape page + 「쪽」**, e.g. `45쪽`. `run(..., src_dir=…)` reads it from the
  landscape slide's `.tesseract-work/<stem>.json`; a landscape slide without a page number (cover) gets no footer.
- **Same text as the landscape slide** — no rewording, no dropped lines, no added headings, no 「(계속)」 or
  other continuation cue. Only allowed edit: table column headers joined into one legend row (§5).

## 1. How to convert one slide (recipe)

1. Open the landscape PNG + its source function in `../slides-detail/src/part_*.py`.
2. Map each landscape block to a portrait component (§5), reading order top band → left column → right
   column → bottom band. Each column head becomes a `section()`; the first one gets `first=True`; use
   `rule=True` where the landscape had a band rule between two blocks. Blocks with no head get none.
3. Copy every string verbatim. Only add ` ` (no-break space) where a WARN or the PNG shows a bad break.
4. Add `("<landscape stem>", fn)` to the part's `run([...])` list and build:
   `python3 src/<part>.py <stem>` → `<OUT>/<stem>.tsrct` + `.png`, printed as `ok <stem> 1080xH`.
5. Fix every `WARN` line, open the PNG, run the checklist (§9).

Example from `src/pilot.py` (landscape: table with a mini-bar column on the left, numbered list on the right, takeaway):

```python
import sys, os; sys.path.insert(0, "/Users/eon/research/airbnb-seminar-2026/slides-mobile/src"); from lib_m import *
SRC = "/Users/eon/research/airbnb-seminar-2026/slides-detail"          # or slides-full
OUT = "/Users/eon/research/airbnb-seminar-2026/slides-mobile/detail"   # or .../summary
K1b = "세션 1  ·  운영 팁"

def refund(d):  # 1c-07-refund-by-date
    y = header(d, K1b, "환불 정책과 최소 숙박일은 날짜별로 다르게 건다",
               "성수기·이벤트는 엄격하게, 비어 있는 임박 날짜는 유연하게")
    y = section(d, y, "날짜별 환불 정책", first=True)                  # left column
    y = cards(d, y, [card("Flexible", "비어 있는 임박 날짜", value="24시간 전", bar=1 / 30),
                     card("Moderate", "비수기", value="5일 전", bar=5 / 30),
                     card("Limited", "수요 많은 날짜", value="14일 전", bar=14 / 30),
                     card("Firm", "성수기·대형 이벤트", value="30일 전", bar=1)],
              keys=("정책 · 전액 환불 마감 · 쓸 날짜",))              # landscape column order
    y = note(d, y, "Limited는 7~14일 전, Firm은 7~30일 전이면 50% 환불")
    y = section(d, y, "비수기만 골라 풀기")                             # right column
    y = numlist(d, y, [("날짜별로 따로 걸 수 있다", "환불 정책·최소 숙박일 모두 — 아직 모르는 호스트가 많다"),
                       ("달력에서 비수기만 쭉 선택", "고른 기간에만 따로 설정"),
                       ("그 기간만 최소 숙박일 줄이기", "노출을 늘리는 방법"),
                       ("환불도 더 유연하게", "비어 있는 임박 날짜는 Flexible")], hi=1)
    takeaway(d, y, "호스트가 할 일 — 달력에서 비수기만 골라 환불은 유연하게, 최소 숙박일은 줄이기")

if __name__ == "__main__":
    run([("1c-07-refund-by-date", refund)], outdir=OUT, src_dir=SRC)   # optional prefix="m-"
```

- Every component takes `y` (top of its block) and returns the `y` under it. Write slides top to bottom.
- CLI args filter by name: `python3 src/part_1c.py 1c-07-refund-by-date` rebuilds one slide.
- `run(slides, outdir, prefix="", src_dir=None)`: `prefix` is an optional file-name prefix; `src_dir`
  is the landscape deck (needed for the page label; warns if no landscape slide has that stem).
- Text is wrapped by lib_m with the real font metrics — never put manual `\n` in body text except to
  separate genuinely separate lines.
- Other worked examples in `pilot.py`: `supply` (bars), `desc_ai` (horizontal timeline → `vtimeline`,
  then two columns stacked), `quick` (two timelines, the second `inline`), `cover` (free layout, no footer).

## 2. Canvas and grid

| item | value |
|---|---|
| width | 1080 (`W`), background BG |
| height | `max(1350, ceil8(content bottom + 72 + 38 + 64))` — content bottom + `FOOT_GAP` 72 + footer slot 38 + `BOTTOM_MARGIN` 64, rounded up to a multiple of 8, minimum 1350 (4:5). No footer (cover): content bottom + 96. No maximum |
| side margins | 72 left/right → content x 72, width 936 (`X`, `CW`) |
| list/timeline indent | 60 (`IND`): number or dot at x 72, text at x 132. If any list on the slide has a wider number (`10`, `7~8`), `build()` widens the indent for ALL lists on that slide (`d.ind` = widest number + 36, rounded to 4) — custom list helpers must use `num_mark(d, x, y, n, red)` and `X + d.ind` |
| kicker top | y 96 |
| footer | anchored to the computed height: text slot top = H − 64 − 38; 28 Regular MUT; left 「호스트, 우리가 만나다 · 2026 대한공유숙박호스트협회 연말 게더링」, right `45쪽` |

`build()` lays the slide out first (lib_m knows every block height from `fontmetrics`), computes H, then
writes `dimensions = 1080 x H` into the project before commit/render. Pilot heights: supply 1576,
cover 2000, quick-reply 2008, desc-ai 2192, refund 2616.

## 3. Type scale (px on the 1080 canvas; ×0.36 = pt on a 390-pt-wide phone)

Every text block uses an explicit line slot (leading); `tx()` centres glyphs in it, so a block of n
lines is exactly n × slot tall.

| role (`TS` key) | size | weight | slot | colour | ≈ pt |
|---|---|---|---|---|---|
| kicker | 30 | SemiBold | 44 | ACC | 10.8 |
| title | 64 | Bold | 80 | INK, ≤ 3 lines (usually 2) | 23 |
| sub (subtitle) | 34 | Regular | 50 | SEC | 12.2 |
| head (section/column head) | 42 | SemiBold | 58 | INK — one step above item titles | 15 |
| body (1-line list item, paragraph) | 38 | Regular | 56 | INK | 13.7 |
| item (list item title with a detail line) | 38 | Medium | 56 | INK | 13.7 |
| label (card row label, timeline step) | 38 | SemiBold | 56 | INK | 13.7 |
| card (card body, inline step body, ink key line) | 36 | Regular | 52 | INK | 13 |
| detail (2nd line of item, step body, bar-row use-line) | 36 | Regular | 52 | SEC | 13 |
| note (caveat, table legend row) | 34 | Regular | 48 | SEC | 12.2 |
| take (takeaway) | 36 | SemiBold | 54 | INK | 13 |
| num (numbers in rows, bar values) | 40 / 38 | Bold | 56 | INK (ACC if the one red) | 14 |
| bigstat | HERO 120 / GRID 96 | Bold, tracking −10 | 1.15 × size | INK / ACC | 43 / 35 |
| footer | 28 | Regular | 38 | MUT | 10 |

Minimums: notes 34, secondary (grey) 36, primary 36~40. Never shrink text to make a slide shorter.

## 4. Spacing

- Header: kicker slot (96→140), +12, title, +10, subtitle, +32, hairline; content starts 44 below the hairline.
- `GAP_S 20` inside a block, `GAP_M 40` between blocks, `GAP_L 64` before a section head or takeaway.
- Lists/cards: hairline above every row and under the last, 22–26 px padding above and below the text.
- Vertical rhythm is fixed: content is top-aligned, pitch comes only from content + padding; the height
  follows the content (§2), so there is no slack to distribute. Do not centre or stretch content.
- 72 px between the last content line and the footer (automatic).

## 5. Components (lib_m)

| landscape pattern | portrait component | notes |
|---|---|---|
| `header()` | `header(d, kicker, title, sub=None)` | returns content top; page comes from `run()` (`page=N` only if the landscape JSON is missing) |
| `col_head()` | `section(d, y, text, first=False, rule=False)` | first section on a slide: `first=True`; `rule=True` = hairline above the head (auto-skipped after a ruled list) |
| two columns side by side | stack them: section A, then section B | left column first |
| `numlist` / `li` / `two` / `rows` | `numlist(d, y, items, hi=None, start=1, pad=22)` | item = `str` or `(title, detail)`; detail may be a list; a detail entry `("text","ink")` renders 36 INK (cover sessions). A ruled list/cards block placed right at `header()`'s return y reuses the header hairline as its top rule (no double hairline; `list_top()` for custom lists). A line starting with `①`/`1)`/`•` hangs: wrapped lines sit under its text |
| `timeline` (horizontal) | `vtimeline(d, y, steps, hi=None, gap=36, inline=None)` | dots + vertical spine; `inline=340` puts short bodies on the label line (7 one-word steps, `gap=16`) |
| `bars` | `bars(d, y, rows, hi=None, maxv=None, label_w=None)` | label on its own line above a full-width bar, value at the bar end; `label_w=220` for inline labels. Same `maxv` for all % bars on a slide. Bars (and card mini-bars) are at least `BAR_MIN` 48 px long |
| `bigstat` | `bigstat(d, x, y, w, value, label, size=HERO\|GRID, acc)` / `stats(d, y, items, size, cols=2)` | automatic 2 per row when each value fits 432 px and its label ≤ 4 lines at 432: `stats(cols=1)` is upgraded to 2 cols, and two consecutive full-width `bigstat`s (≤ 48 px apart, nothing between) — or one after the odd last item of `stats()` — are set side by side |
| `table_head` + rows | `cards(d, y, [card(label, body, value=, value_note=, note=, bar=)], hi=, keys=)` | plain row: label + value right-aligned → body (36 INK) → note. Bar row (`bar=0..1`, a mini-bar column): label → 36 px bar with the value at its end → body in grey (36 SEC). Column headers go ONCE into `keys=("A · B · C",)` (legend row, note style) — **in the landscape column order**; the card order follows the same order. Never repeat a header per row |
| white prompt/quote card | `quote(d, y, text, caption)` | |
| `takeaway()` | `takeaway(d, y, text)` | max one per slide; breaks at a comma when it can; no second rule if the list above closed with one |
| `note()` | `note(d, y, text)` | 34 SEC, never bold/red |
| hairline | `rule(d, y)` | |
| anything else | `tx(d, x, y, w, text, kind)` | wrapped text in any `TS` role; `d.rect(...)` for shapes |

3-column landscape grids → a numlist (one row per column) or cards. Big-number grids → `stats()`.
Free layouts (cover) use `tx`/`rule`/`stats`/`bigstat`/`numlist` directly without `header()`.

## 6. Rules carried over from the landscape spec (ROUND2/3)

One red element per slide = its takeaway number/bar/list number/timeline dot · tight 「·」 inside phrases,
spaced 「 · 」 only between independent items · 「」 for terms, "" for spoken quotes · 「~」 ranges ·
no sentence-final periods · glossary (게스트, 달력, 체크아웃, 시범, 게스트 선호, 1박, 리마인더, 「시간 지정 발송」 …).

## 7. Line breaking

Automatic (lib_m `wrap()`, a cost-minimising breaker over the whole paragraph):
- Breaks only at normal spaces — **never at U+00A0** (no-break space glues a phrase). A spaced 「 · 」
  starts the next line (「· 폐기물」), never ends one; 「—」 stays at the end of its line.
- Near-forbidden (an extra line is cheaper): before a 1-syllable token (수, 것, 원, 때) or a 2-syllable
  auxiliary/particle (두면, 등에, 것은, 말기, 본다); after a 1-syllable word (그, 전, 약, 내); between a
  number and its unit (10만 원, 수천 개, 다섯 가지); inside a 「…」 / "…" / (…) span of ≤ 20 chars;
  verb + auxiliary (쓰지 말고, 되어 있으면, 해야 하는지). Avoided: before any other 2-syllable word
  (주민 동의), at a space inside one item of a tight 「·」 list (…·신규 숙소·…).
- Preferred: after a comma / 「—」 or before 「 · 」 when it falls late enough in the line.
- No orphan: a single short word (< 35 % width) is never left alone on a line unless unavoidable.
- `balance=True` evens out the lines; `"clause"` (takeaways) fills lines and breaks at a comma.

The engine cannot see compounds of longer words (「프리미엄 독채 신축풀빌라」, 「BTS·서울 아레나」): write a
no-break space ` ` between their words. Never fix a break by changing wording. Build WARNs on a line
that is a lone short word (orphan), a line starting with whitespace, a line ending in 「 ·」.

## 8. Renderer facts (tsrct 0.5.0) that lib_m relies on

- Box text with `verticalAlign: "top"`: first baseline ≈ 1.0 × font size below the box top, later lines
  every `leading` px. Without it a box with `leading` is centred vertically — lib_m always sets "top".
- Box text cannot report line counts, so lib_m pre-wraps with `fontmetrics.py` (advance widths from the
  .ttc; matches the renderer within ~1 px) at 98.5 % of the box width.
- Canvas size = `doc["dimensions"]` in the checked-out JSON; lib_m sets it on every build, so an
  existing .tsrct is resized when content changes.
- Tracking unit = 1/1000 em. Fonts must be embedded (`missing_fonts` otherwise): each .tsrct carries
  the 55 MB .ttc (the PNGs are the deliverable). No shrink-to-fit is used.

## 9. Checklist per slide

1. Build shows no WARN. 2. Open the PNG: title ≤ 2 lines ideally, nothing clipped, numbers aligned with
their text, one red, footer 72 px under the content. 3. Footer page = landscape page. 4. Compare with the
landscape PNG line by line: same content, table legend in landscape column order. 5. Check once
downscaled to 390 px wide (`sips --resampleWidth 390 x.png --out /tmp/x.png`):
body text must still be readable.
