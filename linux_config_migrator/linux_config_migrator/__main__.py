#!/usr/bin/env python3
"""Module execution entry point for the Linux Configuration Migrator.

Allows invoking the package directly via `python3 -m linux_config_migrator`.
"""

import argparse
import asyncio
import sys

from .exporter import export_configuration
from .importer import import_configuration
from .types import MigratorError
from .utils import log_error, set_show_traceback


async def _run_export(args: argparse.Namespace) -> int:
    """Async wrapper to run the export subcommand."""
    options = {
        "output_dir": args.output_dir,
        "is_dry_run": args.dry_run,
        "is_silent": args.silent,
        "include_secrets": args.include_secrets,
    }
    
    result = await export_configuration(options)
    
    if result["is_successful"]:
        return 0
        
    log_error(result["error_message"] or "Configuration export completed with errors.")
    return 1


async def _run_import(args: argparse.Namespace) -> int:
    """Async wrapper to run the import subcommand."""
    options = {
        "archive_path": args.archive,
        "is_dry_run": args.dry_run,
        "is_silent": args.silent,
        "yes_to_all": args.yes,
    }
    
    result = await import_configuration(options)
    
    if result["is_successful"]:
        return 0
        
    log_error(result["error_message"] or "Configuration import/restoration completed with errors.")
    return 1


def main() -> int:
    """Main CLI argument parsing and process management routine."""
    parser = argparse.ArgumentParser(
        description="Linux Configuration Migrator: Export and restore system configurations and dotfiles seamlessly.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  # Export configurations including secrets (SSH/GPG) into the current folder
  python3 -m linux_config_migrator export --include-secrets
  
  # Dry-run restoration to preview changes
  python3 -m linux_config_migrator import -a ./system_migration_backup_myhost_20260528.tar.gz --dry-run
  
  # Restore configurations interactively
  python3 -m linux_config_migrator import -a ./system_migration_backup_myhost_20260528.tar.gz
"""
    )
    
    parser.add_argument(
        "--show-traceback",
        action="store_true",
        help="Display the full stacktrace when an unexpected critical error occurs."
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True, help="Migration command to execute.")
    
    # Export Subparser
    export_parser = subparsers.add_parser("export", help="Export active OS configuration and packages into an archive.")
    export_parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default="./",
        help="Target directory where the backup tarball will be written (default: current directory)."
    )
    export_parser.add_argument(
        "--include-secrets",
        action="store_true",
        help="Opt-in to backup sensitive directories (e.g. ~/.ssh/config, ~/.gnupg, ~/.aws/credentials)."
    )
    export_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate the export, printing out what would be archived without generating files."
    )
    export_parser.add_argument(
        "--silent",
        action="store_true",
        help="Suppress all standard console logging."
    )
    
    # Import Subparser
    import_parser = subparsers.add_parser("import", help="Import packages and restore configurations from an archive.")
    import_parser.add_argument(
        "--archive", "-a",
        type=str,
        required=True,
        help="Absolute or relative path to the system_migration_backup_*.tar.gz archive file."
    )
    import_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate the restoration, showing packages to install and dotfiles to overwrite without applying changes."
    )
    import_parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Automatically answer yes to all configuration prompts (ideal for non-interactive/automated runs)."
    )
    import_parser.add_argument(
        "--silent",
        action="store_true",
        help="Suppress all standard console logging."
    )
    
    args = parser.parse_args()
    
    if args.show_traceback:
        set_show_traceback(True)
    
    try:
        if args.command == "export":
            return asyncio.run(_run_export(args))
        elif args.command == "import":
            return asyncio.run(_run_import(args))
    except MigratorError as err:
        log_error(f"Migration operational failure: {err}", exc=err)
        return 2
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Exiting.")
        return 130
    except Exception as err:
        log_error(f"An unexpected critical error occurred: {err}", exc=err)
        return 99
        
    return 0


if __name__ == "__main__":
    sys.exit(main())
