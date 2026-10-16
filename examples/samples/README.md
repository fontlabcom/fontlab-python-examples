---
this_file: examples/samples/README.md
---

# Samples: GUI scripts for FontLab 9

106 single-file PythonQt dialogs for everyday font work: anchors, metrics,
kerning, outlines, masters, names, guides, font info, features, hinting, cleanup,
generators, reports and proofs. Each one works on the current font and offers a master
scope where that makes sense; most list what an Apply will change before you press it,
and a few (such as mark-colour swatches) apply on click. Report, browser and proof
scripts change nothing. Glyph edits are one Undo step per Apply.
Font-wide data (font info, OpenType features, master settings) is written directly
and Edit > Undo may not cover it: for example, Italic Angle (Masters) states that Undo
does not restore its change.

Copy any file into FontLab's `Scripts` folder (for example `Scripts/Samples`) and run
it from the **Scripts** menu, or open it in the Scripting panel. A script needs only
FontLab 9 and its bundled PythonQt; nothing else is installed. Dialogs are modeless,
so the Font window stays usable, and every dialog disconnects its signals when closed.

Each script was run in FontLab 9.0.9783 through its menu path on disposable copies of
GetGo fonts, with screenshots and before/after reads of the changed glyphs. Edits on
glyphs used by automatic composites warn first: FontLab may rebuild those composites'
anchors and locks, and Undo does not restore that rebuild.

## Cleanup (2)

| Script | What it does |
| --- | --- |
| [Remove Empty Auxiliary Layers](cleanup_empty_layers.py) | Delete empty auxiliary layers (no outlines, anchors, guides, note or other data) from the selected glyphs. |
| [Select Unreferenced Glyphs](cleanup_unused_glyphs_report.py) | List unencoded glyphs that nothing references, and select them in the Font window for review. |

## Font Info (6)

| Script | What it does |
| --- | --- |
| [Bump Font Version](fontinfo_version_bumper.py) | Bump the numeric version and version name; optionally append a dated font note. |
| [Calculate Vertical Metrics](fontinfo_vertical_metrics_calculator.py) | Set hhea, Win (and optionally OS/2 typo) vertical metrics to enclose every glyph, per master. |
| [Glyph Order Preview & Export](fontinfo_glyph_order_tool.py) | Sort by Unicode, name or Unicode script; export one glyph name per line for the whole font. |
| [Master Metrics Table](fontinfo_master_metrics_table.py) | Edit ascender, descender, x-height and cap-height across masters; diagram follows the selected row. |
| [Names & Credits](fontinfo_names_editor.py) | Edit family, style, credits and version naming for the current font. |
| [Unicode Ranges & Codepage Hints](fontinfo_unicode_ranges.py) | Report OS/2 range bits and complete printable codepage coverage from every glyph encoding; no font changes. |

## Generators (6)

| Script | What it does |
| --- | --- |
| [Outline Effect](generate_outline_effect.py) | Turn the selected glyphs into outlined (hollow) letters. |
| [Placeholder Glyphs](generate_placeholder_glyphs.py) | Create empty placeholder glyphs from pasted glyph names or characters, on every master. |
| [Shadow Copy](generate_shadow.py) | Add a shifted copy of the selected glyphs' outlines as a separate shadow element. |
| [Small Caps from Capitals](generate_small_caps.py) | Create small-cap glyphs (h.sc, a.sc ...) from the selected capitals, on every master. |
| [Superior & Inferior Figures](generate_superiors.py) | Create superior (.sups) or inferior (.subs) copies of the selected figures, on every master. |
| [Tabular Figure Copies](generate_tabular_copies.py) | Create tabular (.tf) copies of the selected figures, on every master. |

## Guides (6)

| Script | What it does |
| --- | --- |
| [Clear Glyph Guides](guides_clear.py) | Remove glyph guides from the selected glyphs by direction and name. |
| [Copy Guides Between Masters](guides_copy_between_masters.py) | Copy the glyph guides of one master to the other masters of the selected glyphs. |
| [Font Guides Panel](guides_font_guides_panel.py) | Show the font's guides and add one named guide to every master of the selected glyphs. |
| [Grid Generator](guides_grid_generator.py) | Add a regular grid of named glyph guides: N lines every S units from an origin. |
| [Guide List Editor](guides_list_editor.py) | Edit the glyph guides of one glyph as a table: X, Y, angle and name per master. |
| [Metric Reference Lines](guides_metric_lines.py) | Add named horizontal glyph guides at the font's vertical metrics, plus an offset. |

