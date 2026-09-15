#!/usr/bin/env python3
"""Build the static website: edit content/*.yaml, then run python build.py.

Only PyYAML is required. HTML uses Python's standard-library string.Template.
Paths are relative to this script, so it also works from another directory.
The original DOCX is never opened or modified by this builder.
"""
from datetime import date
from html import escape
from pathlib import Path
import re
import json
import shutil
from string import Template
import sys
from urllib.parse import urlsplit

try:
    import yaml
except ImportError:
    raise SystemExit('PyYAML is missing. Run: python -m pip install -r requirements.txt')

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / 'content'
TEMPLATES = ROOT / 'templates'
OUTPUT = ROOT / 'docs'


class ContentError(ValueError):
    """A content problem reported with an editable field name."""


class UniqueKeyLoader(yaml.SafeLoader):
    """Reject duplicate fields instead of silently losing the earlier value."""


def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise ContentError(f'Duplicate YAML key {key!r}, line {key_node.start_mark.line + 1}.')
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def load_content(filename):
    try:
        data = yaml.load((CONTENT / filename).read_text(encoding='utf-8'), Loader=UniqueKeyLoader)
    except (yaml.YAMLError, ContentError) as error:
        raise ContentError(f'{filename}: {error}') from error
    if not isinstance(data, dict):
        raise ContentError(f'{filename} must contain named fields.')
    return data


def text_field(data, key, context, optional=False):
    value = data.get(key)
    if optional and value is None:
        return ''
    if not isinstance(value, str) or not value.strip():
        raise ContentError(f'{context}.{key}: enter nonempty text (quote numeric dates).')
    return value.strip()


def entries(data, key, context):
    value = data.get(key, [])
    if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
        raise ContentError(f'{context}.{key}: expected a list of entries.')
    return value


def html(text):
    return escape(str(text), quote=True)


def render(template_name, **values):
    return Template((TEMPLATES / template_name).read_text(encoding='utf-8')).substitute(values)


def web_url(value, context):
    if value is None or value == '':
        return ''
    if not isinstance(value, str):
        raise ContentError(f'{context}: use a complete https:// URL or null.')
    parsed = urlsplit(value)
    if parsed.scheme not in ('http', 'https') or not parsed.netloc or any(c.isspace() for c in value):
        raise ContentError(f'{context}: use a complete http(s) URL, without spaces.')
    return value


def local_asset(value, context, suffixes):
    if not isinstance(value, str):
        raise ContentError(f'{context}: enter a path such as assets/files/cv.pdf.')
    path = (ROOT / value).resolve()
    if not path.is_relative_to((ROOT / 'assets').resolve()) or not path.is_file():
        raise ContentError(f'{context}: file not found inside assets/: {value}')
    if path.suffix.lower() not in suffixes:
        raise ContentError(f'{context}: expected one of {sorted(suffixes)}.')
    return path.relative_to(ROOT).as_posix()


def anchor(label, url, css_class=''):
    attribute = f' class="{html(css_class)}"' if css_class else ''
    return f'<a{attribute} href="{html(url)}">{html(label)}</a>'


