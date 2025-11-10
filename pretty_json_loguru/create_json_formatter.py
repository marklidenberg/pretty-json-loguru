import sys

from collections import OrderedDict
from datetime import datetime
from typing import Any, Literal, List, Dict, TYPE_CHECKING, cast

from loguru import logger

from pretty_json_loguru.format_traceback import format_traceback

try:
    import ujson as json  # type: ignore[import-not-found]
except ImportError:
    import json

LogKey = Literal[
    "ts",
    "msg",
    "source",
    "extra",
    "error",
    "traceback",
    "level",
    "module",
    "function",
    "filename",
    "line",
    "process_name",
    "process_id",
    "thread_name",
    "thread_id",
    "name",
]

if TYPE_CHECKING:
    try:
        from loguru import Record
    except ImportError:
        # Record does not import this way in loguru 0.6.0 for some reason
        # Use Dict[str, Any] as a fallback type for type checking
        Record = Dict[str, Any]

# Valid keys that can be included in log output (see LogKey type)
# "extra" is a special placeholder for extra fields
VALID_LOG_KEYS = list(LogKey.__args__)  # type: ignore[attr-defined]


def create_json_formatter(
    colorize: bool = True,
    include_traceback: bool = False,
    print_traceback_below: bool = True,
    indent: bool = False,
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
    """Create a JSON formatter for Loguru with optional colorization.

    Args:
        colorize: Adds colors to the log.
        include_traceback: Adds "error" and "traceback" fields to JSON when exceptions occur.
        print_traceback_below: Prints full traceback below the JSON line.
        indent: Formats JSON with indentation for readability.
        keys: Keys to include in the log. Available: "ts", "msg", "source", "extra", "error", "traceback", "level", "module", "function", "filename", "line", "process_name", "process_id", "thread_name", "thread_id", "name".

    Returns:
        A function that formats a loguru log record as a colored JSON string.
    """

    # - Define output formatter

    def _format_as_json_colored(record: "Record"):  # type: ignore[name-defined]
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

        if record["exception"] and include_traceback:
            tb = format_traceback(
                exception=record["exception"],
                colorize=False,
            ).strip()
            record_dic["error"] = tb.split("\n")[-1]
            record_dic["traceback"] = tb

        # Remove empty values from record_dic
        record_dic = {k: v for k, v in record_dic.items() if v}

        # Add extra as a nested key if there are extra fields
        if extra:
            record_dic["extra"] = extra

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
            if kv[0] in VALID_LOG_KEYS or kv[0] == "extra":
                # default keys and extra key
                if kv[0] in keys:
                    return key_to_index[kv[0]]
                else:
                    return len(keys)
            else:
                # This shouldn't happen anymore since extra fields are nested
                return len(keys)

        record_dic = OrderedDict(
            sorted(
                record_dic.items(),
                key=_key_func,
            )
        )

        # - Filter keys

        def _filter_func(k):
            if k in VALID_LOG_KEYS or k == "extra":
                return k in keys
            else:
                # This shouldn't happen anymore since extra fields are nested
                return False

        record_dic = {k: v for k, v in record_dic.items() if _filter_func(k)}

        # - Get json

        output = (
            json.dumps(
                record_dic,
                default=str,
                ensure_ascii=False,
                indent=2 if indent else None,
            )
            .replace(
                "{", "{{"
            )  # loguru uses formatting by default if curly brackets are present. See https://loguru.readthedocs.io/en/stable/resources/troubleshooting.html#why-logging-a-message-with-f-string-sometimes-raises-an-exception
            .replace(
                "}",
                "}}",
            )
        )

        # - Iterate over json and add color tags

        extra_index = 0  # Track index for extra variables

        for key, value in record_dic.items():
            # - Dump to json

            value_str = (
                json.dumps(
                    value,
                    default=str,
                    ensure_ascii=False,
                )
                .replace(
                    "{", "{{"
                )  # loguru uses formatting by default if curly brackets are present. See https://loguru.readthedocs.io/en/stable/resources/troubleshooting.html#why-logging-a-message-with-f-string-sometimes-raises-an-exception
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

                # Handle the nested "extra" dictionary specially
                if key == "extra" and isinstance(value, dict):
                    # Colorize nested extra keys (magenta/purple) and values (yellow)
                    for extra_key, extra_value in value.items():
                        extra_key_str = (
                            json.dumps(extra_key, default=str, ensure_ascii=False)
                            .replace("{", "{{")
                            .replace("}", "}}")
                        )
                        extra_value_str = (
                            json.dumps(extra_value, default=str, ensure_ascii=False)
                            .replace("{", "{{")
                            .replace("}", "}}")
                        )

                        colored_extra_key = (
                            f"<magenta>{{extra[_extra_{extra_index}]}}</magenta>"
                        )
                        colored_extra_value = (
                            f"<yellow>{{extra[_extra_{extra_index + 1}]}}</yellow>"
                        )

                        output = output.replace(
                            f"{extra_key_str}: {extra_value_str}",
                            f"{colored_extra_key}: {colored_extra_value}",
                        )

                        record["extra"][f"_extra_{extra_index}"] = extra_key_str
                        record["extra"][f"_extra_{extra_index + 1}"] = extra_value_str
                        extra_index += 2

                    # Color the "extra" key itself as magenta
                    colored_key = (
                        f'<magenta>"{{extra[_extra_{extra_index}]}}"</magenta>'
                    )
                    colored_value = f"{{extra[_extra_{extra_index + 1}]}}"

                    output = output.replace(
                        f'"extra": {value_str}',
                        f"{colored_key}: {colored_value}",
                    )

                    record["extra"][f"_extra_{extra_index}"] = key
                    record["extra"][f"_extra_{extra_index + 1}"] = value_str
                    extra_index += 2
                else:
                    # Handle regular keys
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
                        f'<{color_key}>"{{extra[_extra_{extra_index}]}}"</{color_key}>'
                        if color_key
                        else f'"{{extra[_extra_{extra_index}]}}"'
                    )
                    colored_value = (
                        f"<{color_value}>{{extra[_extra_{extra_index + 1}]}}</{color_value}>"
                        if color_value
                        else f"{{extra[_extra_{extra_index + 1}]}}"
                    )

                    if key == "msg" and record["level"].name == "CRITICAL":
                        colored_key = f"<RED>{colored_key}</RED>"
                        colored_value = f"<RED>{colored_value}</RED>"

                    output = output.replace(
                        f'"{key}": {value_str}',
                        f"{colored_key}: {colored_value}",
                    )

                    # - Add the key and value to the record, from where loguru will get them

                    record["extra"][f"_extra_{extra_index}"] = key
                    record["extra"][f"_extra_{extra_index + 1}"] = json.dumps(
                        value,
                        ensure_ascii=False,
                        default=str,
                    )
                    extra_index += 2
            else:
                # No colorization, but still need to add to record
                record["extra"][f"_extra_{extra_index}"] = key
                record["extra"][f"_extra_{extra_index + 1}"] = json.dumps(
                    value,
                    ensure_ascii=False,
                    default=str,
                )
                extra_index += 2

        # - Add traceback on a new line

        if print_traceback_below and record["exception"]:
            record["extra"]["_extra_traceback"] = format_traceback(
                exception=record["exception"],
                colorize=colorize,
            )
            output += "\n{extra[_extra_traceback]}"

        # - Add white color to the whole output

        return "<white>" + output + "\n" + "</white>"

    return _format_as_json_colored


def example():
    logger.remove()
    logger.add(
        sys.stdout,
        format=create_json_formatter(
            colorize=True,
            include_traceback=False,
            print_traceback_below=False,
        ),
        level="TRACE",
    )

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
    example()
