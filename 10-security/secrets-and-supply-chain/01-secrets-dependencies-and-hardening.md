# Secrets, Dependencies and Hardening

**Prerequisites:** [Threat modeling and secure Python](../threat-modeling/01-threat-modeling-and-secure-python.md), [packaging and tooling](../../08-modern-python/packaging-tooling/README.md), [logging](../../08-modern-python/exceptions-logging-testing/README.md). **You will learn:** how to keep **secrets** out of code and logs (and find them when they leak), how to defend against **supply-chain attacks** (typosquatted and compromised packages, hash pinning), how to keep a **tamper-evident audit log**, and a practical **hardening checklist** for Python apps and containers.

## 1. In plain words

A **secret** is anything that grants access if someone else has it: passwords, API keys, tokens, private keys, database URLs. The **supply chain** is everything you did not write but run: libraries, their dependencies, build tools, base images. Attackers prefer these because they are easier than breaking your code: one leaked key or one poisoned package reaches everything downstream.

## 2. Keeping secrets out of code

Rules: never commit secrets (git history is forever, even after you delete the file); load them from the **environment** or a **secret manager** (Vault, AWS/GCP secret managers, Kubernetes secrets); use **different secrets per environment**; make them **rotatable**; and give each secret the **least privilege** it needs.

```python
import os

class Secret:
    """Holds a secret and refuses to show itself in logs, prints or tracebacks."""
    def __init__(self, value: str):
        self._value = value
    def reveal(self) -> str:                      # the one deliberate way to read it
        return self._value
    def __repr__(self):
        return "Secret('***')"
    __str__ = __repr__

def require_env(name: str) -> Secret:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"missing required environment variable {name}")   # fail fast at startup
    return Secret(value)

os.environ["DEMO_API_KEY"] = "sk-demo-1234567890"
key = require_env("DEMO_API_KEY")
print(key, f"{key}", [key])
# Secret('***') Secret('***') [Secret('***')]
print(key.reveal()[:8] + "...")
# sk-demo-...
try:
    require_env("NOT_SET_ANYWHERE")
except RuntimeError as e:
    print(e)
# missing required environment variable NOT_SET_ANYWHERE
```

Also: a `.env` file is for local development only, **listed in `.gitignore`**; `pydantic-settings` or similar libraries load and validate configuration for you. Never put secrets in command-line arguments (visible in `ps`), URLs (logged everywhere) or Docker image layers (`ENV` and `COPY .env` are readable by anyone with the image).

## 3. Finding secrets before attackers do

Scanners such as `gitleaks`, `trufflehog` and GitHub's push protection look for known **patterns** (an AWS access key starts with `AKIA`) and for **high-entropy** strings (random-looking text). The idea in miniature:

```python
import math, re
from collections import Counter

def entropy(s: str) -> float:
    """Shannon entropy in bits per character: random keys score high, English words score low."""
    counts = Counter(s)
    return -sum(c / len(s) * math.log2(c / len(s)) for c in counts.values())

PATTERNS = {
    "AWS access key id": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "private key block": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "bearer/long token": re.compile(r"\b[A-Za-z0-9_\-]{32,}\b"),
}

def scan(text: str):
    findings = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for name, rx in PATTERNS.items():
            for m in rx.finditer(line):
                if name == "bearer/long token" and entropy(m.group()) < 4.0:
                    continue                                   # long but low-entropy: probably a word or path
                findings.append((lineno, name, m.group()[:6] + "..."))
    return findings

fake_aws = "AKIA" + "IOSFODNN7EXAMPLE"                           # AWS's documented example id, built in pieces so scanners skip this page
fake_token = "q8Zr4tYw1LkP0vNb7XcD3sFhJ9mAeU2g"                  # random-looking
source = f'''
aws_key = "{fake_aws}"
note = "a_very_long_but_boring_identifier_name_here"
token = "{fake_token}"
-----BEGIN {"RSA "}PRIVATE KEY-----
'''
for f in scan(source):
    print(f)
# (2, 'AWS access key id', 'AKIAIO...')
# (4, 'bearer/long token', 'q8Zr4t...')
# (5, 'private key block', '-----B...')
print(round(entropy("aaaaaaaa"), 2), round(entropy(fake_token), 2) > 4)
# -0.0 True
```

**If a secret leaks, assume it is compromised:** **rotate** it immediately (revoke and reissue), then clean history if you must. Removing the commit does not help: crawlers copy public repositories within minutes.

## 4. Never log secrets (redaction)

```python
import logging, re

class RedactFilter(logging.Filter):
    PATTERN = re.compile(r"(password|token|api[_-]?key|authorization)(\s*[=:]\s*)(\S+)", re.I)
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = self.PATTERN.sub(r"\1\2[REDACTED]", str(record.msg))
        return True

log = logging.getLogger("app")
log.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
handler.addFilter(RedactFilter())
log.addHandler(handler)
log.propagate = False

log.info("login ok for ada, token=abc123xyz")
# INFO login ok for ada, token=[REDACTED]
log.info("calling api with Authorization: Bearer-secret-value")
# INFO calling api with Authorization: [REDACTED]
```

