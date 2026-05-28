"""Asynchronous configuration backup engine for the Linux Configuration Migrator.

Designed with robust guard clauses, RORO interfaces, and modular subprocess calls.
"""

import asyncio
import json
import os
import platform
import shutil
import tempfile
import time
from pathlib import Path
from typing import Optional, Any

from .config import (
    DEFAULT_DOTFILES,
    DEFAULT_SECRETS,
    DEFAULT_ARCHIVE_PREFIX,
)
from .types import (
    ExportOptions,
    ExportResult,
    CommandOptions,
    ArchiveError,
)
from .utils import (
    log_info,
    log_success,
    log_warning,
    log_error,
    log_debug,
    run_shell_command,
    detect_package_manager,
    has_command,
)


async def _export_system_packages(staging_dir: Path) -> dict[str, Any]:
    """Helper to query the system and export installed package configurations.
    
    Returns:
        A dictionary containing statuses of the different package exports.
    """
    pkg_dir = staging_dir / "packages"
    pkg_dir.mkdir(parents=True, exist_ok=True)
    
    pm = detect_package_manager()
    status = {"package_manager": pm, "system_packages": False, "repositories": False, "flatpak": False, "snap": False}
    
    # 1. Primary Package Manager
    try:
        if pm == "apt":
            result = await run_shell_command({
                "cmd": ["apt-mark", "showmanual"],
                "is_shell": False,
                "cwd": None,
                "timeout_seconds": 15.0
            })
            if result["is_successful"]:
                (pkg_dir / "system_packages.txt").write_text(result["stdout"])
                status["system_packages"] = True
                
                # Backup repositories
                sources_dir = Path("/etc/apt/sources.list.d")
                if sources_dir.exists():
                    dest_sources = pkg_dir / "apt_sources"
                    dest_sources.mkdir(parents=True, exist_ok=True)
                    for file in sources_dir.glob("*"):
                        if file.is_file():
                            shutil.copy2(file, dest_sources / file.name)
                    status["repositories"] = True
                    
        elif pm == "pacman":
            result = await run_shell_command({
                "cmd": ["pacman", "-Qqe"],
                "is_shell": False,
                "cwd": None,
                "timeout_seconds": 15.0
            })
            if result["is_successful"]:
                (pkg_dir / "system_packages.txt").write_text(result["stdout"])
                status["system_packages"] = True
                
        elif pm == "dnf":
            result = await run_shell_command({
                "cmd": ["dnf", "repoquery", "--userinstalled"],
                "is_shell": False,
                "cwd": None,
                "timeout_seconds": 30.0
            })
            if result["is_successful"]:
                (pkg_dir / "system_packages.txt").write_text(result["stdout"])
                status["system_packages"] = True
    except Exception as exc:
        log_warning(f"Failed to export native system packages: {exc}")

    # 2. Flatpaks
    if has_command("flatpak"):
        try:
            result = await run_shell_command({
                "cmd": ["flatpak", "list", "--app", "--columns=application"],
                "is_shell": False,
                "cwd": None,
                "timeout_seconds": 15.0
            })
            if result["is_successful"]:
                # Filter out header line if present
                lines = [line.strip() for line in result["stdout"].splitlines() if line.strip() and "Application ID" not in line]
                if lines:
                    (pkg_dir / "flatpak_packages.txt").write_text("\n".join(lines))
                    status["flatpak"] = True
        except Exception as exc:
            log_warning(f"Failed to export Flatpak packages: {exc}")

    # 3. Snaps
    if has_command("snap"):
        try:
            result = await run_shell_command({
                "cmd": "snap list | tail -n +2 | awk '{print $1}'",
                "is_shell": True,
                "cwd": None,
                "timeout_seconds": 15.0
            })
            if result["is_successful"] and result["stdout"]:
                (pkg_dir / "snap_packages.txt").write_text(result["stdout"])
                status["snap"] = True
        except Exception as exc:
            log_warning(f"Failed to export Snap packages: {exc}")
            
    return status


