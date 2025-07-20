from importlib.metadata import version

try:
    __version__ = version("dony")
except Exception:
    __version__ = "unknown"

from .get_loguru_formatter import get_loguru_formatter
from .setup_json_loguru import setup_json_loguru

__all__ = ["get_loguru_formatter", "setup_json_loguru"]