(Redaction is a safety net, not a plan: first, do not log the secret at all. Also scrub stack traces and error-reporting tools such as Sentry.)

## 5. Supply-chain attacks

How attackers get into your dependencies:

| Attack | How it works | Defence |
|--------|--------------|---------|
| **Typosquatting** | a package named `reqeusts` or `python-dateutils` imitates a popular one and runs code on install | check names carefully; use a lock file with exact names |
| **Dependency confusion** | your internal package name exists on the public index with a higher version; the installer picks the public one | use a private index with explicit priority, namespace internal names |
| **Compromised maintainer or build** | a legitimate package is hijacked and a malicious version published | pin versions and hashes, review updates, use trusted publishing and attestation |
| **Malicious install scripts** | code in `setup.py` runs at install time | prefer wheels, install in a sandbox or CI, least privilege |
| **Abandoned packages** | nobody patches known flaws | audit regularly |

A tiny **typosquat detector** using edit distance (see [edit distance](../../09-interview-playbook/worked-problems/02-graph-string-dp-and-design-rounds.md)):

```python
def edit_distance(a: str, b: str) -> int:
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]

POPULAR = ["requests", "numpy", "pandas", "django", "flask", "urllib3", "cryptography"]

def suspicious(name: str):
    if name in POPULAR:
        return None
    best = min(POPULAR, key=lambda p: edit_distance(name, p))
    return best if edit_distance(name, best) <= 2 else None

for pkg in ["requests", "reqeusts", "nunpy", "djangoo", "my-internal-tool"]:
    print(f"{pkg:<18} {suspicious(pkg)}")
# requests           None
# reqeusts           requests
# nunpy              numpy
# djangoo            django
# my-internal-tool   None
```

### Pinning with hashes

A **lock file** fixes exact versions; adding **hashes** makes pip refuse any file whose bytes differ, so a swapped or tampered artifact fails to install:

```text
# requirements.txt (generate with: pip-compile --generate-hashes, or uv pip compile --generate-hashes)
requests==2.32.3 \
    --hash=sha256:55365417734eb18255590a9ff9eb97e9e1da868d4ccd6402399eaf68af20a760
# install with:  pip install --require-hashes -r requirements.txt
```

The check pip performs is a SHA-256 of the downloaded file, which you can reproduce:

```python
import hashlib, tempfile, pathlib

artifact = pathlib.Path(tempfile.mkdtemp()) / "pkg-1.0-py3-none-any.whl"
artifact.write_bytes(b"pretend wheel contents")
expected = hashlib.sha256(b"pretend wheel contents").hexdigest()          # recorded when you locked

def verify_artifact(path: pathlib.Path, expected_sha256: str) -> bool:
    return hashlib.sha256(path.read_bytes()).hexdigest() == expected_sha256

print(verify_artifact(artifact, expected))
# True
artifact.write_bytes(b"pretend wheel contents + backdoor")                 # tampered
print(verify_artifact(artifact, expected))
# False
```

Know what you run: list your environment and audit it.

```python
from importlib.metadata import distributions

installed = sorted(d.metadata["Name"] for d in distributions() if d.metadata["Name"])
print(type(installed).__name__, "of installed package names")      # e.g. ['pip', ...] in a bare environment
# list of installed package names
```

Run `pip-audit` (checks installed packages against known-vulnerability databases), keep dependencies **few and updated** (automated pull requests from Dependabot or Renovate), generate an **SBOM** (software bill of materials) for releases, and prefer **trusted publishing** (short-lived OIDC credentials, no long-lived PyPI tokens) when you publish your own package.

## 6. A tamper-evident audit log

Repudiation ("I never did that") is answered by an **append-only audit log**: who did what, when, from where. Making each entry include the hash of the previous one means any edit or deletion **breaks the chain** and is detectable:

```python
import hashlib, json, time

class AuditLog:
    def __init__(self):
        self.entries = []

    def append(self, actor: str, action: str, target: str):
        prev_hash = self.entries[-1]["hash"] if self.entries else "0" * 64
        body = {"ts": time.time(), "actor": actor, "action": action, "target": target, "prev": prev_hash}
        body["hash"] = hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()
        self.entries.append(body)

    def verify(self) -> bool:
        prev = "0" * 64
        for e in self.entries:
            body = {k: v for k, v in e.items() if k != "hash"}
            if e["prev"] != prev or hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest() != e["hash"]:
                return False
            prev = e["hash"]
        return True

log = AuditLog()
log.append("ada", "login", "-")
log.append("ada", "delete", "note:42")
log.append("bob", "export", "all-notes")
print(log.verify())
# True
log.entries[1]["actor"] = "bob"                      # someone rewrites history
print(log.verify())
# False
```

Real systems also ship logs to a separate, write-only system so an intruder on the app server cannot rewrite them (the same idea as a blockchain, without the coins).

## 7. Hardening checklist

