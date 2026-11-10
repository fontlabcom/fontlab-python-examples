# this_file: tests_docs/test_pipeline_site.py
"""Check the actual generated payload, routes and public source boundaries."""
import json
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'docs'
PREFIX = '/fontlab-python-examples/'
PAGES = ['collections.html', 'contribute.html', 'current/contours/index.html', 'current/contours/node-slope-and-handles.html', 'current/contours/node-table.html', 'current/designer/em-star-polygon.html', 'current/designer/index.html', 'current/dialogs/expandable-glyph-search.html', 'current/dialogs/font-glyph-inventory-tabs.html', 'current/dialogs/fontlab-script-scaffold-wizard.html', 'current/dialogs/glyph-batch-recipe-settings.html', 'current/dialogs/glyph-proof-batch-wizard.html', 'current/dialogs/index.html', 'current/dialogs/proof-text-coverage-dialog.html', 'current/drag-and-drop/deferred-glyph-report-drag.html', 'current/drag-and-drop/draggable-glyph-names.html', 'current/drag-and-drop/font-drop-inspector.html', 'current/drag-and-drop/font-file-drop-shelf.html', 'current/drag-and-drop/glyph-pair-board.html', 'current/drag-and-drop/index.html', 'current/drag-and-drop/proof-word-magnets.html', 'current/drawing/glyph-outline-svg.html', 'current/drawing/glyph-svg-reference.html', 'current/drawing/index.html', 'current/drawing/scale-with-stem-compensation.html', 'current/drawing/stem-blend.html', 'current/forms/glyph-metrics-form.html', 'current/forms/index.html', 'current/getgo-fonts/getgo-arabic-text-coverage.html', 'current/getgo-fonts/getgo-audit-a-real-font.html', 'current/getgo-fonts/getgo-compare-master-topology.html', 'current/getgo-fonts/getgo-compare-two-real-fonts.html', 'current/getgo-fonts/getgo-export-a-ttf-geometry-subset.html', 'current/getgo-fonts/getgo-export-an-otf-geometry-subset.html', 'current/getgo-fonts/getgo-font-info-mini-tool.html', 'current/getgo-fonts/getgo-kerning-and-classes-report.html', 'current/getgo-fonts/getgo-masters-axes-and-instances.html', 'current/getgo-fonts/getgo-name-a-disposable-derivative.html', 'current/getgo-fonts/getgo-outline-pens-and-intersections.html', 'current/getgo-fonts/getgo-sidebearings-from-h.html', 'current/getgo-fonts/getgo-widen-two-glyphs.html', 'current/getgo-fonts/index.html', 'current/graphics/glyph-mark-colour-board.html', 'current/graphics/glyph-proof-layout.html', 'current/graphics/glyph-proof-pad.html', 'current/graphics/glyph-review-cards.html', 'current/graphics/glyph-variant-feature-graph.html', 'current/graphics/index.html', 'current/index.html', 'current/models/glyph-coverage-grid.html', 'current/models/glyph-encoding-chart.html', 'current/models/glyph-filter-model-with-date-range.html', 'current/models/glyph-filter-model-with-local-dates.html', 'current/models/glyph-inventory-xml.html', 'current/models/glyph-mark-colours.html', 'current/models/glyph-metadata-outline.html', 'current/models/glyph-metadata-tree.html', 'current/models/glyph-metrics-model.html', 'current/models/glyph-name-filter.html', 'current/models/glyph-proof-worksheet.html', 'current/models/glyph-review-form.html', 'current/models/glyph-review-priorities.html', 'current/models/glyph-sorting-and-filtering-with-dates.html', 'current/models/glyph-sorting-and-filtering.html', 'current/models/index.html', 'current/text/calendar-proof-builder.html', 'current/text/feature-code-draft.html', 'current/text/font-handoff-letter.html', 'current/text/font-review-notes.html', 'current/text/index.html', 'current/text/script-snippet-notebook.html', 'current/tools/apply-unicode-map.html', 'current/tools/component-dependency-graph-degree-forces.html', 'current/tools/component-dependency-graph.html', 'current/tools/copy-layers-from-font.html', 'current/tools/editable-glyph-outline.html', 'current/tools/editable-glyph-tree.html', 'current/tools/find-font-source-files-bytes.html', 'current/tools/find-font-source-files.html', 'current/tools/font-info-snapshot.html', 'current/tools/font-name-encoding-audit.html', 'current/tools/font-reference-image-viewer-bounded-zoom.html', 'current/tools/font-reference-image-viewer.html', 'current/tools/fontlab-qt-slot-reference.html', 'current/tools/glyph-name-completion-with-focus.html', 'current/tools/glyph-name-completion.html', 'current/tools/glyph-name-pattern-lab.html', 'current/tools/glyph-snapshot-console.html', 'current/tools/glyph-spacing-worksheet-frameless.html', 'current/tools/glyph-spacing-worksheet.html', 'current/tools/import-kerning-pair-list.html', 'current/tools/index.html', 'current/tools/kerning-copy-rules.html', 'current/tools/layer-metric-comparison.html', 'current/tools/localized-font-names.html', 'current/tools/pair-proof-generator.html', 'current/tools/path-problem-report.html', 'current/tools/saved-proof-sample.html', 'current/tools/symbol-tag-search.html', 'current/widgets/font-units-calculator.html', 'current/widgets/glyph-character-map-styles.html', 'current/widgets/glyph-character-map.html', 'current/widgets/glyph-metrics-and-revisions-detailed.html', 'current/widgets/glyph-metrics-and-revisions.html', 'current/widgets/glyph-modification-calendar-with-formats.html', 'current/widgets/glyph-modification-calendar.html', 'current/widgets/glyph-proof-groups.html', 'current/widgets/glyph-sketch-pad.html', 'current/widgets/glyph-spacing-offset-stacked.html', 'current/widgets/glyph-spacing-offset.html', 'current/widgets/index.html', 'current/widgets/script-icon-browser.html', 'current/widgets/script-palette-roles.html', 'current/windows/glyph-snapshot-diff.html', 'current/windows/index.html', 'current/windows/unicode-issues-dock.html', 'elastic-component-graphs.html', 'frontend-notices.html', 'glyph-character-map.html', 'glyph-pattern-lab.html', 'guides/pre-integration.html', 'index.html', 'insights/callback-errors.html', 'insights/compiled-slot-exposure.html', 'insights/contour-canvas.html', 'insights/contour-scene.html', 'insights/glyph-list.html', 'insights/glyph-properties.html', 'insights/index.html', 'insights/loaded-glyph-form.html', 'insights/metric-controls.html', 'insights/metrics-table.html', 'insights/metrics-undo.html', 'insights/owned-dock.html', 'insights/owned-key-filter.html', 'insights/owned-repl.html', 'insights/plugin-tokens.html', 'insights/sandbox-settings.html', 'insights/signal-lifetime.html', 'insights/timer-batch.html', 'insights/worker-glyph-queue.html', 'lessons/dependencies.html', 'lessons/getgo.html', 'lessons/pythonqt.html', 'lessons/readme.html', 'licenses.html', 'plugins.html', 'retained-catalogue/categories/charts.html', 'retained-catalogue/categories/corelib.html', 'retained-catalogue/categories/database.html', 'retained-catalogue/categories/designer-ui.html', 'retained-catalogue/categories/designer.html', 'retained-catalogue/categories/desktop.html', 'retained-catalogue/categories/dialogs.html', 'retained-catalogue/categories/draganddrop.html', 'retained-catalogue/categories/embedded.html', 'retained-catalogue/categories/graphics-painting.html', 'retained-catalogue/categories/gstreamer.html', 'retained-catalogue/categories/itemviews.html', 'retained-catalogue/categories/layouts.html', 'retained-catalogue/categories/mainwindows.html', 'retained-catalogue/categories/matplotlib.html', 'retained-catalogue/categories/multimedia.html', 'retained-catalogue/categories/network.html', 'retained-catalogue/categories/platform.html', 'retained-catalogue/categories/qml.html', 'retained-catalogue/categories/remoteobjects.html', 'retained-catalogue/categories/richtext.html', 'retained-catalogue/categories/threads-processes.html', 'retained-catalogue/categories/tools.html', 'retained-catalogue/categories/tutorials.html', 'retained-catalogue/categories/video-overlay.html', 'retained-catalogue/categories/webengine.html', 'retained-catalogue/categories/widgets.html', 'retained-catalogue/categories/xmlpatterns.html', 'retained-catalogue/getgo.html', 'retained-catalogue/index.html', 'retained-catalogue/insights.html', 'retained-catalogue/recipes/anchors_from_bounds.html', 'retained-catalogue/recipes/contour_direction.html', 'retained-catalogue/recipes/glyph_actions_batch.html', 'retained-catalogue/recipes/glyphs_path_report.html', 'retained-catalogue/recipes/glyphs_tabular_figures.html', 'retained-catalogue/recipes/index.html', 'retained-catalogue/recipes/kerning_from_text.html', 'retained-catalogue/recipes/layer_backup.html', 'retained-catalogue/recipes/round_coordinates.html', 'retained-catalogue/recipes/sidebearings_from_reference.html', 'retained-catalogue/samples.html', 'slider-spacing-offsets.html', 'spacing-worksheets.html', 'echopy-native-examples.html', 'spinbox-worksheets.html', 'tags.html', 'topics.html']


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.tags = []
        self.ids = set()
        self.links = []
        self.text = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if 'id' in attrs:
            self.ids.add(attrs['id'])
        for name in ('href', 'src'):
            if name in attrs:
                self.links.append(attrs[name])

    def handle_data(self, data):
        self.text.append(data)


