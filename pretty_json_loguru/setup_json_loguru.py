import sys
from typing import Literal, List

from loguru import logger

from pretty_json_loguru.get_loguru_formatter import get_loguru_formatter


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
    """

    # - Remove existing sinks if needed

    if remove_existing_sinks:
        logger.remove()

    # - Add a new sink

    logger.add(
        sink=sys.stdout,
        level=level,
        format=get_loguru_formatter(
            traceback=traceback,
            colorize=colorize,
            keys=keys,
        ),
    )
