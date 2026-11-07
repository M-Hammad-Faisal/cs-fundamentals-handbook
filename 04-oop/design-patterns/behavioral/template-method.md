# Template Method Pattern

**Family:** behavioral · **How often you will use it:** very often (frameworks) · **Difficulty:** easy

## 1. In plain words

**Template Method** fixes the **order of the steps** of an algorithm in a base class, and lets subclasses **fill in or change individual steps** without changing the order.

Analogy: a **recipe template for "bake something"**: preheat, mix, bake, cool, serve. Cake and bread follow the same steps in the same order but mix and bake differently.

It is sometimes called the **Hollywood principle**: *"don't call us, we'll call you"*. The base class calls your code, not the other way around.

## 2. The problem

Several classes share the same overall procedure but differ in details, and the shared skeleton gets copy-pasted:

```python
class CsvImporter:
    def run(self, src):
        raw = open_source(src); rows = parse_csv(raw); rows = clean(rows); save(rows)
class JsonImporter:
    def run(self, src):
        raw = open_source(src); rows = parse_json(raw); rows = clean(rows); save(rows)   # same skeleton again
```

## 3. The solution

```text
AbstractClass
 + run()            ◄── the template: calls the steps in a fixed order (never overridden)
 + step_one()       ◄── abstract: subclasses MUST implement
 + step_two()       ◄── hook: optional, has a default
        ▲
 ConcreteClass: overrides the steps
```

## 4. Step by step

```python
from abc import ABC, abstractmethod

class ReportGenerator(ABC):
    def generate(self, data):                           # the template method: fixed order
        rows = self.collect(data)
        body = self.format(rows)
        return self.header() + body + self.footer()

    @abstractmethod
    def collect(self, data): ...                        # required step

    @abstractmethod
    def format(self, rows): ...                         # required step

    def header(self): return ""                         # optional "hook" with a default
    def footer(self): return ""

class CsvReport(ReportGenerator):
    def collect(self, data):
        return sorted(data.items())
    def format(self, rows):
        return "\n".join(f"{k},{v}" for k, v in rows)
    def header(self):
        return "key,value\n"

class HtmlReport(ReportGenerator):
    def collect(self, data):
        return sorted(data.items())
    def format(self, rows):
        return "".join(f"<li>{k}: {v}</li>" for k, v in rows)
    def header(self): return "<ul>"
    def footer(self): return "</ul>"

data = {"b": 2, "a": 1}
print(CsvReport().generate(data))
# key,value
# a,1
# b,2
print(HtmlReport().generate(data))                      # <ul><li>a: 1</li><li>b: 2</li></ul>
```

### A pipeline with a validation hook

```python
class DataPipeline(ABC):
    def run(self):
        rows = self.transform(self.extract())
        if not self.validate(rows):
            raise ValueError("invalid data")
        return self.load(rows)

    @abstractmethod
    def extract(self): ...
    @abstractmethod
    def transform(self, rows): ...
    @abstractmethod
    def load(self, rows): ...
    def validate(self, rows): return True               # hook

class Doubler(DataPipeline):
    def extract(self): return [1, 2, 3]
    def transform(self, rows): return [r * 2 for r in rows]
    def load(self, rows): return sum(rows)

class StrictDoubler(Doubler):
    def validate(self, rows): return all(r > 100 for r in rows)

print(Doubler().run())                                  # 12
try:
    StrictDoubler().run()
except ValueError as e:
    print(e)                                            # invalid data
```

## 5. The Pythonic way

- Frameworks use it everywhere: `unittest.TestCase` (`setUp`, test, `tearDown`), Django class-based views (`dispatch` calls `get` or `post`), `threading.Thread.run`, `json.JSONEncoder.default`, `ast.NodeVisitor`.
- Instead of subclassing, you can pass the varying steps in as **functions** (Strategy style): often simpler.

```python
def pipeline(extract, transform, load):                 # the "template" with steps as arguments
    return load(transform(extract()))

print(pipeline(lambda: [1, 2], lambda xs: [x * 10 for x in xs], sum))     # 30
```

