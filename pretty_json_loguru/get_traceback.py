import sys
import traceback
from typing import Any

from loguru import _defaults, logger
from loguru._better_exceptions import ExceptionFormatter


def get_traceback(
    exception: Any,
    colorize: bool = True,
    encoding: str = "utf-8",
) -> str:
    """Get a formatted traceback from an exception."""

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
        # Use builtin traceback, because loguru fails with colorize=False if 'module' is present (# TODO later: investigate)
        return traceback.format_exc()


def test():
    try:
        raise Exception("test")
    except Exception:
        print(
            get_traceback(
                exception=sys.exc_info(),
                colorize=False,
            ),
        )


if __name__ == "__main__":
    test()
