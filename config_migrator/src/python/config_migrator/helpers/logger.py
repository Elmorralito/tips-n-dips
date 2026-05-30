"""Logging utilities for the macOS Configuration Migrator."""

import os
import sys
import traceback
from typing import Optional

COLOR_RESET = "\033[0m"
COLOR_BOLD = "\033[1m"
COLOR_RED = "\033[31m"
COLOR_GREEN = "\033[32m"
COLOR_YELLOW = "\033[33m"
COLOR_BLUE = "\033[34m"
COLOR_CYAN = "\033[36m"

_SHOW_TRACEBACK = False


def set_show_traceback(enabled: bool) -> None:
    """Enable or disable full traceback logging."""
    global _SHOW_TRACEBACK
    _SHOW_TRACEBACK = enabled


def log_info(message: str) -> None:
    """Print informational message."""
    print(f"{COLOR_BLUE}{COLOR_BOLD}[*]{COLOR_RESET} {message}")


def log_success(message: str) -> None:
    """Print success message."""
    print(f"{COLOR_GREEN}{COLOR_BOLD}[+]{COLOR_RESET} {COLOR_GREEN}{message}{COLOR_RESET}")


def log_warning(message: str) -> None:
    """Print warning message."""
    print(f"{COLOR_YELLOW}{COLOR_BOLD}[!]{COLOR_RESET} {COLOR_YELLOW}{message}{COLOR_RESET}", file=sys.stderr)


def log_error(message: str, exc: Optional[BaseException] = None) -> None:
    """Print error message and optional traceback."""
    print(f"{COLOR_RED}{COLOR_BOLD}[-]{COLOR_RESET} {COLOR_RED}{COLOR_BOLD}ERROR:{COLOR_RESET} {COLOR_RED}{message}{COLOR_RESET}", file=sys.stderr)
    if exc and (_SHOW_TRACEBACK or os.environ.get("MIGRATOR_DEBUG") == "1"):
        traceback.print_exception(type(exc), exc, exc.__traceback__, file=sys.stderr)


def log_debug(message: str) -> None:
    """Print debug message when debug mode is active."""
    if os.environ.get("MIGRATOR_DEBUG") == "1":
        print(f"{COLOR_CYAN}[DEBUG]{COLOR_RESET} {message}")
