# Chenchen Ren — academic research website

A lightweight, two-page website built from editable YAML and reusable HTML templates. It uses Python 3.10+, PyYAML, one CSS file, and a small script for the footer year. No npm, React, database, analytics, cookies, trackers, or third-party scripts are needed.

**Edit content → `python build.py` → preview → commit → push.** Common updates do not require editing HTML.

## Build and preview

Open this project folder in VS Code and open a terminal. Install the only build dependency once:

```bash
python -m pip install -r requirements.txt
```

Then build and start a local preview:

```bash
python build.py
python -m http.server 8000 --bind 127.0.0.1 --directory docs
```

Open **http://127.0.0.1:8000** for the homepage and **http://127.0.0.1:8000/publications.html** for the complete publication list. Keep the server running, rebuild in another terminal after editing, and refresh your browser. Stop the server with Ctrl+C. Choose another port if 8000 is busy.

If your system uses `python3`, substitute it consistently in all commands, including dependency installation. Your existing Anaconda environment with PyYAML also works. Both generated pages can be opened directly from disk; serving `docs/` more closely matches deployment.

## Project structure

```text
content/
  profile.yaml          Name, introduction, affiliation, links, photo, CV, site URL
  research.yaml         Research introduction, three themes, methods
  publications.yaml     Full citations, DOI links, visibility, homepage selection
  experience.yaml       Appointments, education, service, mentoring summary
                        Also retains detailed records not shown on the homepage
templates/
  base.html             Shared page head, navigation, footer, and metadata slot
  index.html            Homepage sections
  publications.html     Full publication page layout
  home.html             Hero layout
  theme.html            Research theme layout
  publication.html      Publication entry shared by both pages
  timeline-entry.html   Appointment and education entry
assets/
  css/style.css         All site styling — edit this source file
  js/main.js            Footer year only; email uses ordinary mailto links
  images/               Portrait and initials favicon.svg
  files/                CV PDFs
build.py                Generates both pages and copies assets to docs/
requirements.txt        PyYAML dependency
scripts/
  validate_site.py      Cross-page links, content, metadata, and build checks
  export_cv_pdf.py      Optional PDF typesetter; not used by the website build
docs/                   Generated output, tracked for GitHub Pages
  index.html            Research profile and selected papers
  publications.html     All visible papers, grouped by year
  assets/               Generated asset copies
  .nojekyll             Serve static files without a Jekyll build
README.md               This guide
SOURCES.md              Factual sources, date questions, and editorial decisions
LINK_CHECKS.md          Earlier external link verification and access restrictions
```

Edit `content/`, `templates/`, and `assets/`, then rebuild. **Do not edit `docs/` as the source:** its HTML and asset copies are regenerated. Commit both the source and generated `docs/` files. Builds do not delete old asset files automatically.

The original Word/PDF CVs remain separate source documents. The build does not read, rewrite, or synchronize them. Word files are excluded by `.gitignore`.

## Update your affiliation and introduction

Edit `content/profile.yaml`:

- `name`, `degree`, `pronouns`: personal heading.
- `appointment`, `appointment_detail`: role and institution/date line.
- `intro`: prominent research identity sentence.
- `about`: optional text retained for future reuse; not rendered in the homepage hero.
- `meta_description`: search and sharing description.

For an appointment change, also update the corresponding history in `content/experience.yaml`. The profile and history are separate, explicit fields.

Current dates say University of Bonn **November 2026–present**, Carnegie Science appointment **2023–2026**, Carnegie mentoring **2023–present**, and iN-Net Research Fellow **2026–present**. The mentoring summary does not assert that mentoring is ongoing. See `SOURCES.md` before changing dates.

## Update research

Edit `content/research.yaml`:

- `intro`: one concise introductory paragraph.
- `themes`: a list of `title` and `description` pairs.
- `methods`: a list automatically separated by centered dots.

The three current themes summarize existing CV research rather than adding new research areas. Add or remove theme entries as needed; no template change is necessary.

## Add publications and select homepage papers

All citations live in `content/publications.yaml`. Copy an existing entry and replace its fields. This example is a syntax guide only; replace the uppercase text before adding it:

```yaml
- status: published
  year: 2026
  title: "EXACT PAPER TITLE"
  authors: "FULL AUTHORS IN ORDER, including Ren, C."
  journal: "JOURNAL NAME"
  details: "VOLUME, PAGES OR ARTICLE NUMBER"
  co_first_author: false
  url: https://doi.org/REPLACE-WITH-VERIFIED-DOI
  selected_order: null
```

The complete page automatically includes every visible entry. Published papers are sorted by year, newest first; order within a year follows the YAML. Titles link to `url`, your name is highlighted, and `co_first_author: true` displays an equal-contribution note. Set `url: null` if a verified link is unavailable.

**Homepage selection:** set `selected_order: 1`, `selected_order: 2`, etc. on the representative papers you want to feature. Ranks must be unique positive integers. The homepage follows that order; the full page still follows years. Remove the field or set it to `null` to keep a paper only on the full page. Aim for 6–8 selected papers; the build does not silently truncate your selection. Only published papers can be selected.

**Visibility:** `visible: false` hides a record from both pages without deleting the source entry. The two working papers remain hidden. Hidden YAML entries are not confidential if the source repository is public. The linked CV retains its original contents, including its working-paper section.

