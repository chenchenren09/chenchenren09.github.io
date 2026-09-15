# Content provenance

## Approved research-profile revision

The homepage now presents the agreed research identity, a supporting sentence, three CV-supported research themes, and eight representative publications selected by `selected_order`. All 30 visible published papers are generated separately at `publications.html`; no bibliographic fields or DOI links were changed. Working papers remain hidden. Appointments and education remain prominent, with concise academic service and mentoring. Reviewing and detailed teaching records are not rendered. Both email links now use mailto; missing profile URLs are omitted.

Date audit: the current DOCX, supplied PDF, linked PDF, and YAML agree on Carnegie Science appointment 2023–2026, Carnegie mentoring 2023–now (YAML: 2023–present), iN-Net Research Fellow 2026–present, and incoming Bonn from 15 November 2026. The mentoring end date is unresolved; the public summary avoids asserting ongoing mentoring. These distinct role dates were not silently reconciled.

Research source wording differs: the current DOCX says “across regions”; the PDF and former research YAML say “across places and social groups.” The approved short introduction uses the sources’ shared structural-conditions framing. Methods use geospatial analysis, explicitly supported by the CV, rather than making a broader methodological claim.

Original CV and portrait assets remain unchanged. The dates and details below are historical records of earlier revisions.

## Previous update

The website now links an exact copy of the user-supplied six-page `Curriculum vitae_Chenchen Ren.pdf` (14 September 2026), with SHA-256 `e01ae2e9ebf26e699ae170ab06fdd043496fccc31b07c2043bd2a2393a7668fd`. It uses the supplied portrait without altering the source image. Research interests are the two original paragraphs from that PDF, with only line wrapping normalized. Working papers and all work-in-progress headings are omitted from the HTML; the original CV PDF remains intact. GitHub has been removed. The direct LinkedIn profile was matched using the Carnegie Science affiliation and the same published papers. Publication links were added through Crossref, publisher, and author-repository verification; see [LINK_CHECKS.md](LINK_CHECKS.md).

The notes below describe the initial build and are retained as historical provenance; the current update supersedes its placeholder, research-summary, missing-link, and PDF notes.


Primary factual source: `Curriculum vitae_Chenchen Ren.docx`, the only file present in the supplied folder at initial inspection on 14 September 2026.

Original SHA-256:

```text
4a80e88fd2844b07c43799557770e5b82e92e82fa8ce1391e6b803319673ec7c
```

The site content was transcribed or summarized from this CV. It does not use the reference academics' biographies, publications, affiliations, or dates. The original Word file is not modified by either the site builder or the optional PDF typesetter.

| Website content | CV source |
| --- | --- |
| Name, degree, pronouns, incoming Bonn role, email | CV heading |
| Four research themes and methods | Research Interests, Publications, Working Papers, Skills |
| 30 published-paper entries | Publications |
| Two working papers, each under review | Working Papers |
| Appointments and education | Academic Appointments, Education |
| Teaching and mentoring | Teaching and Mentoring Experience |
| Editorial boards, iN-Net roles, reviewing | Public and Professional Service |
| AGU session convener | Conference |
| Google Scholar and iN-Net URLs | Embedded hyperlinks in the DOCX |

The four research themes are editorial groupings, not claims that these are named projects or research groups. Grants, awards, thesis mentorship details, and the complete conference history remain available in the CV PDF rather than adding more website sections.

## Preserved distinctions and missing information

- Bonn is **incoming from 15 November 2026**, not a current appointment as of this build.
- Carnegie Science's appointment is dated **2023–2026**. The separate mentoring entry says **2023-now**, rendered as **2023–present**. The supplied dates have not been reconciled by assumption.
- All 30 entries in the CV's Publications section are listed as published. No accepted/in-press status was inferred, including for the 2026 entries.
- The two papers in Working Papers are marked **Under review** without invented years.
- Co-first authorship is preserved for the crop-diversity inequality paper and the land-consolidation paper.
- The CV contains no DOI or paper-specific journal URLs. All initial publication `url` fields are null.
- The Scholar URL retains the exact source account ID and domain; language/session parameters were removed.
- GitHub, LinkedIn, an institutional profile URL, and a photo were absent. Their placeholders are explicit. No institutional department, lab membership, address, or external profile has been guessed.
- Author order and initials are preserved. `Ren C.` is displayed consistently as `Ren, C.`. Citation punctuation is normalized, and co-first notation is displayed separately.
- The working-paper author spellings `Davis, F. K.` and `Zhu, Y. Gu, B.` follow the supplied CV, including its unusual initial order/punctuation. Verify these against the manuscripts before changing them.
- Journal names follow the supplied CV, including `Earth Future` in reviewer activities. They were not silently corrected through external sources.

## PDF

`assets/files/chenchen-ren-cv.pdf` is a separately typeset, five-page copy built from the CV paragraphs. It preserves the CV's textual content and embedded profile links, with normalized whitespace and consistent rendering of Ren's name. Word formatting and pagination are not reproduced exactly. Word's export controls were unavailable to this session, so the local ReportLab typesetter was used. For exact layout fidelity, replace it with a Word-exported PDF using the README instructions.

## Design references

- [Min Liu](https://sites.google.com/view/min-liu/%E9%A6%96%E9%A1%B5): concise profile and academic lists.
- [David Wuepper](https://sites.google.com/view/davidwuepper): direct academic navigation and prominent contact information.

These pages were consulted through web retrieval for structure and content organization. Their designs were not copied, and no screenshots or assets were reused.
