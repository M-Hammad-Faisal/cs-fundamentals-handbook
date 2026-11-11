# Standard Library Toolbox: Exercises

Try each problem before opening its solution. These are the practice problems of this topic's lessons, collected in one place.

## The Standard Library Toolbox

1. Write a regex that extracts all hashtags (`#word`, letters, digits and underscore) from a tweet, lower-cased and without duplicates (keep first appearance order).
2. Validate a UK-style postcode loosely with `fullmatch` (one or two letters, one or two digits, a space, a digit and two letters). Test it on four valid and four invalid examples.
3. A flight departs `2026-10-24 22:00` in `Asia/Karachi` and lands `2026-10-25 06:30` in `Europe/London` (local times). How long is the flight? (UK clocks go back on 2026-10-25 at 02:00.)
4. Run `git --version` (or `python --version`) with `subprocess.run`, capture the output and handle the case where the program does not exist (`FileNotFoundError`).
5. Add an `export` subcommand to the `todo` parser with a `--format` choice of `json` or `csv`, defaulting to `json`, and test parsing.
6. Explain why `datetime.now()` (naive) is a poor choice for a timestamp stored in a database.

<details>
<summary>Solutions</summary>

1. ```python no-run
   def hashtags(text):
       seen = []
       for tag in re.findall(r"#(\w+)", text):
           tag = tag.lower()
           if tag not in seen:
               seen.append(tag)
       return seen
   print(hashtags("Loving #Python and #python3! #Python #AI_2026"))
   # ['python', 'python3', 'ai_2026']
   ```
2. ```python no-run
   POSTCODE = re.compile(r"[A-Za-z]{1,2}\d{1,2} \d[A-Za-z]{2}")
   good = ["M1 1AE", "SW1 2AA", "EC1 4AB", "B33 8TH"]
   bad = ["", "12345", "M1AE", "SW1 2A"]
   print([bool(POSTCODE.fullmatch(p)) for p in good], [bool(POSTCODE.fullmatch(p)) for p in bad])
   # [True, True, True, True] [False, False, False, False]
   ```
   (Real postcodes have more rules; "loose but safe" is a sensible first filter.)
3. ```python no-run
   depart = datetime(2026, 10, 24, 22, 0, tzinfo=ZoneInfo("Asia/Karachi"))
   arrive = datetime(2026, 10, 25, 6, 30, tzinfo=ZoneInfo("Europe/London"))
   print(arrive.astimezone(timezone.utc) - depart.astimezone(timezone.utc))
   # 13:30:00
   ```
   Convert both to UTC and subtract: Karachi (UTC+5) 22:00 is 17:00 UTC; London at 06:30 on 25 October is already back on GMT (UTC+0), so 06:30 UTC; the flight is 13 hours 30 minutes. (Had you subtracted the naive local clock readings, 22:00 to 06:30, you would get 8.5 hours: wrong.)
4. ```python no-run
   try:
       out = subprocess.run(["git", "--version"], capture_output=True, text=True, check=True, timeout=5)
       print(out.stdout.strip().startswith("git version"))
   except FileNotFoundError:
       print("git is not installed")
   # True
   ```
5. ```python no-run
   parser2 = build_parser()
   sub_actions = [a for a in parser2._actions if isinstance(a, argparse._SubParsersAction)][0]
   export = sub_actions.add_parser("export", help="export tasks")
   export.add_argument("--format", choices=["json", "csv"], default="json")
   print(parser2.parse_args(["export"]).format, parser2.parse_args(["export", "--format", "csv"]).format)
   # json csv
   ```
   (The cleaner way is to add the subparser inside `build_parser`; this shows the idea.)
6. A naive local timestamp does not say which zone it is in, so it cannot be compared across servers or users, and it silently changes meaning when the server's zone or DST rules change. Store aware UTC instants.

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [The Standard Library Toolbox](01-regex-datetime-subprocess-argparse.md)
