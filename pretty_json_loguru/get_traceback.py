import sys
import traceback


def get_traceback(exception) -> str:
    """Get formatted traceback from exception."""

    # - Try to get traceback from better_exceptions

    try:
        import better_exceptions

        return "".join(better_exceptions.format_exception(*exception))
    except:
        pass

    # - Fallback to traceback

    return traceback.format_exc()


def test():
    try:
        raise Exception("test")
    except Exception:
        print(get_traceback(exception=sys.exc_info()))


if __name__ == "__main__":
    test()
