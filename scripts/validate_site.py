"""Validate generated output and the routine content-editing workflow.

Run after python build.py. Uses only the builder's existing PyYAML dependency.
No source content, network resources, or PDF files are modified.
"""
from collections import Counter
from copy import deepcopy
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
import re
import json
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import build


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids, self.links, self.css = [], [], []
        self.publications = self.highlighted_names = self.h1s = 0
        self.in_strong = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag in {'a', 'link', 'script', 'img'}:
            value = attrs.get('href', attrs.get('src'))
            if value:
                self.links.append(value)
        if tag == 'link' and attrs.get('rel') == 'stylesheet':
            self.css.append(attrs['href'])
        if tag == 'li' and attrs.get('class') == 'publication':
            self.publications += 1
        if tag == 'h1':
            self.h1s += 1
        if tag == 'strong':
            self.in_strong = True
        if tag == 'img':
            assert attrs.get('alt'), 'Every image needs descriptive alt text.'

    def handle_endtag(self, tag):
        if tag == 'strong':
            self.in_strong = False

    def handle_data(self, text):
        if self.in_strong and text == 'Ren, C.':
            self.highlighted_names += 1


def expect_content_error(callback):
    try:
        callback()
    except build.ContentError:
        return
    raise AssertionError('Expected a helpful content validation error.')


def validate():
    output = ROOT / 'docs'
    all_papers = build.load_content('publications.yaml')
    papers = build.visible_publications(all_papers)
    selected = build.selected_publications(all_papers)
    pages = {}
    for filename in ['index.html', 'publications.html']:
        page_text = (output / filename).read_text(encoding='utf-8')
        page = Page()
        page.feed(page_text)
        pages[filename] = (page, page_text)
    for filename, (page, page_text) in pages.items():
        assert page.h1s == 1, 'Expected exactly one main heading.'
        assert len(page.ids) == len(set(page.ids)), 'Duplicate HTML IDs.'
        assert page.css == ['assets/css/style.css'], 'Use a single main stylesheet.'
        assert not re.search(r'\$(?:[a-z_]+|\{[a-z_]+\})', page_text), 'Unresolved template slots.'
        assert 'Link to be added' not in page_text and 'data-copy-email' not in page_text
        for link in page.links:
            parsed = urlsplit(link)
            if parsed.scheme:
                assert parsed.scheme in {'https', 'http', 'mailto'}, f'Invalid link scheme: {link}'
                continue
            path = (output / unquote(parsed.path or filename)).resolve()
            assert path.is_relative_to(output.resolve()) and path.is_file(), f'Missing asset: {link}'
            if parsed.fragment:
                target = path.name
                assert target in pages and parsed.fragment in pages[target][0].ids, f'Missing cross-page target: {link}'
        expected = selected if filename == 'index.html' else papers
        assert page.publications == len(expected), 'Publication lost or duplicated.'
        assert page.highlighted_names == len(expected) + int(filename == 'publications.html' and any(p['status'] == 'published' for p in papers))
        for paper in expected:
            assert paper['title'] in unescape(page_text), f'Missing title: {paper["title"]}'
            if paper.get('url'):
                assert paper['url'] in unescape(page_text), 'Missing DOI link.'
        for hidden in all_papers['publications']:
            if not hidden.get('visible', True):
                assert hidden['title'] not in unescape(page_text), 'Hidden paper leaked.'
        person = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', page_text, re.S).group(1))
        assert person['@type'] == 'Person' and person['name'] == build.load_content('profile.yaml')['name']
        for marker in ['rel="icon"', 'property="og:title"', 'property="og:description"', 'name="twitter:card"']:
            assert marker in page_text, f'Missing metadata: {marker}'
    home_text = pages['index.html'][1]
    research = build.load_content('research.yaml')
    assert research['intro'] in unescape(home_text)
    for theme in research['themes']:
        assert theme['title'] in unescape(home_text) and theme['description'] in unescape(home_text)
    assert 'Journal reviewing' not in home_text
    assert home_text.count('href="mailto:') == 1
    assert 'mailto:' not in build.profile_fragments(build.load_content('profile.yaml'))['home']
    counts = Counter(p['status'] for p in papers)
    assert ('Accepted / in press' in pages['publications.html'][1]) == bool(counts['accepted'])
    for source in (ROOT / 'assets').rglob('*'):
        if source.is_file():
            copy = output / source.relative_to(ROOT)
            assert copy.read_bytes() == source.read_bytes(), f'Stale generated asset: {copy}'

    # Exercise common future edits in memory; no sample data enters the site.
    sample = deepcopy(papers[0])
    sample.update(status='accepted', year=None, title='Validation <example> & text', url='https://example.org/paper')
    markup = build.publications_fragment({'publications': [sample]})
    assert 'Accepted / in press' in markup and '&lt;example&gt; &amp; text' in markup
    assert 'href="https://example.org/paper"' in markup
    assert build.publications_fragment({'publications': []}) == ''
    sample['visible'] = False
    assert build.publications_fragment({'publications': [sample]}) == ''
    sample['visible'] = True
    sample['status'] = 'in-press-typo'
    expect_content_error(lambda: build.publication_html(sample))
    expect_content_error(lambda: build.web_url('javascript:alert(1)', 'test.url'))
    expect_content_error(lambda: build.local_asset('../missing.pdf', 'test.file', {'.pdf'}))
    expect_content_error(lambda: build.yaml.load('name: A\nname: B\n', Loader=build.UniqueKeyLoader))
    profile = build.load_content('profile.yaml')
    profile['appointment'] = 'Validation appointment'
    profile['links'].append({'label': 'Validation profile', 'url': 'https://example.org/profile', 'show_on_home': True})
    fragments = build.profile_fragments(profile)
    assert 'Validation appointment' in fragments['home']
    assert 'https://example.org/profile' in fragments['home'] and 'https://example.org/profile' in fragments['contact']
    profile['links'][-1]['url'] = None
    assert 'Validation profile' not in build.profile_fragments(profile)['contact']
    ranked = deepcopy(papers[0])
    ranked['selected_order'] = 1
    expect_content_error(lambda: build.selected_publications({'publications': [ranked, deepcopy(ranked)]}))
    ranked['selected_order'] = None
    assert build.selected_publications({'publications': [ranked]}) == []
    profile['site_url'] = 'https://example.org/research/'
    metadata = build.page_metadata(profile, 'publications.html', 'Publications', 'Research')
    assert 'https://example.org/research/publications.html' in metadata
    assert 'https://example.org/research/assets/images/chenchen-ren.jpg' in metadata
    print(f'PASS: two pages, {len(selected)} selected/{len(papers)} full papers, cross-page links, metadata, mailto, and content editing.')


if __name__ == '__main__':
    validate()
