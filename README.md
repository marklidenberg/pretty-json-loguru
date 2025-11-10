# pretty-json-loguru

Pretty Python JSON logs with [loguru](https://github.com/Delgan/loguru).

## Basic usage 

```python
from loguru import logger
from pretty_json_loguru import configure_logger

configure_logger(level="DEBUG")

logger.debug("Hello", who="Friend!")
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

### configure_logger

```python
def configure_logger(
    level: str = "DEBUG",
    colorize: bool = True,
    include_traceback: bool = False,
    print_traceback_below: bool = True,
    indent: bool = False,
    remove_existing_sinks: bool = True,
    keys: List[LogKey] = ["ts", "msg", "source", "extra", "error", "traceback", "level"],
):
    """Configure the Loguru logger with JSON formatting.

    Args:
        level: Logging level. One of ["DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"].
        colorize: Adds colors to the log.
        include_traceback: Adds "error" and "traceback" fields to JSON when exceptions occur.
        print_traceback_below: Prints full traceback below the JSON line.
        indent: Formats JSON with indentation for readability.
        remove_existing_sinks: Removes existing sinks.
        keys: Keys to include in the log. Available: "ts", "msg", "source", "extra", "error", "traceback", "level", "module", "function", "filename", "line", "process_name", "process_id", "thread_name", "thread_id", "name".
    """
```

### create_json_formatter

```python
def create_json_formatter(
    colorize: bool = True,
    include_traceback: bool = False,
    print_traceback_below: bool = True,
    indent: bool = False,
    keys: List[LogKey] = ["ts", "msg", "source", "extra", "error", "traceback", "level"],
):
    """Create a JSON formatter for Loguru with optional colorization.

    Args:
        colorize: Adds colors to the log.
        include_traceback: Adds "error" and "traceback" fields to JSON when exceptions occur.
        print_traceback_below: Prints full traceback below the JSON line.
        indent: Formats JSON with indentation for readability.
        keys: Keys to include in the log. Available: "ts", "msg", "source", "extra", "error", "traceback", "level", "module", "function", "filename", "line", "process_name", "process_id", "thread_name", "thread_id", "name".

    Returns:
        A function that formats a loguru log record as a colored JSON string.
    """
```


## better_exceptions

Install [better-exceptions](https://github.com/Qix-/better-exceptions) for prettier tracebacks (used by default in loguru if installed)

## License

MIT License

## Author

Mark Lidenberg [marklidenberg@gmail.com](mailto:marklidenberg@gmail.com)