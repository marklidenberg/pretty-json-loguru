from importlib.metadata import version

try:
    __version__ = version("dony")
except Exception:
    __version__ = "unknown"

from .setup_json_loguru import setup_json_loguru

from .pretty_json_loguru_formatter import pretty_json_loguru_formatter
