import sys
import traceback
from typing import Any

from loguru import logger
from loguru._better_exceptions import ExceptionFormatter


def format_traceback(
    exception: Any,
    colorize: bool = True,
    encoding: str = "utf-8",
) -> str:
    """Format a traceback from an exception."""

    # - Unpack exception

    type_, value, tb = exception

    # - Get traceback

    if colorize:
        # Use built-in loguru formatter
        return "".join(
            ExceptionFormatter(
                colorize=colorize,
                encoding=encoding,
                diagnose=True,
                backtrace=True,
                hidden_frames_filename=logger.catch.__code__.co_filename,
                prefix="",
            ).format_exception(type_, value, tb)
        )
    else:
        # Use builtin traceback, because loguru fails with colorize=False if 'module' is present (# todo later: investigate)
        return traceback.format_exc()


def example():
    try:
        raise Exception("test")
    except Exception:
        print(
            format_traceback(
                exception=sys.exc_info(),
                colorize=False,
            ),
        )


if __name__ == "__main__":
    example()
