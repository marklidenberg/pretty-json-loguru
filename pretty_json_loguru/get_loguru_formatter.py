import sys

from collections import OrderedDict
from datetime import datetime
from typing import Any, Literal, List

from loguru import logger

from pretty_json_loguru.get_traceback import get_traceback

try:
    from loguru import Record
except ImportError:
    # Record does not import this way in loguru 0.6.0 for some reason
    Record = Any

try:
    import ujson as json
except ImportError:
    import json

BUILTIN_KEYS = [
    "ts",
    "msg",
    "source",
    "error",
    "traceback",
    "level",
    "module",
]  # note: extra is not included, it's a placeholder for extra fields


def get_loguru_formatter(
    colorize: bool = True,
    traceback: Literal["attach", "extra", "drop"] = "attach",
    keys: List[str] = ["ts", "msg", "source", "extra", "error", "traceback", "level"],
):
    """Loguru formatter builder for colored json logs.

    Sample output (colored in the console):
    ```
    {"ts": "2024-07-29 08:19:03.675", "module": "format_as_colored_json", "message": "Simple message"}
    {"ts": "2024-07-29 08:19:03.675", "module": "format_as_colored_json", "message": "Message with extra", "foo": "bar"}
    {"ts": "2024-07-29 08:19:03.675", "module": "format_as_colored_json", "message": "Exception caught", "error": "ValueError: This is an exception", "traceback": "...\nValueError: This is an exception"}
    ```

    Parameters
    ----------
    colorize : bool
        Adds colors to the log.
    traceback : Literal["attach", "extra", "drop"]
        "attach" appends the traceback to the log;
        "extra" adds it to the extra field;
        "drop" discards it.
    keys : List[str]
        Keys to include in the log from the list `["ts", "msg", "source", "extra", "error", "traceback", "level", "module"]`.
        `module` is the only key that's not included by default.
        `extra` is a placeholder for extra fields.

    Returns
    -------
    Callable[[Record], str]
        A function that formats a loguru log record as a colored JSON string.
    """

    # - Check traceback value

    if traceback not in ["attach", "extra", "drop"]:
        raise ValueError(f"Unknown traceback value {traceback}")

    # - Define output formatter

    def _format_as_json_colored(record: Record):
        """
        record:
            {
              "elapsed": "0:00:00.005652",
              "exception": [
                "<class 'ValueError'>",
                "This is an exception",
                "<traceback object at 0x101444c00>"
              ],
              "extra": {
                "foo": "bar"
              },
              "file": "(name='format_as_colored_json.py', path='/Users/marklidenberg/Documents/coding/repos/marklidenberg/pretty-json-loguru/pretty_json_loguru/formatters/format_as_colored_json.py')",
              "function": "test",
              "level": "(name='ERROR', no=40, icon='\u274c')",
              "line": 225,
              "message": "Exception caught",
              "module": "format_as_colored_json",
              "name": "__main__",
              "process": "(id=96919, name='MainProcess')",
              "thread": "(id=8532785856, name='MainThread')",
              "time": "2025-05-09 11:18:46.707576+02:00"
            }
        """

        # - Pop extra

        extra = dict(record["extra"])
        extra.pop("source", None)

        # - Create record_dic that will be serialized as json

        record_dic = {
            "ts": datetime.fromisoformat(str(record["time"])).strftime(
                "%Y-%m-%d %H:%M:%S.%f"
            )[:-3],  # 2023-03-26 13:04:09.512
            "module": record["module"],
            "msg": record["message"],
            "source": record["extra"].get("source", ""),
        }

        if record["exception"] and traceback == "extra":
            record_dic["traceback"] = get_traceback(
                exception=record["exception"],
                colorize=False,
            ).strip()
            record_dic["error"] = record_dic["traceback"].split("\n")[-1]

        record_dic = {k: v for k, v in record_dic.items() if v}
        record_dic.update(extra)

        """
        {
          "msg": "Exception caught",
          "ts": "2025-05-09 11:18:46.707",
          "traceback": "Traceback (most recent call last):\n  File \"/Users/marklidenberg/Documents/coding/repos/marklidenberg/pretty-json-loguru/pretty_json_loguru/formatters/format_as_colored_json.py\", line 223, in test\n    raise ValueError(\"This is an exception\")\nValueError: This is an exception",
          "error": "ValueError: This is an exception",
          "foo": "bar"
        }
        """

        # - Sort keys

        key_to_index = {key: i for i, key in enumerate(keys)}

        def _key_func(kv):
            if kv[0] in BUILTIN_KEYS:
                # default keys
                if kv[0] in keys:
                    return key_to_index[kv[0]]
                else:
                    return len(keys)
            else:
                # extra keys, e.g. foo=bar
                if "extra" in keys:
                    return keys.index("extra")
                else:
                    return len(keys)

        record_dic = OrderedDict(
            sorted(
                record_dic.items(),
                key=_key_func,
            )
        )

        # - Filter keys

        def _filter_func(k):
            if k in BUILTIN_KEYS:
                return k in keys
            else:
                return "extra" in keys

        record_dic = {k: v for k, v in record_dic.items() if _filter_func(k)}

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
            # - Dump to json

            value_str = (
                json.dumps(
                    value,
                    default=str,
                    ensure_ascii=False,
                )
                .replace("{", "{{")
                .replace("}", "}}")
            )

            if colorize:
                # - Init level colors

                """
                Original colors from loguru:
                | Level        | Default Color Tag |               |
                | ------------ | ----------------- | ------------- |
                | **TRACE**    | `<cyan><bold>`    |               |
                | **DEBUG**    | `<blue><bold>`    |               |
                | **INFO**     | `<bold>`          |               |
                | **SUCCESS**  | `<green><bold>`   |               |
                | **WARNING**  | `<yellow><bold>`  |               |
                | **ERROR**    | `<red><bold>`     |               |
                | **CRITICAL** | `<RED><bold>`     | ([GitHub][1]) |
                
                [1]: https://github.com/Delgan/loguru/blob/master/loguru/_defaults.py "loguru/loguru/_defaults.py at master · Delgan/loguru · GitHub"
                """

                level_colors = {
                    "TRACE": "white",
                    "DEBUG": "blue",
                    "INFO": "light-white",
                    "SUCCESS": "green",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "light-white",
                }

                # - Pick a color

                color_key = {
                    "ts": "green",
                    "module": "cyan",
                    "msg": level_colors[record["level"].name],
                }.get(key, "magenta")

                color_value = {
                    "ts": "green",
                    "module": "cyan",
                    "msg": level_colors[record["level"].name],
                }.get(key, "yellow")

                # - Add colors to the key and value

                colored_key = (
                    f'<{color_key}>"{{extra[_extra_{2 * i}]}}"</{color_key}>'
                    if color_key
                    else f'"{{extra[_extra_{2 * i}]}}"'
                )
                colored_value = (
                    f"<{color_value}>{{extra[_extra_{2 * i + 1}]}}</{color_value}>"
                    if color_value
                    else f"{{extra[_extra_{2 * i + 1}]}}"
                )

                if key == "msg" and record["level"].name == "CRITICAL":
                    colored_key = f"<RED>{colored_key}</RED>"
                    colored_value = f"<RED>{colored_value}</RED>"

                output = output.replace(
                    f'"{key}": {value_str}',
                    f"{colored_key}: {colored_value}",
                )

            # - Add the key and value to the record, from where loguru will get them

            if record:
                record["extra"][f"_extra_{2 * i}"] = key
                record["extra"][f"_extra_{2 * i + 1}"] = json.dumps(
                    value,
                    ensure_ascii=False,
                    default=str,
                )

        # - Add traceback on a new line

        if traceback == "attach" and record["exception"]:
            record["extra"]["_extra_traceback"] = get_traceback(
                exception=record["exception"],
                colorize=colorize,
            )
            output += "\n{extra[_extra_traceback]}"

        # - Add white color to the whole output

        return "<white>" + output + "\n" + "</white>"

    return _format_as_json_colored


def test():
    logger.trace("Trace message")
    logger.debug("Debug message")
    logger.info("Info message")
    logger.success("Success message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")

    logger.info("Message with extra", foo="bar")

    try:
        raise ValueError("This is an exception")
    except ValueError:
        logger.exception("Exception caught", foo="bar")


if __name__ == "__main__":
    logger.remove()
    logger.add(
        sys.stdout,
        format=get_loguru_formatter(
            # colorize=True,
            # traceback="extra",
        ),
        level="TRACE",
    )

    test()