class SiteTests(unittest.TestCase):
    def test_all_generated_internal_links_and_fragments_resolve(self):
        for path in SITE.rglob('*.html'):
            for link in Page(path.read_text()).links:
                url = urlsplit(link)
                if url.scheme or url.netloc:
                    continue
                target = unquote(url.path)
                if target.startswith('/'):
                    self.assertTrue(target.startswith(PREFIX), (path, link))
                    dest = SITE / target.removeprefix(PREFIX)
                else:
                    dest = path.parent / target if target else path
                if dest.is_dir():
                    dest = dest / 'index.html'
                self.assertTrue(dest.is_file(), (path, link, dest))
                self.assertTrue(dest.resolve().is_relative_to(SITE.resolve()), link)
                if url.fragment and dest.suffix == '.html':
                    self.assertIn(unquote(url.fragment), Page(dest.read_text()).ids, (path, link))

    def test_pages_have_light_menu_footer_local_search_and_correct_canonical(self):
        for route in PAGES:
            page = Page((SITE / route).read_text())
            with self.subTest(route=route):
                self.assertEqual([attrs.get('mode') for tag, attrs in page.tags if tag == 'fontlab-menu'], ['light'])
                self.assertEqual([attrs.get('mode') for tag, attrs in page.tags if tag == 'fontlab-footer'], ['light'])
                self.assertEqual([attrs.get('data-md-color-scheme') for tag, attrs in page.tags if tag == 'body'], ['default'])
                search = [attrs for tag, attrs in page.tags if attrs.get('data-md-component') == 'search-query']
                self.assertEqual(len(search), 1)
                self.assertFalse(any(attrs.get('data-md-component') == 'palette' for _, attrs in page.tags))
                canonical = [attrs['href'] for tag, attrs in page.tags if attrs.get('rel') == 'canonical']
                self.assertEqual(canonical, ['https://code.fontlab.com/fontlab-python-examples/' + route])

    def test_search_indexes_every_authored_page(self):
        search = json.loads((SITE / 'search/search_index.json').read_text())
        locations = {row['location'].split('#')[0] for row in search['docs']}
        self.assertEqual(locations, {'retained-catalogue/categories/desktop.html', 'current/tools/glyph-name-pattern-lab.html', 'plugins.html', 'retained-catalogue/categories/network.html', 'retained-catalogue/categories/designer-ui.html', 'current/graphics/glyph-proof-layout.html', 'current/getgo-fonts/getgo-compare-two-real-fonts.html', 'collections.html', 'current/tools/find-font-source-files.html', 'current/tools/font-reference-image-viewer.html', 'retained-catalogue/categories/webengine.html', 'retained-catalogue/recipes/contour_direction.html', 'current/tools/symbol-tag-search.html', 'current/graphics/glyph-proof-pad.html', 'insights/metrics-undo.html', 'current/getgo-fonts/index.html', 'current/getgo-fonts/getgo-audit-a-real-font.html', 'current/models/index.html', 'current/drag-and-drop/proof-word-magnets.html', 'current/windows/glyph-snapshot-diff.html', 'current/dialogs/fontlab-script-scaffold-wizard.html', 'current/getgo-fonts/getgo-arabic-text-coverage.html', 'lessons/dependencies.html', 'current/models/glyph-encoding-chart.html', 'current/tools/fontlab-qt-slot-reference.html', 'current/drawing/index.html', 'retained-catalogue/categories/video-overlay.html', 'current/getgo-fonts/getgo-export-an-otf-geometry-subset.html', 'tags.html', 'lessons/pythonqt.html', 'current/drag-and-drop/font-file-drop-shelf.html', 'insights/plugin-tokens.html', 'current/tools/font-info-snapshot.html', 'retained-catalogue/recipes/kerning_from_text.html', 'insights/glyph-properties.html', 'current/widgets/glyph-modification-calendar.html', 'current/getgo-fonts/getgo-font-info-mini-tool.html', 'retained-catalogue/categories/threads-processes.html', 'current/models/glyph-sorting-and-filtering.html', 'retained-catalogue/categories/matplotlib.html', 'retained-catalogue/categories/platform.html', 'lessons/getgo.html', 'lessons/readme.html', 'current/drawing/glyph-outline-svg.html', 'current/dialogs/glyph-batch-recipe-settings.html', 'current/forms/index.html', 'current/drawing/glyph-svg-reference.html', 'current/dialogs/glyph-proof-batch-wizard.html', 'insights/timer-batch.html', 'current/getgo-fonts/getgo-compare-master-topology.html', 'current/dialogs/font-glyph-inventory-tabs.html', 'insights/callback-errors.html', 'current/models/glyph-review-form.html', 'insights/contour-scene.html', 'retained-catalogue/categories/layouts.html', 'current/graphics/glyph-mark-colour-board.html', 'retained-catalogue/recipes/glyphs_tabular_figures.html', 'current/widgets/glyph-spacing-offset.html', 'elastic-component-graphs.html', 'current/models/glyph-metadata-tree.html', 'retained-catalogue/categories/embedded.html', 'echopy-native-examples.html', 'spinbox-worksheets.html', 'retained-catalogue/categories/xmlpatterns.html', 'current/tools/import-kerning-pair-list.html', 'retained-catalogue/recipes/round_coordinates.html', 'current/getgo-fonts/getgo-masters-axes-and-instances.html', 'insights/signal-lifetime.html', 'current/text/font-review-notes.html', 'current/widgets/glyph-proof-groups.html', 'current/models/glyph-metadata-outline.html', 'current/drag-and-drop/index.html', 'current/getgo-fonts/getgo-sidebearings-from-h.html', 'current/tools/font-name-encoding-audit.html', 'current/widgets/script-icon-browser.html', 'glyph-character-map.html', 'current/models/glyph-sorting-and-filtering-with-dates.html', 'index.html', 'current/widgets/font-units-calculator.html', 'insights/glyph-list.html', 'current/getgo-fonts/getgo-widen-two-glyphs.html', 'insights/contour-canvas.html', 'current/tools/glyph-name-completion-with-focus.html', 'current/index.html', 'current/windows/index.html', 'current/tools/glyph-spacing-worksheet-frameless.html', 'current/text/feature-code-draft.html', 'current/graphics/index.html', 'current/drag-and-drop/deferred-glyph-report-drag.html', 'insights/owned-key-filter.html', 'current/getgo-fonts/getgo-export-a-ttf-geometry-subset.html', 'frontend-notices.html', 'insights/worker-glyph-queue.html', 'current/models/glyph-name-filter.html', 'retained-catalogue/categories/corelib.html', 'insights/sandbox-settings.html', 'current/contours/index.html', 'current/getgo-fonts/getgo-outline-pens-and-intersections.html', 'current/tools/saved-proof-sample.html', 'retained-catalogue/categories/tools.html', 'retained-catalogue/recipes/layer_backup.html', 'spacing-worksheets.html', 'retained-catalogue/categories/widgets.html', 'retained-catalogue/insights.html', 'current/tools/font-reference-image-viewer-bounded-zoom.html', 'current/tools/index.html', 'current/models/glyph-proof-worksheet.html', 'insights/owned-repl.html', 'current/graphics/glyph-review-cards.html', 'current/drag-and-drop/draggable-glyph-names.html', 'current/text/calendar-proof-builder.html', 'current/widgets/index.html', 'current/getgo-fonts/getgo-name-a-disposable-derivative.html', 'retained-catalogue/categories/mainwindows.html', 'topics.html', 'retained-catalogue/categories/database.html', 'retained-catalogue/getgo.html', 'current/models/glyph-inventory-xml.html', 'retained-catalogue/categories/graphics-painting.html', 'current/tools/editable-glyph-tree.html', 'current/models/glyph-filter-model-with-date-range.html', 'current/tools/copy-layers-from-font.html', 'current/tools/component-dependency-graph-degree-forces.html', 'current/tools/pair-proof-generator.html', 'current/widgets/script-palette-roles.html', 'current/graphics/glyph-variant-feature-graph.html', 'current/widgets/glyph-sketch-pad.html', 'current/widgets/glyph-character-map-styles.html', 'current/designer/index.html', 'current/dialogs/index.html', 'current/getgo-fonts/getgo-kerning-and-classes-report.html', 'current/models/glyph-mark-colours.html', 'current/models/glyph-review-priorities.html', 'retained-catalogue/categories/designer.html', 'current/tools/glyph-spacing-worksheet.html', 'current/text/index.html', 'retained-catalogue/categories/gstreamer.html', 'current/drag-and-drop/glyph-pair-board.html', 'current/models/glyph-metrics-model.html', 'current/widgets/glyph-metrics-and-revisions.html', 'contribute.html', 'insights/loaded-glyph-form.html', 'current/contours/node-table.html', 'guides/pre-integration.html', 'current/windows/unicode-issues-dock.html', 'current/dialogs/expandable-glyph-search.html', 'glyph-pattern-lab.html', 'retained-catalogue/recipes/sidebearings_from_reference.html', 'current/text/script-snippet-notebook.html', 'retained-catalogue/samples.html', 'current/tools/glyph-snapshot-console.html', 'current/widgets/glyph-metrics-and-revisions-detailed.html', 'current/widgets/glyph-spacing-offset-stacked.html', 'insights/index.html', 'current/tools/glyph-name-completion.html', 'current/designer/em-star-polygon.html', 'current/tools/path-problem-report.html', 'retained-catalogue/categories/richtext.html', 'retained-catalogue/index.html', 'retained-catalogue/recipes/glyph_actions_batch.html', 'licenses.html', 'retained-catalogue/categories/qml.html', 'current/tools/localized-font-names.html', 'current/tools/component-dependency-graph.html', 'current/tools/find-font-source-files-bytes.html', 'current/models/glyph-filter-model-with-local-dates.html', 'insights/compiled-slot-exposure.html', 'current/dialogs/proof-text-coverage-dialog.html', 'current/tools/apply-unicode-map.html', 'current/tools/layer-metric-comparison.html', 'slider-spacing-offsets.html', 'current/models/glyph-coverage-grid.html', 'insights/metric-controls.html', 'current/forms/glyph-metrics-form.html', 'retained-catalogue/categories/charts.html', 'current/tools/kerning-copy-rules.html', 'retained-catalogue/recipes/anchors_from_bounds.html', 'current/text/font-handoff-letter.html', 'current/drawing/scale-with-stem-compensation.html', 'current/widgets/glyph-character-map.html', 'current/tools/editable-glyph-outline.html', 'current/widgets/glyph-modification-calendar-with-formats.html', 'retained-catalogue/categories/multimedia.html', 'retained-catalogue/categories/draganddrop.html', 'retained-catalogue/categories/tutorials.html', 'current/contours/node-slope-and-handles.html', 'retained-catalogue/recipes/index.html', 'insights/metrics-table.html', 'retained-catalogue/categories/dialogs.html', 'insights/owned-dock.html', 'retained-catalogue/categories/itemviews.html', 'current/drag-and-drop/font-drop-inspector.html', 'current/drawing/stem-blend.html', 'retained-catalogue/categories/remoteobjects.html', 'retained-catalogue/recipes/glyphs_path_report.html'})
        text = " ".join(row["text"] for row in search["docs"])
        for term in ['Glyph Name Filter', 'Glyph Name Pattern Lab', '299', '148', '151', 'GetGo']:
            self.assertIn(term, text)

    def test_attribution_downloads_are_exact_and_no_private_payload_is_published(self):
        for name in ['NOTICE', 'LICENSE-APACHE-2.0']:
            self.assertEqual((ROOT / name).read_bytes(), (SITE / 'assets' / name).read_bytes())
        self.assertTrue((SITE / '.nojekyll').is_file())
        private_markers = (b'/Users/', b'/Volumes/', b'/private/', b'ghp_', b'github_pat_', b'-----BEGIN PRIVATE KEY-----')
        sources = [path.read_bytes() for folder in ('src', 'Scripts', 'glyphs', 'examples') if (ROOT / folder).is_dir() for path in (ROOT / folder).rglob('*.py')]
        for path in SITE.rglob('*'):
            if path.is_file():
                self.assertNotIn('.DS_Store', path.parts)
                self.assertNotIn(path.suffix, ('.py', '.pyi', '.vfpy', '.whl', '.zip'))
                payload = path.read_bytes()
                for marker in private_markers:
                    self.assertFalse(marker in payload.replace(b"/private/var", b""), (path, marker))
                for source in sources:
                    if len(source) > 80:
                        self.assertFalse(source in payload, path)

    def test_workflow_builds_every_main_push_and_requalifies_immutable_output(self):
        workflow = yaml.safe_load((ROOT / '.github/workflows/docs.yml').read_text())
        events = workflow.get('on', workflow.get(True))
        self.assertEqual(events['push'], {'branches': ['main']})
        self.assertNotIn('concurrency', workflow)
        build = workflow['jobs']['build']
        verify = workflow['jobs']['qualify-generated-output']
        self.assertNotIn('concurrency', build)
        self.assertEqual(verify['needs'], 'build')
        self.assertEqual(build['outputs']['epoch'], '${{ steps.epoch.outputs.value }}')
        for job, epoch in ((build, '${{ steps.epoch.outputs.value }}'), (verify, '${{ needs.build.outputs.epoch }}')):
            build_step = next(s for s in job['steps'] if s.get('run') == 'sh src_docs/build.sh')
            self.assertEqual(build_step['env']['SOURCE_DATE_EPOCH'], epoch)
        self.assertEqual(verify['steps'][0]['with']['ref'], '${{ needs.build.outputs.sha }}')
        self.assertEqual(verify['permissions'], {'contents': 'read', 'pages': 'write'})
        for job in (build, verify):
            runs = '\n'.join(step.get('run', '') for step in job['steps'])
            self.assertIn('sh src_docs/build.sh', runs)
            self.assertIn('--require-hashes -r src_docs/requirements.txt', runs)
        self.assertIn('git diff --exit-code HEAD -- docs', '\n'.join(s.get('run', '') for s in verify['steps']))
        self.assertIn('git ls-files --others -- docs', '\n'.join(s.get('run', '') for s in verify['steps']))
        self.assertFalse(any('publish.sh' in s.get('run', '') for s in verify['steps']))

    def test_public_request_uses_qualified_output_and_avoids_redundant_push_build(self):
        workflow = yaml.safe_load((ROOT / '.github/workflows/docs.yml').read_text())
        job = workflow['jobs']['qualify-generated-output']
        request = next(s for s in job['steps'] if s.get('name') == 'Request branch-source Pages build')
        self.assertEqual(request['if'], "github.event_name == 'workflow_dispatch' || needs.build.outputs.sha != github.sha")
        self.assertEqual(request['env']['OUTPUT_SHA'], '${{ needs.build.outputs.sha }}')
        self.assertEqual(request['run'], 'sh src_docs/request-pages.sh "$OUTPUT_SHA"')

    def test_complete_content_and_source_identity(self):
        import hashlib
        import ast
        from urllib.parse import quote
        menus = sorted((ROOT / 'Scripts').glob('*/*.py'))
        self.assertEqual(len(menus), 100)
        pages = [p for p in (ROOT / 'src_docs/md/current').glob('*/*.md') if p.name != 'index.md']
        self.assertEqual(len(pages), 100)
        descriptions = []
        for source in menus:
            data = source.read_bytes()
            description = ast.get_docstring(ast.parse(data))
            self.assertTrue(description and len(description.strip()) > 20, source)
            sha = hashlib.sha256(data).hexdigest()
            matches = [p for p in pages if sha in p.read_text()]
            self.assertEqual(len(matches), 1, source)
            text = matches[0].read_text()
            self.assertIn(description, text)
            self.assertIn(quote(source.relative_to(ROOT).as_posix(), safe='/'), text)
            self.assertRegex(text, r'/blob/[0-9a-f]{40}/')
            self.assertNotIn('codeinclude', text)
