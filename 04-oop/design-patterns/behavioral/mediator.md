# Mediator Pattern

**Family:** behavioral · **How often you will use it:** occasionally (UI, chat, event buses) · **Difficulty:** medium

## 1. In plain words

A **Mediator** is a **go-between**: instead of many objects talking to each other directly (and each knowing all the others), they all talk **only to the mediator**, which decides who needs to know what.

Analogy: **air traffic control**. Planes do not negotiate with each other; each pilot talks to the tower, and the tower coordinates landings and takeoffs.

## 2. The problem

Many objects reference each other, producing a tangle that is hard to change:

```python
class Checkbox:
    def toggle(self):
        self.checked = not self.checked
        submit_button.enabled = self.checked      # knows the button
        error_label.visible = not self.checked    # knows the label
        # every new widget makes every other widget more complicated
```

With N components talking to each other you can have N x (N-1) connections.

## 3. The solution

```text
Before:  A ↔ B ↔ C ↔ D (everyone knows everyone)

After:        A
              │
          B ─ Mediator ─ C       (everyone knows only the mediator)
              │
              D
```

## 4. Step by step

### A chat room

```python
class ChatRoom:                                         # the mediator
    def __init__(self):
        self.users = {}
    def join(self, user):
        self.users[user.name] = user
        user.room = self
    def send(self, sender, text, to=None):
        if to:
            targets = [self.users[to]]                  # private message
        else:
            targets = [u for n, u in self.users.items() if n != sender.name]    # broadcast
        for u in targets:
            u.receive(sender.name, text)

class User:                                             # a colleague: knows only the room
    def __init__(self, name):
        self.name, self.inbox, self.room = name, [], None
    def say(self, text, to=None):
        self.room.send(self, text, to)
    def receive(self, sender, text):
        self.inbox.append(f"{sender}: {text}")

room = ChatRoom()
ana, bo, cy = User("ana"), User("bo"), User("cy")
for u in (ana, bo, cy):
    room.join(u)
ana.say("hi all")
bo.say("psst", to="cy")
print(bo.inbox)                                         # ['ana: hi all']
print(cy.inbox)                                         # ['ana: hi all', 'bo: psst']
```

Adding a new participant touches only the room; users never reference each other.

### A dialog that coordinates its widgets

```python
class Checkbox:
    def __init__(self, mediator):
        self.mediator, self.checked = mediator, False
    def toggle(self):
        self.checked = not self.checked
        self.mediator.notify(self, "toggled")

class Button:
    def __init__(self):
        self.enabled = False

class Dialog:                                           # the mediator holds the interaction logic
    def __init__(self):
        self.agree = Checkbox(self)
        self.submit = Button()
    def notify(self, sender, event):
        if sender is self.agree and event == "toggled":
            self.submit.enabled = self.agree.checked    # the rule lives in ONE place

d = Dialog()
print(d.submit.enabled)                                 # False
d.agree.toggle(); print(d.submit.enabled)               # True
d.agree.toggle(); print(d.submit.enabled)               # False
```

### A tiny event bus (a topic-based mediator)

```python
class EventBus:
    def __init__(self):
        self.subscribers = {}
    def subscribe(self, topic, fn):
        self.subscribers.setdefault(topic, []).append(fn)
    def publish(self, topic, payload):
        for fn in self.subscribers.get(topic, []):
            fn(payload)

bus, received = EventBus(), []
bus.subscribe("order.created", lambda o: received.append(f"inventory reserves {o}"))
bus.subscribe("order.created", lambda o: received.append(f"email confirms {o}"))
bus.publish("order.created", "order-1")
print(received)                                         # ['inventory reserves order-1', 'email confirms order-1']
```

## 5. The Pythonic way

- A mediator can be a plain class, a module with functions, or an **event bus** (Django signals, message brokers, `asyncio` queues).
- Frameworks: GUI dialog controllers, Redux-style stores, CQRS command/query buses, Python `blinker` signals.
- Keep it **thin**: it routes and coordinates; business rules belong in the colleagues or services.

## 6. When to use it (and when not to)