async def _export_desktop_settings(staging_dir: Path) -> bool:
    """Helper to dump dconf / GNOME settings if available."""
    desktop_dir = staging_dir / "desktop"
    desktop_dir.mkdir(parents=True, exist_ok=True)
    
    if has_command("dconf"):
        try:
            # Check if we can reach the dconf database
            result = await run_shell_command({
                "cmd": ["dconf", "dump", "/"],
                "is_shell": False,
                "cwd": None,
                "timeout_seconds": 10.0
            })
            if result["is_successful"] and result["stdout"]:
                (desktop_dir / "dconf_dump.ini").write_text(result["stdout"])
                return True
            else:
                log_debug(f"dconf query finished with code {result['exit_code']}: {result['stderr']}")
        except Exception as exc:
            log_debug(f"Skipping dconf backup (could not connect to session DBus): {exc}")
            
    return False


async def _export_cron_jobs(staging_dir: Path) -> bool:
    """Helper to backup user's crontab settings."""
    cron_dir = staging_dir / "cron"
    cron_dir.mkdir(parents=True, exist_ok=True)
    
    if has_command("crontab"):
        try:
            result = await run_shell_command({
                "cmd": ["crontab", "-l"],
                "is_shell": False,
                "cwd": None,
                "timeout_seconds": 10.0
            })
            if result["is_successful"] and result["stdout"]:
                (cron_dir / "crontab.txt").write_text(result["stdout"])
                return True
        except Exception as exc:
            log_debug(f"Crontab export skipped: {exc}")
            
    return False


def _export_dotfiles(staging_dir: Path, include_secrets: bool) -> list[str]:
    """Helper to copy selected config files and dotfiles from home folder.
    
    Returns:
        List of files/folders successfully backed up relative to home.
    """
    home = Path.home()
    dotfiles_dest = staging_dir / "dotfiles"
    dotfiles_dest.mkdir(parents=True, exist_ok=True)
    
    # Compile the final list of target configuration paths
    targets = list(DEFAULT_DOTFILES)
    if include_secrets:
        targets.extend(DEFAULT_SECRETS)
        
    backed_up_items = []
    
    for item in targets:
        src_path = home / item
        if not src_path.exists():
            continue
            
        dest_path = dotfiles_dest / item
        try:
            # Recreate target parent directories if nested
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            if src_path.is_file():
                # Avoid copying absolute symlinks directly; copy contents or symlink
                if src_path.is_symlink():
                    link_target = os.readlink(src_path)
                    os.symlink(link_target, dest_path)
                else:
                    shutil.copy2(src_path, dest_path)
                backed_up_items.append(item)
                
            elif src_path.is_dir():
                shutil.copytree(src_path, dest_path, symlinks=True, dirs_exist_ok=True)
                backed_up_items.append(item)
                
        except Exception as exc:
            log_warning(f"Skipped dotfile '{item}' during copy: {exc}")
            
    return backed_up_items


