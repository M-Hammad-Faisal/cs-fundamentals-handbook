"""Advisory check: does the value in a trailing comment match what the line really prints?

    python tools/check_outputs.py                 # every page
    python tools/check_outputs.py path/to/page.md # selected pages

Only single-line `print(...)  # expected` statements are compared (blocks run top to bottom in one shared namespace, like
check_code_blocks.py). A comment is accepted if it contains the output, the output contains it, or both are numbers within
6 percent. Anything else is listed as a candidate: read it, it is usually an explanation rather than a mismatch.
This is not run in CI because comments often add prose and some values depend on the machine (page size, timings).
"""
import ast
import contextlib
import io
import re
import sys
import textwrap
import tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FENCE = re.compile(r"```python\n(.*?)```", re.S)
DATA = re.compile(r"^(\d|-\d|\[|\(|\{|'|\"|True|False|None|b')")


def comments(src):
    found = {}
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type == tokenize.COMMENT:
                found[tok.start[0]] = tok.string[1:].strip()
    except tokenize.TokenError:
        pass
    return found


def squash(text):
    return re.sub(r"\s+", " ", text.strip())


def number(text):
    m = re.match(r"-?\d+(\.\d+)?(e-?\d+)?", text)
    return float(m.group(0)) if m else None


def agrees(comment, output):
    if comment in output or output in comment or not DATA.match(comment):
        return True
    a, b = number(comment), number(output)
    return a is not None and b not in (None, 0) and abs(a - b) / abs(b) < 0.06


def check(page):
    text = page.read_text()
    if "# file:" in text:
        return []
    namespace, found = {"__name__": "__lesson__"}, []
    for match in FENCE.finditer(text):
        source = textwrap.dedent(match.group(1))
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        notes = comments(source)
        for stmt in tree.body:
            buffer = io.StringIO()
            try:
                with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(io.StringIO()):
                    exec(compile(ast.Module([stmt], []), "block", "exec", dont_inherit=True), namespace)
            except BaseException:
                return found
            output = squash(buffer.getvalue())
            is_print = isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call) and getattr(stmt.value.func, "id", "") == "print"
            if is_print and stmt.lineno == stmt.end_lineno and output and stmt.lineno in notes:
                comment = squash(notes[stmt.lineno])
                if not agrees(comment, output):
                    found.append((page.relative_to(ROOT).as_posix(), stmt.lineno, comment[:70], output[:70]))
    return found


def main(argv):
    pages = [Path(a).resolve() for a in argv[1:]] or sorted(p for p in ROOT.rglob("*.md") if ".git" not in p.parts)
    total = 0
    for page in pages:
        for row in check(page):
            print(" | ".join(map(str, row)))
            total += 1
    print(f"{total} candidates to read")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
