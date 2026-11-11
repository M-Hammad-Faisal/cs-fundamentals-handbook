"""Give every topic folder the same set of pages in the same format, without overwriting hand-written content.

For each topic folder (a folder with a README.md inside a numbered part):
  * summary.md   - created if missing: the README's "Quick reference" plus the self-check questions and answers of its lessons
  * exercises.md - created if missing: the "Practice" sections (questions and collapsible solutions) of its lessons
  * titles and footers of exercises.md / summary.md are normalised
  * exercises.md: intro line, "## Problems" with optional "### group" headings, collapsible setup and solutions
  * summary.md: "## Key facts", "## Pitfalls", then an optional "## Self-check" (checked in --check mode)
  * README.md gets the standard "Detailed lessons" and "Practice and review" sections (and a "Quick reference" if it has none)

    python tools/normalize_topics.py           # apply
    python tools/normalize_topics.py --check   # exit 1 if anything would change (CI)
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PARTS = [d for d in sorted(ROOT.iterdir()) if d.is_dir() and re.match(r"(0[0-9]|1[0-9])-", d.name) and d.name not in ("00-start-here", "00-career-path")]
NOT_LESSONS = {"README.md", "exercises.md", "summary.md"}
changed = []


def h1(path):
    return path.read_text().splitlines()[0][2:].strip()


def short(title):
    m = re.match(r"^[A-Za-z ]+ \d+: (.+)$", title)
    if m:
        title = m.group(1)
    return re.split(r" \(|: |\? | — ", title)[0]


def write(path, text):
    old = path.read_text() if path.exists() else None
    if old != text:
        path.write_text(text)
        changed.append(path.relative_to(ROOT).as_posix())


def topics():
    for part in PARTS:
        for d in sorted(p for p in part.iterdir() if p.is_dir() and (p / "README.md").exists()):
            yield d


def lessons_of(topic):
    if topic.name == "design-patterns":
        return sorted(f for f in topic.rglob("*.md") if f.name != "README.md")
    files = sorted(f for f in topic.glob("*.md") if f.name not in NOT_LESSONS)
    text = (topic / "README.md").read_text()
    files.sort(key=lambda f: (text.find("(" + f.name) if text.find("(" + f.name) >= 0 else 10**9, f.name))
    return files


def section(text, name):
    """Body of the '## N. <name>' section, up to the next '## ' heading."""
    m = re.search(r"^## [\d. ]*" + name + r"\b[^\n]*\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    return m.group(1).strip("\n") if m else ""


def check_pairs(text):
    body = section(text, "Check yourself")
    if not body:
        return []
    questions = dict(re.findall(r"^(\d+)\. (.+)$", body.split("<details>")[0], re.M))
    ans = body.split("<summary>Answers</summary>")[-1].split("</details>")[0] if "<summary>Answers</summary>" in body else ""
    answers = dict(re.findall(r"^(\d+)\. (.+)$", ans, re.M))
    return [(questions[n], answers[n]) for n in sorted(questions, key=int) if n in answers]


def quick_reference(readme):
    m = re.search(r"^## Quick reference\n(.*?)(?=\n## |\nRelated|\nBack to|\Z)", readme.read_text(), re.S | re.M)
    return m.group(1).strip() if m else ""


def go_deeper(topic):
    files = [f for f in lessons_of(topic) if f.parent == topic]
    if not files:
        return ""
    return "<!-- go-deeper -->\n**Go deeper (detailed step-by-step lessons):** " + " · ".join(f"[{short(h1(f))}]({f.name})" for f in files)


def normalise_footer(text, footer_links, deeper):
    lines = text.rstrip("\n").split("\n")
    while lines and (not lines[-1].strip() or lines[-1].startswith(("[Lesson]", "[Back to", "<!-- go-deeper", "**Go deeper"))):
        lines.pop()
    return "\n".join(lines) + "\n\n" + footer_links + ("\n\n" + deeper if deeper else "") + "\n"


def build_summary(topic, title):
    readme = topic / "README.md"
    pairs = []
    sources = lessons_of(topic) or [readme]
    per = 1 if topic.name == "design-patterns" else 6
    for f in sources:
        pairs += check_pairs(f.read_text())[:per]
    if not pairs:
        pairs = check_pairs(readme.read_text())[:12]
    qr = quick_reference(readme)
    out = [f"# {title}: One-Page Summary", ""]
    if qr:
        out += ["## Key facts", "", qr, ""]
    if pairs:
        out += ["## Self-check", ""] + [f"- **{q}** {a}" for q, a in pairs[:12]] + [""]
    return "\n".join(out)


def build_exercises(topic, title):
    out = [f"# {title}: Exercises", "", "## Problems", ""]
    sources = lessons_of(topic) or [topic / "README.md"]
    if not any(section(f.read_text(), "Practice") for f in sources):
        sources = [topic / "README.md"]
    found = False
    for f in sources:
        body = section(f.read_text(), "Practice")
        if body:
            found = True
            body = body.replace("```python\n", "```python no-run\n")      # solutions rely on code from the lesson and were run there
            out += [f"### {short(h1(f))}", "", body, ""]
    if not found:                                                       # tutorials without a Practice section: use the self-check as exercises
        for f in sources:
            pairs = check_pairs(f.read_text())
            if pairs:
                out += [f"### {short(h1(f))}", ""]
                out += [f"{i}. {q}" for i, (q, _) in enumerate(pairs, 1)]
                out += ["", "<details>", "<summary>Answers</summary>", ""] + [f"{i}. {a}" for i, (_, a) in enumerate(pairs, 1)] + ["", "</details>", ""]
    return "\n".join(out)


BOILERPLATE = [
    r"Try each (?:problem|one) before opening (?:its|the) solution\.",
    r"These are the practice problems of this topic's lessons, collected in one place\.",
    r"Write the answer and the reasoning\.",
    r"Work through these after (?:the )?\[[^\]]*\]\([^)]*\)\.",
    r"Each exercise is small enough to solve with the standard library; try it before opening the solution\.",
    r"Answer each question, then check yourself\.",
    r"These problems go with the \[[^\]]*\]\(README\.md\)\.",
]
START = re.compile(r"^(## |### |\d+\. |\*\*[A-Z]?\d)", re.M)


def outside_fences(lines):
    """Yield (index, line, in_fence) so heading logic ignores code."""
    fence = False
    for i, line in enumerate(lines):
        if line.startswith("```"):
            fence = not fence
            yield i, line, True
        else:
            yield i, line, fence


def normalise_exercises(text, title):
    head, _, rest = text.partition("\n")
    footer_at = rest.find("\n[Lesson](")
    footer = rest[footer_at:] if footer_at >= 0 else ""
    body = rest[:footer_at] if footer_at >= 0 else rest
    body = body.replace("\n## Problems\n", "\n", 1) if body.lstrip().startswith("## Problems") or "\n## Problems\n" in body else body
    first = START.search(body)
    region, questions = (body[:first.start()], body[first.start():]) if first else (body, "")
    setups = re.findall(r"<details>\n<summary>Setup.*?</details>", region, re.S)
    region = re.sub(r"<details>\n<summary>Setup.*?</details>", "", region, flags=re.S)
    for pattern in BOILERPLATE:
        region = re.sub(pattern, "", region)
    extra = re.sub(r"[ \t]+\n", "\n", region).strip()
    extra = re.sub(r"\n{3,}", "\n\n", extra)
    intro = f"These problems go with the [{title} lesson](README.md). Try each one before opening its solution."
    if extra:
        intro += "\n\n" + extra
    lines = questions.split("\n")
    h2 = [i for i, l, f in outside_fences(lines) if not f and l.startswith("## ")]
    if len(h2) == 1:
        del lines[h2[0]]
    else:
        for i in h2:
            lines[i] = "#" + lines[i]
    questions = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip("\n")
    questions = re.sub(r"([^\n])\n(\*\*\d+\.\*\*)", r"\1\n\n\2", questions)
    out = [head, "", intro, ""]
    for block in setups:
        out += [block, ""]
    out += ["## Problems", "", questions]
    return "\n".join(out).rstrip("\n") + "\n" + footer.rstrip("\n") + "\n"


RENAME = {"Facts": "Key facts", "Quick reference": "Key facts", "Questions worth remembering": "Self-check"}
LAST = ("Pitfalls", "Self-check")          # every summary ends with these, in this order; everything else is a key fact


def split_sections(body):
    """Return (preface, [(title, content), ...]) split at '## ' headings that are outside code fences."""
    lines = body.split("\n")
    marks = [i for i, line, fence in outside_fences(lines) if not fence and line.startswith("## ")]
    preface = "\n".join(lines[:marks[0]]) if marks else body
    sections = []
    for n, i in enumerate(marks):
        end = marks[n + 1] if n + 1 < len(marks) else len(lines)
        sections.append((RENAME.get(lines[i][3:].strip(), lines[i][3:].strip()), "\n".join(lines[i + 1:end]).strip("\n")))
    return preface.strip("\n"), sections


def normalise_summary(text):
    """One shape for every summary: '## Key facts', then '## Pitfalls' (optional), then '## Self-check' (optional)."""
    head, _, rest = text.partition("\n")
    footer_at = rest.find("\n[Lesson](")
    footer = rest[footer_at:] if footer_at >= 0 else ""
    body = rest[:footer_at] if footer_at >= 0 else rest
    body = re.sub(r"\n+Practice problems with solutions are in the[^\n]*", "", body)
    preface, sections = split_sections(body)
    facts = [c for t, c in sections if t == "Key facts"]
    others = [(t, c) for t, c in sections if t != "Key facts" and t not in LAST]
    key = [preface] if preface else []
    key += facts
    if others and (len(others) > 1 or key):
        key += [f"### {t}\n\n{c}" for t, c in others]
    elif others:
        key += [others[0][1]]
    key_text = "\n\n".join(k for k in key if k)
    out = [head, ""] + (["## Key facts", "", key_text] if key_text else [])
    for name in LAST:
        content = "\n\n".join(c for t, c in sections if t == name)
        if content:
            out += ["", f"## {name}", "", content]
    return "\n".join(out).rstrip("\n") + "\n" + footer.rstrip("\n") + "\n"


def normalise_readme(topic):
    readme = topic / "README.md"
    text = readme.read_text()
    text = re.sub(r"^## Detailed lessons? ?(\(start here if you are new\))?$", "## Detailed lessons", text, flags=re.M)
    thin = len(text.split()) < 400
    if "## Practice and review" not in text:
        block = "## Practice and review\n\n- [Exercises](exercises.md) with solutions\n- [One-page summary](summary.md)\n\n"
        anchor = re.search(r"^## Quick reference", text, re.M) or re.search(r"^Related:", text, re.M) or re.search(r"^Back to", text, re.M)
        text = text[:anchor.start()] + block + text[anchor.start():] if anchor else text.rstrip("\n") + "\n\n" + block
    if thin and "## Quick reference" not in text:
        pairs = check_pairs(lessons_of(topic)[0].read_text())[:5] if lessons_of(topic) else []
        if pairs:
            table = "## Quick reference\n\n| Question | Answer |\n|----------|--------|\n" + "\n".join(
                f"| {q.replace('|', '/')} | {a.replace('|', '/')} |" for q, a in pairs) + "\n\n"
            anchor = re.search(r"^Related:", text, re.M) or re.search(r"^Back to", text, re.M)
            text = text[:anchor.start()] + table + text[anchor.start():] if anchor else text.rstrip("\n") + "\n\n" + table
    if not re.search(r"^Back to", text, re.M):
        text = text.rstrip("\n") + "\n\nBack to the [part overview](../README.md).\n"
    write(readme, text)


def main():
    for topic in topics():
        readme = topic / "README.md"
        title = short(h1(readme))
        if not (topic / "summary.md").exists():
            write(topic / "summary.md", build_summary(topic, title) + "\n")
        if not (topic / "exercises.md").exists():
            write(topic / "exercises.md", build_exercises(topic, title) + "\n")
        deeper = go_deeper(topic)
        for name, label in (("summary.md", "Exercises"), ("exercises.md", "Summary")):
            p = topic / name
            text = p.read_text()
            kind = "One-Page Summary" if name == "summary.md" else "Exercises"
            text = re.sub(r"\A# .*", f"# {title}: {kind}", text, count=1)
            text = normalise_exercises(text, title) if name == "exercises.md" else normalise_summary(text)
            other = "exercises.md" if name == "summary.md" else "summary.md"
            links = f"[Lesson](README.md) · [{label}]({other})"
            write(p, normalise_footer(text, links, deeper))
        normalise_readme(topic)
    empty = []
    for t in topics():
        text = (t / "summary.md").read_text()
        for needed in ("## Key facts", "## Pitfalls"):
            if needed not in text:
                empty.append(t.relative_to(ROOT).as_posix())
                print(f"summary has no '{needed}' section:", empty[-1])
    if "--check" in sys.argv:
        for c in changed:
            print("would change:", c)
        return 1 if changed or empty else 0
    print(len(changed), "files written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