def profile_fragments(profile):
    fields = {key: html(text_field(profile, key, 'profile')) for key in (
        'name', 'degree', 'appointment', 'appointment_detail', 'research_label',
        'intro', 'meta_description')}
    pronouns = text_field(profile, 'pronouns', 'profile', optional=True)
    fields['pronouns'] = f'<span class="pronouns">({html(pronouns)})</span>' if pronouns else ''
    cv = profile.get('cv')
    if not isinstance(cv, dict):
        raise ContentError('profile.cv: expected file and description fields.')
    cv_file = local_asset(cv.get('file'), 'profile.cv.file', {'.pdf'})
    home_links = [f'<a class="button" href="{html(cv_file)}">View CV <span class="file-type">PDF</span></a>']
    contact_links, scholar = [], ''
    for link in entries(profile, 'links', 'profile'):
        label = text_field(link, 'label', 'profile.links')
        url = web_url(link.get('url'), f'profile.links.{label}')
        on_home = link.get('show_on_home', False)
        if not isinstance(on_home, bool):
            raise ContentError(f'profile.links.{label}.show_on_home: use true or false.')
        if url:
            contact_links.append(anchor(label, url))
            if on_home:
                home_links.append(anchor(label, url))
            if label == 'Google Scholar':
                scholar = anchor(label, url, 'section-link')
    email = text_field(profile, 'email', 'profile', optional=True)
    if email:
        if not re.fullmatch(r'[^\s@<>?&#]+@[^\s@<>?&#]+\.[^\s@<>?&#]+', email):
            raise ContentError('profile.email: enter a plain email address, without mailto:.')
        contact_email = anchor(email, f'mailto:{email}', 'contact-email')
    else:
        contact_email = ''
    fields['links'] = '\n'.join(home_links)
    photo = profile.get('photo', {})
    if not isinstance(photo, dict):
        raise ContentError('profile.photo: expected file, alt, and initials fields.')
    if photo.get('file'):
        file = local_asset(photo['file'], 'profile.photo.file', {'.jpg', '.jpeg', '.png', '.webp', '.avif'})
        alt = text_field(photo, 'alt', 'profile.photo')
        portrait = f'<figure class="portrait"><img src="{html(file)}" alt="{html(alt)}" width="400" height="500"></figure>'
    else:
        portrait = ''
    contact = contact_email + '<div class="contact-links">' + '\n'.join(contact_links) + '</div>'
    return dict(name=fields['name'], meta_description=fields['meta_description'],
                home=render('home.html', **fields), portrait=portrait, contact=contact,
                scholar_link=scholar, cv_file=html(cv_file),
                cv_description=html(text_field(cv, 'description', 'profile.cv')))


def research_fragments(research):
    themes = [render('theme.html', number=f'{i:02}',
                     title=html(text_field(theme, 'title', 'research.themes')),
                     description=html(text_field(theme, 'description', 'research.themes')))
              for i, theme in enumerate(entries(research, 'themes', 'research'), 1)]
    methods = research.get('methods')
    if not isinstance(methods, list) or not methods or any(not isinstance(m, str) or not m.strip() for m in methods):
        raise ContentError('research.methods: enter a list of methods.')
    return dict(research_heading=html(text_field(research, 'heading', 'research')),
                research_intro='<p>' + html(text_field(research, 'intro', 'research')) + '</p>',
                research_themes='\n'.join(themes), research_methods=html(' · '.join(methods)))


def publication_html(paper, heading_level=4):
    title = text_field(paper, 'title', 'publication')
    authors = text_field(paper, 'authors', title)
    year, status = paper.get('year'), paper.get('status')
    if status not in {'published', 'accepted', 'working'}:
        raise ContentError(f'{title}: status must be published, accepted, or working.')
    if year is not None and (type(year) is not int or not 1000 <= year <= 9999):
        raise ContentError(f'{title}: year must be a four-digit number or null.')
    if status == 'published' and year is None:
        raise ContentError(f'{title}: published papers require a year.')
    journal = text_field(paper, 'journal', title, optional=status != 'published')
    details = text_field(paper, 'details', title, optional=True)
    note = text_field(paper, 'note', title, optional=True)
    if status == 'accepted' and not note:
        note = 'Accepted / in press'
    if status == 'working' and not note:
        note = 'Working paper'
    url = web_url(paper.get('url'), f'{title}.url')
    co_first = paper.get('co_first_author', False)
    if not isinstance(co_first, bool):
        raise ContentError(f'{title}.co_first_author: use true or false.')
    metadata = ', '.join(part for part in (journal, details) if part)
    metadata = ' · '.join(part for part in (metadata, str(year) if year else '', note) if part)
    # Highlight only the exact author token, not partial names or title text.
    authors_markup = re.sub(r'(?<![A-Za-z])Ren,\s*C\.(?![A-Za-z])', '<strong>Ren, C.</strong>', html(authors))
    return render('publication.html', heading_level=heading_level, title=anchor(title, url) if url else html(title),
                  authors=authors_markup, metadata=html(metadata),
                  contribution='<p class="equal-contribution">Co-first author</p>' if co_first else '')


