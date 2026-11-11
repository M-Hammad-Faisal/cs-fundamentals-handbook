"""Report broken relative links between Markdown pages. Usage: python tools/check_links.py"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r"\]\(([^)#\s]+\.md)(#[^)]*)?\)")

bad = []
for page in ROOT.rglob("*.md"):
    if ".git" in page.parts:
        continue
    for match in LINK.finditer(page.read_text()):
        target = (page.parent / match.group(1)).resolve()
        if not target.exists():
            bad.append((page.relative_to(ROOT).as_posix(), match.group(1)))
for page, link in bad:
    print("BROKEN", page, "->", link)
print(f"{len(bad)} broken links")
sys.exit(1 if bad else 0)
