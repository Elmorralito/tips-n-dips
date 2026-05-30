"""Base adapter contract for platform-specific migrators."""

from __future__ import annotations

import argparse
from abc import ABC, abstractmethod

from ..helpers.types import ExportOptions, ExportResult, ImportOptions, ImportResult


class MigratorAdapter(ABC):
    """Defines the interface that each OS adapter must implement."""

    os_name: str

    def add_custom_arguments(
        self,
        export_parser: argparse.ArgumentParser,
        import_parser: argparse.ArgumentParser,
    ) -> None:
        """Register OS-specific CLI arguments for export/import commands."""

    def get_export_options(self, args: argparse.Namespace) -> ExportOptions:
        """Return adapter-specific export options derived from parsed args."""
        return {}

    def get_import_options(self, args: argparse.Namespace) -> ImportOptions:
        """Return adapter-specific import options derived from parsed args."""
        return {}

    @abstractmethod
    async def export_configuration(self, options: ExportOptions) -> ExportResult:
        """Export system configuration into an archive."""

    @abstractmethod
    async def import_configuration(self, options: ImportOptions) -> ImportResult:
        """Import configuration from an archive."""
