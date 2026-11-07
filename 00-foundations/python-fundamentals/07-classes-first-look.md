# Python Basics 7: Classes and Objects, a First Look

**Prerequisites:** [functions](03-functions.md) and [collections](04-strings-lists-dicts-sets.md). **You will learn:** why classes exist, how to define one, attributes and methods, `__init__`, `__str__`, a small bank-account program, and where to go next in the OOP chapters.

## 1. In plain words

Until now we kept data in variables, lists and dictionaries, and wrote separate functions that work on them. As programs grow, a pattern appears: **some data and the functions that work on that data belong together**. A **class** bundles them.

- A **class** is a **blueprint** (like the plan of a house).
- An **object** (or **instance**) is **one thing built from the blueprint** (an actual house). You can build many.
- **Attributes** are the data an object holds (`balance`); **methods** are the functions it can perform (`deposit`).

```text
class BankAccount (blueprint)          objects (instances)
  attributes: owner, balance           ayesha = BankAccount("Ayesha", 100)   -> its own owner and balance
  methods: deposit(), withdraw()       bilal  = BankAccount("Bilal", 50)     -> a different one
```

## 2. Your first class

```python
class Dog:
    def __init__(self, name, age):           # the constructor: runs when you create a Dog
        self.name = name                     # attributes are stored on `self`, the object being created
        self.age = age

    def bark(self):                          # a method: a function that belongs to the class
        return f"{self.name} says woof!"

    def birthday(self):
        self.age += 1                        # methods can change the object's own data

rex = Dog("Rex", 3)                          # create an object (an "instance")
fido = Dog("Fido", 5)
print(rex.name, rex.age, rex.bark())         # Rex 3 Rex says woof!
rex.birthday()
print(rex.age, fido.age)                     # 4 5       (each object has its own data)
print(type(rex).__name__, isinstance(rex, Dog))     # Dog True
```

Key points:

- `self` is the object the method is working on; Python passes it automatically (`rex.bark()` means `Dog.bark(rex)`).
- `__init__` is the **initializer** (often called the constructor): it sets up the new object's attributes.
- Class names use `CapitalizedWords`; methods and attributes use `snake_case`.

## 3. Making objects print nicely

```python
print(rex)                                   # <__main__.Dog object at 0x...>    not helpful

class Dog2(Dog):                             # (inheritance: reuse Dog and add to it; more in the OOP chapters)
    def __str__(self):                       # what print() and str() show
        return f"Dog(name={self.name!r}, age={self.age})"

    def __repr__(self):                      # what the REPL and debuggers show
        return f"Dog2({self.name!r}, {self.age!r})"

buddy = Dog2("Buddy", 2)
print(buddy)                                 # Dog(name='Buddy', age=2)
print([buddy])                               # [Dog2('Buddy', 2)]
```

Always give your classes a good `__repr__` (it saves hours of debugging).

## 4. A complete example: a bank account

```python
class BankAccount:
    """A simple bank account that cannot go negative."""

    def __init__(self, owner, balance=0):
        if balance < 0:
            raise ValueError("opening balance cannot be negative")
        self.owner = owner
        self.balance = balance
        self.history = []                          # each object gets its OWN list

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("deposit must be positive")
        self.balance += amount
        self.history.append(("deposit", amount))

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("withdrawal must be positive")
        if amount > self.balance:
            raise ValueError("insufficient funds")
        self.balance -= amount
        self.history.append(("withdraw", amount))

    def __str__(self):
        return f"{self.owner}: balance {self.balance}"

acct = BankAccount("Ayesha", 100)
acct.deposit(50)
acct.withdraw(30)
print(acct)                                        # Ayesha: balance 120
print(acct.history)                                # [('deposit', 50), ('withdraw', 30)]

try:
    acct.withdraw(1000)
except ValueError as error:
    print("rejected:", error)                      # rejected: insufficient funds

other = BankAccount("Bilal")
other.deposit(10)
print(acct.balance, other.balance)                 # 120 10      (independent objects)
```

The class **protects its own rules** (no negative balance): the rules live in one place, so no part of the program can break them by accident ([encapsulation](../../04-oop/encapsulation-abstraction/README.md)).

## 5. Class attributes and methods

```python
class Circle:
    PI = 3.14159                                   # class attribute: shared by all circles

    def __init__(self, radius):
        self.radius = radius                       # instance attribute: one per circle

    def area(self):
        return Circle.PI * self.radius ** 2

    @classmethod
    def from_diameter(cls, diameter):              # an alternative constructor
        return cls(diameter / 2)

    @staticmethod
    def is_valid_radius(value):                    # a plain utility inside the class (no self)
        return value > 0

print(round(Circle(2).area(), 2), Circle.from_diameter(10).radius, Circle.is_valid_radius(-1))      # 12.57 5.0 False
```

## 6. Lists of objects

```python
class Student:
    def __init__(self, name, scores):
        self.name = name
        self.scores = scores

    def average(self):
        return sum(self.scores) / len(self.scores)

    def __repr__(self):
        return f"Student({self.name!r}, avg={self.average():.1f})"

class_list = [Student("Ana", [90, 85]), Student("Bo", [70, 95, 80]), Student("Cy", [60, 65])]
best = max(class_list, key=lambda s: s.average())
print(best)                                                            # Student('Ana', avg=87.5)
print(sorted(class_list, key=lambda s: s.average(), reverse=True))     # sorted from best to worst
print([s.name for s in class_list if s.average() >= 80])               # ['Ana', 'Bo']
```

