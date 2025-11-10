from importlib.metadata import version

try:
    __version__ = version("dony")
except Exception:
    __version__ = "unknown"

from .create_json_formatter import create_json_formatter
from .configure_logger import configure_logger

__all__ = ["create_json_formatter", "configure_logger"]
