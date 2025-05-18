# Obsidian Zotero Importer

This script automatically converts entries from a Zotero `.bib` export (via Better BibTeX) into Obsidian-ready Markdown notes. It is designed for use with a structured note-taking system in which each bibliographic reference is stored as a literature note (`LN`) with standardized filenames and YAML frontmatter.

---

## 🔧 Setup

### 1. Configure Zotero with Better BibTeX
- In Zotero, right-click your **Library** or a **Collection**
- Choose `Export Library...` or `Export Collection...`
- Format: **Better BibTeX**
- ✅ Check `Keep updated`
- Output file path: `/home/dan/zoterobib/bibliography.bib`

> 📁 This file is continuously maintained by Zotero on the local system `Wealtheow`.

### 2. Project Structure
```
~/zoterobib/
└── bibliography.bib   # auto-updating BibTeX export from Zotero

~/wealtheow/
└── LN Literature Notes/
    └── LN LastName YYYY Short Title.md  # Generated Markdown notes
```

### 3. Run the Script
Install dependencies:
```bash
pip install bibtexparser python-slugify
```

Run:
```bash
python zotero_obsidian_sync.py
```

Each BibTeX entry is converted into a note with:
- YAML frontmatter (including `citekey` and `type`)
- Chicago-style citation
- Abstract
- Keywords (as Obsidian `[[wikilinks]]`)
- A preserved notes block for personal commentary

---

## ⚠️ Sync Strategy
This project assumes that:
- Zotero + `.bib` export + Markdown generation is managed **only on Wealtheow**
- Obsidian Sync (or another sync system) distributes the resulting `.md` files to other machines
- Only this machine runs the sync script

---

## 📄 Example Output File
```
LN Haraway 1985 Cyborg Manifesto.md
```
```markdown
---
citekey: "haraway1985cyborg"
type: "article"
---
# Chicago Author-Year Bibliography
Haraway, Donna. 1985. "A Cyborg Manifesto." *Socialist Review* 80: 65–108.

# Abstract
This is a theoretical exploration of the cyborg as a metaphor...

# Keywords
[[cyborg]], [[feminism]], [[Donna Haraway]]

# Notes
<!-- BEGIN NOTEMARKER -->
Your notes here.
<!-- END NOTEMARKER -->

# Related Files and URLs
- Online: https://example.com/article
```

---

## License
MIT
