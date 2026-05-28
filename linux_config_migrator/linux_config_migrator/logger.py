"""Dedicated logging subsystem for the Linux Configuration Migrator.

Provides colored output, structured debug/error flows, and traceback printing guardrails.
"""

import os
import sys
import traceback
from typing import Optional, Any

# Terminal color constants
COLOR_RESET: str = "\033[0m"
COLOR_BOLD: str = "\033[1m"
COLOR_RED: str = "\033[31m"
COLOR_GREEN: str = "\033[32m"
COLOR_YELLOW: str = "\033[33m"
COLOR_BLUE: str = "\033[34m"
COLOR_CYAN: str = "\033[36m"

# Global state configuration
_SHOW_TRACEBACK: bool = False


def set_show_traceback(enabled: bool) -> None:
    """Configures whether full error stacktraces should be output to stderr."""
    global _SHOW_TRACEBACK
    _SHOW_TRACEBACK = enabled


def should_show_traceback() -> bool:
    """Checks if traceback print is active."""
    return _SHOW_TRACEBACK


def log_info(message: str) -> None:
    """Print an informational message to standard output."""
    print(f"{COLOR_BLUE}{COLOR_BOLD}[*]{COLOR_RESET} {message}")


def log_success(message: str) -> None:
    """Print a success confirmation message to standard output."""
    print(f"{COLOR_GREEN}{COLOR_BOLD}[+]{COLOR_RESET} {COLOR_GREEN}{message}{COLOR_RESET}")


def log_warning(message: str) -> None:
    """Print a warning message to standard error."""
    print(f"{COLOR_YELLOW}{COLOR_BOLD}[!]{COLOR_RESET} {COLOR_YELLOW}{message}{COLOR_RESET}", file=sys.stderr)


def log_error(message: str, exc: Optional[BaseException] = None) -> None:
    """Print an error message to stderr, optionally rendering a full stacktrace if enabled.
    
    Args:
        message: Friendly summary of the failure.
        exc: Optional captured exception object to trace.
    """
    print(f"{COLOR_RED}{COLOR_BOLD}[-]{COLOR_RESET} {COLOR_RED}{COLOR_BOLD}ERROR:{COLOR_RESET} {COLOR_RED}{message}{COLOR_RESET}", file=sys.stderr)
    
    # Check if a full traceback should be printed
    if exc and (_SHOW_TRACEBACK or os.environ.get("MIGRATOR_DEBUG") == "1"):
        print(f"\n{COLOR_RED}{COLOR_BOLD}--- BEGIN CRITICAL STACKTRACE ---{COLOR_RESET}", file=sys.stderr)
        traceback.print_exception(type(exc), exc, exc.__traceback__, file=sys.stderr)
        print(f"{COLOR_RED}{COLOR_BOLD}--- END CRITICAL STACKTRACE ---{COLOR_RESET}\n", file=sys.stderr)


def log_debug(message: str) -> None:
    """Print a debugging message to stdout if debug mode is active."""
    if os.environ.get("MIGRATOR_DEBUG") == "1":
        print(f"{COLOR_CYAN}[DEBUG]{COLOR_RESET} {message}")
