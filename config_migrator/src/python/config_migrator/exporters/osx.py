"""Configuration backup engine for the macOS Configuration Migrator."""

import json
import os
import platform
import shutil
import tempfile
import time
from pathlib import Path
from typing import Any

from ..defaults.osx import DEFAULT_ARCHIVE_PREFIX, DEFAULT_DOTFILES, DEFAULT_SECRETS
from ..helpers.types import ExportOptions, ExportResult
from ..helpers.utils import detect_os_family, run_shell_command


def _export_dotfiles(staging_dir: Path, include_secrets: bool) -> list[str]:
    """Copy selected user configuration files into staging."""
    home = Path.home()
    dotfiles_dest = staging_dir / "dotfiles"
    dotfiles_dest.mkdir(parents=True, exist_ok=True)

    targets = list(DEFAULT_DOTFILES)
    if include_secrets:
        targets.extend(DEFAULT_SECRETS)

    backed_up_items: list[str] = []
    for item in targets:
        src_path = home / item
        if not src_path.exists():
            continue

        dest_path = dotfiles_dest / item
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        if src_path.is_file():
            if src_path.is_symlink():
                os.symlink(os.readlink(src_path), dest_path)
            else:
                shutil.copy2(src_path, dest_path)
            backed_up_items.append(item)
        elif src_path.is_dir():
            shutil.copytree(src_path, dest_path, symlinks=True, dirs_exist_ok=True)
            backed_up_items.append(item)

    return backed_up_items


async def _export_brew_packages(staging_dir: Path) -> dict[str, bool]:
    """Export Homebrew package lists if brew is available."""
    packages_dir = staging_dir / "packages"
    packages_dir.mkdir(parents=True, exist_ok=True)
    status = {"brew_formulae": False, "brew_casks": False, "brew_taps": False}

    formulae = await run_shell_command(
        {"cmd": ["brew", "list", "--formula"], "is_shell": False, "cwd": None, "timeout_seconds": 20.0}
    )
    if formulae["is_successful"] and formulae["stdout"]:
        (packages_dir / "brew_formulae.txt").write_text(formulae["stdout"])
        status["brew_formulae"] = True

    casks = await run_shell_command(
        {"cmd": ["brew", "list", "--cask"], "is_shell": False, "cwd": None, "timeout_seconds": 20.0}
    )
    if casks["is_successful"] and casks["stdout"]:
        (packages_dir / "brew_casks.txt").write_text(casks["stdout"])
        status["brew_casks"] = True

    taps = await run_shell_command(
        {"cmd": ["brew", "tap"], "is_shell": False, "cwd": None, "timeout_seconds": 20.0}
    )
    if taps["is_successful"] and taps["stdout"]:
        (packages_dir / "brew_taps.txt").write_text(taps["stdout"])
        status["brew_taps"] = True

    return status


async def export_configuration(options: ExportOptions) -> ExportResult:
    """Gather and compress macOS configuration into a migration archive."""
    output_path = Path(options.get("output_dir", "./")).resolve()
    include_secrets = options.get("include_secrets", False)
    is_dry_run = options.get("is_dry_run", False)
    export_brew_packages = options.get("macos_export_brew_packages", True)

    if not is_dry_run:
        output_path.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="osx_migrator_staging_") as temp_dir_str:
        staging_dir = Path(temp_dir_str)
        copied_dotfiles = _export_dotfiles(staging_dir, include_secrets)
        brew_status: dict[str, bool] = {"brew_formulae": False, "brew_casks": False, "brew_taps": False}

        if export_brew_packages and detect_os_family() == "macos":
            try:
                brew_status = await _export_brew_packages(staging_dir)
            except Exception:
                brew_status = {"brew_formulae": False, "brew_casks": False, "brew_taps": False}

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        hostname = platform.node()
        manifest: dict[str, Any] = {
            "version": "1.0",
            "hostname": hostname,
            "timestamp": timestamp,
            "os_family": detect_os_family(),
            "os_version": platform.mac_ver()[0] or "unknown",
            "architecture": platform.machine(),
            "has_secrets_included": include_secrets,
            "packages_exported": brew_status,
            "dotfiles_backed_up": copied_dotfiles,
        }
        (staging_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))

        archive_name = f"{DEFAULT_ARCHIVE_PREFIX}_{hostname}_{timestamp}.tar.gz"
        archive_dest = output_path / archive_name
        if is_dry_run:
            return {
                "is_successful": True,
                "archive_path": str(archive_dest),
                "manifest": manifest,
                "error_message": None,
            }

        shutil.make_archive(
            str(archive_dest.with_suffix("").with_suffix("")),
            "gztar",
            root_dir=staging_dir,
        )

        return {
            "is_successful": archive_dest.exists(),
            "archive_path": str(archive_dest) if archive_dest.exists() else None,
            "manifest": manifest,
            "error_message": None if archive_dest.exists() else "Archive creation failed.",
        }