## Hinting (3)

| Script | What it does |
| --- | --- |
| [Autohint Selected Layers](hints_autohint.py) | Run FontLab's PostScript autohinter on the selected glyphs, per master. |
| [Remove PostScript Hints](hints_remove.py) | Remove PostScript stem hints from the selected glyphs, horizontal and/or vertical, per master. |
| [Suggest Zones from Overshoots](zones_from_glyphs.py) | Set PostScript alignment zones from the overshoots of H/O (baseline, caps) and x/o (x-height). |

## Kerning (12)

| Script | What it does |
| --- | --- |
| [Classes Browser](kerning_classes_browser.py) | Browse kerning classes: their side, members, and every pair that uses them on each master. |
| [Compare Masters](kerning_compare_masters.py) | Line up every kerning pair across all masters and flag the ones that look inconsistent. |
| [Copy Between Masters](kerning_copy_between_masters.py) | Copy the kerning of one master to other masters, optionally scaled. |
| [Exceptions Finder](kerning_exceptions_finder.py) | Find kerning exceptions: pairs that override a class pair, and remove the ones you tick. |
| [Missing Pairs](kerning_missing_pairs.py) | List the combinations of two glyph groups that no kerning pair covers on a master. |
| [Pair Editor](kerning_pair_editor.py) | Edit every kerning pair that involves one glyph, with one column per master. |
| [Pair List](kerning_list_browser.py) | Browse every kerning pair of a master: filter, sort by any column, export to CSV. |
| [Pairs from Text](kerning_pairs_from_text.py) | Type a word, see each adjacent pair's kerning on every master, and set the ones you tick. |
| [Remove Small Pairs](kerning_remove_small.py) | Delete kerning pairs whose value is smaller than a threshold, on one or all masters. |
| [Round Values](kerning_round_values.py) | Round kerning values to a step (5, 10 …) on one or all masters, previewing every change. |
| [Scale Values](kerning_scale_values.py) | Scale all kerning values by a percentage on one or all masters. |
| [Text Preview](kerning_text_preview.py) | Set text from the font's outlines with its kerning applied, per master, at any size. |

## Masters (13)

| Script | What it does |
| --- | --- |
| [Back Up Master Layers](masters_backup_layer.py) | Copy the master layers of the selected glyphs to named backup layers before risky edits. |
| [Compatibility Check](masters_compatibility_check.py) | Check that every master of each glyph can interpolate: same contours, nodes, anchors, components. |
| [Copy Layer Between Masters](masters_copy_layer.py) | Copy the outline (and optionally anchors and advance width) from one master to others. |
| [Copy Outline to Mask](masters_copy_to_mask.py) | Copy the outline of each selected glyph's master layer into its mask layer, for reference. |
| [Glyph Weight Chart](masters_glyph_weight_chart.py) | Bar chart of the ink area of the selected glyphs in every master. |
| [Interpolation Preview](masters_interpolation_preview.py) | Preview a glyph between two masters with a slider, from the masters' own nodes. |
| [Italic Angle](masters_italic_angle.py) | Read and set the italic angle of every master, with a painted gauge comparing them. |
| [Layer Cleanup](masters_layer_cleanup.py) | List the non-master layers of the selected glyphs (masks, backups, others) and delete the ticked ones. |
| [Master Switcher](masters_switcher_palette.py) | A small palette with one button per master: click to make that master current. |
| [Masters Overview](masters_overview.py) | One table of all masters: axis location, vertical metrics and italic angle. |
| [Restore Backup Layer](masters_restore_backup.py) | Restore a backup layer (such as "Regular backup") into the master it was taken from. |
| [Sync Sidebearings](masters_sync_metrics.py) | Copy side-bearings from a reference master to the other masters, proportionally or as-is. |
| [Width Chart](masters_width_chart.py) | Line chart of the advance widths of the selected glyphs across masters. |

