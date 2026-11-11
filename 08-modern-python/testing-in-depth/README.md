# Testing in Depth

pytest, fixtures, mocking and property-based testing with Hypothesis.

## Detailed lessons

- [Testing in depth: pytest, fixtures, mocking and property-based testing](01-pytest-mocking-and-property-testing.md)

## Practice and review

- [Exercises](exercises.md) with solutions
- [One-page summary](summary.md)

## Quick reference

| Question | Answer |
|----------|--------|
| What is the arrange-act-assert pattern? | Set up inputs, call the code under test, then check the result. |
| What do `parametrize` and fixtures each give you? | `parametrize` runs one test body over many input rows as separate tests; fixtures supply (and clean up) the objects tests need, injected by parameter name. |
| Why prefer dependency injection over patching? | A fake passed as an argument needs no patching magic, keeps tests readable and keeps the code more modular. |
| Where should you patch a name, and why? | Where the name is looked up (the module under test), because that is the reference being replaced. |
| What is a property-based test and what is shrinking? | A test that states a rule holding for all inputs, with generated inputs; shrinking reduces a failing input to the smallest one that still fails. |

Back to [modern Python](../README.md).
