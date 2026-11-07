# Glossary

Every important term in the handbook in plain words, with a link to the lesson that teaches it. (Use your browser's search to find a word quickly.)


## A

- **Abstract class**: A class that cannot be instantiated directly; it defines methods that subclasses must provide. [Learn more](04-oop/encapsulation-abstraction/README.md)
- **Abstraction**: Using something through a simple interface while hiding how it works inside. [Learn more](04-oop/encapsulation-abstraction/README.md)
- **ACID**: Atomicity, Consistency, Isolation, Durability: the guarantees of a database transaction. [Learn more](05-databases/transactions-acid/README.md)
- **Algorithm**: A finite, step-by-step procedure that solves a problem. [Learn more](01-complexity/big-o/README.md)
- **Amortized cost**: The average cost per operation over a long sequence, even if a single operation is occasionally expensive (for example appending to a dynamic array). [Learn more](01-complexity/big-o/README.md)
- **API**: Application Programming Interface: the set of operations a piece of software offers to other programs. [Learn more](07-networking/dns-http/README.md)
- **Argument / parameter**: A parameter is a name in a function definition; an argument is the value passed when calling it. [Learn more](00-foundations/python-fundamentals/03-functions.md)
- **Array**: A sequence of items stored contiguously in memory, accessed by index (Python's `list` is a dynamic array). [Learn more](02-data-structures/arrays-strings/README.md)
- **ASCII**: An early character encoding of 128 characters; the first part of Unicode. [Learn more](00-foundations/computer-basics/binary-and-data-representation.md)
- **Async / await**: Syntax for cooperative concurrency on one thread: a task pauses at `await` while others run. [Learn more](08-modern-python/async-concurrency/README.md)
- **Atomic operation**: An operation that happens completely or not at all, with no visible middle state. [Learn more](06-operating-systems/concurrency-deadlocks/README.md)

## B

- **B-tree**: A balanced tree with many keys per node, used by databases and file systems for indexes. [Learn more](05-databases/indexes-query-plans/README.md)
- **Backtracking**: Building a solution step by step and undoing a step when it leads nowhere. [Learn more](03-algorithms/recursion-backtracking/README.md)
- **Base case**: The simplest case of a recursive function, which stops the recursion. [Learn more](03-algorithms/recursion-backtracking/README.md)
- **BFS (breadth-first search)**: Graph traversal that visits nodes level by level using a queue; finds shortest paths in unweighted graphs. [Learn more](02-data-structures/graphs/README.md)
- **Big-O**: Notation describing how an algorithm's cost grows with input size, ignoring constants. [Learn more](01-complexity/big-o/README.md)
- **Binary search**: Finding an item in sorted data by repeatedly halving the search range; O(log n). [Learn more](03-algorithms/searching/README.md)
- **Binary tree**: A tree in which each node has at most two children. [Learn more](02-data-structures/trees/README.md)
- **Bit / byte**: A bit is 0 or 1; a byte is 8 bits. [Learn more](00-foundations/computer-basics/binary-and-data-representation.md)
- **Blocking call**: A call that makes the caller wait until it finishes. [Learn more](08-modern-python/async-concurrency/README.md)
- **Branch (Git)**: A movable pointer to a commit, used for a separate line of development. [Learn more](00-foundations/command-line-and-git/git-branches-and-merging.md)
- **Bytecode**: The intermediate instructions Python compiles source code into and its virtual machine executes. [Learn more](00-foundations/computer-basics/how-computers-work.md)

## C

- **Cache**: Fast storage for recently or frequently used data to avoid slower work. [Learn more](09-interview-playbook/system-design-basics/README.md)
- **CAP theorem**: During a network partition a distributed system must choose between consistency and availability. [Learn more](05-databases/nosql/README.md)
- **CDN**: Content delivery network: servers around the world caching content near users. [Learn more](07-networking/load-balancing-cdn/README.md)
- **Class / object**: A class is a blueprint; an object is an instance built from it. [Learn more](04-oop/classes-objects/README.md)
- **Closure**: A function that remembers variables from the scope where it was created. [Learn more](08-modern-python/generators-functional/README.md)
- **Code point**: The number Unicode assigns to a character. [Learn more](00-foundations/computer-basics/binary-and-data-representation.md)
- **Commit (Git)**: A snapshot of the project with a message, author and pointer to its parent commit(s). [Learn more](00-foundations/command-line-and-git/git-basics.md)
- **Complexity**: How much time or memory an algorithm needs as the input grows. [Learn more](01-complexity/big-o/README.md)
- **Composition**: Building behavior by holding other objects (has-a) instead of inheriting (is-a). [Learn more](04-oop/composition-design/README.md)
- **Concurrency**: Structuring a program so several tasks make progress during overlapping time. [Learn more](08-modern-python/async-concurrency/README.md)
- **Context manager**: An object used with `with` that guarantees setup and cleanup (files, locks). [Learn more](04-oop/polymorphism-dunder/README.md)
- **Context switch**: The OS saving one task's CPU state and loading another's. [Learn more](06-operating-systems/scheduling/README.md)
- **Cookie**: A small piece of data a server asks the browser to store and send back. [Learn more](07-networking/dns-http/README.md)
- **Coupling / cohesion**: Coupling is how much modules depend on each other; cohesion is how well a module's parts belong together. [Learn more](04-oop/composition-design/README.md)
- **CPU**: The processor that executes instructions. [Learn more](00-foundations/computer-basics/how-computers-work.md)

## D

- **Dataclass**: A class whose boilerplate (`__init__`, `__repr__`, `__eq__`) is generated from annotated fields. [Learn more](08-modern-python/dataclasses-enums/README.md)
- **Deadlock**: Tasks waiting on each other forever, none able to proceed. [Learn more](06-operating-systems/concurrency-deadlocks/README.md)
- **Decorator**: A function that wraps another to add behavior (`@decorator`); also a structural design pattern. [Learn more](04-oop/design-patterns/structural/decorator.md)
- **Dependency injection**: Passing an object the things it needs instead of letting it build them. [Learn more](04-oop/composition-design/README.md)
- **DFS (depth-first search)**: Graph traversal that goes as deep as possible before backtracking, using recursion or a stack. [Learn more](02-data-structures/graphs/README.md)
- **Dictionary**: A mapping from keys to values with O(1) average lookup (a hash table). [Learn more](02-data-structures/hash-tables/README.md)
- **Dijkstra's algorithm**: Finds shortest paths from a source in a graph with non-negative edge weights. [Learn more](03-algorithms/graph-algorithms/README.md)
- **DNS**: Domain Name System: translates names like example.com into IP addresses. [Learn more](07-networking/dns-http/README.md)
- **Dynamic programming**: Solving problems by combining solutions of overlapping subproblems, storing results. [Learn more](03-algorithms/dynamic-programming/README.md)

## E

- **Encapsulation**: Bundling data with the code that works on it and controlling access to protect invariants. [Learn more](04-oop/encapsulation-abstraction/README.md)
- **Encoding (text)**: The rule that maps characters to bytes (UTF-8, ASCII). [Learn more](00-foundations/computer-basics/binary-and-data-representation.md)
- **Enum**: A fixed set of named constants. [Learn more](08-modern-python/dataclasses-enums/README.md)
- **Event loop**: The scheduler in `asyncio` that runs tasks and resumes them when awaited things finish. [Learn more](08-modern-python/async-concurrency/README.md)
- **Exception**: An error raised during execution that can be caught with `try/except`. [Learn more](08-modern-python/exceptions-logging-testing/README.md)

## F

- **f-string**: A string literal (`f"...{x}..."`) that embeds expressions. [Learn more](00-foundations/python-fundamentals/01-variables-types-operators.md)
- **Factory pattern**: A function or method that decides which class to instantiate. [Learn more](04-oop/design-patterns/creational/factory-method.md)
- **Floating point**: The binary format for decimals; most decimal fractions are stored inexactly. [Learn more](00-foundations/computer-basics/binary-and-data-representation.md)
- **Foreign key**: A column that references the primary key of another table. [Learn more](05-databases/relational-sql/README.md)
- **Function**: A named reusable block of code that takes parameters and may return a value. [Learn more](00-foundations/python-fundamentals/03-functions.md)

## G

- **Garbage collection**: Automatic freeing of memory for objects no longer referenced. [Learn more](00-foundations/computer-basics/memory-stack-heap.md)
- **Generator**: A function using `yield` that produces values lazily, one at a time. [Learn more](08-modern-python/generators-functional/README.md)
- **GIL**: Global Interpreter Lock: lets only one thread run Python bytecode at a time in CPython. [Learn more](08-modern-python/async-concurrency/README.md)
- **Git**: The distributed version-control system used to track and share code history. [Learn more](00-foundations/command-line-and-git/git-basics.md)
- **Graph**: Nodes connected by edges, modeling networks and relationships. [Learn more](02-data-structures/graphs/README.md)
- **Greedy algorithm**: Makes the locally best choice at each step, hoping for a global optimum (valid only when provable). [Learn more](03-algorithms/greedy/README.md)

## H

- **Hash function**: Maps data of any size to a fixed-size number; the same input always gives the same output. [Learn more](02-data-structures/hash-tables/README.md)
- **Hash table**: A structure using a hash function to store key-value pairs with O(1) average access. [Learn more](02-data-structures/hash-tables/README.md)
- **Heap (data structure)**: A tree-based structure that gives quick access to the minimum or maximum (priority queue). [Learn more](02-data-structures/heaps/README.md)
- **Heap (memory)**: The region of memory where objects live until they are no longer referenced. [Learn more](00-foundations/computer-basics/memory-stack-heap.md)
- **HTTP / HTTPS**: The request-response protocol of the web; HTTPS adds TLS encryption. [Learn more](07-networking/dns-http/README.md)

## I

- **Idempotent**: An operation that has the same effect whether done once or many times. [Learn more](07-networking/dns-http/README.md)
- **Immutable / mutable**: Immutable objects cannot be changed after creation; mutable ones can. [Learn more](00-foundations/computer-basics/memory-stack-heap.md)
- **Index (database)**: A structure (usually a B-tree) that speeds up lookups at the cost of slower writes. [Learn more](05-databases/indexes-query-plans/README.md)
- **Inheritance**: A class reusing and specializing another (is-a). [Learn more](04-oop/inheritance-mro/README.md)
- **Interface**: The set of operations something offers, without saying how they work. [Learn more](04-oop/encapsulation-abstraction/README.md)
- **IP address**: The numeric address of a host on a network (IPv4 32 bits, IPv6 128 bits). [Learn more](07-networking/tcp-ip-osi/README.md)
- **Iterator / iterable**: An iterable can produce an iterator; an iterator yields values one by one with `next`. [Learn more](04-oop/design-patterns/behavioral/iterator.md)

## J

- **JOIN (SQL)**: Combining rows from two tables based on a related column. [Learn more](05-databases/relational-sql/README.md)
- **JSON**: A text format for structured data (objects, arrays, strings, numbers). [Learn more](00-foundations/python-fundamentals/05-files-modules-errors.md)

## L

- **Lambda**: A small anonymous function written inline. [Learn more](00-foundations/python-fundamentals/03-functions.md)
- **Linked list**: Nodes each holding a value and a pointer to the next node. [Learn more](02-data-structures/linked-lists/README.md)
- **Load balancer**: Spreads requests across several servers and removes unhealthy ones. [Learn more](07-networking/load-balancing-cdn/README.md)
- **Lock / mutex**: A tool that lets only one thread at a time into a critical section. [Learn more](06-operating-systems/concurrency-deadlocks/README.md)
- **Logarithm**: The inverse of an exponent: how many times a number can be halved (log2). [Learn more](00-foundations/math-for-cs/exponents-and-logarithms.md)

## M

- **Memoization**: Caching a function's results by its arguments to avoid recomputation. [Learn more](03-algorithms/dynamic-programming/README.md)
- **Merge conflict**: Git cannot automatically combine changes to the same lines; you must resolve it. [Learn more](00-foundations/command-line-and-git/git-branches-and-merging.md)
- **MRO**: Method resolution order: the order in which Python searches base classes for an attribute. [Learn more](04-oop/inheritance-mro/README.md)

## N

- **Normalization**: Organizing tables so each fact is stored once, avoiding anomalies. [Learn more](05-databases/normalization-schema-design/README.md)
- **NoSQL**: Databases that do not use the relational table model (key-value, document, wide-column, graph). [Learn more](05-databases/nosql/README.md)

## O

- **OOP**: Object-oriented programming: organizing code as objects with state and behavior. [Learn more](04-oop/README.md)
- **Operating system**: Software that manages hardware and shares it between programs. [Learn more](00-foundations/computer-basics/how-computers-work.md)

## P

- **Page fault**: The CPU trap when a needed memory page is not currently mapped; the OS loads it. [Learn more](06-operating-systems/memory-virtual-memory/README.md)
- **Polymorphism**: The same call doing the right thing for different object types. [Learn more](04-oop/polymorphism-dunder/README.md)
- **Primary key**: A column (or set) that uniquely identifies each row in a table. [Learn more](05-databases/relational-sql/README.md)
- **Priority queue**: A queue where the highest-priority item leaves first (usually a heap). [Learn more](02-data-structures/heaps/README.md)
- **Process**: A running program with its own address space and resources. [Learn more](06-operating-systems/processes-threads/README.md)
- **Protocol (networking)**: An agreed set of rules for communication (TCP, HTTP, DNS). [Learn more](07-networking/tcp-ip-osi/README.md)
- **Protocol (Python typing)**: A class describing the methods an object must have, checked structurally. [Learn more](08-modern-python/typing-hints/README.md)

## Q

- **Queue**: A first-in, first-out collection. [Learn more](02-data-structures/stacks-queues/README.md)

## R

- **Race condition**: A bug whose outcome depends on the timing of concurrent operations. [Learn more](06-operating-systems/concurrency-deadlocks/README.md)
- **RAM**: Fast, temporary memory for programs and data in use. [Learn more](00-foundations/computer-basics/how-computers-work.md)
- **Recursion**: A function calling itself on a smaller input until a base case. [Learn more](03-algorithms/recursion-backtracking/README.md)
- **Reference**: A name or pointer that refers to an object in memory. [Learn more](00-foundations/computer-basics/memory-stack-heap.md)
- **REPL**: Read-Eval-Print Loop: the interactive Python prompt. [Learn more](00-foundations/setup/README.md)
- **Replication**: Keeping copies of data on several machines. [Learn more](05-databases/nosql/README.md)
- **REST**: An API style using HTTP methods and URLs to act on resources. [Learn more](07-networking/dns-http/README.md)

## S

- **Scheduler**: The OS component that decides which task runs on the CPU next. [Learn more](06-operating-systems/scheduling/README.md)
- **Semaphore**: A counter that allows up to N tasks into a resource at once. [Learn more](06-operating-systems/concurrency-deadlocks/README.md)
- **Sharding**: Splitting data across machines by key. [Learn more](05-databases/nosql/README.md)
- **SOLID**: Five object-oriented design principles: SRP, OCP, LSP, ISP, DIP. [Learn more](04-oop/solid/README.md)
- **SQL**: Structured Query Language for relational databases. [Learn more](05-databases/relational-sql/README.md)
- **Stack (call stack)**: Memory holding the frames of function calls in progress. [Learn more](00-foundations/computer-basics/memory-stack-heap.md)
- **Stack (data structure)**: A last-in, first-out collection. [Learn more](02-data-structures/stacks-queues/README.md)
- **Subnet / CIDR**: A block of IP addresses defined by a prefix length such as /24. [Learn more](07-networking/tcp-ip-osi/README.md)

## T

- **TCP / UDP**: TCP is reliable and ordered; UDP is fast and best-effort. [Learn more](07-networking/tcp-ip-osi/README.md)
- **Thread**: A unit of execution inside a process sharing its memory. [Learn more](06-operating-systems/processes-threads/README.md)
- **TLS**: Transport Layer Security: encrypts and authenticates connections (HTTPS). [Learn more](07-networking/tls-security/README.md)
- **Transaction**: A group of database operations that succeed or fail as one unit. [Learn more](05-databases/transactions-acid/README.md)
- **Tree**: A hierarchy of nodes with one root and child nodes. [Learn more](02-data-structures/trees/README.md)
- **Trie**: A tree storing strings by shared prefixes. [Learn more](02-data-structures/tries/README.md)
- **Tuple**: An immutable ordered collection. [Learn more](00-foundations/python-fundamentals/04-strings-lists-dicts-sets.md)
- **Type hint**: An annotation describing intended types, checked by tools but not enforced at runtime. [Learn more](08-modern-python/typing-hints/README.md)

## U

- **Unicode / UTF-8**: The universal character set and its most common byte encoding. [Learn more](00-foundations/computer-basics/binary-and-data-representation.md)
- **Union-find**: A structure tracking which items are in the same group with near-O(1) merges and lookups. [Learn more](09-interview-playbook/problem-solving-patterns/README.md)
- **Unit test**: An automated test of a small piece of code in isolation. [Learn more](08-modern-python/exceptions-logging-testing/README.md)

## V

- **Variable**: A name that refers to a value. [Learn more](00-foundations/python-fundamentals/01-variables-types-operators.md)
- **Virtual environment**: An isolated Python installation with its own packages for one project. [Learn more](00-foundations/setup/README.md)
- **Virtual memory**: Each process sees a private address space that the OS maps onto physical memory and disk. [Learn more](06-operating-systems/memory-virtual-memory/README.md)

## W

- **WebSocket**: A persistent two-way connection between browser and server. [Learn more](07-networking/dns-http/README.md)

[Back to the index](INDEX.md) · [Start here](00-start-here/README.md)
