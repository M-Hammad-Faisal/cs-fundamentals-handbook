"""Regenerate the navigation pages from the files on disk so they can never drift apart.

    python tools/build_index.py           # rewrite INDEX.md, revision/PROGRESS.md and the generated parts of README.md
    python tools/build_index.py --check   # exit 1 if any of them is out of date (used in CI)

One format everywhere: a part is a table with one row per topic (or per loose lesson):
    Topic | Lessons | Exercises | Summary | Status      (INDEX.md)
    Topic | Read | Ex | R1 | R2 | R3 | R4 | R5          (revision/PROGRESS.md)

To add a lesson: put the .md file in its topic folder (give it a "# Title" first line) and run this script.
To add a topic: create the folder with a README.md and add its folder name to ORDER below.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# (key, heading, folder, one-line description, topic folders in teaching order)
PARTS = [
    ("start", "Start here", "00-start-here", "How the handbook works and how to study with it.", []),
    ("career", "Career path", "00-career-path", "Where the profession is heading, which roles are growing, and the working habits that matter.", []),
    ("00", "00 Foundations", "00-foundations", "Everything the rest assumes: setup, how computers work, math, Python, the command line and Git.",
     ["setup", "computer-basics", "math-for-cs", "python-fundamentals", "command-line-and-git"]),
    ("01", "01 Complexity", "01-complexity", "Measuring how fast and how big.", ["big-o"]),
    ("02", "02 Data structures", "02-data-structures", "Storing and organizing data.",
     ["arrays-strings", "linked-lists", "stacks-queues", "hash-tables", "trees", "heaps", "tries", "graphs"]),
    ("03", "03 Algorithms", "03-algorithms", "Solving problems efficiently.",
     ["sorting", "searching", "recursion-backtracking", "divide-and-conquer", "dynamic-programming", "greedy",
      "number-theory", "string-algorithms", "graph-algorithms"]),
    ("04", "04 Object-oriented design", "04-oop", "Structuring larger programs.",
     ["classes-objects", "encapsulation-abstraction", "inheritance-mro", "polymorphism-dunder", "composition-design", "solid", "design-patterns"]),
    ("05", "05 Databases", "05-databases", "Storing data reliably.",
     ["relational-sql", "indexes-query-plans", "transactions-acid", "normalization-schema-design", "nosql", "postgresql"]),
    ("06", "06 Operating systems", "06-operating-systems", "What runs under your code.",
     ["processes-threads", "scheduling", "memory-virtual-memory", "concurrency-deadlocks", "file-systems-io", "boot-and-startup", "containers"]),
    ("07", "07 Networking", "07-networking", "How computers talk.",
     ["tcp-ip-osi", "routing", "dns-http", "tls-security", "load-balancing-cdn", "apis-realtime", "debugging"]),
    ("08", "08 Modern Python", "08-modern-python", "Professional Python: the language, the tools and the backend stack.",
     ["typing-hints", "dataclasses-enums", "generators-functional", "async-concurrency", "concurrency", "modern-syntax",
      "performance-profiling", "internals", "exceptions-logging-testing", "testing-in-depth", "packaging-tooling",
      "engineering-workflow", "stdlib-toolbox", "backend-with-fastapi", "database-access", "data-with-numpy-pandas"]),
    ("09", "09 Interview playbook", "09-interview-playbook", "Turning knowledge into offers.",
     ["problem-solving-patterns", "worked-problems", "system-design-basics", "python-and-cs-rapid-fire", "behavioral-and-process"]),
    ("10", "10 Security", "10-security", "Writing software that holds up against attackers.",
     ["threat-modeling", "authentication", "web-vulnerabilities", "secrets-and-supply-chain"]),
    ("11", "11 Distributed systems", "11-distributed-systems", "How systems made of many machines stay correct and available.",
     ["foundations", "replication-sharding", "consensus", "transactions", "messaging-storage", "observability"]),
]

NOT_LESSONS = {"README.md", "exercises.md", "summary.md"}


def h1(path):
    for line in path.read_text().splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem


def short(title):
    m = re.match(r"^[A-Za-z ]+ \d+: (.+)$", title)          # "Python Basics 3: Functions" -> "Functions"
    if m:
        title = m.group(1)
    return re.split(r" \(|: |\? | — ", title)[0]


def rel(path, base):
    return path.relative_to(base).as_posix() if base else path.relative_to(ROOT).as_posix()


def rows_for(part_dir):
    """Yield dicts: title, lessons (list of (label, path)), ex, sum, readme (topic README or lesson path) for each topic in a part."""
    key = next(p for p in PARTS if p[2] == part_dir.name)
    order = key[4]
    rows = []
    # loose lessons at the root of the part (numbered lessons such as 01-complexity/01-what-is-an-algorithm.md)
    for f in sorted(part_dir.glob("*.md")):
        if f.name in NOT_LESSONS:
            continue
        rows.append({"title": short(h1(f)), "lessons": [("lesson", f)], "ex": None, "sum": None, "main": f})
    folders = [d for d in part_dir.iterdir() if d.is_dir() and not d.name.startswith(".")]
    folders.sort(key=lambda d: (order.index(d.name) if d.name in order else 999, d.name))
    for d in folders:
        readme = d / "README.md"
        detailed = sorted(f for f in d.glob("*.md") if f.name not in NOT_LESSONS)
        if readme.exists():                                    # teach in the order the topic README links them
            text = readme.read_text()
            detailed.sort(key=lambda f: (text.find("(" + f.name) if text.find("(" + f.name) >= 0 else 10**9, f.name))
        lessons = []
        if readme.exists():
            lessons.append(("overview" if detailed else "lesson", readme))
        lessons += [(short(h1(f)), f) for f in detailed]
        if not lessons:
            continue
        rows.append({"title": short(h1(readme)) if readme.exists() else d.name, "lessons": lessons,
                     "ex": d / "exercises.md" if (d / "exercises.md").exists() else None,
                     "sum": d / "summary.md" if (d / "summary.md").exists() else None, "main": readme if readme.exists() else lessons[0][1]})
    return rows


def link(label, path, base):
    return f"[{label}]({path.relative_to(ROOT).as_posix() if base is None else '../' + path.relative_to(ROOT).as_posix()})"


def build_index():
    out = ["# Index",
           "",
           "The map of the whole handbook, in reading order. **This page is generated** by `tools/build_index.py` from the files on disk, so it always matches them.",
           "",
           "Every topic is one row: its overview and detailed lessons, the exercises (with solutions) and the one-page summary. "
           "For definitions of terms see the [glossary](GLOSSARY.md); to track your own progress use the [progress tracker](revision/PROGRESS.md) and the [spaced schedule](revision/schedule.md).",
           ""]
    for key, heading, folder, desc, _ in PARTS:
        part = ROOT / folder
        if key == "start":
            out += [f"## {heading}", "", f"{desc} [{folder}/README.md]({folder}/README.md)", ""]
            continue
        out += [f"## {heading}", "", desc + f" Overview: [{folder}/README.md]({folder}/README.md).", ""]
        rows = rows_for(part)
        if key == "career":
            rows.insert(0, {"title": short(h1(part / "README.md")), "lessons": [("lesson", part / "README.md")], "ex": None, "sum": None, "main": part / "README.md"})
        out += ["| Topic | Lessons | Exercises | Summary | Status |", "|-------|---------|-----------|---------|--------|"]
        for r in rows:
            lessons = "<br>".join(link(label, p, None) if label not in ("overview", "lesson") else link(label, p, None)
                                  for label, p in r["lessons"])
            ex = link("ex", r["ex"], None) if r["ex"] else "–"
            sm = link("sum", r["sum"], None) if r["sum"] else "–"
            out.append(f"| {r['title']} | {lessons} | {ex} | {sm} | done |")
        out.append("")
    out += ["## Revision tools", "", "| Page | Purpose |", "|------|---------|",
            "| [Glossary](GLOSSARY.md) | every term in plain words, linked to the lesson that teaches it |",
            "| [Spaced schedule](revision/schedule.md) | when to review what |",
            "| [Progress tracker](revision/PROGRESS.md) | tick off topics and log mistakes |",
            "| [Roadmap](ROADMAP.md) | verification status and what is still missing |", ""]
    return "\n".join(out)


def build_progress():
    old = (ROOT / "revision" / "PROGRESS.md").read_text() if (ROOT / "revision" / "PROGRESS.md").exists() else ""
    tail = old[old.index("## Mistake log"):] if "## Mistake log" in old else (
        "## Mistake log\nWrite down anything you got wrong and the fix. Review weekly.\n\n| Date | Topic | What I got wrong | Correct idea |\n|------|-------|------------------|--------------|\n|      |       |                  |              |\n")
    boxes = "| [ ] | [ ] | [ ] | [ ] | [ ] | [ ] | [ ] |"
    # keep any ticks the reader already made: map "topic link target" -> its boxes
    kept = {}
    for line in old.splitlines():
        m = re.match(r"\| \[[^\]]*\]\(([^)]+)\) (\| .* \|)$", line)
        if m and "[x]" in m.group(2).lower():
            kept[m.group(1)] = m.group(2)
    out = ["# Progress Tracker", "",
           "Tick items as you finish them. Add dates so the [spaced schedule](schedule.md) works. This page lists **every topic** in the [index](../INDEX.md), in the same order; it is regenerated by `tools/build_index.py` and keeps your ticks.", "",
           "Legend: **Read** = topic read, **Ex** = exercises done, **R1** to **R5** = scheduled reviews.", ""]
    for key, heading, folder, desc, _ in PARTS:
        if key == "start":
            continue
        out += [f"## {heading}", "", "| Topic | Read | Ex | R1 | R2 | R3 | R4 | R5 |", "|-------|------|----|----|----|----|----|----|"]
        rows = [{"title": "Career path overview and engineering practice", "main": ROOT / folder / "README.md"}] if key == "career" else rows_for(ROOT / folder)
        if key == "career":
            rows = [{"title": short(h1(ROOT / folder / "README.md")), "main": ROOT / folder / "README.md"}] + [
                {"title": short(h1(f)), "main": f} for f in sorted((ROOT / folder).glob("*.md")) if f.name != "README.md"]
        for r in rows:
            target = "../" + r["main"].relative_to(ROOT).as_posix()
            out.append(f"| [{r['title']}]({target}) " + kept.get(target, boxes))
        out.append("")
    return "\n".join(out) + "\n" + tail


def stats():
    pages = lines = blocks = 0
    for f in ROOT.rglob("*.md"):
        if ".git" in f.parts:
            continue
        text = f.read_text()
        pages += 1
        lines += text.count("\n")
        blocks += len(re.findall(r"```python", text))
    terms = len(re.findall(r"^- \*\*", (ROOT / "GLOSSARY.md").read_text(), re.M))
    return pages, lines, blocks, terms


def build_readme_table():
    rows = ["| Part | Topics |", "|------|--------|"]
    for key, heading, folder, desc, _ in PARTS:
        if key == "start":
            continue
        part = ROOT / folder
        if key == "career":
            items = [f"[{short(h1(f))}]({folder}/{f.name})" for f in sorted(part.glob("*.md"))]
        else:
            items = []
            for r in rows_for(part):
                items.append(f"[{r['title']}]({r['main'].relative_to(ROOT).as_posix()})")
        rows.append(f"| [{heading}]({folder}/README.md) | " + ", ".join(items) + " |")
    pages, lines, blocks, terms = stats()
    summary = f"**{pages} pages, about {lines // 1000 * 1000:,} lines, {blocks:,} Python code blocks and {terms} glossary terms.**"
    return "\n".join(rows), summary


def replace_between(text, start, end, new):
    a, b = text.index(start) + len(start), text.index(end)
    return text[:a] + "\n" + new + "\n" + text[b:]


def main():
    check = "--check" in sys.argv
    targets = {}
    targets[ROOT / "INDEX.md"] = build_index() + "\n"
    targets[ROOT / "revision" / "PROGRESS.md"] = build_progress()
    readme = (ROOT / "README.md").read_text()
    table, summary = build_readme_table()
    readme = replace_between(readme, "<!-- contents:start -->", "<!-- contents:end -->", table)
    readme = replace_between(readme, "<!-- stats:start -->", "<!-- stats:end -->", summary)
    targets[ROOT / "README.md"] = readme
    stale = [p for p, text in targets.items() if not p.exists() or p.read_text() != text]
    if check:
        for p in stale:
            print("out of date:", p.relative_to(ROOT))
        return 1 if stale else 0
    for p, text in targets.items():
        p.write_text(text)
    print("wrote", ", ".join(p.relative_to(ROOT).as_posix() for p in targets))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
