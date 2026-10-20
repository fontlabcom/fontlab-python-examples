---
this_file: src_docs/md/elastic-component-graphs.md
---

# Component dependency graphs

Open either graph from Tools. Both capture every current-master glyph in font
order; missing bases follow in first-reference order. Repeated references and
cycles remain visible. Hover a node for its exact glyph name; the report retains
each directed `glyph → base` occurrence and isolated glyph. No font writer runs.
Refresh after font or master changes; a failed capture clears stale graph data.

The regular graph retains part2's600×500 scene,30ms timer,170/distance repulsion,
0.015 springs, clipped five-unit force steps,0.2 settling and1.15 zoom strictly
between0.1 and5. It has one destination arrow. Arrow keys move the centre node;
Space/Return shuffle; Plus/Equal/Minus and wheel zoom.

Degree Forces retains part3's400×400 scene,40ms basic timer,degree-weighted
springs,150/(2×distance²) repulsion,0.1 per-axis settling,ten-unit margins,0.8
initial zoom,custom gradient nodes and two arrows,scene shadows/instructions,
caching and mouse/view-centred anchors. Space/Enter shuffle with integer
coordinates; Plus/Minus zoom1.2 and wheel uses inverse exponential scaling,
limited to0.07..100. Double arrows are the original visual policy; the textual
report records the directed component relationship without ambiguity.

Choose Original Nine-node Graph to exercise each complete fixed example. Stop
Motion stops the local simulation; drag/shuffle alter only local coordinates.
The held node stays fixed during physics. Finish a drag before Refresh or Close.
Large captures/construction/force steps have deadlines: an overrun stops motion
or rejects the entire snapshot; no subset is silently presented as complete.

Both exact original identities and source hashes remain in menu-adaptations.json
and rescue-index.json. These are17 native-pending adaptations among494 indexed
origins, with477 remaining backlog identities. Neither menu implies original
workflow acceptance. Actual FontLab PythonQt virtuals, painting, timer/drag
lifetime and full getter/cache/history/dirty/save/reopen preservation are pending.