- Mark steps that *must* be overridden with `@abstractmethod`; document hooks clearly.

## 6. When to use it (and when not to)

**Use it when** several classes share the same algorithm structure and differ in some steps; to let framework users plug in behavior at defined points; to avoid duplicating a skeleton.

**Skip it when** variation should change at runtime (use [Strategy](strategy.md)) or when inheritance would create deep hierarchies; prefer composition then.

## 7. Pros and cons

| Pros | Cons |
|------|------|
| Removes duplicated skeleton code | Coupled through inheritance (fragile base class) |
| Subclasses cannot break the overall order | Harder to follow control flow ("who calls what?") |
| Clear extension points | Limited to the one inheritance axis; cannot swap at runtime |

## 8. Related patterns

- [Strategy](strategy.md): composition and runtime swapping; Template Method uses inheritance.
- [Factory Method](../creational/factory-method.md): a factory method is a template-method step that creates an object.
- [Observer](observer.md), [Command](command.md): other ways to let code plug into a flow.

## 9. Two real-world examples

**Example 1: Test frameworks.** `unittest.TestCase.run` is the template: set up, run the test method, tear down, record results. You only override `setUp` and `test_*`.

**Example 2: Django class-based views.** `View.dispatch()` decides which HTTP method handler to call; `ListView` then calls `get_queryset()`, `get_context_data()` and renders a template. You override just those hooks.

## 10. Common mistakes

- Overriding the template method itself and breaking the order.
- Too many hooks, making the base class hard to understand.
- Forgetting `super()` when a hook has important default behavior.
- Deep inheritance trees of templates.

## 11. Practice

1. Write a `Beverage` template with `boil_water`, `brew`, `pour`, `add_condiments` (hook); implement `Tea` and `Coffee`.
2. Add a hook `should_cache()` to `DataPipeline` that skips `load` when false.
3. Rewrite the pipeline using functions instead of subclasses.

<details>
<summary>Solutions</summary>

**1.**
```python
class Beverage(ABC):
    def prepare(self):
        steps = ["boil water", self.brew(), "pour in cup"]
        if self.wants_condiments():
            steps.append(self.add_condiments())
        return steps
    @abstractmethod
    def brew(self): ...
    @abstractmethod
    def add_condiments(self): ...
    def wants_condiments(self): return True
class Tea(Beverage):
    def brew(self): return "steep tea bag"
    def add_condiments(self): return "add lemon"
class Coffee(Beverage):
    def brew(self): return "drip coffee"
    def add_condiments(self): return "add milk"
    def wants_condiments(self): return False
print(Tea().prepare(), Coffee().prepare())
```

**2.**
```python
class CachedPipeline(DataPipeline):
    def should_cache(self): return True
    def run(self):
        rows = self.transform(self.extract())
        return None if not self.should_cache() else self.load(rows)
class Demo(CachedPipeline, Doubler): pass
print(Demo().run())
```
(Better: add the `should_cache` hook inside `DataPipeline.run` itself so every subclass benefits.)

**3.** `pipeline(extract, transform, load)` shown above; the "steps" are plain functions.

</details>

## 12. Check yourself

1. What does the template method fix and what can subclasses change?
2. What is a hook?
3. Template Method versus Strategy?
4. Name two framework examples.

<details>
<summary>Answers</summary>

1. It fixes the order of the algorithm's steps; subclasses override individual steps.
2. An optional step with a default (often empty) implementation that subclasses may override.
3. Template Method varies steps via inheritance at design time; Strategy varies the algorithm via composition and can change at runtime.
4. `unittest.TestCase` setup/teardown flow; Django class-based view hooks (`get_queryset`, `get_context_data`).

</details>

## More examples

Runnable script (added to your companion repository with this lesson): [`behavioralPattern/templateMethodPattern.py`](https://github.com/M-Hammad-Faisal/design-patterns-python/blob/master/behavioralPattern/templateMethodPattern.py)

[Family overview](README.md) · [All patterns](../README.md)
