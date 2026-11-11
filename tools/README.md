# Tools

Small scripts that keep the handbook honest. They also run in CI (`.github/workflows/check.yml`).

| Script | What it does |
|--------|--------------|
| `check_code_blocks.py` | Runs every ```` ```python ```` block on every page (each page in a fresh process, blocks in order, sharing one namespace). Pages with `# file: name.py` blocks are written to a temporary folder and tested with pytest. A block opened with ```` ```python no-run ```` is skipped. |
| `check_links.py` | Reports relative Markdown links that point to files that do not exist. |
| `known-sketches.txt` | Pages deliberately skipped by the code checker, one per line, with the reason after `#`. |
| `requirements-check.txt` | Third-party packages that a few lessons import (pytest, numpy, pandas, fastapi, sqlalchemy, ...). |

```bash
pip install -r tools/requirements-check.txt
python tools/check_links.py
python tools/check_code_blocks.py                      # everything (takes a few minutes)
python tools/check_code_blocks.py 10-security/authentication/01-authn-authz-sessions-jwt.md   # one page
```

What the checker does **not** do: it does not compare the output comments (`# True`) with real output; those were checked by hand when each lesson was written, and a page whose code stops running will fail here, which is the early warning that its comments need re-checking too.
