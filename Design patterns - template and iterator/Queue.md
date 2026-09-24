# Python Queue Classes — Design Notes

Source: https://github.com/python/cpython/blob/3.11/Lib/queue.py

---

## 1. Differences Between the Three Queue Types

### Queue (FIFO — First In, First Out)
Items are removed in the same order they were added. The oldest item is always served first.

**Real-world example:** A checkout line at a supermarket. The first customer in line is the first to be served.

### PriorityQueue
Items are removed in order of priority (lowest value = highest priority). Internally uses a **heap** data structure to always serve the most important item next.

**Real-world example:** A hospital emergency room triage system. Patients with the most critical condition (lowest priority number) are treated first, regardless of arrival order.

### LifoQueue (LIFO — Last In, First Out)
Items are removed in reverse order of insertion. The most recently added item is the first to be removed. This is essentially a **stack**.

**Real-world example:** A stack of plates in a cafeteria. You always take the plate from the top (the most recently placed one).

---

## 2. Code Excerpts — Key Methods

### Queue class

```python
class Queue:
    def __init__(self, maxsize=0):
        self.maxsize = maxsize
        self._init(maxsize)           # delegates data structure setup to _init
        self.mutex = threading.Lock()
        self.not_empty = threading.Condition(self.mutex)
        self.not_full = threading.Condition(self.mutex)
        self.all_tasks_done = threading.Condition(self.mutex)
        self.unfinished_tasks = 0

    def _init(self, maxsize):
        self.queue = deque()          # uses a deque for efficient O(1) popleft

    def _qsize(self):
        return len(self.queue)

    def _put(self, item):
        self.queue.append(item)       # add to the right end

    def _get(self):
        return self.queue.popleft()   # remove from the left end (FIFO)

    def put(self, item, block=True, timeout=None):
        with self.not_full:
            if self.maxsize > 0:
                if not block:
                    if self._qsize() >= self.maxsize:
                        raise Full
                elif timeout is None:
                    while self._qsize() >= self.maxsize:
                        self.not_full.wait()          # wait until space is available
                elif timeout < 0:
                    raise ValueError("'timeout' must be a non-negative number")
                else:
                    endtime = time() + timeout
                    while self._qsize() >= self.maxsize:
                        remaining = endtime - time()
                        if remaining <= 0.0:
                            raise Full
                        self.not_full.wait(remaining)
            self._put(item)                           # delegates actual insert to _put
            self.unfinished_tasks += 1
            self.not_empty.notify()                   # wake up any waiting getters

    def get(self, block=True, timeout=None):
        with self.not_empty:
            if not block:
                if not self._qsize():
                    raise Empty
            elif timeout is None:
                while not self._qsize():
                    self.not_empty.wait()             # wait until an item is available
            elif timeout < 0:
                raise ValueError("'timeout' must be a non-negative number")
            else:
                endtime = time() + timeout
                while not self._qsize():
                    remaining = endtime - time()
                    if remaining <= 0.0:
                        raise Empty
                    self.not_empty.wait(remaining)
            item = self._get()                        # delegates actual removal to _get
            self.not_full.notify()                    # wake up any waiting putters
            return item
```

---

### PriorityQueue class

```python
class PriorityQueue(Queue):
    def _init(self, maxsize):
        self.queue = []               # uses a plain list (heap-managed)

    def _qsize(self):
        return len(self.queue)

    def _put(self, item):
        heappush(self.queue, item)    # insert while maintaining heap order

    def _get(self):
        return heappop(self.queue)    # removes and returns the smallest item
```

---

### LifoQueue class

```python
class LifoQueue(Queue):
    def _init(self, maxsize):
        self.queue = []               # uses a plain list (stack behaviour)

    def _qsize(self):
        return len(self.queue)

    def _put(self, item):
        self.queue.append(item)       # add to the end

    def _get(self):
        return self.queue.pop()       # remove from the end (LIFO)
```

---

## 3. How Queue Acts as a Template for the Other Two

### The Template Method Pattern

`Queue` uses a classic OOP design called the **Template Method pattern**. The public methods `put()` and `get()` define the *algorithm skeleton* — all the thread-safety logic (locking, waiting, notifying) lives there and is **never repeated** in the subclasses.

The low-level data-structure operations are extracted into small, private "hook" methods:

| Method    | Responsibility                          |
|-----------|-----------------------------------------|
| `_init`   | Create the internal data structure      |
| `_qsize`  | Return current number of items          |
| `_put`    | Insert an item into the data structure  |
| `_get`    | Remove and return an item               |

Subclasses **only override these four hook methods** to change the ordering behaviour. They inherit `put()` and `get()` entirely unchanged.

### What is the SAME across all three classes

- `put()` — full thread-safe logic: blocking, timeout, `not_full` condition, `unfinished_tasks` counter
- `get()` — full thread-safe logic: blocking, timeout, `not_empty` condition
- `__init__` — mutex, conditions, and `maxsize` setup
- `task_done()`, `join()`, `qsize()`, `empty()`, `full()` — all inherited from `Queue`

### What is DIFFERENT

| Method  | Queue          | PriorityQueue          | LifoQueue        |
|---------|----------------|------------------------|------------------|
| `_init` | `deque()`      | `[]`                   | `[]`             |
| `_put`  | `append(item)` | `heappush(queue, item)`| `append(item)`   |
| `_get`  | `popleft()`    | `heappop(queue)`       | `pop()`          |
| Order   | FIFO           | Smallest item first    | LIFO             |

### Why this design is powerful

- **No code duplication:** ~60 lines of thread-safety logic in `put`/`get` are written once and reused by all three classes.
- **Easy to extend:** To create a new queue type (e.g. a random-order queue), you only need to override 4 small methods — the threading logic is inherited for free.
- **Separation of concerns:** The *what to store* (data structure) is decoupled from *how to store safely* (threading).
