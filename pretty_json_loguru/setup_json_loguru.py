import sys

from loguru import logger

from pretty_json_loguru.formatters.format_as_colored_json import (
    format_as_colored_json,
)


def setup_json_loguru(
    level: str = "DEBUG",
    attach_raw_traceback: bool = True,
    remove_existing_sinks: bool = True,
):
    """Set up loguru logger with JSON format (colored).

    Parameters
    ----------
    level : str
        Logging level
    attach_raw_traceback : bool
        If True, extra traceback will be appended to the log, as if we use the vanilla formatter.
    remove_existing_sinks : bool
        Whether to remove existing sinks

    """
    if remove_existing_sinks:
        logger.remove()

    logger.add(
        sink=sys.stdout,
        level=level,
        format=format_as_colored_json(
            attach_raw_traceback=attach_raw_traceback,
        ),
    )
