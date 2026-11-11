"""Run every ```python block in the handbook and report the ones that fail.

Usage:
    python tools/check_code_blocks.py                 # every page
    python tools/check_code_blocks.py path/to/page.md # selected pages

How a page is checked
    * Blocks are executed top to bottom in ONE shared namespace, like a notebook (each page is a fresh process).
    * Code is dedented first, so solutions indented inside numbered lists work.
    * A block opened with ```python no-run is skipped (fragments and illustrative code).
    * Pages that contain blocks starting with "# file: name.py" describe a small project: those files are written
      to a temporary folder and pytest is run there instead of executing the blocks one by one.
    * tools/known-sketches.txt lists pages that are skipped on purpose, one per line, with the reason after a "#".

Pages that need third-party packages (pytest, numpy, ...) require them to be installed:
    pip install -r tools/requirements-check.txt
"""
import os
import re
import subprocess
import sys
import tempfile
import textwrap
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FENCE = re.compile(r"```python\n(.*?)```", re.S)
FILE_MARK = re.compile(r"# file: (\S+)\n")
TIMEOUT = 180


def known_sketches():
    path = ROOT / "tools" / "known-sketches.txt"
    if not path.exists():
        return set()
    names = set()
    for line in path.read_text().splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            names.add(line)
    return names


def run_one(page: Path) -> int:
    """Execute a single page in this process; return 0 on success."""
    source = page.read_text()
    blocks = FENCE.findall(source)
    if any(FILE_MARK.match(b) for b in blocks):
        return run_project_page(blocks)
    namespace = {"__name__": "__lesson__"}
    for index, block in enumerate(blocks):
        try:
            exec(compile(textwrap.dedent(block), f"{page.name}#block{index}", "exec", dont_inherit=True), namespace)
        except SystemExit:
            pass
        except Exception:
            traceback.print_exc()
            print(f"FAILED in block {index}", file=sys.stderr)
            return 1
    return 0


def run_project_page(blocks):
    folder = Path(tempfile.mkdtemp())
    for block in blocks:
        match = FILE_MARK.match(block)
        if match:
            target = folder / match.group(1)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(block[match.end():])
    result = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"], cwd=folder, capture_output=True, text=True)
    sys.stdout.write(result.stdout[-800:])
    return result.returncode


def main(argv: list[str]) -> int:
    if len(argv) == 3 and argv[1] == "--one":
        return run_one(Path(argv[2]))
    pages = [Path(a).resolve() for a in argv[1:]] or sorted(p for p in ROOT.rglob("*.md") if ".git" not in p.parts)
    skipped = known_sketches()
    failures, checked, skipped_count = [], 0, 0
    for page in pages:
        rel = page.relative_to(ROOT).as_posix()
        if not FENCE.search(page.read_text()):
            continue
        if rel in skipped:
            skipped_count += 1
            continue
        checked += 1
        try:
            result = subprocess.run([sys.executable, __file__, "--one", str(page)], capture_output=True, text=True, timeout=TIMEOUT,
                                    env={**os.environ, "PYTHONHASHSEED": "0"})
            ok = result.returncode == 0
            detail = (result.stderr or result.stdout)[-600:]
        except subprocess.TimeoutExpired:
            ok, detail = False, f"timed out after {TIMEOUT}s"
        if not ok:
            failures.append(rel)
            print(f"FAIL {rel}\n{textwrap.indent(detail.strip(), '    ')}\n")
    print(f"checked {checked} pages with code, skipped {skipped_count} listed sketches, {len(failures)} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
