# Distributed Transactions and Reliability Patterns: Exercises

These problems go with the [Distributed Transactions and Reliability Patterns lesson](README.md). Try each one before opening its solution.

<details>
<summary>Setup code the solutions use (copied from the lessons)</summary>

```python
import random

calls = {"n": 0}

def flaky():
    calls["n"] += 1
    if calls["n"] < 4:
        raise TimeoutError("slow server")
    return f"succeeded on call {calls['n']}"
```

</details>

## Problems

1. Make the `retry` function also accept a `deadline` (total seconds budget) and stop retrying when the next sleep would exceed it.
2. Why is `UPDATE accounts SET balance = balance - 10 WHERE id = 1` not idempotent, and how would you make a money transfer idempotent?
3. Add a fourth step "send confirmation email" to the saga. Where should it go and why?
4. In the circuit breaker, what happens in `half-open` state if the trial call fails? Trace it.
5. A consumer crashes after processing a message but before acknowledging it. What happens on restart, and what must the handler do?
6. Compute the worst-case number of calls to the bottom service when 3 layers each make up to 3 attempts.

<details>
<summary>Solutions</summary>

1. ```python
   def retry_with_deadline(fn, budget, base=0.1, rng=None, retryable=(TimeoutError,)):
       rng = rng or random.Random(0)
       spent, n = 0.0, 0
       while True:
           try:
               return fn()
           except retryable:
               wait = rng.uniform(0, min(5.0, base * 2 ** n))
               if spent + wait > budget:
                   raise
               spent += wait
               n += 1
   calls["n"] = 0
   print(retry_with_deadline(flaky, budget=10))
   # succeeded on call 4
   ```
2. Running it twice subtracts 20. Give each transfer a unique id and record `transfer_id` in a table with a unique constraint **in the same transaction** as the balance update; a repeat hits the constraint and does nothing.
3. Last, after shipment: an email cannot be un-sent, so run it only when nothing after it can fail (or make its compensation "send a cancellation").
4. The next call is allowed through; it raises, so `self.state == "half-open"` triggers `state = "open"` and `opened_at = now`; the cool-down starts again.
5. The broker redelivers the message (it was never acknowledged), so the handler runs again; it must be idempotent (record processed ids, or make the effect repeat-safe).
6. `3 * 3 * 3 = 27` calls: each layer multiplies the attempts below it.

</details>

[Lesson](README.md) · [Summary](summary.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Idempotency, Retries, Circuit Breakers, Sagas and the Outbox](01-idempotency-retries-and-sagas.md)
