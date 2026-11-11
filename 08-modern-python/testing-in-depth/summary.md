# Testing in Depth: One-Page Summary

## Key facts

- **pytest basics:** plain `assert`, functions named `test_*`, `pytest.raises(Error)`, `@pytest.mark.parametrize`, fixtures with `yield` for teardown, built-ins `tmp_path` and `monkeypatch`, shared fixtures in `conftest.py`.
- **Isolation:** inject dependencies first (pass the clock, client or `sleep` function), mock second; `Mock(spec=Cls)` rejects calls that do not exist; patch a name where it is used, not where it is defined.
- **Property-based tests:** Hypothesis `@given(strategies)` generates inputs and shrinks failures; useful properties are round-trips, idempotence, invariants and agreement with a slow reference.
- **Coverage:** `pytest --cov` shows which lines ran, not whether they were checked; branch coverage is stricter.
- **Suite design:** many fast unit tests, fewer integration tests, very few end-to-end; tests are independent, deterministic and follow arrange, act, assert.

## Pitfalls

- Over-mocking, so the test only checks the mock; patching the wrong import path.
- Tests that depend on order, wall-clock time or the network; real `sleep` calls.
- Asserting private implementation details instead of behaviour.
- Chasing 100% coverage while skipping edge cases; ignoring flaky tests.

## Self-check

- **What is the arrange-act-assert pattern?** Set up inputs, call the code under test, then check the result.
- **What do `parametrize` and fixtures each give you?** `parametrize` runs one test body over many input rows as separate tests; fixtures supply (and clean up) the objects tests need, injected by parameter name.
- **Why prefer dependency injection over patching?** A fake passed as an argument needs no patching magic, keeps tests readable and keeps the code more modular.
- **Where should you patch a name, and why?** Where the name is looked up (the module under test), because that is the reference being replaced.
- **What is a property-based test and what is shrinking?** A test that states a rule holding for all inputs, with generated inputs; shrinking reduces a failing input to the smallest one that still fails.
- **What does 100 percent line coverage prove, and what does it not?** It proves every line ran at least once; it does not prove assertions were meaningful or that logic is correct.

[Lesson](README.md) · [Exercises](exercises.md)

<!-- go-deeper -->
**Go deeper (detailed step-by-step lessons):** [Testing in Depth](01-pytest-mocking-and-property-testing.md)
