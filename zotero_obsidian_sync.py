# zotero_obsidian_sync.py

"""
Script to convert entries from a Better BibTeX-exported .bib file into Obsidian-ready .md files
with YAML frontmatter, Chicago-style citation, and user-preserved notes.

Filename format: LN LastName YYYY Short Title.md
"""

import bibtexparser
import os
import re
from pathlib import Path
from slugify import slugify  # pip install python-slugify

# --- CONFIGURABLE OPTIONS ---
VAULT_DIR = Path("/home/dan/wealtheow/LN Literature Notes")  # Change this to your Obsidian LN dir
BIB_FILE = Path("/home/dan/zoterobib/bibliography.bib")     # Change this to your Better BibTeX export

# --- UTILITY FUNCTIONS ---
def get_filename(entry):
    author_last = entry.get("author", "Anon").split(" and ")[0].split()[-1]
    year = entry.get("year", "n.d.")
    title = entry.get("title", "untitled")
    short_title = " ".join(title.strip("{}()").split()[:4])
    return f"LN {author_last} {year} {short_title}.md"

def chicago_citation(entry):
    author = entry.get("author", "Anon")
    year = entry.get("year", "n.d.")
    title = entry.get("title", "Untitled")
    journal = entry.get("journal", "")
    volume = entry.get("volume", "")
    number = entry.get("number", "")
    pages = entry.get("pages", "")
    url = entry.get("url", "")

    parts = [f"{author}. {year}. \"{title}.\""]
    if journal:
        parts.append(f"*{journal}*")
    if volume:
        parts[-1] += f" {volume}"
    if number:
        parts[-1] += f" ({number})"
    if pages:
        parts[-1] += f": {pages}"
    if url:
        parts.append(url)
    return " ".join(parts)

def yaml_block(entry):
    return f"""---
citekey: "{entry.get('ID', '')}"
type: "{entry.get('ENTRYTYPE', '')}"
---
"""

def generate_markdown(entry):
    md = yaml_block(entry)
    md += "# Chicago Author-Year Bibliography\n"
    md += chicago_citation(entry) + "\n\n"
    md += "# Abstract\n"
    md += entry.get("abstract", "") + "\n\n"
    md += "# Keywords\n"
    keywords = entry.get("keywords", "")
    md += ", ".join(f"[[{kw.strip()}]]" for kw in keywords.split(",")) + "\n\n"
    md += "# Notes\n"
    md += "<!-- BEGIN NOTEMARKER -->\nYour notes here.\n<!-- END NOTEMARKER -->\n\n"
    md += "# Related Files and URLs\n"
    if 'file' in entry:
        md += f"- Attached: {entry['file']}\n"
    if 'url' in entry:
        md += f"- Online: {entry['url']}\n"
    return md

# --- MAIN SCRIPT ---
def main():
    with open(BIB_FILE, encoding='utf-8') as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file)

    for entry in bib_database.entries:
        filename = get_filename(entry)
        output_path = VAULT_DIR / filename

        if output_path.exists():
            print(f"Skipping existing: {filename}")
            continue

        markdown = generate_markdown(entry)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown)
            print(f"Written: {filename}")

if __name__ == "__main__":
    main()
