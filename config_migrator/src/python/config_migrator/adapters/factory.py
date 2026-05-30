"""Factory helpers for selecting migrator adapters."""

from __future__ import annotations

from .base import MigratorAdapter
from .linux import LinuxMigratorAdapter
from .osx import MacOSMigratorAdapter

SUPPORTED_OS = ("linux", "macos")


def detect_or_select_os(selected_os: str | None, detected_os: str) -> str:
    """Return selected OS when provided, otherwise use detected OS."""
    os_name = (selected_os or detected_os).lower()
    if os_name == "osx":
        return "macos"
    if os_name not in SUPPORTED_OS:
        raise ValueError(f"Unsupported OS '{os_name}'. Supported values: {', '.join(SUPPORTED_OS)}")
    return os_name


def get_adapter(os_name: str) -> MigratorAdapter:
    """Create adapter for the provided os name."""
    if os_name == "linux":
        return LinuxMigratorAdapter()
    if os_name == "macos":
        return MacOSMigratorAdapter()
    raise ValueError(f"Unsupported OS '{os_name}'.")
