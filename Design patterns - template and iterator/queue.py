"""
Excerpts from CPython's queue.py (3.11)
Source: https://github.com/python/cpython/blob/3.11/Lib/queue.py

Focuses on the three queue classes and their key methods:
put, get, _init, _qsize, _put, _get
"""

import threading
import time
from collections import deque
from heapq import heappush, heappop

__all__ = ['Empty', 'Full', 'Queue', 'PriorityQueue', 'LifoQueue']


class Empty(Exception):
    """Raised when get() is called on an empty queue."""
    pass


class Full(Exception):
    """Raised when put() is called on a full queue."""
    pass


# ---------------------------------------------------------------------------
# Queue — FIFO (First In, First Out)
# Uses a deque: append() on right, popleft() from left
# ---------------------------------------------------------------------------

class Queue:
    def __init__(self, maxsize=0):
        self.maxsize = maxsize
        self._init(maxsize)               # delegates data structure setup to _init
        self.mutex = threading.Lock()
        self.not_empty = threading.Condition(self.mutex)
        self.not_full = threading.Condition(self.mutex)
        self.all_tasks_done = threading.Condition(self.mutex)
        self.unfinished_tasks = 0

    # --- Hook methods (overridden by subclasses) ----------------------------

    def _init(self, maxsize):
        self.queue = deque()              # O(1) append and popleft

    def _qsize(self):
        return len(self.queue)

    def _put(self, item):
        self.queue.append(item)           # add to the right end

    def _get(self):
        return self.queue.popleft()       # remove from the left end (FIFO)

    # --- Public interface (inherited unchanged by all subclasses) -----------

    def put(self, item, block=True, timeout=None):
        with self.not_full:
            if self.maxsize > 0:
                if not block:
                    if self._qsize() >= self.maxsize:
                        raise Full
                elif timeout is None:
                    while self._qsize() >= self.maxsize:
                        self.not_full.wait()           # wait until space is available
                elif timeout < 0:
                    raise ValueError("'timeout' must be a non-negative number")
                else:
                    endtime = time.monotonic() + timeout
                    while self._qsize() >= self.maxsize:
                        remaining = endtime - time.monotonic()
                        if remaining <= 0.0:
                            raise Full
                        self.not_full.wait(remaining)
            self._put(item)                            # delegates actual insert to _put
            self.unfinished_tasks += 1
            self.not_empty.notify()                    # wake up any waiting getters

    def get(self, block=True, timeout=None):
        with self.not_empty:
            if not block:
                if not self._qsize():
                    raise Empty
            elif timeout is None:
                while not self._qsize():
                    self.not_empty.wait()              # wait until an item is available
            elif timeout < 0:
                raise ValueError("'timeout' must be a non-negative number")
            else:
                endtime = time.monotonic() + timeout
                while not self._qsize():
                    remaining = endtime - time.monotonic()
                    if remaining <= 0.0:
                        raise Empty
                    self.not_empty.wait(remaining)
            item = self._get()                         # delegates actual removal to _get
            self.not_full.notify()                     # wake up any waiting putters
            return item


# ---------------------------------------------------------------------------
# PriorityQueue — smallest item is always returned first
# Uses a heap list: heappush / heappop maintain heap invariant
# ---------------------------------------------------------------------------

class PriorityQueue(Queue):
    def _init(self, maxsize):
        self.queue = []                   # plain list managed as a heap

    def _qsize(self):
        return len(self.queue)

    def _put(self, item):
        heappush(self.queue, item)        # insert while maintaining heap order

    def _get(self):
        return heappop(self.queue)        # removes and returns the smallest item


# ---------------------------------------------------------------------------
# LifoQueue — last item added is the first returned (stack)
# Uses a plain list: append() to push, pop() to pull from the same end
# ---------------------------------------------------------------------------

class LifoQueue(Queue):
    def _init(self, maxsize):
        self.queue = []                   # plain list used as a stack

    def _qsize(self):
        return len(self.queue)

    def _put(self, item):
        self.queue.append(item)           # push onto the top

    def _get(self):
        return self.queue.pop()           # pop from the top (LIFO)
