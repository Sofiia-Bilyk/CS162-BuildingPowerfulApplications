# Python Logging Library — Class Hierarchy & Handler Methods

---

## How the Logging Library Works

The `logging` module provides a flexible event-logging system built around four components:

- **Logger** — the entry point (`logging.getLogger(name)`). You call `.debug()`, `.info()`, `.warning()`, `.error()`, `.critical()` on it.
- **Handler** — decides *where* a log record goes (file, console, socket, email, etc.).
- **Formatter** — controls *how* the record looks (timestamp, level name, message).
- **Filter** — optionally narrows *which* records a handler or logger processes.

A Logger passes a `LogRecord` to its attached Handlers. Each Handler formats it and sends it to its destination. The root logger sits at the top; child loggers propagate records up to it by default.

---

## Class Hierarchy in `logging` + `logging.handlers`

```
object
├── logging.Filterer
│     ├── logging.Logger
│     └── logging.Handler                      (core)
│           ├── logging.StreamHandler          (core)
│           │     └── logging.FileHandler      (core)
│           │           ├── BaseRotatingHandler
│           │           │     ├── RotatingFileHandler
│           │           │     └── TimedRotatingFileHandler
│           │           └── WatchedFileHandler
│           ├── logging.NullHandler            (core)
│           ├── SocketHandler
│           │     └── DatagramHandler
│           ├── SysLogHandler
│           ├── SMTPHandler
│           ├── NTEventLogHandler
│           ├── HTTPHandler
│           ├── BufferingHandler
│           │     └── MemoryHandler
│           └── QueueHandler
└── QueueListener                              (not a Handler)
```

### Summary table

| Class                      | Direct Parent            | Module               |
|----------------------------|--------------------------|----------------------|
| `Filterer`                 | `object`                 | `logging`            |
| `Logger`                   | `Filterer`               | `logging`            |
| `Handler`                  | `Filterer`               | `logging`            |
| `StreamHandler`            | `Handler`                | `logging`            |
| `FileHandler`              | `StreamHandler`          | `logging`            |
| `NullHandler`              | `Handler`                | `logging`            |
| `BaseRotatingHandler`      | `FileHandler`            | `logging.handlers`   |
| `RotatingFileHandler`      | `BaseRotatingHandler`    | `logging.handlers`   |
| `TimedRotatingFileHandler` | `BaseRotatingHandler`    | `logging.handlers`   |
| `WatchedFileHandler`       | `FileHandler`            | `logging.handlers`   |
| `SocketHandler`            | `Handler`                | `logging.handlers`   |
| `DatagramHandler`          | `SocketHandler`          | `logging.handlers`   |
| `SysLogHandler`            | `Handler`                | `logging.handlers`   |
| `SMTPHandler`              | `Handler`                | `logging.handlers`   |
| `NTEventLogHandler`        | `Handler`                | `logging.handlers`   |
| `HTTPHandler`              | `Handler`                | `logging.handlers`   |
| `BufferingHandler`         | `Handler`                | `logging.handlers`   |
| `MemoryHandler`            | `BufferingHandler`       | `logging.handlers`   |
| `QueueHandler`             | `Handler`                | `logging.handlers`   |
| `QueueListener`            | `object`                 | `logging.handlers`   |

---

## Chosen Class: `RotatingFileHandler`

**Full inheritance chain:**
```
object → Filterer → Handler → StreamHandler → FileHandler
       → BaseRotatingHandler → RotatingFileHandler
```

---

### All callable methods on `RotatingFileHandler`

Methods are grouped by the class that defines them, from most specific to most general.

#### Defined in `RotatingFileHandler`

| Method | Signature | Description |
|--------|-----------|-------------|
| `__init__` | `(filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=False)` | Opens the log file. `maxBytes` sets the size limit; `backupCount` sets how many old files to keep. If `maxBytes=0`, the file grows forever and rollover never occurs. |
| `doRollover` | `()` | Performs the actual rotation: renames existing backup files (`.1`→`.2`, etc.), renames the current file to `.1`, then opens a fresh log file. |
| `shouldRollover` | `(record)` | Returns `1` if writing `record` would exceed `maxBytes`; returns `0` otherwise. Called automatically before every `emit`. |

#### Defined in `BaseRotatingHandler`

| Method | Signature | Description |
|--------|-----------|-------------|
| `emit` | `(record)` | Calls `shouldRollover`; if true, calls `doRollover`; then delegates to `FileHandler.emit`. Catches exceptions via `handleError`. |
| `rotation_filename` | `(default_name)` | Returns the filename to use for a rotated file. If `self.namer` is callable, it is called with `default_name`; otherwise returns `default_name` unchanged. Lets you customize backup filenames. |
| `rotate` | `(source, dest)` | Performs the actual OS-level rename. If `self.rotator` is callable, calls it; otherwise calls `os.rename(source, dest)`. Lets you customize rotation (e.g. compress the old file). |

#### Defined in `FileHandler`

| Method | Signature | Description |
|--------|-----------|-------------|
| `close` | `()` | Flushes and closes the file stream, then calls `StreamHandler.close`. |
| `_open` | `()` | Opens the file with `self.baseFilename`, `self.mode`, and `self.encoding`. Called internally. |

#### Defined in `StreamHandler`

| Method | Signature | Description |
|--------|-----------|-------------|
| `flush` | `()` | Flushes the underlying stream to disk immediately. |
| `setStream` | `(stream)` | Replaces the current stream; flushes the old one first. Returns the old stream. |

#### Defined in `logging.Handler`

| Method | Signature | Description |
|--------|-----------|-------------|
| `setLevel` | `(level)` | Sets the minimum severity level this handler will process (e.g. `logging.WARNING`). Records below this level are ignored. |
| `setFormatter` | `(fmt)` | Attaches a `Formatter` object to control how records are rendered into strings. |
| `format` | `(record)` | Applies the attached formatter (or a default one) to a `LogRecord` and returns the formatted string. |
| `handle` | `(record)` | Acquires the lock, calls `filter` then `emit`, then releases the lock. This is the public entry point called by loggers. |
| `handleError` | `(record)` | Called when `emit` raises an exception. By default prints the traceback to `sys.stderr` and swallows the error so logging never crashes the app. |
| `createLock` | `()` | Creates a `threading.RLock` for thread-safe emit calls. Called during `__init__`. |
| `acquire` | `()` | Acquires the handler's thread lock. |
| `release` | `()` | Releases the handler's thread lock. |

#### Defined in `logging.Filterer` (also available on Handler)

| Method | Signature | Description |
|--------|-----------|-------------|
| `addFilter` | `(filter)` | Adds a `Filter` object (or logger name string) to the handler's filter list. |
| `removeFilter` | `(filter)` | Removes a previously added filter. |
| `filter` | `(record)` | Passes the record through all attached filters. Returns `True` if the record should be processed, `False` if it should be dropped. |

