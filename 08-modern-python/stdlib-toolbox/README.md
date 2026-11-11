# Standard Library Toolbox

Regular expressions, dates and time zones, subprocesses and command-line tools.

## Detailed lessons

- [The standard library toolbox](01-regex-datetime-subprocess-argparse.md)

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

## Quick reference

| Question | Answer |
|----------|--------|
| When should you use `fullmatch` instead of `match` or `search`? | When the entire string must fit the pattern (validation); `match` only anchors at the start and `search` finds a match anywhere. |
| What do named groups and `re.VERBOSE` buy you? | Readable, self-documenting patterns and results accessed by name instead of position. |
| Why store times in UTC and keep an IANA zone name for display? | UTC is unambiguous and comparable; the zone name lets you apply the right local rules (including DST) when showing a time to a person. |
| Why is "tomorrow at noon" sometimes not 24 hours away? | Daylight saving changes make some days 23 or 25 hours long; wall-clock arithmetic and elapsed-time arithmetic differ. |
| Why pass a list to `subprocess.run`, and what does `check=True` do? | A list bypasses the shell so arguments cannot inject commands; `check=True` raises `CalledProcessError` if the exit code is non-zero. |

Back to [modern Python](../README.md).