**Application:** validate all input; parameterize queries; auto-escape output; hash passwords with scrypt or argon2; HTTPS everywhere; security headers; rate limits; debug off; dependency audit in CI.

**Python runtime:** run as an unprivileged user; avoid unsafe deserialization and dynamic evaluation of untrusted data; pin dependencies; use virtual environments; keep Python patched.

**Containers** (see [containers](../../06-operating-systems/containers/01-containers-and-namespaces.md)): non-root `USER`, minimal base image (slim or distroless), no secrets baked into layers, read-only root filesystem, drop Linux capabilities, resource limits, scan images.

**Infrastructure:** least-privilege IAM roles per service; network segmentation (database not reachable from the internet); secrets in a manager; encryption at rest and in transit; backups tested; logging and alerts.

## 8. Common mistakes

- Committing `.env` or a key "just for now", then deleting it without rotating.
- One powerful credential shared by every service and developer.
- Secrets in `docker build` arguments or `ENV` lines.
- `pip install` of whatever a blog post says, as root, on a production host.
- Unpinned dependencies (`requests>=2`), so an attacker's new release is installed automatically.
- Logging whole request headers (which contain tokens) or whole objects (which contain passwords).
- Trusting "internal" tokens that never expire.

## 9. Two real-world examples

**Example 1: A key on a public repository.** A developer pushed a script with a cloud key. Within minutes automated bots found it and launched expensive servers for crypto-mining; the bill arrived the next day. Moving secrets to environment variables, enabling push protection, restricting the key's permissions and setting a billing alert would each have limited the damage.

**Example 2: The poisoned update.** A widely used package was hijacked for a few hours and a release published that sent environment variables to an attacker. Projects pinning exact versions with hashes were unaffected until they deliberately upgraded; projects with floating versions installed it on their next build.

## 10. Practice

1. Extend `scan` to flag Slack tokens that start with `xoxb-` followed by 20 or more characters.
2. Add `Secret.__eq__` so two secrets compare in constant time without revealing either.
3. Add a `RedactFilter` rule for credit-card-like numbers (13 to 16 digits).
4. Why does the audit log chain include the previous hash? What attack remains if the attacker can rewrite *every* entry and recompute all hashes?
5. List five things you would check before adding a new dependency.
6. A key was committed and pushed ten minutes ago. In order, what do you do?

<details>
<summary>Solutions</summary>

1. ```python
   PATTERNS["Slack bot token"] = re.compile(r"\bxoxb-[A-Za-z0-9-]{20,}\b")
   print(scan('slack = "xoxb-' + "1" * 24 + '"')[0][1])
   # Slack bot token
   ```
2. ```python
   import hmac
   def secret_eq(self, other):
       return isinstance(other, Secret) and hmac.compare_digest(self._value.encode(), other._value.encode())
   Secret.__eq__ = secret_eq
   print(Secret("a") == Secret("a"), Secret("a") == Secret("b"))
   # True False
   ```
3. ```python
   card = re.compile(r"\b\d{13,16}\b")
   print(card.sub("[CARD]", "paid with 4111111111111111 ok"))
   # paid with [CARD] ok
   ```
4. Each entry's hash covers the previous hash, so editing or deleting one entry invalidates every later entry. An attacker who can rewrite and recompute the **entire** chain can still forge history, which is why you also keep the latest hash somewhere the attacker cannot reach (a separate write-only log server, a signed checkpoint or a public timestamp).
5. Examples: maintenance activity and recent releases; number of maintainers; known vulnerabilities; size of its own dependency tree; licence; whether you could write the 20 lines yourself instead; whether the name is exactly the one you intended.
6. (1) Revoke and rotate the key immediately; (2) check the provider's logs for use of the old key; (3) remove it from the code and load it from the environment; (4) clean history only afterwards; (5) add scanning and push protection so it cannot recur.

</details>

## 11. Check yourself

1. Why is deleting a leaked secret from the latest commit not enough?
2. Where should secrets live instead of source code?
3. How does a scanner recognise secrets?
4. What is typosquatting, and what is dependency confusion?
5. What does `--require-hashes` protect against?
6. How does hash chaining make a log tamper-evident?
7. Give three container hardening measures.

<details>
<summary>Answers</summary>

1. It stays in git history and in any clone or fork, and bots harvest public leaks within minutes; the secret must be revoked and rotated.
2. In environment variables or a secret manager, injected at runtime, different per environment, scoped to least privilege, and rotatable.
3. By known formats (for example the `AKIA` prefix) and by detecting high-entropy, random-looking strings.
4. Typosquatting: a malicious package with a name close to a popular one. Dependency confusion: a public package with the same name as an internal one that the installer prefers.
5. A tampered or substituted file (a compromised mirror or a hijacked re-upload), because the installer refuses any artifact whose hash differs from the one recorded.
6. Each entry includes the hash of the previous one, so changing any entry changes its hash and breaks the link to the next one; verification fails.
7. For example: run as non-root, use a minimal base image, keep secrets out of layers, read-only filesystem, drop capabilities, set resource limits, scan images.

</details>

[Back to Security](../README.md)
