"""Create a separately typeset PDF from every nonempty paragraph in the source CV.

This preserves text and hyperlinks, not Word's exact pagination or formatting.
Usage: python scripts/export_cv_pdf.py SOURCE.docx OUTPUT.pdf
Requires reportlab; never writes to the DOCX.
"""
import argparse
import hashlib
import re
from html import escape
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
R = '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}'
HEADINGS = {
    'Research Interests', 'Academic Appointments', 'Education', 'Publications',
    'Working Papers', 'Teaching and Mentoring Experience', 'Ph.D. Thesis Mentorship',
    'Grants', 'Conference', 'Public and Professional Service', 'Honors and Awards', 'Skills',
}


class UnsplitParagraph(Paragraph):
    """Move a whole paragraph to the next page instead of splitting citations."""

    def split(self, available_width, available_height):
        return []


def clean(text):
    return re.sub(r'\s+', ' ', text.replace('\ufeff', '')).strip()


def render_pdf(source, destination):
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    with ZipFile(source) as archive:
        document = ET.fromstring(archive.read('word/document.xml'))
        rels = ET.fromstring(archive.read('word/_rels/document.xml.rels'))
        links = {r.get('Id'): r.get('Target') for r in rels if r.get('TargetMode') == 'External'}

    body = ParagraphStyle('body', fontName='Times-Roman', fontSize=10.5, leading=14, spaceAfter=6)
    heading = ParagraphStyle('heading', parent=body, fontName='Helvetica-Bold', fontSize=12,
                             leading=16, spaceBefore=13, spaceAfter=7, keepWithNext=True)
    title = ParagraphStyle('title', parent=body, fontName='Times-Bold', fontSize=24,
                           leading=29, spaceAfter=8, alignment=TA_CENTER, keepWithNext=True)
    subtitle = ParagraphStyle('subtitle', parent=body, alignment=TA_CENTER, keepWithNext=True)
    paired = ParagraphStyle('paired', parent=body, keepWithNext=True)
    story = []
    nonempty_index = 0
    paragraphs = [p for p in document.iter(W + 'p') if clean(''.join(t.text or '' for t in p.iter(W + 't')))]
    for index, paragraph in enumerate(paragraphs):
        text = clean(''.join(t.text or '' for t in paragraph.iter(W + 't')))
        if not text:
            continue
        # Escape source text before using ReportLab's small markup vocabulary.
        markup = escape(text)
        for hyperlink in paragraph.iter(W + 'hyperlink'):
            label = clean(''.join(t.text or '' for t in hyperlink.iter(W + 't')))
            url = links.get(hyperlink.get(R + 'id'))
            if label and url and url.startswith(('https://', 'http://', 'mailto:')):
                markup = markup.replace(escape(label), f'<link href="{escape(url, quote=True)}" color="#173f59">{escape(label)}</link>', 1)
        style = title if nonempty_index == 0 else subtitle if nonempty_index < 4 else heading if text in HEADINGS else body
        next_text = clean(''.join(t.text or '' for t in paragraphs[index + 1].iter(W + 't'))) if index + 1 < len(paragraphs) else ''
        # Keep thesis titles with mentee names, degrees with institutions,
        # and certificates with standalone dates across page boundaries.
        if style == body and (next_text.startswith('(') or next_text == 'in Cropland'
                              or re.fullmatch(r'\d{4}(?:[-–]\d{4})?', next_text)
                              or next_text in {'Zhejiang University, China', 'Shandong Agricultural University, China'}):
            style = paired
        if style in (body, paired):
            markup = re.sub(r'Ren,?\s*C\.', '<b>Ren, C.</b>', markup)
        story.append(UnsplitParagraph(markup, style))
        nonempty_index += 1

    destination.parent.mkdir(parents=True, exist_ok=True)

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#56636d'))
        canvas.drawString(48, 27, 'Chenchen Ren | Curriculum vitae')
        canvas.drawRightString(A4[0] - 48, 27, str(doc.page))
        canvas.restoreState()

    pdf = SimpleDocTemplate(str(destination), pagesize=A4, leftMargin=48, rightMargin=48,
                            topMargin=42, bottomMargin=45, title='Chenchen Ren — Curriculum vitae',
                            author='Chenchen Ren')
    pdf.build(story, onFirstPage=footer, onLaterPages=footer)
    if hashlib.sha256(source.read_bytes()).hexdigest() != before:
        raise RuntimeError('The source CV changed during PDF generation.')
    print(f'Created {destination}; included {nonempty_index} source paragraphs. DOCX unchanged.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    if args.destination.exists():
        parser.error('Output already exists. Choose a new filename so the previous PDF is preserved.')
    render_pdf(args.source, args.destination)
