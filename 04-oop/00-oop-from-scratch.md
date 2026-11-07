# OOP From Scratch: Your First Classes

**Prerequisites:** [Python functions and data types](../00-foundations/python-fundamentals/README.md) and the idea of a `dict`. **You will learn:** what problem object-oriented programming solves, the words **class**, **object**, **attribute**, **method** and `self`, how to build a small system out of cooperating objects, and a first look at the four pillars (**encapsulation, abstraction, inheritance, polymorphism**). This is the on-ramp; the deeper lessons that follow assume you have read it.

## 1. The problem OOP solves

Imagine a program for a small bank. Without classes you track each account with separate variables, then with a dictionary:

```python
account_1 = {"owner": "Ana", "balance": 100}
account_2 = {"owner": "Bo", "balance": 50}

def deposit(account, amount):
    account["balance"] += amount

def withdraw(account, amount):
    if amount > account["balance"]:
        raise ValueError("insufficient funds")
    account["balance"] -= amount

deposit(account_1, 25)
withdraw(account_2, 20)
print(account_1, account_2)       # {'owner': 'Ana', 'balance': 125} {'owner': 'Bo', 'balance': 30}
```

It works, but nothing stops a bug elsewhere from doing `account_1["balance"] = -999`, the functions live apart from the data they belong to, and every new kind of account means more loose functions. **OOP bundles data and the behavior that works on that data into one unit: an object.**

## 2. Class and object

- A **class** is a **blueprint** (a cookie cutter): it says what data an object holds and what it can do.
- An **object** (or **instance**) is one thing built from the blueprint (one cookie). You can build many objects from one class, each with its own data.

```python
class Account:
    def __init__(self, owner, balance=0):       # runs when you create an Account
        self.owner = owner                      # attributes: the object's data
        self.balance = balance

    def deposit(self, amount):                  # methods: what the object can do
        self.balance += amount

    def withdraw(self, amount):
        if amount > self.balance:
            raise ValueError("insufficient funds")
        self.balance -= amount

    def __str__(self):                          # how the object prints
        return f"{self.owner}: {self.balance}"

ana = Account("Ana", 100)                       # create (instantiate) two objects
bo = Account("Bo", 50)
ana.deposit(25)
bo.withdraw(20)
print(ana, "|", bo)                             # Ana: 125 | Bo: 30
print(ana.balance, bo.balance)                  # 125 30
```

### The vocabulary, one thing at a time

| Word | Meaning | In the example |
|------|---------|----------------|
| **Class** | the blueprint | `Account` |
| **Object / instance** | one thing made from it | `ana`, `bo` |
| **Attribute** | a variable that belongs to an object | `ana.balance` |
| **Method** | a function that belongs to an object | `ana.deposit(25)` |
| **Constructor** | the code that sets up a new object | `__init__` |
| **`self`** | "the object this method is working on" | `self.balance` |

### What `self` really is

When you write `ana.deposit(25)`, Python calls `Account.deposit(ana, 25)`: the object before the dot is passed automatically as the first argument, which by convention is named `self`. That is how one method body works for every account:

```python
print(Account.deposit(bo, 5), bo.balance)       # None 35   (same as bo.deposit(5): the method returns nothing)
```

### Objects are independent

```python
a, b = Account("A", 10), Account("B", 10)
a.deposit(90)
print(a.balance, b.balance)                     # 100 10    (changing a does not touch b)
```

## 3. Objects working together

Real programs are **several objects that cooperate**, each doing one job. A bank has customers, accounts and a bank that holds them:

```python
class Bank:
    def __init__(self, name):
        self.name = name
        self.accounts = {}                      # owner -> Account

    def open_account(self, owner, deposit=0):
        if owner in self.accounts:
            raise ValueError(f"{owner} already has an account")
        self.accounts[owner] = Account(owner, deposit)
        return self.accounts[owner]

    def transfer(self, source, target, amount):
        self.accounts[source].withdraw(amount)  # if this raises, nothing was deposited yet
        self.accounts[target].deposit(amount)

    def total_deposits(self):
        return sum(acc.balance for acc in self.accounts.values())

bank = Bank("Lahore Savings")
bank.open_account("Ana", 100)
bank.open_account("Bo", 50)
bank.transfer("Ana", "Bo", 30)
print(bank.accounts["Ana"], "|", bank.accounts["Bo"], "|", bank.total_deposits())      # Ana: 70 | Bo: 80 | 150
try:
    bank.transfer("Ana", "Bo", 1000)
except ValueError as e:
    print("refused:", e)                        # refused: insufficient funds
```

Notice how you read the program: `bank.transfer("Ana", "Bo", 30)` says what happens, not how. Each object hides its own details behind a few clearly named methods.

## 4. The four pillars, each in one small example

You will study each in depth in the next lessons; here is the first taste.

### Encapsulation: keep data safe behind methods

Put the rules where the data lives, so nobody can break them by accident. Python marks "internal" attributes with a leading underscore (a convention that says "please do not touch from outside").

