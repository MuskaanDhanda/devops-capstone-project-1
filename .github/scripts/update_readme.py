#!/usr/bin/env python3
"""Rebuild the "Project files" table in README.md from the files in the repo.

Every tracked file and folder (except README.md and hidden paths such as
.github/) gets a linked row. Descriptions you write by hand in the table are
kept; new entries get an automatic description you can edit later.
"""
import os
import re
import subprocess
from urllib.parse import quote, unquote

README = "README.md"
START = "<!-- PROJECT-FILES:START -->"
END = "<!-- PROJECT-FILES:END -->"

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}
KNOWN = {
    "dockerfile": "Instructions for building the Docker image",
    "jenkinsfile": "Jenkins pipeline configuration",
    "makefile": "Build commands",
    "license": "License",
}
EXT_DESC = {
    ".yml": "YAML configuration", ".yaml": "YAML configuration",
    ".sh": "Shell script", ".py": "Python script", ".java": "Java source file",
    ".xml": "XML configuration", ".json": "JSON configuration",
    ".tf": "Terraform configuration", ".html": "HTML page", ".txt": "Text file",
    ".pdf": "PDF document", ".md": "Documentation",
}


def tracked_files():
    out = subprocess.run(["git", "ls-files"], capture_output=True, text=True, check=True).stdout
    files = []
    for path in out.splitlines():
        if path == README or any(part.startswith(".") for part in path.split("/")):
            continue
        files.append(path)
    return files


def md_heading(path):
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.startswith("#"):
                    return line.lstrip("#").strip()
    except (OSError, UnicodeDecodeError):
        pass
    return None


def auto_description(path, is_dir):
    if is_dir:
        return md_heading(os.path.join(path, "README.md")) or "Folder"
    name = os.path.basename(path)
    stem, ext = os.path.splitext(name)
    ext = ext.lower()
    if name.lower() in KNOWN:
        return KNOWN[name.lower()]
    if ext in IMAGE_EXT:
        return stem.replace("-", " ").replace("_", " ").capitalize() + " image"
    if ext == ".md":
        return md_heading(path) or "Documentation"
    return EXT_DESC.get(ext, "Project file")


def existing_descriptions(block):
    """Map link target -> description from the current table."""
    descs = {}
    for line in block.splitlines():
        m = re.match(r"\|.*?\]\(([^)]+)\)\s*\|(.*)\|\s*$", line)
        if m:
            cells = [c.strip() for c in m.group(2).split("|")]
            descs[unquote(m.group(1)).rstrip("/")] = cells[-1]
    return descs


def build_entries(files):
    entries = set()
    for f in files:
        parts = f.split("/")
        for i in range(1, len(parts)):
            entries.add(("/".join(parts[:i]), True))
        entries.add((f, False))
    # Folders before the files inside them, alphabetical (case-insensitive)
    return sorted(entries, key=lambda e: [p.lower() for p in e[0].split("/")])


def main():
    with open(README, encoding="utf-8") as f:
        text = f.read()
    if START not in text or END not in text:
        raise SystemExit(f"Markers {START} / {END} not found in {README}")

    head, rest = text.split(START, 1)
    block, tail = rest.split(END, 1)
    descs = existing_descriptions(block)

    rows = ["| File / Folder | What's inside |", "|---------------|---------------|"]
    for path, is_dir in build_entries(tracked_files()):
        depth = path.count("/")
        name = os.path.basename(path) + ("/" if is_dir else "")
        icon = "📁" if is_dir else ("🖼️" if os.path.splitext(path)[1].lower() in IMAGE_EXT else "📄")
        indent = "&nbsp;&nbsp;&nbsp;&nbsp;" * depth
        desc = descs.get(path) or auto_description(path, is_dir)
        rows.append(f"| {indent}{icon} [{name}]({quote(path)}) | {desc} |")

    new_text = f"{head}{START}\n" + "\n".join(rows) + f"\n{END}{tail}"
    if new_text != text:
        with open(README, "w", encoding="utf-8") as f:
            f.write(new_text)
        print("README.md updated")
    else:
        print("README.md already up to date")


if __name__ == "__main__":
    main()
