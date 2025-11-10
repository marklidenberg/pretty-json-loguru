import sys
from typing import List, cast

from loguru import logger

from pretty_json_loguru.create_json_formatter import create_json_formatter, LogKey


def configure_logger(
    level: str = "DEBUG",
    colorize: bool = True,
    include_traceback: bool = False,
    print_traceback_below: bool = True,
    indent: bool = False,
    remove_existing_sinks: bool = True,
    keys: List[LogKey] = cast(
        List[LogKey],
        [
            "ts",
            "msg",
            "source",
            "extra",
            "error",
            "traceback",
            "level",
        ],
    ),
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

    # - Remove existing sinks if needed

    if remove_existing_sinks:
        logger.remove()

    # - Add a new sink

    logger.add(
        sink=sys.stdout,
        level=level,
        format=create_json_formatter(
            colorize=colorize,
            include_traceback=include_traceback,
            print_traceback_below=print_traceback_below,
            indent=indent,
            keys=keys,
        ),
    )