```python
class SafeAccount:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self._balance = balance                 # internal: change it only through methods

    @property
    def balance(self):                          # read-only access that looks like an attribute
        return self._balance

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("deposit must be positive")
        self._balance += amount

acct = SafeAccount("Ana", 100)
acct.deposit(50)
print(acct.balance)                             # 150
try:
    acct.balance = 1_000_000                    # no setter defined: refused
except AttributeError as e:
    print("blocked:", e)                        # blocked: property 'balance' of 'SafeAccount' object has no setter
```

### Abstraction: show *what*, hide *how*

A driver uses the steering wheel and pedals; they do not need the engine's internals. Callers of `transfer` do not need to know how `Bank` stores accounts, which means you can change the storage later (a database instead of a dict) without breaking any caller.

### Inheritance: reuse and specialize

A new class can **start from an existing class** and add or change behavior. Use it for a real **"is a"** relationship (a savings account *is an* account).

```python
class SavingsAccount(Account):                  # SavingsAccount IS-A Account
    def __init__(self, owner, balance=0, rate=0.02):
        super().__init__(owner, balance)        # let Account set up owner and balance
        self.rate = rate

    def add_interest(self):
        self.deposit(self.balance * self.rate)

s = SavingsAccount("Cy", 1000, rate=0.05)
s.add_interest()
s.withdraw(50)                                  # inherited from Account
print(s, isinstance(s, Account))                # Cy: 1000.0 True
```

### Polymorphism: one call, different behavior

Different kinds of objects respond to the same method name in their own way, so the caller does not need `if` chains on the type.

```python
class CheckingAccount(Account):
    def withdraw(self, amount):                 # overrides: checking allows an overdraft of 100
        if amount > self.balance + 100:
            raise ValueError("overdraft limit exceeded")
        self.balance -= amount

accounts = [Account("A", 50), CheckingAccount("B", 50), SavingsAccount("C", 50)]
for acc in accounts:
    try:
        acc.withdraw(120)                       # the SAME call; each class decides what it means
        print(type(acc).__name__, "allowed ->", acc.balance)
    except ValueError as e:
        print(type(acc).__name__, "refused:", e)
# Account refused: insufficient funds
# CheckingAccount allowed -> -70
# SavingsAccount refused: insufficient funds
```

## 5. When to use classes (and when not to)

Classes shine when you have **state** (data that changes over time) together with **behavior** that must keep that state valid, and when you will have **several similar things**. They are overkill for a one-off calculation: a plain function is simpler.

| Use a function | Use a class |
|----------------|-------------|
| Same input always gives the same output (a calculation) | Data persists and changes (accounts, game characters, connections) |
| No data to remember between calls | Several operations share the same data |
| One-off transformation | Many objects of the same kind |

Python also offers lighter tools for plain data: `dict`, `tuple`, `namedtuple`, and `@dataclass` (see [modern Python](../08-modern-python/README.md)).

```python
from dataclasses import dataclass

@dataclass
class Point:                                    # a class that is mostly data: dataclass writes __init__ and __repr__ for you
    x: float
    y: float

print(Point(1.5, 2), Point(1, 2) == Point(1, 2))       # Point(x=1.5, y=2) True
```

## 6. A complete mini-project: a library

Putting everything together: books, members and a library that lends books.

```python
class Book:
    def __init__(self, title, author):
        self.title, self.author = title, author
        self.borrowed_by = None                 # None means available

    def __str__(self):
        status = f"borrowed by {self.borrowed_by}" if self.borrowed_by else "available"
        return f"{self.title} by {self.author} ({status})"

class Library:
    def __init__(self):
        self.books = []
        self.loans = {}                         # member -> list of Books

    def add(self, book):
        self.books.append(book)

    def lend(self, title, member, limit=2):
        book = next((b for b in self.books if b.title == title), None)
        if book is None:
            raise LookupError(f"no such book: {title}")
        if book.borrowed_by:
            raise ValueError(f"{title} is already borrowed")
        if len(self.loans.get(member, [])) >= limit:
            raise ValueError(f"{member} reached the limit of {limit} books")
        book.borrowed_by = member
        self.loans.setdefault(member, []).append(book)

    def give_back(self, title, member):
        book = next(b for b in self.loans.get(member, []) if b.title == title)
        self.loans[member].remove(book)
        book.borrowed_by = None

    def available(self):
        return [b.title for b in self.books if b.borrowed_by is None]

lib = Library()
for title, author in [("Dune", "Herbert"), ("Emma", "Austen"), ("Ulysses", "Joyce"), ("Hamlet", "Shakespeare")]:
    lib.add(Book(title, author))

lib.lend("Dune", "Ana")
lib.lend("Emma", "Ana")
print(lib.available())                          # ['Ulysses', 'Hamlet']
try:
    lib.lend("Ulysses", "Ana")                  # third book: over the limit
except ValueError as e:
    print("refused:", e)                        # refused: Ana reached the limit of 2 books
lib.give_back("Dune", "Ana")
print(lib.books[0])                             # Dune by Herbert (available)
print(lib.books[1])                             # Emma by Austen (borrowed by Ana)
```

