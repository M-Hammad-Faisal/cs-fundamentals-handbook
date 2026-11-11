# Standard Library Toolbox: One-Page Summary

## Key facts

- **`re`:** `search` (anywhere), `match` (at the start), `fullmatch`, `findall`, `finditer`, `sub`; groups `(...)` and named groups `(?P<name>...)`; write patterns as raw strings `r"..."`; `.*?` is the lazy form; `re.VERBOSE` allows comments.
- **`datetime`:** a naive value has no zone, an aware one does. Store and compute in UTC (`datetime.now(timezone.utc)`), convert for display with `zoneinfo.ZoneInfo`; `timedelta` for differences; `isoformat` and `fromisoformat` for text.
- **`subprocess`:** `subprocess.run(["cmd", "arg"], capture_output=True, text=True, check=True, timeout=10)`; pass a list, not a string, and avoid `shell=True`.
- **`argparse`:** `ArgumentParser`, `add_argument`, `action="store_true"` for flags, subcommands for tools with several verbs; end scripts with `if __name__ == "__main__": raise SystemExit(main())`.
- **Worth knowing:** `pathlib`, `json`, `csv`, `collections`, `itertools`, `functools`, `logging`, `tempfile`, `shutil`, `hashlib`, `secrets`.

## Pitfalls

- `re.match` when you meant `search`; parsing HTML or nested JSON with regular expressions.
- Nested quantifiers such as `(a+)+` can backtrack catastrophically (ReDoS).
- Mixing naive and aware datetimes; assuming every day has 24 hours.
- `shell=True` with user input (command injection); forgetting `check=True`, so failures pass silently.

## Self-check

- **When should you use `fullmatch` instead of `match` or `search`?** When the entire string must fit the pattern (validation); `match` only anchors at the start and `search` finds a match anywhere.
- **What do named groups and `re.VERBOSE` buy you?** Readable, self-documenting patterns and results accessed by name instead of position.
- **Why store times in UTC and keep an IANA zone name for display?** UTC is unambiguous and comparable; the zone name lets you apply the right local rules (including DST) when showing a time to a person.
- **Why is "tomorrow at noon" sometimes not 24 hours away?** Daylight saving changes make some days 23 or 25 hours long; wall-clock arithmetic and elapsed-time arithmetic differ.
- **Why pass a list to `subprocess.run`, and what does `check=True` do?** A list bypasses the shell so arguments cannot inject commands; `check=True` raises `CalledProcessError` if the exit code is non-zero.
- **How do you make an `argparse` CLI easy to test?** Build the parser in a function and call `parse_args([...])` with explicit lists, instead of relying on `sys.argv`.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [The Standard Library Toolbox](01-regex-datetime-subprocess-argparse.md)