## Metrics (13)

| Script | What it does |
| --- | --- |
| [Alignment Zones](metrics_zones_editor.py) | Edit the PostScript alignment zones (blue zones) of each master in a table. |
| [Centre in Advance](metrics_center_in_advance.py) | Centre the outlines of the selected glyphs in their advance width, optionally with a new width. |
| [Copy from Reference](metrics_copy_from_reference.py) | Give the selected glyphs the sidebearings or the advance width of a reference glyph. |
| [Equalize Sidebearings](metrics_equalize_sidebearings.py) | Make the left and right sidebearings of the selected glyphs equal, on one or all masters. |
| [Italic Sidebearings](metrics_italic_sidebearings.py) | Report and set sidebearings measured along the italic angle, not straight up. |
| [Round Advances](metrics_round_advances.py) | Round advance widths to a step (2, 5, 10 … units), keeping every outline where it is. |
| [Scale Advances](metrics_scale_advances.py) | Scale the advance widths of the selected glyphs by a percentage, each outline staying centred. |
| [Sidebearings Tuner](metrics_sidebearings_tuner.py) | Set, add to or scale the side-bearings of the selected glyphs on one or all masters. |
| [Spacing String Preview](metrics_spacing_string_preview.py) | Render a spacing control string such as HOHnono from the font's own outlines and advances. |
| [Tabular Width](metrics_tabular_width.py) | Give figures (and optionally currency signs) one shared advance width, each outline centred. |
| [Vertical Metrics Diagram](metrics_vertical_metrics_diagram.py) | See and edit ascender, cap height, x-height and descender of every master in one diagram. |
| [Width Table](metrics_width_table.py) | Advance widths of the selected glyphs across all masters, sortable, with odd progressions flagged. |
| [Zero-Width Marks](metrics_zero_width_marks.py) | Set the advance width of combining marks to zero, keeping or re-placing their outlines. |

## Names (12)

| Script | What it does |
| --- | --- |
| [Batch Rename](names_batch_rename.py) | Find and replace in glyph names (plain text or regular expression) with a live preview. |
| [Case Pairs](names_case_pairs.py) | Find the upper- or lowercase counterparts of the selected glyphs and select them. |
| [Character Info](names_character_info.py) | A live panel describing the character of the glyph selected in the Font window. |
| [Charset Compare](names_charset_compare.py) | Paste a text or a character set and compare it with the font's encoded characters. |
| [Duplicate Unicodes](names_duplicate_unicodes.py) | Find code points assigned to more than one glyph and remove them from the extra glyphs. |
| [Glyph Finder](names_glyph_finder.py) | Type to find glyphs by name, character or code point; Enter selects them in the Font window. |
| [Glyph Notes](names_glyph_notes.py) | Read and edit the note of the selected glyph, and browse every glyph that has a note. |
| [Glyph Tags](names_glyph_tags.py) | View, add and remove glyph tags across the selected glyphs. |
| [Mark Color Palette](names_mark_color_palette.py) | Click a colour swatch to mark the selected glyphs with it (or clear the mark). |
| [Select by Mark](names_select_by_mark.py) | Select glyphs in the Font window by their mark colour. |
| [Suffix Tool](names_suffix_tool.py) | Add, remove or replace a glyph-name suffix (.ss01, .sc, .alt…) on the selected glyphs. |
| [Unicode from Names](names_unicode_from_names.py) | Assign Unicode code points derived from glyph names, with a preview first. |

## OpenType (6)

| Script | What it does |
| --- | --- |
| [Alternate Glyph Proof](features_alternate_preview.py) | Compare a base glyph and its suffixed alternates in each master. Read-only; outlines share one scale per row. |
| [Feature Code Inspector](features_code_viewer.py) | Read-only feature source for the whole font. Choose a feature and search its code. |
| [Ligature Recipe Finder](features_ligature_finder.py) | Find underscore-named glyphs and existing input glyphs. Name-derived recipes do not imply outline components. |
| [OpenType Class Browser](features_classes_browser.py) | Browse feature classes and their members. Filter by class name or glyph; font-wide across masters. |
| [Suffix Feature Report](features_suffix_report.py) | Suffix inventory across the whole font. Suggestions are naming hints; review the generated code. |
| [Suffix Substitution Builder](features_build_substitution.py) | Preview a font-wide suffix substitution. Append to source only; compile and test in the Features panel. |

