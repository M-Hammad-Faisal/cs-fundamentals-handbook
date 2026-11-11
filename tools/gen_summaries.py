"""Create a one-page summary.md for topic folders that do not have one yet.

The summary is built from material that already exists in the topic: the "Quick reference" section of its README (if any)
and the question-and-answer pairs from each lesson's "Check yourself" section. Existing summary.md files are never overwritten.

    python tools/gen_summaries.py
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_PARTS = {"00-foundations", "00-start-here", "00-career-path", "revision"}
NOT_LESSONS = {"README.md", "exercises.md", "summary.md"}


def check_pairs(text):
    m = re.search(r"^## [\d. ]*Check yourself.*?$(.*)", text, re.S | re.M)
    if not m:
        return []
    body = m.group(1)
    qpart = body.split("<details>")[0]
    questions = dict(re.findall(r"^(\d+)\. (.+)$", qpart, re.M))
    ans_part = body.split("<summary>Answers</summary>")[-1] if "<summary>Answers</summary>" in body else ""
    answers = dict(re.findall(r"^(\d+)\. (.+)$", ans_part.split("</details>")[0], re.M))
    return [(questions[n], answers[n]) for n in sorted(questions, key=int) if n in answers]


def quick_reference(readme):
    m = re.search(r"^## Quick reference\n(.*?)(?=\n## |\nBack to|\Z)", readme.read_text(), re.S | re.M)
    return m.group(1).strip() if m else ""


def main():
    created = []
    for part in sorted(ROOT.iterdir()):
        if not part.is_dir() or part.name in SKIP_PARTS or not re.match(r"\d\d-", part.name):
            continue
        for topic in sorted(d for d in part.iterdir() if d.is_dir()):
            readme = topic / "README.md"
            if not readme.exists() or (topic / "summary.md").exists() or topic.name in ("design-patterns",):
                continue
            title = re.sub(r":.*", "", readme.read_text().splitlines()[0][2:]).strip()
            lessons = sorted(f for f in topic.glob("*.md") if f.name not in NOT_LESSONS)
            pairs = []
            for lesson in lessons:
                pairs += check_pairs(lesson.read_text())[:6]
            qr = quick_reference(readme)
            out = [f"# {title}: One-Page Summary", ""]
            if qr:
                out += ["## Quick reference", "", qr, ""]
            if pairs:
                out += ["## Questions worth remembering", ""]
                out += [f"- **{q}** {a}" for q, a in pairs[:12]]
                out.append("")
            out += ["Practice problems with solutions are in the **Practice** section of each lesson.", "",
                    "[Lesson](README.md)"]
            out[-1] += "".join(f" · [{re.sub(r':.*', '', lesson.read_text().splitlines()[0][2:])}]({lesson.name})" for lesson in lessons)
            (topic / "summary.md").write_text("\n".join(out) + "\n")
            created.append(topic.relative_to(ROOT).as_posix())
    print(len(created), "summaries created")
    for c in created:
        print(" ", c)


if __name__ == "__main__":
    main()
