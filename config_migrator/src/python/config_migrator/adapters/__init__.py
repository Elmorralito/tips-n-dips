"""Adapter layer for OS-specific migrator implementations."""

from .base import MigratorAdapter
from .factory import detect_or_select_os, get_adapter

__all__ = ["MigratorAdapter", "detect_or_select_os", "get_adapter"]
