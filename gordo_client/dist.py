"""
Package distribution related utils.
"""
import importlib

from typing import Optional


def get_version() -> Optional[str]:
    """
    Get the current gordo-client version. ``None`` if not installed in the system.
    """
    try:
        return importlib.metadata.version("gordo-client")
    except ImportError:
        pass
    return None