## 7. Why use classes?

| Without classes | With classes |
|-----------------|--------------|
| Parallel lists: `names = [...]`, `ages = [...]` that must stay in sync | One `Student` object per student |
| Functions take 6 loose arguments | Methods use the object's own data |
| Rules (valid balance) scattered through the code | Rules enforced in one place |
| Hard to add a new kind of thing | Create new classes (`SavingsAccount`) that reuse existing ones |

Classes are for **things with state and behavior** (accounts, users, orders, game characters). For simple data you can use a dictionary or a [dataclass](../../08-modern-python/dataclasses-enums/README.md); for pure calculations a plain function is fine. **Not everything needs a class.**

## 8. Where to go next

This was a first look. The OOP part of the handbook goes much deeper:

1. [Classes and objects in depth](../../04-oop/classes-objects/README.md): identity, attributes, `__slots__`, equality.
2. [Encapsulation and abstraction](../../04-oop/encapsulation-abstraction/README.md): properties, protecting data.
3. [Inheritance](../../04-oop/inheritance-mro/README.md): reusing and specializing classes.
4. [Polymorphism and dunder methods](../../04-oop/polymorphism-dunder/README.md).
5. [Composition, SOLID and design patterns](../../04-oop/README.md).

## 9. Two real-world examples

**Example 1: A game.** `Player`, `Enemy` and `Item` are classes. Each `Enemy` object has its own health and position; the `attack()` method reduces another object's health; a list of 50 `Enemy` objects is just a list. Adding a new enemy type is writing one more class.

**Example 2: A web app's user.** A `User` class stores email, password hash and join date, and offers methods `set_password()`, `can_edit(post)` and `send_welcome_email()`. Every part of the site uses the same `User`, and changes to the rules (password length) happen in one method.

## 10. Common mistakes

- Forgetting `self` as the first parameter of a method (`TypeError: ... takes 1 positional argument but 2 were given`).
- Forgetting `self.` when setting an attribute (`name = name` just assigns a local variable).
- Putting a mutable object (list, dict) as a class attribute and expecting separate copies per object.
- Mixing up the class (`Dog`) and an object (`rex`).
- Making a class for something a function or dictionary would do.
- Writing `__init__` that does heavy work (network calls) or has no validation.

## 11. Practice

1. Write a `Rectangle` class with `width`, `height`, `area()`, `perimeter()` and a nice `__str__`.
2. Write a `Counter` class with `increment()`, `reset()` and a `value` attribute; create two counters and show they are independent.
3. Extend `BankAccount` with a `transfer(other, amount)` method.
4. Write a `Stack` class (a list inside) with `push`, `pop`, `peek` and `is_empty`.
5. Create a `Library` class that holds a list of book titles and can `add`, `remove` and `search` (case-insensitive substring).

<details>
<summary>Solutions</summary>

**1.**
```python
class Rectangle:
    def __init__(self, width, height):
        self.width, self.height = width, height
    def area(self): return self.width * self.height
    def perimeter(self): return 2 * (self.width + self.height)
    def __str__(self): return f"Rectangle({self.width} x {self.height})"
r = Rectangle(3, 4)
print(r, r.area(), r.perimeter())                  # Rectangle(3 x 4) 12 14
```

**2.**
```python
class Counter:
    def __init__(self): self.value = 0
    def increment(self): self.value += 1
    def reset(self): self.value = 0
a, b = Counter(), Counter()
a.increment(); a.increment(); b.increment()
print(a.value, b.value)                            # 2 1
```

**3.**
```python
class BankAccount2(BankAccount):
    def transfer(self, other, amount):
        self.withdraw(amount)                      # raises if there are insufficient funds
        other.deposit(amount)
a, b = BankAccount2("A", 100), BankAccount2("B", 0)
a.transfer(b, 40)
print(a.balance, b.balance)                        # 60 40
```

**4.**
```python
class Stack:
    def __init__(self): self._items = []
    def push(self, x): self._items.append(x)
    def pop(self): return self._items.pop()
    def peek(self): return self._items[-1]
    def is_empty(self): return not self._items
s = Stack(); s.push(1); s.push(2)
print(s.pop(), s.peek(), s.is_empty())             # 2 1 False
```

**5.**
```python
class Library:
    def __init__(self): self.titles = []
    def add(self, title): self.titles.append(title)
    def remove(self, title): self.titles.remove(title)
    def search(self, text): return [t for t in self.titles if text.lower() in t.lower()]
lib = Library(); lib.add("Python Basics"); lib.add("Advanced Python"); lib.add("Cooking")
print(lib.search("python"))                        # ['Python Basics', 'Advanced Python']
```

</details>

## 12. Check yourself

1. What is the difference between a class and an object?
2. What is `self`?
3. What does `__init__` do?
4. What is the difference between an attribute and a method?
5. When is a class a good idea, and when is it overkill?

<details>
<summary>Answers</summary>

1. A class is the blueprint; an object is one instance built from it.
2. The object a method is working on; Python passes it as the first argument.
3. It initializes a new object, usually setting its attributes.
4. An attribute is data stored on the object; a method is a function that belongs to the class.
5. A class is good for bundling state and behavior that belong together and may have several instances; it is overkill for one simple calculation or plain data.

</details>

[Back to Python fundamentals](README.md) · Previous: [debugging and testing](06-debugging-and-testing.md)
