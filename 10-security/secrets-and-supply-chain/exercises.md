# Secrets and Supply Chain: Exercises

Try each problem before opening its solution. These are the practice problems of this topic's lessons, collected in one place.

## Secrets, Dependencies and Hardening

1. Extend `scan` to flag Slack tokens that start with `xoxb-` followed by 20 or more characters.
2. Add `Secret.__eq__` so two secrets compare in constant time without revealing either.
3. Add a `RedactFilter` rule for credit-card-like numbers (13 to 16 digits).
4. Why does the audit log chain include the previous hash? What attack remains if the attacker can rewrite *every* entry and recompute all hashes?
5. List five things you would check before adding a new dependency.
6. A key was committed and pushed ten minutes ago. In order, what do you do?

<details>
<summary>Solutions</summary>

1. ```python no-run
   PATTERNS["Slack bot token"] = re.compile(r"\bxoxb-[A-Za-z0-9-]{20,}\b")
   print(scan('slack = "xoxb-' + "1" * 24 + '"')[0][1])
   # Slack bot token
   ```
2. ```python no-run
   import hmac
   def secret_eq(self, other):
       return isinstance(other, Secret) and hmac.compare_digest(self._value.encode(), other._value.encode())
   Secret.__eq__ = secret_eq
   print(Secret("a") == Secret("a"), Secret("a") == Secret("b"))
   # True False
   ```
3. ```python no-run
   card = re.compile(r"\b\d{13,16}\b")
   print(card.sub("[CARD]", "paid with 4111111111111111 ok"))
   # paid with [CARD] ok
   ```
4. Each entry's hash covers the previous hash, so editing or deleting one entry invalidates every later entry. An attacker who can rewrite and recompute the **entire** chain can still forge history, which is why you also keep the latest hash somewhere the attacker cannot reach (a separate write-only log server, a signed checkpoint or a public timestamp).
5. Examples: maintenance activity and recent releases; number of maintainers; known vulnerabilities; size of its own dependency tree; licence; whether you could write the 20 lines yourself instead; whether the name is exactly the one you intended.
6. (1) Revoke and rotate the key immediately; (2) check the provider's logs for use of the old key; (3) remove it from the code and load it from the environment; (4) clean history only afterwards; (5) add scanning and push protection so it cannot recur.

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Secrets, Dependencies and Hardening](01-secrets-dependencies-and-hardening.md)