async def export_configuration(options: ExportOptions) -> ExportResult:
    """Gathers and compresses all OS and user configurations into an archive.
    
    Adheres to the Receive an Object, Return an Object (RORO) pattern.
    
    Args:
        options: A TypedDict containing backup options (output_dir, include_secrets, etc).
        
    Returns:
        An ExportResult containing the success status and location of the backup.
    """
    output_dir_str = options.get("output_dir", "./")
    is_dry_run = options.get("is_dry_run", False)
    is_silent = options.get("is_silent", False)
    include_secrets = options.get("include_secrets", False)

    # 1. Validate Output Directory
    output_path = Path(output_dir_str).resolve()
    if not is_dry_run:
        try:
            output_path.mkdir(parents=True, exist_ok=True)
        except Exception as exc:
            err_msg = f"Cannot create output directory '{output_path}': {exc}"
            if not is_silent:
                log_error(err_msg)
            return {"is_successful": False, "archive_path": None, "manifest": None, "error_message": err_msg}

    if not is_silent:
        log_info(f"Starting Linux configuration export process...")
        if is_dry_run:
            log_info("DRY-RUN MODE ENABLED. No files will be permanently written.")
        if include_secrets:
            log_warning("SECRET EXPORT OPT-IN: Private credentials and keys (SSH/AWS/GPG) will be included.")

    # 2. Setup Staging Workspace
    with tempfile.TemporaryDirectory(prefix="migrator_staging_") as temp_dir_str:
        staging_dir = Path(temp_dir_str)
        
        # 3. Collect Package Manager and Repositories lists
        if not is_silent:
            log_info("Exporting package installations and repositories...")
        pkg_status = await _export_system_packages(staging_dir)
        
        # 4. Collect Gnome Settings
        if not is_silent:
            log_info("Dumping desktop and GNOME configuration...")
        has_desktop_cfg = await _export_desktop_settings(staging_dir)
        
        # 5. Collect Cron Jobs
        if not is_silent:
            log_info("Exporting crontabs...")
        has_cron = await _export_cron_jobs(staging_dir)
        
        # 6. Copy Dotfiles & Config Directories
        if not is_silent:
            log_info("Backing up selected user dotfiles and application configs...")
        copied_dotfiles = _export_dotfiles(staging_dir, include_secrets)
        
        # 7. Generate Manifest metadata
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        hostname = platform.node()
        os_name = "unknown"
        os_version = "unknown"
        
        # Retrieve OS Release details
        os_release = Path("/etc/os-release")
        if os_release.exists():
            try:
                for line in os_release.read_text().splitlines():
                    if line.startswith("NAME="):
                        os_name = line.split("=")[1].strip('"')
                    elif line.startswith("VERSION_ID="):
                        os_version = line.split("=")[1].strip('"')
            except Exception:
                pass
                
        manifest = {
            "version": "1.0",
            "hostname": hostname,
            "timestamp": timestamp,
            "os_distribution": os_name,
            "os_version": os_version,
            "architecture": platform.machine(),
            "has_secrets_included": include_secrets,
            "package_manager": pkg_status["package_manager"],
            "packages_exported": {
                "system": pkg_status["system_packages"],
                "repositories": pkg_status["repositories"],
                "flatpak": pkg_status["flatpak"],
                "snap": pkg_status["snap"],
            },
            "has_desktop_settings": has_desktop_cfg,
            "has_cron_jobs": has_cron,
            "dotfiles_backed_up": copied_dotfiles,
        }
        
        # Write metadata manifest
        manifest_path = staging_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2))
        
        # Guard clause: Check if anything at all was exported
        has_any_backup = (
            pkg_status["system_packages"] 
            or pkg_status["flatpak"] 
            or pkg_status["snap"] 
            or has_desktop_cfg 
            or has_cron 
            or len(copied_dotfiles) > 0
        )
        if not has_any_backup:
            err_msg = "Nothing was exported. No configurations, packages, or crontabs were found on this system."
            if not is_silent:
                log_error(err_msg)
            return {"is_successful": False, "archive_path": None, "manifest": None, "error_message": err_msg}

        # 8. Create compressed tarball
        archive_name = f"{DEFAULT_ARCHIVE_PREFIX}_{hostname}_{timestamp}.tar.gz"
        archive_dest_path = output_path / archive_name
        
        if is_dry_run:
            if not is_silent:
                log_success(f"[DRY-RUN] Would create backup: {archive_dest_path}")
                log_success(f"[DRY-RUN] Manifest data: {json.dumps(manifest, indent=2)}")
            return {
                "is_successful": True,
                "archive_path": str(archive_dest_path),
                "manifest": manifest,
                "error_message": None,
            }
            
        try:
            # We compress staging_dir to archive_dest_path
            # To ensure standard directory structure inside archive, pack relative to staging_dir
            shutil.make_archive(
                str(archive_dest_path.with_suffix("").with_suffix("")),  # strip .tar.gz for make_archive
                "gztar",
                root_dir=staging_dir,
            )
            
            # Since make_archive adds .tar.gz automatically, verify
            if not archive_dest_path.exists():
                raise ArchiveError("Tarball creation failed silently. File not generated.")
                
            if not is_silent:
                log_success(f"Configuration archive successfully generated: {archive_dest_path}")
                log_success(f"Archived {len(copied_dotfiles)} dotfile items and package lists.")
                
            return {
                "is_successful": True,
                "archive_path": str(archive_dest_path),
                "manifest": manifest,
                "error_message": None,
            }
            
        except Exception as exc:
            err_msg = f"Failed to compress backup workspace directory: {exc}"
            if not is_silent:
                log_error(err_msg)
            return {"is_successful": False, "archive_path": None, "manifest": None, "error_message": err_msg}
