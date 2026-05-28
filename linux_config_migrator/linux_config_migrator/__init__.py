"""Linux Configuration Migrator core module package.

Exposes clean named exports for commands and utilities following python-cybersec rules.
"""

from .exporter import export_configuration
from .importer import import_configuration
from .types import ExportOptions, ExportResult, ImportOptions, ImportResult
from .utils import detect_package_manager

__all__ = [
    "export_configuration",
    "import_configuration",
    "ExportOptions",
    "ExportResult",
    "ImportOptions",
    "ImportResult",
    "detect_package_manager",
]