## Outlines (14)

| Script | What it does |
| --- | --- |
| [Add Extremes](outlines_add_extremes.py) | Insert on-curve nodes at the horizontal and vertical extremes of curve segments. |
| [Contour Order View](outlines_contour_order_view.py) | Show every master of a glyph side by side with numbered contours, start points and directions. |
| [Correct Contour Direction](outlines_correct_direction.py) | Set PostScript contour direction on the selected glyphs and report what changed per master. |
| [Delete Duplicate Contours](outlines_delete_duplicate_contours.py) | Find contours drawn twice in the same layer and keep only the first copy. |
| [Delete Small Contours](outlines_delete_small_contours.py) | Remove contours whose area is below a threshold: stray specks left by drawing or tracing. |
| [Fix Zero Handles](outlines_fix_zero_handles.py) | Find curve handles that sit on their own node and clean them up. |
| [Node Coordinates Panel](outlines_node_coordinates_panel.py) | A small live panel listing the selected nodes of the current glyph with coordinates. |
| [Node Statistics](outlines_node_statistics.py) | Contours and nodes per glyph and master in one table, with incompatible glyphs flagged. |
| [Optimize Start Points](outlines_optimize_start_points.py) | Move every contour's start node to its bottom-left on-curve node, consistently across masters. |
| [Remove Overlap](outlines_remove_overlap.py) | Remove overlaps on the chosen masters of the selected glyphs, master compatibility checked first. |
| [Round Coordinates](outlines_round_coordinates.py) | Round node coordinates of the selected glyphs to a grid, optionally anchors and component offsets. |
| [Slant](outlines_slant.py) | Slant (skew) the selected glyphs by an angle, optionally the font's italic angle. |
| [Straighten Short Curves](outlines_straighten_short_curves.py) | Turn short curve segments whose handles lie on the chord into straight lines. |
| [Transform](outlines_transform_dialog.py) | Scale, skew, rotate and move the outlines of the selected glyphs with a live preview. |

## Proofs (4)

| Script | What it does |
| --- | --- |
| [Glyph Grid](proof_glyph_grid.py) | Show the selected glyphs on every master side by side, drawn from their outlines. |
| [Text by Master](proof_text_by_master.py) | Render the same text once per master, stacked, to compare weight and width at a glance. |
| [Waterfall](proof_waterfall.py) | Render a line of text in a cascade of sizes, drawn straight from the glyph outlines. |
| [Word Finder](proof_word_finder.py) | Find real words to proof with: words the font can set, that use the letters you are working on. |

## Reports (8)

| Script | What it does |
| --- | --- |
| [Empty Glyphs](report_empty_glyphs.py) | List glyphs that have no outlines and no components on some or all masters, and select them. |
| [Font Overview](report_font_overview.py) | A one-screen dashboard of the current font: glyphs, encoding, masters, kerning, composites. |
| [Glyph Info Live](report_glyph_info_live.py) | A live panel for the glyph you are working on: widths, side-bearings, bounds and counts per master. |
| [Glyph Table CSV](report_glyph_table_csv.py) | A sortable table of glyphs (name, Unicode, width per master, contours, components) with CSV export. |
| [Label Statistics](report_label_statistics.py) | Count glyphs by mark colour and by name suffix (.sc, .ss01, .loclPLK…); click a row to select them. |
| [Nodes Near Zones](report_nodes_near_zones.py) | Find on-curve nodes that sit within a few units of a vertical metric but not on it. |
| [Open Contours](report_open_contours.py) | Find open contours on every master and select the glyphs that have them. |
| [Unicode Coverage](report_unicode_coverage.py) | Unicode coverage of the current font, block by block, with progress bars. |

## Utilities (1)

| Script | What it does |
| --- | --- |
| [Batch Glyph Notes](utility_batch_glyph_notes.py) | Set or append a note on every selected glyph at once. |
