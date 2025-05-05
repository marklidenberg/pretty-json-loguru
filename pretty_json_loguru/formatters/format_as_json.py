import json
import math
import sys

from loguru import logger

from pretty_json_loguru.get_traceback import get_traceback


def format_as_json(
    record: dict,
    attach_raw_traceback: bool = True,
) -> str:
    """Loguru json formatter.

    Sample output:
    {"level": "INFO", "message": "Simple message", "ts": 1722241041459, "source": "", "extra": {}, "stack": "", "error": ""}
    {"level": "INFO", "message": "Message with extra", "ts": 1722241041459, "source": "", "extra": {"extra": {"foo": "bar"}}, "stack": "", "error": ""}
    {"level": "ERROR", "message": "Exception caught", "ts": 1722241041459, "source": "", "extra": {}, "stack": "...\nValueError: This is an exception\n", "error": ""}

    """
    assert "_json" not in record["extra"]

    extra = dict(record["extra"])
    extra.pop("source", None)

    record_dic = {
        "level": record["level"].name,
        "message": record["message"],
        "ts": int(math.floor(record["time"].timestamp() * 1000)),  # epoch millis
        "source": record["extra"].get("source", ""),
        "extra": extra,
        "stack": "",
        "error": "",
    }

    if record["exception"]:
        record_dic["traceback"] = get_traceback(exception=record["exception"]).strip()
        record_dic["error"] = record_dic["stack"].split("\n")[-1]

    record["extra"]["_json"] = json.dumps(record_dic, default=str)

    output = "{extra[_json]}\n"

    if attach_raw_traceback and "traceback" in record_dic:
        record["extra"]["_extra_traceback"] = record_dic["traceback"]
        output += "\n<red>{extra[_extra_traceback]}</red>"

    return output


def test():
    logger.info("Simple message")
    logger.info("Message with extra", extra={"foo": "bar"})

    try:
        raise ValueError("This is an exception")
    except ValueError:
        logger.exception("Exception caught")


def example():
    logger.remove()
    logger.add(sys.stderr, format=format_as_json)
    test()

    logger.remove()
    logger.add(
        sys.stderr,
        format=lambda record: format_as_json(record, attach_raw_traceback=True),
    )
    test()


if __name__ == "__main__":
    example()
