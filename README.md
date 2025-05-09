# pretty-json-loguru

Pretty json loguru logs. 

## Basic usage 

```python

from pretty_json_loguru import setup_json_loguru

setup_json_loguru(level="DEBUG")

```


## How it looks 

### loguru

![Before](docs/logger_default.png "Before")

### pretty-json-loguru

![After](docs/logger_pretty_json_loguru.png "After")

## Why JSON logs? 

- Clear for developers and parsers alike.
- Paste into any JSON viewer to expand and explore fields.

## API

```python
from typing import Literal, List


def setup_json_loguru(
        level: str = "DEBUG",
        traceback: Literal["attach", "extra", "drop"] = "attach",
        colorize: bool = True,
        remove_existing_sinks: bool = True,
        keys: List[Literal["ts", "module", "msg", "source", "extra", "error", "traceback", "level"]] = [
            "ts",
            # "module", # module is skipped by default for brevity
            "msg",
            "source",
            "extra",
            "error",
            "traceback",
            "level",
        ],
):
    """Set up loguru logger with JSON format (colored).

    Parameters
    ----------
    level : str
        Logging level
    traceback : Literal["attach", "extra", "drop"]
        If "attach", traceback will be appended to the log, as if we use the vanilla formatter.
        if "extra", traceback will be added to the extra field
        if "drop", traceback will be dropped
    colorize : bool
        If True, colors will be added to the log. If colorize=False, vanilla traceback will be used (`traceback.format_exc()`)
     keys : List[Literal["ts", "module", "msg", "source", "extra", "error", "traceback", "level"]]
        List and order of keys to include in the log. `extra` is a placeholder for extra fields
    remove_existing_sinks : bool
        Whether to remove existing sinks
    """
	...
```


## better_exceptions

Install `better_exceptions` for prettier tracebacks, used by default by loguru.