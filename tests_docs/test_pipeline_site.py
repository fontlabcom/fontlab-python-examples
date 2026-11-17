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
PAGES = sorted(
    path.relative_to(ROOT / "src_docs/md").with_suffix(".html").as_posix()
    for path in (ROOT / "src_docs/md").rglob("*.md")
    if "includes" not in path.relative_to(ROOT / "src_docs/md").parts
)


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
        self.assertEqual(locations, set(PAGES))
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
        self.assertTrue(menus)
        pages = [p for p in (ROOT / 'src_docs/md/current').glob('*/*.md') if p.name != 'index.md']
        self.assertEqual(len(pages), len(menus))
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
            relative = source.relative_to(ROOT).as_posix()
            if "uncommitted" in text:
                self.assertIn(relative, text)
                self.assertNotIn('/blob/', text)
            else:
                self.assertIn(quote(relative, safe='/'), text)
                self.assertRegex(text, r'/blob/[0-9a-f]{40}/')
            self.assertNotIn('codeinclude', text)
