# Observability: Exercises

Try each problem before opening its solution. These are the practice problems of this topic's lessons, collected in one place.

## Observability

1. Add a `p90` line to the latency output. Which of mean, p50, p90, p95 and p99 would you alert on, and why?
2. Compute the chance that a request making 20 independent backend calls hits at least one p99 slow call.
3. Extend `Span` to record an `error` flag when the `with` block raises, and show it in the printout.
4. A service handles 5 million requests a month with a 99.95 percent SLO. How many failed requests may it have? How many minutes of total outage?
5. Make `handle_request` log the amount only when it is under 100 and redact it otherwise. Why?
6. Explain why you cannot average the p99 latencies of three servers to get the overall p99.

<details>
<summary>Solutions</summary>

1. ```python no-run
   print(percentile(lat, 90))
   # 20
   ```
   Alert on a high percentile of a user-facing SLI (for example p99 or the SLO burn rate); the mean hides the tail and the median hides it too.
2. ```python no-run
   print(round(1 - 0.99 ** 20, 3))
   # 0.182
   ```
3. ```python no-run
   class Span2(Span):
       def __exit__(self, exc_type, exc, tb):
           self.error = exc_type is not None
           super().__exit__(exc_type, exc, tb)
   try:
       with Span2("flaky.call") as sp:
           raise ValueError("boom")
   except ValueError:
       print(sp.error)
   # True
   ```
4. ```python no-run
   print(round(5_000_000 * (1 - 0.9995)), round(30 * 24 * 60 * (1 - 0.9995), 1))
   # 2500 21.6
   ```
   2,500 failed requests, or about 21.6 minutes of full outage in a 30-day month.
5. Logging a sensitive or high-cardinality value everywhere is a privacy and cost risk; redacting at the logging call keeps useful fields while preventing leaks. (Apply the rule at the source rather than trusting a downstream filter.)
6. A percentile depends on the whole distribution and on how many requests each server handled; the 99th percentile of the combined data can be higher or lower than any weighted mix of the individual p99s. Merge the histograms (bucket counts) and compute the percentile from the merged histogram.

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Observability](01-observability-logs-metrics-traces-slos.md)