**Use it when** many objects interact in complex ways and the web of references is hard to follow; when you want components to be reusable without knowing their peers (chat rooms, form widgets, air-traffic style coordination, microservice event buses).

**Skip it when** only two objects talk (call directly), or when it would turn into one huge class holding all logic.

## 7. Pros and cons

| Pros | Cons |
|------|------|
| Reduces many-to-many dependencies to many-to-one | The mediator can become a **god object** |
| Colleagues become simpler and reusable | Centralized logic is harder to understand and test if it grows |
| Interaction rules live in one place | A single point of failure/bottleneck |

## 8. Related patterns

- [Observer](observer.md): one-to-many broadcast; Mediator centralizes two-way coordination (and is often *implemented* with Observer).
- [Facade](../structural/facade.md): simplifies a subsystem one way (client to subsystem); Mediator coordinates colleagues in both directions.
- [Command](command.md): command buses are mediators.

## 9. Two real-world examples

**Example 1: Form controllers.** On a signup form, selecting "Company" shows extra fields, ticking "I agree" enables Submit, an error on email highlights a label. A form-controller mediator holds these rules, so each widget stays dumb.

**Example 2: Microservices event bus.** Order, inventory, billing and notification services do not call each other directly. They publish and subscribe events on a broker, which coordinates the workflow.

## 10. Common mistakes

- Letting the mediator absorb all business logic.
- Colleagues sneaking direct references to each other, defeating the pattern.
- Mediator too chatty (every tiny change broadcast to everyone).

## 11. Practice

1. Extend `ChatRoom` with a `leave()` method and a mute list.
2. Build a `SignupForm` mediator: when "type" is "company", show a "company name" field; "Submit" enabled only if email is present and terms accepted.
3. What is the difference between a mediator and an observer subject?

<details>
<summary>Solutions</summary>

**1.**
```python
class ChatRoom2(ChatRoom):
    def __init__(self):
        super().__init__()
        self.muted = set()
    def leave(self, user):
        self.users.pop(user.name, None)
    def mute(self, name): self.muted.add(name)
    def send(self, sender, text, to=None):
        if sender.name in self.muted:
            return
        super().send(sender, text, to)
r = ChatRoom2(); a, b = User("a"), User("b"); r.join(a); r.join(b)
r.mute("a"); a.say("hello"); print(b.inbox)             # []
r.muted.clear(); a.say("hello"); r.leave(b); a.say("x"); print(b.inbox)    # ['a: hello']
```

**2.**
```python
class SignupForm:
    def __init__(self):
        self.type, self.email, self.terms = "person", "", False
        self.company_field_visible, self.submit_enabled = False, False
    def set(self, field, value):
        setattr(self, field, value)
        self._refresh()
    def _refresh(self):                                 # the mediator's rules
        self.company_field_visible = self.type == "company"
        self.submit_enabled = bool(self.email) and self.terms
f = SignupForm(); f.set("type", "company"); f.set("email", "a@x.com"); f.set("terms", True)
print(f.company_field_visible, f.submit_enabled)        # True True
```

**3.** A subject broadcasts its own state changes one-way to observers who react independently; a mediator receives messages from peers, applies coordination rules, and sends targeted messages back (many-to-many routed through one point).

</details>

## 12. Check yourself

1. What problem does Mediator solve?
2. What is its main risk?
3. Mediator versus Facade versus Observer?
4. Give two real examples.

<details>
<summary>Answers</summary>

1. A tangle of direct references between many interacting objects; it replaces them with one coordinator.
2. It becoming a god object that contains all the logic.
3. Mediator: two-way coordination between peers. Facade: simple one-way entry point to a subsystem. Observer: a subject broadcasts changes to subscribers.
4. Chat rooms/air traffic control, form controllers, event buses in microservices.

</details>

## More examples

Runnable script (added to your companion repository with this lesson): [`behavioralPattern/mediatorPattern.py`](https://github.com/M-Hammad-Faisal/design-patterns-python/blob/master/behavioralPattern/mediatorPattern.py)

[Family overview](README.md) · [All patterns](../README.md)
