import sys
from typing import Literal, List

from loguru import logger

from pretty_json_loguru import pretty_json_loguru_formatter


def setup_json_loguru(
    level: str = "DEBUG",
    traceback: Literal["attach", "extra", "drop"] = "attach",
    colorize: bool = True,
    remove_existing_sinks: bool = True,
    keys: List[
        Literal["ts", "module", "msg", "source", "extra", "error", "traceback", "level"]
    ] = [
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
    if remove_existing_sinks:
        logger.remove()

    logger.add(
        sink=sys.stdout,
        level=level,
        format=pretty_json_loguru_formatter(
            traceback=traceback,
            colorize=colorize,
        ),
    )
