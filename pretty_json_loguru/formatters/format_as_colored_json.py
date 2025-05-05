import sys

from collections import OrderedDict
from datetime import datetime
from typing import Any

from loguru import logger

from pretty_json_loguru.get_traceback import get_traceback

try:
    from loguru import Record
except ImportError:
    # for some reason, Record does not import this way in loguru 0.6.0
    Record = Any

try:
    import ujson as json
except ImportError:
    import json


def format_as_colored_json(
    attach_raw_traceback: bool = True,
):
    """Loguru formatter builder for colored json logs.

    Sample output (colored in the console):
    {"ts": "2024-07-29 08:19:03.675", "module": "format_as_colored_json", "message": "Simple message"}
    {"ts": "2024-07-29 08:19:03.675", "module": "format_as_colored_json", "message": "Message with extra", "foo": "bar"}
    {"ts": "2024-07-29 08:19:03.675", "module": "format_as_colored_json", "message": "Exception caught", "error": "ValueError: This is an exception", "traceback": "...\nValueError: This is an exception"}

    Parameters
    ----------
    append_non_json_traceback : bool
        If True, extra traceback will be appended to the log, as if we use the vanilla formatter.

    """

    def _format_as_json_colored(record: Record):
        # - Validate record

        assert "_json" not in record["extra"]

        # - Pop extra

        extra = dict(record["extra"])
        extra.pop("source", None)

        # - Create record_dic that will be serialized as json

        record_dic = {
            "msg": record["message"],
            # "module": record["module"],
            "ts": datetime.fromisoformat(str(record["time"])).strftime(
                "%Y-%m-%d %H:%M:%S.%f"
            )[:-3],  # 2023-03-26 13:04:09.512
            "source": record["extra"].get("source", ""),
        }

        if record["exception"]:
            record_dic["traceback"] = get_traceback(
                exception=record["exception"]
            ).strip()
            record_dic["error"] = record_dic["traceback"].split("\n")[-1]

        record_dic = {k: v for k, v in record_dic.items() if v}
        record_dic.update(extra)

        # - Sort keys

        record_dic = OrderedDict(
            sorted(
                record_dic.items(),
                key=lambda kv: {
                    "ts": 0,
                    # "module": 1,
                    "msg": 2,
                    "source": 3,
                    "extra": 4,
                    "error": 5,
                    "traceback": 6,
                    "level": 7,
                }.get(kv[0], 4),  # default is extra
            )
        )

        # - Get json

        output = (
            json.dumps(
                record_dic,
                default=str,
                ensure_ascii=False,
            )
            .replace("{", "{{")
            .replace(
                "}",
                "}}",
            )
        )

        # - Iterate over json and add color tags

        for i, (key, value) in enumerate(record_dic.items()):
            # - Pick color

            color_key = {
                "ts": "green",
                "module": "cyan",
                "msg": "level",
                "error": "red",
                "traceback": "red",
            }.get(key, "magenta")

            color_value = {
                "ts": "green",
                "module": "cyan",
                "msg": "level",
                "error": "red",
                "traceback": "red",
            }.get(key, "yellow")

            # - Dump to json

            value_str = (
                json.dumps(value, default=str, ensure_ascii=False)
                .replace("{", "{{")
                .replace("}", "}}")
            )

            # - Add colors for keys and values

            output = output.replace(
                f'"{key}": {value_str}',
                f'<{color_key}>"{{extra[_extra_{2 * i}]}}"</{color_key}>: <{color_value}>{{extra[_extra_{2 * i + 1}]}}</{color_value}>',
            )

            # - Add key and value to record, from where loguru will get them

            if record:
                record["extra"][f"_extra_{2 * i}"] = key
                record["extra"][f"_extra_{2 * i + 1}"] = json.dumps(
                    value,
                    ensure_ascii=False,
                    default=str,
                )

        # - Add traceback on new line

        if attach_raw_traceback and "traceback" in record_dic:
            record["extra"]["_extra_traceback"] = record_dic["traceback"]
            output += "\n<red>{extra[_extra_traceback]}</red>"

        # - Add white color for the whole output

        return "<white>" + output + "\n" + "</white>"

    return _format_as_json_colored


def test():
    logger.info("Simple message")
    logger.info("Message with extra", foo="bar")

    try:
        raise ValueError("This is an exception")
    except ValueError:
        logger.exception("Exception caught")


if __name__ == "__main__":
    logger.remove()
    logger.add(sys.stdout, format=format_as_colored_json(attach_raw_traceback=False))
    test()