def visible_publications(data):
    """Retain hidden drafts in source YAML without including them in the page."""
    papers = entries(data, 'publications', 'publications')
    for paper in papers:
        if not isinstance(paper.get('visible', True), bool):
            raise ContentError('publication.visible: use true or false.')
    return [paper for paper in papers if paper.get('visible', True)]


def publications_fragment(data):
    papers = visible_publications(data)
    rendered = [(paper, publication_html(paper, 4 if paper["status"] == "published" else 3)) for paper in papers]
    sections = []
    for status, heading in [('published', 'Published papers'), ('accepted', 'Accepted / in press'), ('working', 'Working papers')]:
        selected = [(paper, markup) for paper, markup in rendered if paper['status'] == status]
        if not selected:
            continue
        section = f'<section class="publication-category"><h2 class="subsection-title">{heading}</h2>'
        if status == 'published':
            section += '<p class="publication-note"><strong>Ren, C.</strong> is highlighted throughout. Equal-contribution papers are marked “co-first author.”</p>'
            for year in sorted({paper['year'] for paper, _ in selected}, reverse=True):
                items = '\n'.join(markup for paper, markup in selected if paper['year'] == year)
                section += f'<div class="publication-year"><h3 class="year-heading">{year}</h3><ol class="publication-list">{items}</ol></div>'
        else:
            section += '<ol class="publication-list">' + '\n'.join(markup for _, markup in selected) + '</ol>'
        sections.append(section + '</section>')
    return '\n'.join(sections)


def selected_publications(data):
    """One optional rank selects a paper; all bibliographic data stays in one place."""
    selected = []
    ranks = set()
    for paper in visible_publications(data):
        rank = paper.get('selected_order')
        if rank is None:
            continue
        if type(rank) is not int or rank < 1 or rank in ranks:
            raise ContentError('selected_order must be a unique positive integer or null.')
        if paper.get('status') != 'published':
            raise ContentError('Only published papers may be selected for the homepage.')
        ranks.add(rank)
        selected.append(paper)
    return sorted(selected, key=lambda p: p['selected_order'])


def experience_fragment(data):
    fragments = []
    for key, title in [('appointments', 'Academic appointments'), ('education', 'Education')]:
        items = []
        for entry in entries(data, key, 'experience'):
            fields = {name: html(text_field(entry, name, f'experience.{key}')) for name in ('dates', 'title', 'institution')}
            description = text_field(entry, 'description', f'experience.{key}', optional=True)
            fields['description'] = f'<p>{html(description)}</p>' if description else ''
            items.append(render('timeline-entry.html', **fields))
        if items:
            fragments.append(f'<h3 class="subsection-title">{html(title)}</h3><div class="timeline">' + '\n'.join(items) + '</div>')
    service = []
    for entry in entries(data, 'service', 'experience'):
        title = text_field(entry, 'title', 'experience.service')
        dates = text_field(entry, 'dates', 'experience.service', optional=True)
        label = title + (f' · {dates}' if dates else '')
        organization = text_field(entry, 'organization', 'experience.service')
        service.append(f'<li><strong>{html(label)}</strong><br>{html(organization)}</li>')
    if service:
        fragments.append('<h3 class="subsection-title">Academic Service</h3><ul class="service-list">' + '\n'.join(service) + '</ul>')
    mentoring = text_field(data, 'mentoring_summary', 'experience', optional=True)
    if mentoring:
        fragments.append('<h3 class="subsection-title">Mentoring</h3><p class="mentoring-summary">' + html(mentoring) + '</p>')
    return '\n'.join(fragments)


