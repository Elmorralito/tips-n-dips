"""Linux migrator adapter."""

from __future__ import annotations

import argparse

from ..exporters.linux import export_configuration as export_linux_configuration
from ..helpers.types import ExportOptions, ExportResult, ImportOptions, ImportResult
from ..importers.linux import import_configuration as import_linux_configuration
from .base import MigratorAdapter


class LinuxMigratorAdapter(MigratorAdapter):
    """Adapter that binds linux importer/exporter implementations."""

    os_name = "linux"

    def add_custom_arguments(
        self,
        export_parser: argparse.ArgumentParser,
        import_parser: argparse.ArgumentParser,
    ) -> None:
        export_parser.add_argument(
            "--linux-skip-packages",
            action="store_true",
            help="Skip Linux package export (native package manager, Flatpak, Snap).",
        )
        export_parser.add_argument(
            "--linux-skip-desktop-settings",
            action="store_true",
            help="Skip GNOME/dconf desktop settings export.",
        )
        export_parser.add_argument(
            "--linux-skip-cron-jobs",
            action="store_true",
            help="Skip crontab export.",
        )
        import_parser.add_argument(
            "--linux-skip-system-packages",
            action="store_true",
            help="Skip native package install step during import.",
        )
        import_parser.add_argument(
            "--linux-skip-flatpak",
            action="store_true",
            help="Skip Flatpak install step during import.",
        )
        import_parser.add_argument(
            "--linux-skip-snap",
            action="store_true",
            help="Skip Snap install step during import.",
        )
        import_parser.add_argument(
            "--linux-skip-desktop-settings",
            action="store_true",
            help="Skip GNOME/dconf desktop settings restore.",
        )
        import_parser.add_argument(
            "--linux-skip-cron-jobs",
            action="store_true",
            help="Skip crontab restore.",
        )

    def get_export_options(self, args: argparse.Namespace) -> ExportOptions:
        return {
            "linux_export_packages": not args.linux_skip_packages,
            "linux_export_desktop_settings": not args.linux_skip_desktop_settings,
            "linux_export_cron_jobs": not args.linux_skip_cron_jobs,
        }

    def get_import_options(self, args: argparse.Namespace) -> ImportOptions:
        return {
            "linux_restore_system_packages": not args.linux_skip_system_packages,
            "linux_restore_flatpak": not args.linux_skip_flatpak,
            "linux_restore_snap": not args.linux_skip_snap,
            "linux_restore_desktop_settings": not args.linux_skip_desktop_settings,
            "linux_restore_cron_jobs": not args.linux_skip_cron_jobs,
        }

    async def export_configuration(self, options: ExportOptions) -> ExportResult:
        return await export_linux_configuration(options)

    async def import_configuration(self, options: ImportOptions) -> ImportResult:
        return await import_linux_configuration(options)
