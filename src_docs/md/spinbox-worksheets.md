---
this_file: src_docs/md/spinbox-worksheets.md
---

# Glyph metrics and revision worksheets

Widgets > Glyph Metrics and Revisions and its Detailed companion keep the two
complete retained spinbox profiles. Select glyph layers in FontLab, then open a
worksheet. Integer and decimal offsets are independent recipes in font units;
decimal scaling applies after its offset. The 12pt point-width estimate uses
captured UPM and integer zoom, without kerning or shaping. Prices estimate a
proof quote per distinct selected glyph, rather than per repeated layer.

Detailed zero zoom means Automatic: fit absolute total advance to500pt. Detailed
zero decimal scale means No scaling. The basic profile keeps literal zero and
negative scales. Change precision to round all three decimal inputs, just as in
the retained source. All estimates remain local.

The date and time cutoffs independently count whole-font glyph revisions on or
before the chosen date/time. The instant counts strictly earlier revisions,
including milliseconds. Unknown dates are counted separately. Dates use Qt local
time. Detailed retains its historical2005–2010 date range,09:00–16:30 time
range and format-dependent historical instant ranges. These controls are useful
for an archive revision audit; no font date is changed. Hidden date sections of
time-only instant formats remain present and the full cutoff is shown.

Refresh replaces the complete capture while keeping all local controls. Failed
capture clears stale results. Both panels are nonmodal; Close/Escape releases
owned callbacks. Reopening replaces only the matching profile. Use Python3.11,
Fly and reviewed App>=0.2.90.dev0. Native FontLab lifecycle, getters/cache,
whole-font/history/dirty/save/reopen qualification remain pending.