## 7. Common beginner mistakes

- Forgetting `self.` when reading or setting an attribute (`balance = 5` creates a local variable instead of setting `self.balance`).
- Forgetting `self` as the first parameter of a method (`TypeError: ... takes 1 positional argument but 2 were given`).
- Using a mutable default argument (`def __init__(self, items=[])`): every object shares one list. Use `items=None` then `self.items = items or []`.
- Calling a method without parentheses (`acc.deposit` is the method itself; `acc.deposit(5)` calls it).
- Building giant classes that do everything (see [SOLID](solid/README.md)).
- Using inheritance for convenience instead of a true "is a" (prefer [composition](composition-design/README.md)).

The mutable-default trap in action:

```python
class Bad:
    def __init__(self, items=[]):               # ONE list is created when the function is defined
        self.items = items

x, y = Bad(), Bad()
x.items.append("shared!")
print(y.items)                                  # ['shared!']   y was changed by an action on x

class Good:
    def __init__(self, items=None):
        self.items = [] if items is None else items

p, q = Good(), Good()
p.items.append("mine")
print(q.items)                                  # []
```

## 8. Practice

1. Write a `Rectangle` class with `width`, `height`, and methods `area()` and `perimeter()`. Create two rectangles and print their areas.
2. Add `__str__` to `Rectangle` so `print(rect)` shows `Rectangle(3 x 4)`.
3. Write a `Counter` class with `increment()`, `reset()` and a `value` attribute. Show that two counters are independent.
4. Write `Student` with a name and a list of grades, a method `add_grade(g)` that rejects values outside 0-100, and `average()`.
5. Create `Square` that inherits from `Rectangle` and takes a single `side`.
6. Which of these should be a class, and which a function? (a) compute tax for an amount, (b) a shopping cart, (c) convert Celsius to Fahrenheit, (d) a game character with health and position.
7. What is wrong with `class Basket: def __init__(self, items=[]): self.items = items`? Fix it.

<details>
<summary>Solutions</summary>

**1-2.**
```python
class Rectangle:
    def __init__(self, width, height):
        self.width, self.height = width, height
    def area(self):
        return self.width * self.height
    def perimeter(self):
        return 2 * (self.width + self.height)
    def __str__(self):
        return f"Rectangle({self.width} x {self.height})"

r1, r2 = Rectangle(3, 4), Rectangle(5, 2)
print(r1.area(), r2.area(), r1)                 # 12 10 Rectangle(3 x 4)
```

**3.**
```python
class Counter:
    def __init__(self):
        self.value = 0
    def increment(self):
        self.value += 1
    def reset(self):
        self.value = 0

c1, c2 = Counter(), Counter()
c1.increment(); c1.increment(); c2.increment()
print(c1.value, c2.value)                       # 2 1
```

**4.**
```python
class Student:
    def __init__(self, name):
        self.name, self.grades = name, []
    def add_grade(self, g):
        if not 0 <= g <= 100:
            raise ValueError("grade must be between 0 and 100")
        self.grades.append(g)
    def average(self):
        return sum(self.grades) / len(self.grades) if self.grades else 0

s = Student("Ana"); s.add_grade(90); s.add_grade(80)
print(s.average())                              # 85.0
```

**5.**
```python
class Square(Rectangle):
    def __init__(self, side):
        super().__init__(side, side)
print(Square(4).area(), Square(4))              # 16 Rectangle(4 x 4)
```

**6.** (a) function, (b) class (state: items change), (c) function, (d) class (state and behavior).

**7.** The default list is shared by all baskets. Fix:
```python
class Basket:
    def __init__(self, items=None):
        self.items = [] if items is None else list(items)
```

</details>

## 9. Check yourself

1. What is the difference between a class and an object?
2. What is `self`?
3. What does `__init__` do and when does it run?
4. Name the four pillars of OOP in one phrase each.
5. When is a plain function better than a class?
6. Why is `def __init__(self, items=[])` a bug?

<details>
<summary>Answers</summary>

1. A class is the blueprint; an object is one instance built from it with its own data.
2. The object the method is currently working on, passed automatically as the first argument.
3. It initializes a new object's attributes; it runs when you create the object (`Account("Ana")`).
4. Encapsulation: bundle data with rules and protect it. Abstraction: expose what, hide how. Inheritance: build on an existing class. Polymorphism: same call, behavior chosen by the object's type.
5. For stateless calculations or one-off transformations with nothing to remember.
6. The default list is created once and shared by every object that uses the default.

</details>

**Where next:** [classes and objects in depth](classes-objects/README.md) (object lifecycle, `__slots__`, equality and copying).

Back to [OOP overview](README.md)
