"""Configuration import and restoration engine for the macOS Configuration Migrator."""

import json
import os
import shutil
import sys
import tarfile
import tempfile
import time
from pathlib import Path

from ..defaults.osx import DEFAULT_ROLLBACK_PREFIX
from ..helpers.types import ImportOptions, ImportResult
from ..helpers.utils import has_command, run_shell_command


def _prompt_user(prompt: str, default: bool, yes_to_all: bool) -> bool:
    """Prompt user for yes/no, handling non-interactive sessions."""
    if yes_to_all:
        return True
    if not sys.stdin.isatty():
        return default
    suffix = " [Y/n]: " if default else " [y/N]: "
    response = input(f"{prompt}{suffix}").strip().lower()
    if not response:
        return default
    return response in ("y", "yes")


def _create_rollback_backup(dotfiles_backed_up: list[str], rollback_dir: Path) -> int:
    """Backup existing local files before overwrite."""
    home = Path.home()
    count = 0
    for item in dotfiles_backed_up:
        source = home / item
        if not source.exists():
            continue
        destination = rollback_dir / item
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.is_file():
            if source.is_symlink():
                os.symlink(os.readlink(source), destination)
            else:
                shutil.copy2(source, destination)
            count += 1
        elif source.is_dir():
            shutil.copytree(source, destination, symlinks=True, dirs_exist_ok=True)
            count += 1
    return count


def _restore_dotfiles(extracted_staging: Path, dotfiles_backed_up: list[str]) -> int:
    """Restore staged dotfiles into user home directory."""
    home = Path.home()
    source_base = extracted_staging / "dotfiles"
    restored = 0
    for item in dotfiles_backed_up:
        source = source_base / item
        if not source.exists():
            continue
        destination = home / item
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.is_file() or destination.is_symlink():
            destination.unlink()
        elif destination.is_dir():
            shutil.rmtree(destination)

        if source.is_file():
            if source.is_symlink():
                os.symlink(os.readlink(source), destination)
            else:
                shutil.copy2(source, destination)
            restored += 1
        elif source.is_dir():
            shutil.copytree(source, destination, symlinks=True, dirs_exist_ok=True)
            restored += 1
    return restored


async def _install_homebrew(is_dry_run: bool) -> bool:
    """Install Homebrew if it is missing."""
    if has_command("brew"):
        return True
    if is_dry_run:
        return True
    result = await run_shell_command(
        {
            "cmd": '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
            "is_shell": True,
            "cwd": None,
            "timeout_seconds": 600.0,
        }
    )
    return result["is_successful"]


async def _install_required_tools(is_dry_run: bool) -> list[str]:
    """Install pyenv, poetry, uv, and oh-my-zsh using brew/curl flows."""
    installed: list[str] = []

    if await _install_homebrew(is_dry_run):
        installed.append("homebrew")
    else:
        return installed

    brew_targets = [("pyenv", "pyenv"), ("uv", "uv")]
    for label, package in brew_targets:
        if has_command(label):
            installed.append(label)
            continue
        if is_dry_run:
            installed.append(label)
            continue
        result = await run_shell_command(
            {"cmd": ["brew", "install", package], "is_shell": False, "cwd": None, "timeout_seconds": 300.0}
        )
        if result["is_successful"]:
            installed.append(label)

    # Poetry official installer if command missing.
    if has_command("poetry"):
        installed.append("poetry")
    elif is_dry_run:
        installed.append("poetry")
    else:
        installer = await run_shell_command(
            {
                "cmd": "curl -sSL https://install.python-poetry.org | python3 -",
                "is_shell": True,
                "cwd": None,
                "timeout_seconds": 300.0,
            }
        )
        if installer["is_successful"]:
            installed.append("poetry")

    # oh-my-zsh installer (keep typo-friendly label for user request context).
    if Path.home().joinpath(".oh-my-zsh").exists():
        installed.append("oh-my-zsh")
    elif is_dry_run:
        installed.append("oh-my-zsh")
    else:
        ohmyzsh = await run_shell_command(
            {
                "cmd": 'RUNZSH=no CHSH=no KEEP_ZSHRC=yes sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"',
                "is_shell": True,
                "cwd": None,
                "timeout_seconds": 300.0,
            }
        )
        if ohmyzsh["is_successful"]:
            installed.append("oh-my-zsh")

    return installed


async def import_configuration(options: ImportOptions) -> ImportResult:
    """Extract an archive and restore configuration on macOS."""
    archive_path = Path(options.get("archive_path", "")).resolve()
    is_dry_run = options.get("is_dry_run", False)
    yes_to_all = options.get("yes_to_all", False)
    install_tools = options.get("macos_install_tools", True)
    if not archive_path.exists():
        return {
            "is_successful": False,
            "restored_items": [],
            "rollback_path": None,
            "error_message": f"Archive not found: {archive_path}",
        }

    with tempfile.TemporaryDirectory(prefix="osx_migrator_extract_") as tmp_dir:
        staging_dir = Path(tmp_dir)
        with tarfile.open(archive_path, "r:gz") as tar:
            try:
                tar.extractall(path=staging_dir, filter="fully_trusted")
            except TypeError:
                tar.extractall(path=staging_dir)

        manifest_path = staging_dir / "manifest.json"
        if not manifest_path.exists():
            return {
                "is_successful": False,
                "restored_items": [],
                "rollback_path": None,
                "error_message": "Invalid archive: missing manifest.json",
            }

        manifest = json.loads(manifest_path.read_text())
        dotfiles_to_restore = manifest.get("dotfiles_backed_up", [])
        rollback_location = None
        restored_items: list[str] = []

        if dotfiles_to_restore and not is_dry_run:
            rollback_dir = Path.home() / "backups" / f"{DEFAULT_ROLLBACK_PREFIX}_{time.strftime('%Y%m%d_%H%M%S')}"
            rollback_dir.mkdir(parents=True, exist_ok=True)
            _create_rollback_backup(dotfiles_to_restore, rollback_dir)
            rollback_location = str(rollback_dir)

        if dotfiles_to_restore:
            if is_dry_run:
                restored_items.append("dotfiles")
            else:
                restored_count = _restore_dotfiles(staging_dir, dotfiles_to_restore)
                if restored_count > 0:
                    restored_items.append("dotfiles")

        if install_tools and _prompt_user("Install Homebrew + pyenv + poetry + uv + oh-my-zsh?", True, yes_to_all):
            tools = await _install_required_tools(is_dry_run)
            restored_items.extend(f"tool:{name}" for name in tools)

        return {
            "is_successful": True,
            "restored_items": restored_items,
            "rollback_path": rollback_location,
            "error_message": None,
        }
