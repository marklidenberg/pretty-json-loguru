# pretty-json-loguru

Pretty Python JSON logs with [loguru](https://github.com/Delgan/loguru).

## Basic usage 

```python

from loguru import logger
from pretty_json_loguru import setup_json_loguru

setup_json_loguru(level="DEBUG")

loguru.debug("Hello", who="Friend!")

```

## Why JSON logs?

- Optimized for both developers and automated parsers
- Load large logs into any JSON viewer to expand and inspect every field

## How it looks 

### Vanilla loguru

![Before](docs/logger_default.png "Before")


### pretty-json-loguru

![After](docs/logger_pretty_json_loguru.png "After")

## API

```python

def setup_json_loguru(
    level: str = "DEBUG",
    traceback: Literal["attach", "extra", "drop"] = "attach",
    colorize: bool = True,
    remove_existing_sinks: bool = True,
    keys: List[str] = ["ts", "msg", "source", "extra", "error", "traceback", "level"],
):
    """Set up pretty-json-loguru logger.

    Parameters
    ----------
    level : str
        Logging level. One of `["DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"]`.
    
    traceback : Literal["attach", "extra", "drop"]
        "attach" appends the traceback to the log;
        "extra" adds it to the extra field;
        "drop" discards it.
    
    colorize : bool
        Adds colors to the log.
    
    keys : List[str]
        Keys to include in the log from the list `["ts", "msg", "source", "extra", "error", "traceback", "level", "module"]`.
        `module` is the only key that's not included by default.
        `extra` is a placeholder for extra fields.

    remove_existing_sinks : bool
        Removes existing sinks.
...
```


## better_exceptions

Install [better-exceptions](https://github.com/Qix-/better-exceptions) for prettier tracebacks (used by default in loguru if installed)

## License

MIT License

## Author

Mark Lidenberg [marklidenberg@gmail.com](mailto:marklidenberg@gmail.com)