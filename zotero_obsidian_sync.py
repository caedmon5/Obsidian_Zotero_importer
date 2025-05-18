# zotero_obsidian_sync.py

"""
Script to convert entries from a Better BibTeX-exported .bib file into Obsidian-ready .md files
with YAML frontmatter, Chicago-style citation, and user-preserved notes.

Filename format: LN LastName YYYY Short Title.md
"""

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import homogenize_latex_encoding
import os
import re
from pathlib import Path
from slugify import slugify  # pip install python-slugify
import logging
from datetime import datetime
import argparse

# --- CONFIGURABLE OPTIONS ---
VAULT_DIR = Path("/home/dan/wealtheow/LN Literature Notes")  # Change this to your Obsidian LN dir
BIB_FILE = Path("/home/dan/zoterobib/My Library.bib")     # Change this to your Better BibTeX export

# --- UTILITY FUNCTIONS ---
def get_filename(entry):
    author_last = entry.get("author", "Anon").split(" and ")[0].split()[-1]
    year = entry.get("year", "n.d.").split("T")[0]  # Trim timestamp if present
    title = entry.get("title", "untitled")

    # Sanitize filename to remove or replace unsafe characters
    title_clean = (
        title.replace("{", "")
             .replace("}", "")
             .replace("/", "-")
             .replace("\\", "-")
             .replace(":", "-")
             .replace("*", "")
             .replace("?", "")
             .replace("\"", "")
             .replace("<", "")
             .replace(">", "")
             .replace("|", "")
    )

    short_title = " ".join(title_clean.strip("()[]").split()[:4])
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
autoupdate: true
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

# --- LOGGING SETUP ---
logfile = Path(__file__).parent / "sync.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(logfile, mode="a", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

# --- MAIN SCRIPT ---
def main():
    parser = argparse.ArgumentParser(description="Export Zotero BibTeX entries to Obsidian Markdown.")
    parser.add_argument("--dry-run", action="store_true", help="Preview output without writing files.")
    args = parser.parse_args()
    dry_run = args.dry_run

    with open(BIB_FILE, encoding='utf-8') as bibtex_file:
        parser = BibTexParser(common_strings=False)
#        parser.customization = homogenize_latex_encoding # temporarily disabled to prevent crash
        bib_database = bibtexparser.load(bibtex_file, parser=parser)
    count_written = 0
    failed = []
    for entry in bib_database.entries:
        try:
            filename = get_filename(entry)
            output_path = VAULT_DIR / filename

            preserved = ""
            split_marker = "<!-- Content below this line is not updated by Zotero -->"
            if output_path.exists():
                with open(output_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "autoupdate: true" not in content:
                        logging.info(f"Skipping existing (no autoupdate): {filename}")
                        continue
                    if split_marker in content:
                        preserved = content.split(split_marker, 1)[1]
                    else:
                        logging.warning(f"Missing preservation marker in {filename}; overwriting entire file.")


            logging.info(f"Writing: {filename}")
            markdown = generate_markdown(entry)

            if not dry_run:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(markdown + preserved)

            count_written += 1

        except Exception as e:
            entry_id = entry.get('ID', 'unknown')
            logging.error(f"Error processing entry {entry_id}: {e}")
            failed.append(entry_id)
    if failed:
        logging.warning(f"{len(failed)} entries failed to write:")
        for entry_id in failed:
            logging.warning(f" - {entry_id}")



if __name__ == "__main__":
    main()
