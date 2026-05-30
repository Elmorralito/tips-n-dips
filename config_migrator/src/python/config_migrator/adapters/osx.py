"""macOS migrator adapter."""

from __future__ import annotations

import argparse

from ..exporters.osx import export_configuration as export_osx_configuration
from ..helpers.logger import log_warning
from ..helpers.types import ExportOptions, ExportResult, ImportOptions, ImportResult
from ..importers.osx import import_configuration as import_osx_configuration
from .base import MigratorAdapter


class MacOSMigratorAdapter(MigratorAdapter):
    """Adapter that binds macOS importer/exporter implementations."""

    os_name = "macos"

    def add_custom_arguments(
        self,
        export_parser: argparse.ArgumentParser,
        import_parser: argparse.ArgumentParser,
    ) -> None:
        export_parser.add_argument(
            "--macos-skip-brew-packages",
            action="store_true",
            help="Skip Homebrew formula/cask/tap export.",
        )
        export_parser.add_argument(
            "--macos-include-home-credentials",
            action="store_true",
            help="Include credential material from home (for example .ssh, .aws, .gnupg).",
        )
        import_parser.add_argument(
            "--macos-skip-tool-installation",
            action="store_true",
            help="Skip Homebrew/pyenv/poetry/uv/oh-my-zsh installation step.",
        )

    def get_export_options(self, args: argparse.Namespace) -> ExportOptions:
        return {
            "macos_export_brew_packages": not args.macos_skip_brew_packages,
            "include_secrets": args.include_secrets or args.macos_include_home_credentials,
        }

    def get_import_options(self, args: argparse.Namespace) -> ImportOptions:
        return {
            "macos_install_tools": not args.macos_skip_tool_installation,
        }

    async def export_configuration(self, options: ExportOptions) -> ExportResult:
        if options.get("include_secrets", False) and not options.get("is_silent", False):
            log_warning(
                "Sensitive export enabled: credentials from home directories (for example .ssh/.aws/.gnupg) "
                "may be included in the archive."
            )
        return await export_osx_configuration(options)

    async def import_configuration(self, options: ImportOptions) -> ImportResult:
        return await import_osx_configuration(options)
