"""CLI entrypoint for the config migrator."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from .adapters import detect_or_select_os, get_adapter
from .adapters.base import MigratorAdapter
from .helpers.logger import log_error, log_info, log_success
from .helpers.utils import detect_os_family


def _build_parser(adapter: MigratorAdapter) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="config-migrator",
        description="Export and import configuration backups across supported OS targets.",
    )
    parser.add_argument(
        "--os",
        dest="target_os",
        choices=["linux", "macos", "osx"],
        default=None,
        help="Target OS adapter. If omitted, the current OS is auto-detected.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show actions without writing changes.",
    )
    parser.add_argument(
        "--silent",
        action="store_true",
        help="Suppress operation logs from import/export routines.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    export_parser = subparsers.add_parser("export", help="Export current configuration into an archive.")
    export_parser.add_argument(
        "--output-dir",
        default=str(Path.cwd()),
        help="Directory where the archive is created.",
    )
    export_parser.add_argument(
        "--include-secrets",
        action="store_true",
        help="Include high-risk secrets such as SSH/GPG/AWS material.",
    )

    import_parser = subparsers.add_parser("import", help="Import configuration from an archive.")
    import_parser.add_argument(
        "--archive-path",
        required=True,
        help="Path to the source migration archive.",
    )
    import_parser.add_argument(
        "--yes-to-all",
        action="store_true",
        help="Auto-accept prompts when possible.",
    )
    adapter.add_custom_arguments(export_parser, import_parser)
    return parser


async def _run() -> int:
    pre_parser = argparse.ArgumentParser(add_help=False)
    pre_parser.add_argument("--os", dest="target_os", choices=["linux", "macos", "osx"], default=None)
    pre_args, _ = pre_parser.parse_known_args()

    detected_os = detect_os_family()
    try:
        resolved_os = detect_or_select_os(pre_args.target_os, detected_os)
        adapter = get_adapter(resolved_os)
    except ValueError as exc:
        parser = _build_parser(get_adapter("linux"))
        parser.error(str(exc))
        return 2

    parser = _build_parser(adapter)
    args = parser.parse_args()

    log_info(f"Using '{adapter.os_name}' adapter.")

    if args.command == "export":
        export_options = {
            "output_dir": args.output_dir,
            "is_dry_run": args.dry_run,
            "is_silent": args.silent,
            "include_secrets": args.include_secrets,
        }
        export_options.update(adapter.get_export_options(args))
        result = await adapter.export_configuration(
            export_options
        )
        if not result["is_successful"]:
            log_error(result.get("error_message") or "Export failed.")
            return 1
        log_success(f"Export completed: {result.get('archive_path')}")
        return 0

    import_options = {
        "archive_path": args.archive_path,
        "is_dry_run": args.dry_run,
        "is_silent": args.silent,
        "yes_to_all": args.yes_to_all,
    }
    import_options.update(adapter.get_import_options(args))
    result = await adapter.import_configuration(
        import_options
    )
    if not result["is_successful"]:
        log_error(result.get("error_message") or "Import failed.")
        return 1
    restored_count = len(result.get("restored_items", []))
    log_success(f"Import completed: restored {restored_count} item(s).")
    if result.get("rollback_path"):
        log_info(f"Rollback path: {result['rollback_path']}")
    return 0


def main() -> None:
    try:
        code = asyncio.run(_run())
    except KeyboardInterrupt:
        code = 130
    sys.exit(code)


if __name__ == "__main__":
    main()
