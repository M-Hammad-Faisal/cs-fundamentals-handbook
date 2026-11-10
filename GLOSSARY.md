# Glossary

Every important term in the handbook in plain words, with a link to the lesson that teaches it. (Use your browser's search to find a word quickly.)


## A

- **Abstract class**: A class that cannot be instantiated directly; it defines methods that subclasses must provide. [Learn more](04-oop/encapsulation-abstraction/README.md)
- **Abstraction**: Using something through a simple interface while hiding how it works inside. [Learn more](04-oop/encapsulation-abstraction/README.md)
- **ACID**: Atomicity, Consistency, Isolation, Durability: the guarantees of a database transaction. [Learn more](05-databases/transactions-acid/README.md)
- **Algorithm**: A finite, step-by-step procedure that solves a problem. [Learn more](01-complexity/big-o/README.md)
- **Amortized cost**: The average cost per operation over a long sequence, even if a single operation is occasionally expensive (for example appending to a dynamic array). [Learn more](01-complexity/big-o/README.md)
- **Anti-join**: Rows of one table that have no match in another, found with `LEFT JOIN ... WHERE b.id IS NULL` or `NOT EXISTS`. [Learn more](05-databases/relational-sql/02-aggregation-and-joins-lab.md)
- **API**: Application Programming Interface: the set of operations a piece of software offers to other programs. [Learn more](07-networking/dns-http/README.md)
- **Argument / parameter**: A parameter is a name in a function definition; an argument is the value passed when calling it. [Learn more](00-foundations/python-fundamentals/03-functions.md)
- **Array**: A sequence of items stored contiguously in memory, accessed by index (Python's `list` is a dynamic array). [Learn more](02-data-structures/arrays-strings/README.md)
- **ASCII**: An early character encoding of 128 characters; the first part of Unicode. [Learn more](00-foundations/computer-basics/binary-and-data-representation.md)
- **Async / await**: Syntax for cooperative concurrency on one thread: a task pauses at `await` while others run. [Learn more](08-modern-python/async-concurrency/README.md)
- **Atomic operation**: An operation that happens completely or not at all, with no visible middle state. [Learn more](06-operating-systems/concurrency-deadlocks/README.md)
- **Avalanche effect**: A tiny change to a hash function's input changes about half the output bits. [Learn more](07-networking/tls-security/01-cryptography-and-tls-lab.md)

## B

- **B-tree**: A balanced tree with many keys per node, used by databases and file systems for indexes. [Learn more](05-databases/indexes-query-plans/README.md)
- **Backtracking**: Building a solution step by step and undoing a step when it leads nowhere. [Learn more](03-algorithms/recursion-backtracking/README.md)
- **Banker's algorithm**: A deadlock-avoidance method that grants a resource request only if the system stays in a safe state. [Learn more](06-operating-systems/concurrency-deadlocks/02-deadlock.md)
- **Base case**: The simplest case of a recursive function, which stops the recursion. [Learn more](03-algorithms/recursion-backtracking/README.md)
- **Belady's anomaly**: Giving a FIFO page-replacement policy more frames can produce more page faults. [Learn more](06-operating-systems/memory-virtual-memory/02-page-replacement-algorithms.md)
- **BFS (breadth-first search)**: Graph traversal that visits nodes level by level using a queue; finds shortest paths in unweighted graphs. [Learn more](02-data-structures/graphs/README.md)
- **Big-O**: Notation describing how an algorithm's cost grows with input size, ignoring constants. [Learn more](01-complexity/big-o/README.md)
- **Binary search**: Finding an item in sorted data by repeatedly halving the search range; O(log n). [Learn more](03-algorithms/searching/README.md)
- **Binary tree**: A tree in which each node has at most two children. [Learn more](02-data-structures/trees/README.md)
- **Bit / byte**: A bit is 0 or 1; a byte is 8 bits. [Learn more](00-foundations/computer-basics/binary-and-data-representation.md)
- **Blocking call**: A call that makes the caller wait until it finishes. [Learn more](08-modern-python/async-concurrency/README.md)
- **Bloom filter**: A compact structure that says an item is definitely absent or probably present, with no false negatives. [Learn more](02-data-structures/hash-tables/03-dict-set-internals-and-bloom-filters.md)
- **Branch (Git)**: A movable pointer to a commit, used for a separate line of development. [Learn more](00-foundations/command-line-and-git/git-branches-and-merging.md)
- **Bridge (graph)**: An edge whose removal disconnects a graph; a single point of failure. [Learn more](03-algorithms/graph-algorithms/02-connectivity-scc-and-flow.md)
- **Bytecode**: The intermediate instructions Python compiles source code into and its virtual machine executes. [Learn more](00-foundations/computer-basics/how-computers-work.md)

## C

- **Cache**: Fast storage for recently or frequently used data to avoid slower work. [Learn more](09-interview-playbook/system-design-basics/README.md)
- **CAP theorem**: During a network partition a distributed system must choose between consistency and availability. [Learn more](05-databases/nosql/README.md)
- **CDN**: Content delivery network: servers around the world caching content near users. [Learn more](07-networking/load-balancing-cdn/README.md)
- **Certificate (TLS)**: A document binding a public key to an identity such as a domain name, signed by a certificate authority. [Learn more](07-networking/tls-security/01-cryptography-and-tls-lab.md)
- **Chinese remainder theorem**: Remainders modulo pairwise coprime numbers determine a number modulo their product. [Learn more](03-algorithms/number-theory/01-number-theory-for-programmers.md)
- **Circuit breaker**: A pattern that stops calling a failing dependency for a while so it can recover and callers fail fast. [Learn more](07-networking/load-balancing-cdn/01-load-balancing-and-resilience-lab.md)
- **Class / object**: A class is a blueprint; an object is an instance built from it. [Learn more](04-oop/classes-objects/README.md)
- **Class diagram**: A UML diagram of classes, their attributes and methods, and the relationships between them. [Learn more](04-oop/01-uml-and-class-diagrams.md)
- **Closure**: A function that remembers variables from the scope where it was created. [Learn more](08-modern-python/generators-functional/README.md)
- **Code point**: The number Unicode assigns to a character. [Learn more](00-foundations/computer-basics/binary-and-data-representation.md)
- **Collision (hash)**: Two different keys that produce the same hash slot; every hash table needs a plan for them. [Learn more](02-data-structures/hash-tables/01-hash-functions-and-collisions.md)
- **Commit (Git)**: A snapshot of the project with a message, author and pointer to its parent commit(s). [Learn more](00-foundations/command-line-and-git/git-basics.md)
- **Complexity**: How much time or memory an algorithm needs as the input grows. [Learn more](01-complexity/big-o/README.md)
- **Composite index**: A database index on several columns, usable for queries on its leading columns (leftmost-prefix rule). [Learn more](05-databases/indexes-query-plans/01-indexes-lab.md)
- **Composition**: Building behavior by holding other objects (has-a) instead of inheriting (is-a). [Learn more](04-oop/composition-design/README.md)
- **Concurrency**: Structuring a program so several tasks make progress during overlapping time. [Learn more](08-modern-python/async-concurrency/README.md)
- **Consistent hashing**: Placing keys and servers on a ring so adding or removing a server moves only a small share of keys. [Learn more](02-data-structures/hash-tables/03-dict-set-internals-and-bloom-filters.md)
- **Context manager**: An object used with `with` that guarantees setup and cleanup (files, locks). [Learn more](04-oop/polymorphism-dunder/README.md)
- **Context switch**: The OS saving one task's CPU state and loading another's. [Learn more](06-operating-systems/scheduling/README.md)
- **Convoy effect**: Short jobs stuck waiting behind one long job in a non-preemptive first-come-first-served queue. [Learn more](06-operating-systems/scheduling/01-scheduling-simulator.md)
- **Cookie**: A small piece of data a server asks the browser to store and send back. [Learn more](07-networking/dns-http/README.md)
- **Coprime**: Two integers whose greatest common divisor is 1. [Learn more](03-algorithms/number-theory/01-number-theory-for-programmers.md)
- **Copy-on-write**: Sharing memory pages until one side writes, then copying just that page; makes `fork` cheap. [Learn more](06-operating-systems/memory-virtual-memory/01-paging-and-address-translation.md)
- **Counting sort**: A non-comparison sort that counts occurrences of small integer keys; runs in O(n + k). [Learn more](03-algorithms/sorting/03-linear-time-sorts-and-timsort.md)
- **Coupling / cohesion**: Coupling is how much modules depend on each other; cohesion is how well a module's parts belong together. [Learn more](04-oop/composition-design/README.md)
- **Covering index**: An index that contains every column a query needs, so the table is never read. [Learn more](05-databases/indexes-query-plans/01-indexes-lab.md)
- **CPU**: The processor that executes instructions. [Learn more](00-foundations/computer-basics/how-computers-work.md)
- **Critical section**: Code that touches shared data and must not run in two threads at once. [Learn more](06-operating-systems/concurrency-deadlocks/01-race-conditions-and-synchronization.md)
- **CTE (common table expression)**: A named temporary result defined with `WITH` and used by the query that follows. [Learn more](05-databases/relational-sql/03-ctes-and-window-functions-lab.md)

## D

- **Dataclass**: A class whose boilerplate (`__init__`, `__repr__`, `__eq__`) is generated from annotated fields. [Learn more](08-modern-python/dataclasses-enums/README.md)
- **Deadlock**: Tasks waiting on each other forever, none able to proceed. [Learn more](06-operating-systems/concurrency-deadlocks/README.md)
- **Decorator**: A function that wraps another to add behavior (`@decorator`); also a structural design pattern. [Learn more](04-oop/design-patterns/structural/decorator.md)
- **Dependency injection**: Passing an object the things it needs instead of letting it build them. [Learn more](04-oop/composition-design/README.md)
- **DFS (depth-first search)**: Graph traversal that goes as deep as possible before backtracking, using recursion or a stack. [Learn more](02-data-structures/graphs/README.md)
- **Dictionary**: A mapping from keys to values with O(1) average lookup (a hash table). [Learn more](02-data-structures/hash-tables/README.md)
- **Diffie-Hellman**: A key-exchange method that lets two parties agree on a shared secret over a public channel. [Learn more](07-networking/tls-security/01-cryptography-and-tls-lab.md)
- **Dijkstra's algorithm**: Finds shortest paths from a source in a graph with non-negative edge weights. [Learn more](03-algorithms/graph-algorithms/README.md)
- **Divide and conquer**: Solving a problem by splitting it into independent smaller copies, solving them recursively and combining the answers. [Learn more](03-algorithms/divide-and-conquer/01-divide-and-conquer.md)
- **DNS**: Domain Name System: translates names like example.com into IP addresses. [Learn more](07-networking/dns-http/README.md)
- **Dynamic programming**: Solving problems by combining solutions of overlapping subproblems, storing results. [Learn more](03-algorithms/dynamic-programming/README.md)

## E

- **Edit distance**: The minimum number of insertions, deletions and substitutions that turn one string into another. [Learn more](03-algorithms/dynamic-programming/02-dp-on-two-sequences-and-grids.md)
- **Encapsulation**: Bundling data with the code that works on it and controlling access to protect invariants. [Learn more](04-oop/encapsulation-abstraction/README.md)
- **Encoding (text)**: The rule that maps characters to bytes (UTF-8, ASCII). [Learn more](00-foundations/computer-basics/binary-and-data-representation.md)
- **Enum**: A fixed set of named constants. [Learn more](08-modern-python/dataclasses-enums/README.md)
- **Euclid's algorithm**: Computes the GCD with repeated remainders: gcd(a, b) = gcd(b, a mod b). [Learn more](03-algorithms/number-theory/01-number-theory-for-programmers.md)
- **Euler's totient**: phi(n): how many numbers from 1 to n are coprime to n; the exponent in Euler's theorem and in RSA. [Learn more](03-algorithms/number-theory/01-number-theory-for-programmers.md)
- **Event loop**: The scheduler in `asyncio` that runs tasks and resumes them when awaited things finish. [Learn more](08-modern-python/async-concurrency/README.md)
- **Eventual consistency**: If writes stop, all replicas eventually converge to the same value; reads may be stale until then. [Learn more](05-databases/nosql/01-nosql-lab.md)
- **Exception**: An error raised during execution that can be caught with `try/except`. [Learn more](08-modern-python/exceptions-logging-testing/README.md)
- **Exchange argument**: A proof technique showing a greedy choice can replace part of an optimal solution without making it worse. [Learn more](03-algorithms/greedy/01-greedy-algorithms.md)

## F

- **f-string**: A string literal (`f"...{x}..."`) that embeds expressions. [Learn more](00-foundations/python-fundamentals/01-variables-types-operators.md)
- **Factory pattern**: A function or method that decides which class to instantiate. [Learn more](04-oop/design-patterns/creational/factory-method.md)
- **Fast exponentiation**: Computing a^n (mod m) in O(log n) by repeated squaring; Python's `pow(a, n, m)`. [Learn more](03-algorithms/number-theory/01-number-theory-for-programmers.md)
- **Fenwick tree**: A compact structure for prefix sums with point updates in O(log n) (binary indexed tree). [Learn more](02-data-structures/trees/04-segment-and-fenwick-trees.md)
- **Floating point**: The binary format for decimals; most decimal fractions are stored inexactly. [Learn more](00-foundations/computer-basics/binary-and-data-representation.md)
- **Floyd-Warshall**: A dynamic-programming algorithm for shortest paths between all pairs of vertices in O(V^3). [Learn more](03-algorithms/graph-algorithms/01-all-pairs-and-heuristic-shortest-paths.md)
- **Foreign key**: A column that references the primary key of another table. [Learn more](05-databases/relational-sql/README.md)
- **Free-threaded Python**: An optional CPython build (3.13+) without the GIL, letting threads run Python code in parallel. [Learn more](06-operating-systems/processes-threads/02-threads-and-the-gil-lab.md)
- **fsync**: A call that forces buffered file data to be written to disk before returning. [Learn more](06-operating-systems/file-systems-io/01-file-systems-in-depth.md)
- **Function**: A named reusable block of code that takes parameters and may return a value. [Learn more](00-foundations/python-fundamentals/03-functions.md)

## G

- **Gaps and islands**: Finding runs of consecutive values, for example by grouping on value minus row number. [Learn more](05-databases/relational-sql/03-ctes-and-window-functions-lab.md)
- **Garbage collection**: Automatic freeing of memory for objects no longer referenced. [Learn more](00-foundations/computer-basics/memory-stack-heap.md)
- **Generator**: A function using `yield` that produces values lazily, one at a time. [Learn more](08-modern-python/generators-functional/README.md)
- **GIL**: Global Interpreter Lock: lets only one thread run Python bytecode at a time in CPython. [Learn more](08-modern-python/async-concurrency/README.md)
- **Git**: The distributed version-control system used to track and share code history. [Learn more](00-foundations/command-line-and-git/git-basics.md)
- **Graph**: Nodes connected by edges, modeling networks and relationships. [Learn more](02-data-structures/graphs/README.md)
- **Greedy algorithm**: Makes the locally best choice at each step, hoping for a global optimum (valid only when provable). [Learn more](03-algorithms/greedy/README.md)

## H

- **Hard link**: Another directory entry (name) pointing to the same inode as an existing file. [Learn more](06-operating-systems/file-systems-io/01-file-systems-in-depth.md)
- **Hash function**: Maps data of any size to a fixed-size number; the same input always gives the same output. [Learn more](02-data-structures/hash-tables/README.md)
- **Hash table**: A structure using a hash function to store key-value pairs with O(1) average access. [Learn more](02-data-structures/hash-tables/README.md)
- **Heap (data structure)**: A tree-based structure that gives quick access to the minimum or maximum (priority queue). [Learn more](02-data-structures/heaps/README.md)
- **Heap (memory)**: The region of memory where objects live until they are no longer referenced. [Learn more](00-foundations/computer-basics/memory-stack-heap.md)
- **Heapify**: Turning an array into a heap in place in O(n) by sifting nodes down from the last parent. [Learn more](02-data-structures/heaps/01-binary-heaps-and-heapsort.md)
- **HMAC**: A hash-based message authentication code: a tag only holders of the shared secret key can create or verify. [Learn more](07-networking/tls-security/01-cryptography-and-tls-lab.md)
- **HTTP / HTTPS**: The request-response protocol of the web; HTTPS adds TLS encryption. [Learn more](07-networking/dns-http/README.md)

## I

- **Idempotent**: An operation that has the same effect whether done once or many times. [Learn more](07-networking/dns-http/README.md)
- **IDOR (insecure direct object reference)**: Letting a user access another user's data just by changing an id in a URL, because ownership is not checked. [Learn more](07-networking/apis-realtime/01-rest-apis-and-websockets-lab.md)
- **Immutable / mutable**: Immutable objects cannot be changed after creation; mutable ones can. [Learn more](00-foundations/computer-basics/memory-stack-heap.md)
- **Index (database)**: A structure (usually a B-tree) that speeds up lookups at the cost of slower writes. [Learn more](05-databases/indexes-query-plans/README.md)
- **Inheritance**: A class reusing and specializing another (is-a). [Learn more](04-oop/inheritance-mro/README.md)
- **Inode**: The file-system record holding a file's metadata and block locations (not its name). [Learn more](06-operating-systems/file-systems-io/01-file-systems-in-depth.md)
- **Interface**: The set of operations something offers, without saying how they work. [Learn more](04-oop/encapsulation-abstraction/README.md)
- **Inverted index**: A map from each word to the documents that contain it; the core of search engines. [Learn more](05-databases/nosql/01-nosql-lab.md)
- **IP address**: The numeric address of a host on a network (IPv4 32 bits, IPv6 128 bits). [Learn more](07-networking/tcp-ip-osi/README.md)
- **Iterator / iterable**: An iterable can produce an iterator; an iterator yields values one by one with `next`. [Learn more](04-oop/design-patterns/behavioral/iterator.md)

## J

- **JOIN (SQL)**: Combining rows from two tables based on a related column. [Learn more](05-databases/relational-sql/README.md)
- **Journaling**: Logging intended changes first so a file system or database can recover consistently after a crash. [Learn more](06-operating-systems/file-systems-io/01-file-systems-in-depth.md)
- **JSON**: A text format for structured data (objects, arrays, strings, numbers). [Learn more](00-foundations/python-fundamentals/05-files-modules-errors.md)

## K

- **Karatsuba algorithm**: A divide-and-conquer multiplication using three half-size products instead of four, in O(n^1.585). [Learn more](03-algorithms/divide-and-conquer/01-divide-and-conquer.md)
- **Kernel**: The always-running core of the operating system, in privileged mode, managing CPU, memory and devices. [Learn more](06-operating-systems/00-what-is-an-operating-system.md)

## L

- **Lambda**: A small anonymous function written inline. [Learn more](00-foundations/python-fundamentals/03-functions.md)
- **LCP array**: For a suffix array, the length of the common prefix of each pair of adjacent sorted suffixes. [Learn more](03-algorithms/string-algorithms/01-string-matching-and-suffix-structures.md)
- **LCS (longest common subsequence)**: The longest sequence of items appearing in the same order in two sequences (not necessarily adjacent). [Learn more](03-algorithms/dynamic-programming/02-dp-on-two-sequences-and-grids.md)
- **Linked list**: Nodes each holding a value and a pointer to the next node. [Learn more](02-data-structures/linked-lists/README.md)
- **Load balancer**: Spreads requests across several servers and removes unhealthy ones. [Learn more](07-networking/load-balancing-cdn/README.md)
- **Load factor**: Items divided by slots in a hash table; resizing keeps it bounded so lookups stay O(1). [Learn more](02-data-structures/hash-tables/01-hash-functions-and-collisions.md)
- **Lock / mutex**: A tool that lets only one thread at a time into a critical section. [Learn more](06-operating-systems/concurrency-deadlocks/README.md)
- **Logarithm**: The inverse of an exponent: how many times a number can be halved (log2). [Learn more](00-foundations/math-for-cs/exponents-and-logarithms.md)
- **Lost update**: Two read-modify-write cycles overwrite each other so one change disappears. [Learn more](05-databases/transactions-acid/01-transactions-lab.md)

## M

- **Manacher's algorithm**: Finds the longest palindromic substring (and all palindrome radii) in linear time. [Learn more](03-algorithms/string-algorithms/01-string-matching-and-suffix-structures.md)
- **Master theorem**: A formula giving the growth of recurrences T(n) = aT(n/b) + n^d by comparing d with log_b a. [Learn more](03-algorithms/divide-and-conquer/01-divide-and-conquer.md)
- **Memoization**: Caching a function's results by its arguments to avoid recomputation. [Learn more](03-algorithms/dynamic-programming/README.md)
- **Merge conflict**: Git cannot automatically combine changes to the same lines; you must resolve it. [Learn more](00-foundations/command-line-and-git/git-branches-and-merging.md)
- **Mermaid**: A text format for diagrams (class, sequence, state, flow) that renders in GitHub and documentation tools. [Learn more](04-oop/01-uml-and-class-diagrams.md)
- **Miller-Rabin test**: A fast probabilistic primality test, deterministic with fixed bases for 64-bit numbers. [Learn more](03-algorithms/number-theory/01-number-theory-for-programmers.md)
- **Modular inverse**: For b mod m, the number b^-1 with b * b^-1 = 1 (mod m); exists when gcd(b, m) = 1. [Learn more](03-algorithms/number-theory/01-number-theory-for-programmers.md)
- **Monotonic stack**: A stack kept sorted so each element is pushed and popped once; solves next-greater-element problems in O(n). [Learn more](02-data-structures/stacks-queues/03-stack-and-queue-applications.md)
- **MRO**: Method resolution order: the order in which Python searches base classes for an attribute. [Learn more](04-oop/inheritance-mro/README.md)
- **MVCC / snapshot isolation**: Each transaction reads its own consistent snapshot of the data, so readers and writers do not block each other. [Learn more](05-databases/transactions-acid/01-transactions-lab.md)

## N

- **Normalization**: Organizing tables so each fact is stored once, avoiding anomalies. [Learn more](05-databases/normalization-schema-design/README.md)
- **NoSQL**: Databases that do not use the relational table model (key-value, document, wide-column, graph). [Learn more](05-databases/nosql/README.md)

## O

- **OOP**: Object-oriented programming: organizing code as objects with state and behavior. [Learn more](04-oop/README.md)
- **Operating system**: Software that manages hardware and shares it between programs. [Learn more](00-foundations/computer-basics/how-computers-work.md)
- **Optimistic concurrency**: Proceed without locks and detect conflicts at write time (for example with a version number), then retry. [Learn more](05-databases/transactions-acid/01-transactions-lab.md)

## P

- **Page fault**: The CPU trap when a needed memory page is not currently mapped; the OS loads it. [Learn more](06-operating-systems/memory-virtual-memory/README.md)
- **Page replacement**: The policy that chooses which in-memory page to evict when a new page is needed (FIFO, LRU, Clock). [Learn more](06-operating-systems/memory-virtual-memory/02-page-replacement-algorithms.md)
- **Page table**: The structure mapping a process's virtual pages to physical frames. [Learn more](06-operating-systems/memory-virtual-memory/01-paging-and-address-translation.md)
- **Pagination**: Returning a large collection in pages (offset/page or cursor/keyset) instead of all at once. [Learn more](07-networking/apis-realtime/01-rest-apis-and-websockets-lab.md)
- **Pipe**: A one-way kernel buffer connecting the output of one process to the input of another. [Learn more](06-operating-systems/processes-threads/01-processes-in-practice.md)
- **Polymorphism**: The same call doing the right thing for different object types. [Learn more](04-oop/polymorphism-dunder/README.md)
- **Primary key**: A column (or set) that uniquely identifies each row in a table. [Learn more](05-databases/relational-sql/README.md)
- **Priority queue**: A queue where the highest-priority item leaves first (usually a heap). [Learn more](02-data-structures/heaps/README.md)
- **Process**: A running program with its own address space and resources. [Learn more](06-operating-systems/processes-threads/README.md)
- **Protocol (networking)**: An agreed set of rules for communication (TCP, HTTP, DNS). [Learn more](07-networking/tcp-ip-osi/README.md)
- **Protocol (Python typing)**: A class describing the methods an object must have, checked structurally. [Learn more](08-modern-python/typing-hints/README.md)

## Q

- **Queue**: A first-in, first-out collection. [Learn more](02-data-structures/stacks-queues/README.md)
- **Quickselect**: Finding the k-th smallest item in average O(n) by partitioning only one side. [Learn more](03-algorithms/sorting/02-merge-sort-and-quicksort.md)
- **Quorum**: Reading from R and writing to W of N replicas; if R + W > N a read always overlaps the latest write. [Learn more](05-databases/nosql/01-nosql-lab.md)

## R

- **Rabin-Karp**: String search that compares rolling hashes of windows, verifying matches. [Learn more](03-algorithms/string-algorithms/01-string-matching-and-suffix-structures.md)
- **Race condition**: A bug whose outcome depends on the timing of concurrent operations. [Learn more](06-operating-systems/concurrency-deadlocks/README.md)
- **Radix sort**: Sorting numbers digit by digit with a stable sort; effectively linear for fixed-width keys. [Learn more](03-algorithms/sorting/03-linear-time-sorts-and-timsort.md)
- **RAM**: Fast, temporary memory for programs and data in use. [Learn more](00-foundations/computer-basics/how-computers-work.md)
- **Rate limiter**: A mechanism (token bucket, sliding window) that caps how many requests a client may make over time. [Learn more](07-networking/load-balancing-cdn/01-load-balancing-and-resilience-lab.md)
- **Recurrence relation**: An equation expressing a quantity (such as an algorithm's running time) in terms of smaller inputs. [Learn more](03-algorithms/divide-and-conquer/01-divide-and-conquer.md)
- **Recursion**: A function calling itself on a smaller input until a base case. [Learn more](03-algorithms/recursion-backtracking/README.md)
- **Recursive CTE**: A CTE that refers to itself (anchor plus recursive step) to walk hierarchies or generate sequences. [Learn more](05-databases/relational-sql/03-ctes-and-window-functions-lab.md)
- **Reference**: A name or pointer that refers to an object in memory. [Learn more](00-foundations/computer-basics/memory-stack-heap.md)
- **Reference counting**: Memory management that frees an object when its count of references drops to zero (CPython's main scheme). [Learn more](06-operating-systems/processes-threads/02-threads-and-the-gil-lab.md)
- **REPL**: Read-Eval-Print Loop: the interactive Python prompt. [Learn more](00-foundations/setup/README.md)
- **Replication**: Keeping copies of data on several machines. [Learn more](05-databases/nosql/README.md)
- **REST**: An API style using HTTP methods and URLs to act on resources. [Learn more](07-networking/dns-http/README.md)
- **Reverse proxy**: A server in front of backends that forwards client requests to them (and may balance, cache or terminate TLS). [Learn more](07-networking/load-balancing-cdn/01-load-balancing-and-resilience-lab.md)
- **Rolling hash**: A hash of a sliding window updated in O(1) by removing the old character and adding the new one. [Learn more](03-algorithms/string-algorithms/01-string-matching-and-suffix-structures.md)

## S

- **Salt**: Random data added to each password before hashing so equal passwords hash differently and precomputed tables fail. [Learn more](07-networking/tls-security/01-cryptography-and-tls-lab.md)
- **Scheduler**: The OS component that decides which task runs on the CPU next. [Learn more](06-operating-systems/scheduling/README.md)
- **Segment tree**: A tree storing answers for ranges, supporting range queries and updates in O(log n). [Learn more](02-data-structures/trees/04-segment-and-fenwick-trees.md)
- **Semaphore**: A counter that allows up to N tasks into a resource at once. [Learn more](06-operating-systems/concurrency-deadlocks/README.md)
- **Sequence diagram**: A UML diagram showing the ordered messages between objects or services in one scenario. [Learn more](04-oop/01-uml-and-class-diagrams.md)
- **Server-Sent Events (SSE)**: A one-way stream of text events from server to browser over a long-lived HTTP response. [Learn more](07-networking/apis-realtime/01-rest-apis-and-websockets-lab.md)
- **Sharding**: Splitting data across machines by key. [Learn more](05-databases/nosql/README.md)
- **Shunting-yard algorithm**: Dijkstra's method for converting infix expressions to postfix using an operator stack. [Learn more](02-data-structures/stacks-queues/03-stack-and-queue-applications.md)
- **Sieve of Eratosthenes**: Finds all primes up to N by crossing out multiples of each prime, in O(N log log N). [Learn more](03-algorithms/number-theory/01-number-theory-for-programmers.md)
- **Signal**: A small asynchronous notification sent to a process (SIGTERM, SIGKILL, SIGINT). [Learn more](06-operating-systems/processes-threads/01-processes-in-practice.md)
- **Socket**: The operating system's handle for one end of a network conversation. [Learn more](07-networking/tcp-ip-osi/02-sockets-tcp-udp-lab.md)
- **SOLID**: Five object-oriented design principles: SRP, OCP, LSP, ISP, DIP. [Learn more](04-oop/solid/README.md)
- **SQL**: Structured Query Language for relational databases. [Learn more](05-databases/relational-sql/README.md)
- **SQL injection**: An attack where user input changes the meaning of a SQL query; prevented with parameterized queries. [Learn more](07-networking/tls-security/01-cryptography-and-tls-lab.md)
- **Stack (call stack)**: Memory holding the frames of function calls in progress. [Learn more](00-foundations/computer-basics/memory-stack-heap.md)
- **Stack (data structure)**: A last-in, first-out collection. [Learn more](02-data-structures/stacks-queues/README.md)
- **Starvation**: A process or thread that never gets a resource because others always go first; aging is a common cure. [Learn more](06-operating-systems/scheduling/01-scheduling-simulator.md)
- **Strongly connected component**: A maximal set of vertices in a directed graph where every vertex can reach every other. [Learn more](03-algorithms/graph-algorithms/02-connectivity-scc-and-flow.md)
- **Subnet / CIDR**: A block of IP addresses defined by a prefix length such as /24. [Learn more](07-networking/tcp-ip-osi/README.md)
- **Suffix array**: The start positions of all suffixes of a string in sorted order; supports fast substring queries. [Learn more](03-algorithms/string-algorithms/01-string-matching-and-suffix-structures.md)
- **Symbolic link**: A small file containing a path to another file; it can dangle if the target is removed. [Learn more](06-operating-systems/file-systems-io/01-file-systems-in-depth.md)
- **System call**: A controlled request from a user program to the kernel (open, read, fork). [Learn more](06-operating-systems/00-what-is-an-operating-system.md)

## T

- **TCP / UDP**: TCP is reliable and ordered; UDP is fast and best-effort. [Learn more](07-networking/tcp-ip-osi/README.md)
- **Thrashing**: A system spending most of its time moving pages between disk and memory because working sets exceed RAM. [Learn more](06-operating-systems/memory-virtual-memory/02-page-replacement-algorithms.md)
- **Thread**: A unit of execution inside a process sharing its memory. [Learn more](06-operating-systems/processes-threads/README.md)
- **Thread-local storage**: Data that each thread sees as its own private copy (`threading.local`). [Learn more](06-operating-systems/processes-threads/02-threads-and-the-gil-lab.md)
- **Timsort**: Python's stable hybrid sort (merge sort plus insertion sort) that is O(n) on already-sorted runs. [Learn more](03-algorithms/sorting/03-linear-time-sorts-and-timsort.md)
- **TLB (translation lookaside buffer)**: A small fast cache of recent virtual-to-physical page translations. [Learn more](06-operating-systems/memory-virtual-memory/01-paging-and-address-translation.md)
- **TLS**: Transport Layer Security: encrypts and authenticates connections (HTTPS). [Learn more](07-networking/tls-security/README.md)
- **Token bucket**: A rate limiter that refills tokens at a steady rate and spends one per request, allowing short bursts. [Learn more](07-networking/load-balancing-cdn/01-load-balancing-and-resilience-lab.md)
- **Topological sort**: An ordering of a directed acyclic graph's vertices in which every edge points forward. [Learn more](02-data-structures/graphs/02-graph-algorithms.md)
- **Transaction**: A group of database operations that succeed or fail as one unit. [Learn more](05-databases/transactions-acid/README.md)
- **Tree**: A hierarchy of nodes with one root and child nodes. [Learn more](02-data-structures/trees/README.md)
- **Trie**: A tree storing strings by shared prefixes. [Learn more](02-data-structures/tries/README.md)
- **TTL (time to live)**: How long a cached record (DNS answer, cache entry) may be reused before it expires. [Learn more](07-networking/dns-http/02-dns-in-depth.md)
- **Tuple**: An immutable ordered collection. [Learn more](00-foundations/python-fundamentals/04-strings-lists-dicts-sets.md)
- **Type hint**: An annotation describing intended types, checked by tools but not enforced at runtime. [Learn more](08-modern-python/typing-hints/README.md)

## U

- **UML**: Unified Modeling Language: a standard visual vocabulary for describing software structure and behavior. [Learn more](04-oop/01-uml-and-class-diagrams.md)
- **Unicode / UTF-8**: The universal character set and its most common byte encoding. [Learn more](00-foundations/computer-basics/binary-and-data-representation.md)
- **Union-find**: A structure tracking which items are in the same group with near-O(1) merges and lookups. [Learn more](09-interview-playbook/problem-solving-patterns/README.md)
- **Unit test**: An automated test of a small piece of code in isolation. [Learn more](08-modern-python/exceptions-logging-testing/README.md)

## V

- **Variable**: A name that refers to a value. [Learn more](00-foundations/python-fundamentals/01-variables-types-operators.md)
- **Virtual environment**: An isolated Python installation with its own packages for one project. [Learn more](00-foundations/setup/README.md)
- **Virtual memory**: Each process sees a private address space that the OS maps onto physical memory and disk. [Learn more](06-operating-systems/memory-virtual-memory/README.md)

## W

- **Webhook**: An HTTP request one system sends to a URL another system registered, to notify it of an event. [Learn more](07-networking/apis-realtime/01-rest-apis-and-websockets-lab.md)
- **WebSocket**: A persistent two-way connection between browser and server. [Learn more](07-networking/dns-http/README.md)
- **Window function**: A function computed over related rows (a window) that keeps every row, such as `RANK()` or a running `SUM`. [Learn more](05-databases/relational-sql/03-ctes-and-window-functions-lab.md)
- **Write skew**: Two transactions read overlapping data and make different writes that together break a rule, undetected by snapshot isolation. [Learn more](05-databases/transactions-acid/01-transactions-lab.md)

## X

- **XSS (cross-site scripting)**: Injecting script into a page by putting unescaped user input into HTML; prevented by output escaping and CSP. [Learn more](07-networking/tls-security/01-cryptography-and-tls-lab.md)

## Z

- **Z-function**: z[i] is the length of the longest common prefix of a string and its suffix starting at i; computed in O(n). [Learn more](03-algorithms/string-algorithms/01-string-matching-and-suffix-structures.md)
- **Zombie process**: A child that has exited but whose parent has not yet collected its exit status. [Learn more](06-operating-systems/processes-threads/01-processes-in-practice.md)

[Back to the index](INDEX.md) · [Start here](00-start-here/README.md)