Supported statuses are `published`, `accepted`, and `working`. Published papers require a numeric year and journal. Other categories accept `year: null` and an optional `note` such as `Under review` when accurate. Empty categories are omitted. When a paper becomes published, update its existing record to avoid duplication.

## Update experience

Edit `content/experience.yaml`. The homepage displays:

- `appointments` and `education`, in YAML order;
- `service`, under Academic Service;
- optional `mentoring_summary`, as a short paragraph.

Use quoted dates such as `"2023–2026"` or `"2018"`. Service dates may be `null` when unknown. The detailed `teaching` and `reviewer_journals` records remain in YAML for reference but are not rendered. Detailed reviewing information remains available in the CV.

## Change links and email

Edit `email` and `links` in `content/profile.yaml`. A link with a real URL appears in Contact; `show_on_home: true` also includes it in the hero. An empty/null URL omits the item entirely, with no unfinished placeholder text. GitHub is not included.

Both the hero’s **Email** link and the Contact address use `mailto:` and open the visitor’s configured email client. There is no copy button or clipboard script. A missing email is omitted.

## Replace your portrait

1. Save the new portrait in `assets/images/`, using a new filename if you want to keep the previous version.
2. Change `photo.file` in `content/profile.yaml`, e.g. `assets/images/chenchen-ren-new.jpg`.
3. Update `photo.alt` with descriptive alternative text, then rebuild.

JPEG, PNG, WebP, and AVIF are supported. The portrait uses a 4:5 display crop; `.portrait img` in the CSS controls crop positioning. If `photo.file` is null, no portrait placeholder is shown. The supplied original photograph is never modified.

## Replace the CV

1. Export a PDF from Word to preserve its formatting.
2. Put the PDF in `assets/files/`, preferably using a dated filename.
3. Update `cv.file` in `content/profile.yaml` and rebuild.
4. Open the PDF from the preview and review it.

All CV buttons share this path. The current file is `assets/files/chenchen-ren-cv-2026-11-17.pdf`, updated to show the University of Bonn appointment as current. Earlier PDFs are retained but unlinked. YAML updates do not update the PDF, and CV edits do not overwrite YAML.

The optional `scripts/export_cv_pdf.py` can typeset a separate PDF if Word export is unavailable. It requires ReportLab, preserves factual text but not Word’s layout, and refuses to overwrite an existing output. It is not part of routine building:

```bash
python -m pip install reportlab
python scripts/export_cv_pdf.py "Curriculum vitae_Chenchen Ren.docx" assets/files/new-cv.pdf
```

## Metadata and appearance

Edit only `assets/css/style.css` for colors, typography, spacing, and responsive rules. Shared tokens are at the top. The design uses local system fonts and no animation or third-party assets.

The favicon path is configured in `profile.yaml`; the supplied SVG uses your initials. Both pages have distinct titles/descriptions, Open Graph tags, social-card tags, and schema.org Person data based on your profile.

**After deployment**, set `site_url` to the real public base URL, including any repository path and preferably a trailing slash. For example, replace both placeholders in `https://YOUR-USERNAME.github.io/YOUR-REPOSITORY/`. Rebuild to enable absolute canonical URLs and portrait images for sharing. While `site_url: null`, those URL-dependent tags are omitted rather than guessed. Text sharing metadata remains present.

Templates use Python’s standard `string.Template` slots (`$name`, etc.). Only edit templates for layout changes; a literal dollar sign in a template must be written `$$`.

## Validation and troubleshooting

```bash
python build.py
python scripts/validate_site.py
```

Checks cover both pages, navigation including cross-page fragments, local assets, selected/full lists, hidden papers, name highlighting, DOI links, metadata, and common content-editing cases. They do not guarantee third-party availability or replace reviewing the appearance in desktop/mobile browsers.

Use spaces rather than tabs in YAML. Quote strings containing `: ` or `#`. Use `>-` followed by indented lines for paragraphs. Publication years are numbers; experience dates are strings. Duplicate keys/ranks, invalid statuses/URLs, or missing assets produce errors. Install dependencies with the same Python interpreter used for the build.

## GitHub Pages and routine updates

Use a dedicated repository for the website. GitHub Pages can publish the generated `docs/` folder directly:

1. Push the source and `docs/` to your repository.
2. Open **Settings → Pages → Deploy from a branch**.
3. Select your branch (usually `main`) and **`/docs`**, then save.
4. Use GitHub’s displayed URL to set `site_url`, rebuild, and push again.

Relative navigation and asset links work at both a personal-site root and a repository subpath. No GitHub Actions build configuration is required. Publishing also exposes the linked CV PDF.

## Updating the live website

After the initial deployment, edit `content/*.yaml` and save your changes. Then run:

```bash
python3 build.py
python3 scripts/validate_site.py
python3 -m http.server 8000 --bind 127.0.0.1 --directory docs
```

Preview at `http://127.0.0.1:8000`, then stop the preview server with Ctrl+C and run:

```bash
git add .
git commit -m "Update website"
git push
```

Commit regenerated `docs/` after every content update: GitHub Pages does not rebuild YAML. Once Pages is configured to publish from `main` → `/docs`, it updates automatically after each push to `main`; your public URL stays the same. Allow time for GitHub's deployment to finish. Review staged files so unrelated personal documents are not uploaded.

Official guide: [Configuring a publishing source for GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).