def page_metadata(profile, filename, title, description):
    """Do not invent a public domain. Absolute sharing URLs wait for site_url."""
    site_url = web_url(profile.get('site_url'), 'profile.site_url').rstrip('/')
    favicon = local_asset(profile.get('favicon'), 'profile.favicon', {'.svg', '.ico', '.png'})
    tags = [f'<link rel="icon" href="{html(favicon)}">']
    properties = {'og:type': 'profile' if filename == 'index.html' else 'website',
                  'og:title': title, 'og:description': description, 'og:site_name': profile['name']}
    person = {'@context': 'https://schema.org', '@type': 'Person', 'name': profile['name'],
              'honorificSuffix': profile['degree'], 'description': profile['intro'],
              'jobTitle': profile['appointment']}
    # An incoming role must not be represented as a current worksFor affiliation.
    if profile.get('email'):
        person['email'] = 'mailto:' + profile['email']
    person['sameAs'] = [link['url'] for link in profile.get('links', [])
                        if link.get('url') and link['label'] in {'Google Scholar', 'LinkedIn', 'Institutional profile'}]
    if site_url:
        url = site_url + '/' + filename
        properties['og:url'] = url
        tags.append(f'<link rel="canonical" href="{html(url)}">')
        person['url'] = site_url + '/'
        photo = profile.get('photo', {})
        if photo.get('file'):
            person['image'] = site_url + '/' + photo['file']
            properties['og:image'] = person['image']
            properties['og:image:alt'] = photo['alt']
            tags.append(f'<meta name="twitter:image" content="{html(person["image"])}">')
            tags.append(f'<meta name="twitter:image:alt" content="{html(photo["alt"])}">')
    tags.extend(f'<meta property="{key}" content="{html(value)}">' for key, value in properties.items())
    tags.extend([f'<meta name="twitter:card" content="summary">',
                 f'<meta name="twitter:title" content="{html(title)}">',
                 f'<meta name="twitter:description" content="{html(description)}">'])
    # Prevent text content from prematurely closing the JSON-LD script element.
    structured = json.dumps(person, ensure_ascii=False).replace('<', '\\u003c')
    tags.append(f'<script type="application/ld+json">{structured}</script>')
    return '\n  '.join(tags)


def build():
    profile = load_content('profile.yaml')
    research = load_content('research.yaml')
    publications = load_content('publications.yaml')
    experience = load_content('experience.yaml')
    fields = profile_fragments(profile)
    fields.update(research_fragments(research))
    selected = selected_publications(publications)
    fields.update(publications='<ol class="publication-list">' + '\n'.join(publication_html(p, 3) for p in selected) + '</ol>',
                  experience=experience_fragment(experience), year=date.today().year)
    bodies = {'index.html': render('index.html', **fields),
              'publications.html': render('publications.html', scholar_link=fields['scholar_link'],
                                          publications=publications_fragment(publications))}
    pages = {}
    for filename, body in bodies.items():
        title = profile['name'] + (' | Agricultural Sustainability Research' if filename == 'index.html' else ' | Publications')
        description = profile['meta_description'] if filename == 'index.html' else f"Publications by {profile['name']} on agricultural structure, resource use, sustainability, and climate resilience."
        pages[filename] = render('base.html', name=fields['name'], year=fields['year'], body=body,
                                 page_title=html(title), meta_description=html(description),
                                 metadata=page_metadata(profile, filename, title, description),
                                 back_to_top='#home' if filename == 'index.html' else '#main',
                                 publications_current=' aria-current="page"' if filename == 'publications.html' else '')
    # Validate/render everything before writing. Only generated output is updated.
    OUTPUT.mkdir(exist_ok=True)
    shutil.copytree(ROOT / 'assets', OUTPUT / 'assets', dirs_exist_ok=True)
    for filename, page in pages.items():
        (OUTPUT / filename).write_text('<!-- Generated by build.py. Edit content/ or templates/, then rebuild. -->\n' + page, encoding='utf-8')
    (OUTPUT / '.nojekyll').touch()
    print(f'Built homepage with {len(selected)} selected papers and publications.html with {len(visible_publications(publications))} papers.')
    print('Preview: python -m http.server 8000 --bind 127.0.0.1 --directory docs')


if __name__ == '__main__':
    try:
        build()
    except (ContentError, OSError, KeyError, ValueError) as error:
        print(f'Build failed: {error}', file=sys.stderr)
        sys.exit(1)
