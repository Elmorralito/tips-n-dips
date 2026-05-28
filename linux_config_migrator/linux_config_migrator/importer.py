"""Asynchronous configuration import and restoration engine for the Linux Configuration Migrator.

Enforces deep safety guardrails, auto-rollback backups, compatibility checks, and RORO.
"""

import asyncio
import json
import os
import shutil
import sys
import tarfile
import tempfile
import time
from pathlib import Path
from typing import Optional, Any

from .config import DEFAULT_ROLLBACK_PREFIX
from .types import (
    ImportOptions,
    ImportResult,
    CommandOptions,
    CompatibilityError,
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


def _create_rollback_backup(dotfiles_backed_up: list[str], rollback_dir: Path) -> int:
    """Creates a local safety backup of conflicting active configuration files.
    
    Args:
        dotfiles_backed_up: List of dotfile paths relative to home that will be overwritten.
        rollback_dir: Local path where backups will be securely stored.
        
    Returns:
        The count of files successfully backed up.
    """
    home = Path.home()
    backed_up_count = 0
    
    for item in dotfiles_backed_up:
        local_path = home / item
        if not local_path.exists():
            continue
            
        dest_path = rollback_dir / item
        try:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            if local_path.is_file():
                if local_path.is_symlink():
                    link_target = os.readlink(local_path)
                    os.symlink(link_target, dest_path)
                else:
                    shutil.copy2(local_path, dest_path)
                backed_up_count += 1
                
            elif local_path.is_dir():
                shutil.copytree(local_path, dest_path, symlinks=True, dirs_exist_ok=True)
                backed_up_count += 1
                
        except Exception as exc:
            log_warning(f"Could not create safety rollback backup for '{item}': {exc}")
            
    return backed_up_count


def _restore_dotfiles(extracted_staging: Path, dotfiles_backed_up: list[str]) -> int:
    """Restores the dotfiles from extracted staging into the active home directory.
    
    Args:
        extracted_staging: Temporary location of extracted archive.
        dotfiles_backed_up: List of dotfile paths to copy.
        
    Returns:
        Count of items successfully restored.
    """
    home = Path.home()
    src_dotfiles_dir = extracted_staging / "dotfiles"
    restored_count = 0
    
    for item in dotfiles_backed_up:
        src_path = src_dotfiles_dir / item
        if not src_path.exists():
            continue
            
        dest_path = home / item
        try:
            # Recreate parent folders if necessary
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Remove current target to clean overwrite
            if dest_path.is_file() or dest_path.is_symlink():
                dest_path.unlink()
            elif dest_path.is_dir():
                shutil.rmtree(dest_path)
                
            # Copy new item
            if src_path.is_file():
                if src_path.is_symlink():
                    link_target = os.readlink(src_path)
                    os.symlink(link_target, dest_path)
                else:
                    shutil.copy2(src_path, dest_path)
                restored_count += 1
                
            elif src_path.is_dir():
                shutil.copytree(src_path, dest_path, symlinks=True, dirs_exist_ok=True)
                restored_count += 1
                
        except Exception as exc:
            log_error(f"Failed to restore configuration item '{item}': {exc}")
            
    return restored_count


async def _get_missing_system_packages(extracted_staging: Path, pm: str) -> list[str]:
    """Scans system to determine which backed up packages are currently missing."""
    backup_file = extracted_staging / "packages" / "system_packages.txt"
    if not backup_file.exists():
        return []
        
    try:
        backup_pkgs = {line.strip() for line in backup_file.read_text().splitlines() if line.strip()}
    except Exception:
        return []
        
    current_pkgs = set()
    try:
        if pm == "apt":
            result = await run_shell_command({
                "cmd": ["apt-mark", "showmanual"],
                "is_shell": False,
                "cwd": None,
                "timeout_seconds": 15.0
            })
            if result["is_successful"]:
                current_pkgs = {line.strip() for line in result["stdout"].splitlines() if line.strip()}
                
        elif pm == "pacman":
            result = await run_shell_command({
                "cmd": ["pacman", "-Qqe"],
                "is_shell": False,
                "cwd": None,
                "timeout_seconds": 15.0
            })
            if result["is_successful"]:
                current_pkgs = {line.strip() for line in result["stdout"].splitlines() if line.strip()}
                
        elif pm == "dnf":
            result = await run_shell_command({
                "cmd": ["dnf", "repoquery", "--userinstalled"],
                "is_shell": False,
                "cwd": None,
                "timeout_seconds": 30.0
            })
            if result["is_successful"]:
                current_pkgs = {line.strip() for line in result["stdout"].splitlines() if line.strip()}
    except Exception as exc:
        log_warning(f"Could not retrieve current package list for delta analysis: {exc}")
        
    # Return difference
    return sorted(list(backup_pkgs - current_pkgs))


async def _get_missing_flatpaks(extracted_staging: Path) -> list[str]:
    """Retrieves list of Flatpaks in backup not currently installed on this system."""
    backup_file = extracted_staging / "packages" / "flatpak_packages.txt"
    if not backup_file.exists() or not has_command("flatpak"):
        return []
        
    try:
        backup_apps = {line.strip() for line in backup_file.read_text().splitlines() if line.strip()}
    except Exception:
        return []
        
    try:
        result = await run_shell_command({
            "cmd": ["flatpak", "list", "--app", "--columns=application"],
            "is_shell": False,
            "cwd": None,
            "timeout_seconds": 10.0
        })
        if result["is_successful"]:
            current_apps = {line.strip() for line in result["stdout"].splitlines() if line.strip() and "Application ID" not in line}
            return sorted(list(backup_apps - current_apps))
    except Exception:
        pass
        
    return sorted(list(backup_apps))


async def _get_missing_snaps(extracted_staging: Path) -> list[str]:
    """Retrieves list of Snaps in backup not currently installed on this system."""
    backup_file = extracted_staging / "packages" / "snap_packages.txt"
    if not backup_file.exists() or not has_command("snap"):
        return []
        
    try:
        backup_snaps = {line.strip() for line in backup_file.read_text().splitlines() if line.strip()}
    except Exception:
        return []
        
    try:
        result = await run_shell_command({
            "cmd": "snap list | tail -n +2 | awk '{print $1}'",
            "is_shell": True,
            "cwd": None,
            "timeout_seconds": 10.0
        })
        if result["is_successful"]:
            current_snaps = {line.strip() for line in result["stdout"].splitlines() if line.strip()}
            # Ignore core systems
            ignore_list = {"core", "core18", "core20", "core22", "core24", "snapd", "bare", "gtk-common-themes", "gnome-3-38-2004", "gnome-46-2404", "mesa-2404"}
            filtered_backup = {s for s in backup_snaps if s not in ignore_list}
            filtered_current = {s for s in current_snaps if s not in ignore_list}
            return sorted(list(filtered_backup - filtered_current))
    except Exception:
        pass
        
    return sorted(list(backup_snaps))


def _prompt_user(prompt: str, default: bool, yes_to_all: bool) -> bool:
    """Prompt the user for a yes/no decision, respecting interactive boundaries."""
    if yes_to_all:
        return True
        
    # Check if standard input is interactive
    if not sys.stdin.isatty():
        log_debug("Non-interactive terminal detected: returning default value.")
        return default
        
    choice_suffix = " [Y/n]: " if default else " [y/N]: "
    try:
        response = input(f"{prompt}{choice_suffix}").strip().lower()
        if not response:
            return default
        return response in ("y", "yes")
    except (KeyboardInterrupt, EOFError):
        print()
        return False


async def import_configuration(options: ImportOptions) -> ImportResult:
    """Extracts, validates, and restores configurations on the target system.
    
    Adheres strictly to the RORO design pattern and provides rollback capabilities.
    
    Args:
        options: A TypedDict containing import options (archive_path, dry_run, etc).
        
    Returns:
        An ImportResult object summarizing the restoration action.
    """
    archive_path_str = options.get("archive_path")
    is_dry_run = options.get("is_dry_run", False)
    is_silent = options.get("is_silent", False)
    yes_to_all = options.get("yes_to_all", False)

    # 1. Guard Clause: Check if backup file is provided and exists
    if not archive_path_str:
        err_msg = "Fatal: Missing archive file path parameter."
        if not is_silent:
            log_error(err_msg)
        return {"is_successful": False, "restored_items": [], "rollback_path": None, "error_message": err_msg}
        
    archive_path = Path(archive_path_str).resolve()
    if not archive_path.exists():
        err_msg = f"Fatal: Migration backup archive not found at path: {archive_path}"
        if not is_silent:
            log_error(err_msg)
        return {"is_successful": False, "restored_items": [], "rollback_path": None, "error_message": err_msg}

    if not is_silent:
        log_info(f"Initiating configuration restoration process from archive: {archive_path.name}")
        if is_dry_run:
            log_info("DRY-RUN MODE ACTIVE. No system changes will be executed.")

    # 2. Extract Archive to Temporary Workspace
    restored_components = []
    rollback_location = None
    
    with tempfile.TemporaryDirectory(prefix="migrator_extract_") as temp_dir_str:
        staging_dir = Path(temp_dir_str)
        
        try:
            with tarfile.open(archive_path, "r:gz") as tar:
                try:
                    tar.extractall(path=staging_dir, filter="fully_trusted")
                except TypeError:
                    # Fallback for Python versions < 3.12 that do not support the 'filter' parameter
                    tar.extractall(path=staging_dir)
        except Exception as exc:
            err_msg = f"Could not extract backup archive: {exc}"
            if not is_silent:
                log_error(err_msg)
            return {"is_successful": False, "restored_items": [], "rollback_path": None, "error_message": err_msg}
            
        manifest_path = staging_dir / "manifest.json"
        if not manifest_path.exists():
            err_msg = "Fatal: Invalid backup archive structure. manifest.json missing."
            if not is_silent:
                log_error(err_msg)
            return {"is_successful": False, "restored_items": [], "rollback_path": None, "error_message": err_msg}
            
        try:
            manifest = json.loads(manifest_path.read_text())
        except Exception as exc:
            err_msg = f"Fatal: Manifest file is malformed: {exc}"
            if not is_silent:
                log_error(err_msg)
            return {"is_successful": False, "restored_items": [], "rollback_path": None, "error_message": err_msg}

        # 3. Perform OS and Compatibility Assessments
        source_pm = manifest.get("package_manager", "unknown")
        target_pm = detect_package_manager()
        
        if not is_silent:
            log_info(f"Backup Source Information:")
            print(f"  - Hostname:   {manifest.get('hostname')}")
            print(f"  - OS Version: {manifest.get('os_distribution')} {manifest.get('os_version')}")
            print(f"  - Timestamp:  {manifest.get('timestamp')}")
            print(f"  - Packages:   {source_pm}")
            
        is_pm_compatible = (source_pm == target_pm) and (source_pm != "unknown")
        
        if not is_pm_compatible and not is_silent:
            log_warning(f"Warning: Destination package manager '{target_pm}' differs from backup source manager '{source_pm}'.")
            log_warning("Native system packages from backup cannot be installed automatically. Skipping native packages.")

        # 4. Generate Local Rollback Backup
        dotfiles_to_restore = manifest.get("dotfiles_backed_up", [])
        if dotfiles_to_restore and not is_dry_run:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            rollback_path = Path.home() / "backups" / f"{DEFAULT_ROLLBACK_PREFIX}_{timestamp}"
            rollback_location = str(rollback_path)
            
            if not is_silent:
                log_info(f"Creating dated safety rollback directory: {rollback_path}")
            
            rollback_path.mkdir(parents=True, exist_ok=True)
            copied_count = _create_rollback_backup(dotfiles_to_restore, rollback_path)
            
            if copied_count > 0:
                if not is_silent:
                    log_success(f"Backed up {copied_count} existing configuration items to protect active configs.")
            else:
                # Clean empty rollback dir if nothing was backed up
                try:
                    rollback_path.rmdir()
                    rollback_location = None
                except OSError:
                    pass

        # 5. Restore Dotfiles
        if dotfiles_to_restore:
            if not is_silent:
                log_info(f"Restoring {len(dotfiles_to_restore)} dotfiles and directories into home directory...")
            
            if is_dry_run:
                if not is_silent:
                    log_success(f"[DRY-RUN] Would restore: {', '.join(dotfiles_to_restore)}")
                restored_components.append("dotfiles")
            else:
                restored_count = _restore_dotfiles(staging_dir, dotfiles_to_restore)
                if restored_count > 0:
                    if not is_silent:
                        log_success(f"Successfully restored {restored_count} files/folders into your home directory.")
                    restored_components.append("dotfiles")
                else:
                    log_warning("No dotfiles were restored successfully.")
        
        # 6. Restore GNOME Desktop configurations (dconf)
        has_desktop = manifest.get("has_desktop_settings", False)
        dconf_src = staging_dir / "desktop" / "dconf_dump.ini"
        if has_desktop and dconf_src.exists():
            if has_command("dconf"):
                is_approved = _prompt_user("Restore GNOME shell/desktop theme and settings?", True, yes_to_all)
                if is_approved:
                    if is_dry_run:
                        if not is_silent:
                            log_success("[DRY-RUN] Would restore GNOME settings via: dconf load / < dconf_dump.ini")
                        restored_components.append("desktop_settings")
                    else:
                        if not is_silent:
                            log_info("Restoring GNOME dconf settings...")
                        try:
                            # Safely feed file to stdin
                            with open(dconf_src, "r") as file_in:
                                content = file_in.read()
                                
                            process = await asyncio.create_subprocess_exec(
                                "dconf", "load", "/",
                                stdin=asyncio.subprocess.PIPE,
                                stdout=asyncio.subprocess.PIPE,
                                stderr=asyncio.subprocess.PIPE
                            )
                            stdout, stderr = await process.communicate(input=content.encode())
                            
                            if process.returncode == 0:
                                if not is_silent:
                                    log_success("GNOME desktop configurations successfully restored.")
                                restored_components.append("desktop_settings")
                            else:
                                log_error(f"Failed to load dconf settings: {stderr.decode()}")
                        except Exception as exc:
                            log_error(f"Exception during dconf restoration: {exc}")
            else:
                if not is_silent:
                    log_warning("Desktop settings in backup skipped (dconf utility is not available on target).")

        # 7. Restore Crontabs
        has_cron = manifest.get("has_cron_jobs", False)
        cron_src = staging_dir / "cron" / "crontab.txt"
        if has_cron and cron_src.exists():
            if has_command("crontab"):
                is_approved = _prompt_user("Restore custom cron jobs?", False, yes_to_all)
                if is_approved:
                    if is_dry_run:
                        if not is_silent:
                            log_success("[DRY-RUN] Would restore crontab via: crontab < crontab.txt")
                        restored_components.append("cron_jobs")
                    else:
                        if not is_silent:
                            log_info("Restoring user crontab settings...")
                        try:
                            with open(cron_src, "r") as file_in:
                                content = file_in.read()
                                
                            process = await asyncio.create_subprocess_exec(
                                "crontab", "-",
                                stdin=asyncio.subprocess.PIPE,
                                stdout=asyncio.subprocess.PIPE,
                                stderr=asyncio.subprocess.PIPE
                            )
                            stdout, stderr = await process.communicate(input=content.encode())
                            
                            if process.returncode == 0:
                                if not is_silent:
                                    log_success("Crontabs successfully imported.")
                                restored_components.append("cron_jobs")
                            else:
                                log_error(f"Failed to load crontab settings: {stderr.decode()}")
                        except Exception as exc:
                            log_error(f"Exception during crontab restoration: {exc}")
            else:
                if not is_silent:
                    log_warning("Cron configurations in backup skipped (crontab utility not available).")

        # 8. Restore System Packages, Flatpaks, and Snaps
        # Evaluate deltas to only suggest missing packages
        if not is_silent:
            log_info("Scanning active system installations to compute differences...")
            
        # 8a. System packages
        if is_pm_compatible:
            missing_system = await _get_missing_system_packages(staging_dir, target_pm)
            if missing_system:
                if not is_silent:
                    log_warning(f"Identified {len(missing_system)} system packages that are missing on this PC.")
                    print(f"  Missing: {', '.join(missing_system[:15])}" + (f", and {len(missing_system)-15} more..." if len(missing_system) > 15 else ""))
                
                # We ask if they want to install them
                is_approved = _prompt_user(f"Would you like to install the {len(missing_system)} missing native packages?", False, yes_to_all)
                if is_approved:
                    install_cmd = []
                    if target_pm == "apt":
                        install_cmd = ["sudo", "apt", "install", "-y"] + missing_system
                    elif target_pm == "pacman":
                        install_cmd = ["sudo", "pacman", "-S", "--noconfirm"] + missing_system
                    elif target_pm == "dnf":
                        install_cmd = ["sudo", "dnf", "install", "-y"] + missing_system
                        
                    if install_cmd:
                        if is_dry_run:
                            if not is_silent:
                                log_success(f"[DRY-RUN] Would execute: {' '.join(install_cmd)}")
                            restored_components.append("system_packages")
                        else:
                            if not is_silent:
                                log_info(f"Executing: {' '.join(install_cmd)}")
                            # Set up subprocess to pipe output interactively to user console
                            try:
                                proc = await asyncio.create_subprocess_exec(*install_cmd)
                                await proc.wait()
                                if proc.returncode == 0:
                                    if not is_silent:
                                        log_success("Missing system packages successfully installed.")
                                    restored_components.append("system_packages")
                                else:
                                    log_error(f"Package installer returned failure code: {proc.returncode}")
                            except Exception as exc:
                                log_error(f"Failed to execute package installer: {exc}")
            else:
                if not is_silent:
                    log_success("All native packages from backup are already installed on this machine.")

        # 8b. Flatpaks
        missing_flatpaks = await _get_missing_flatpaks(staging_dir)
        if missing_flatpaks:
            if not is_silent:
                log_warning(f"Found {len(missing_flatpaks)} Flatpaks missing on this system.")
                print(f"  Missing Flatpaks: {', '.join(missing_flatpaks)}")
                
            is_approved = _prompt_user(f"Install the {len(missing_flatpaks)} missing Flatpaks?", False, yes_to_all)
            if is_approved:
                # Install each flatpak
                for flatpak_id in missing_flatpaks:
                    flatpak_cmd = ["flatpak", "install", "-y", "flathub", flatpak_id]
                    if is_dry_run:
                        if not is_silent:
                            log_success(f"[DRY-RUN] Would install Flatpak: {' '.join(flatpak_cmd)}")
                        restored_components.append(f"flatpak:{flatpak_id}")
                    else:
                        if not is_silent:
                            log_info(f"Installing Flatpak: {flatpak_id}...")
                        try:
                            proc = await asyncio.create_subprocess_exec(*flatpak_cmd)
                            await proc.wait()
                            if proc.returncode == 0:
                                restored_components.append(f"flatpak:{flatpak_id}")
                            else:
                                log_error(f"Flatpak failed to install application '{flatpak_id}'.")
                        except Exception as exc:
                            log_error(f"Failed to run Flatpak installer: {exc}")

        # 8c. Snaps
        missing_snaps = await _get_missing_snaps(staging_dir)
        if missing_snaps:
            if not is_silent:
                log_warning(f"Found {len(missing_snaps)} Snaps missing on this system.")
                print(f"  Missing Snaps: {', '.join(missing_snaps)}")
                
            is_approved = _prompt_user(f"Install the {len(missing_snaps)} missing Snaps?", False, yes_to_all)
            if is_approved:
                for snap_id in missing_snaps:
                    snap_cmd = ["sudo", "snap", "install", snap_id]
                    if is_dry_run:
                        if not is_silent:
                            log_success(f"[DRY-RUN] Would install Snap: {' '.join(snap_cmd)}")
                        restored_components.append(f"snap:{snap_id}")
                    else:
                        if not is_silent:
                            log_info(f"Installing Snap: {snap_id}...")
                        try:
                            proc = await asyncio.create_subprocess_exec(*snap_cmd)
                            await proc.wait()
                            if proc.returncode == 0:
                                restored_components.append(f"snap:{snap_id}")
                            else:
                                log_error(f"Snap failed to install application '{snap_id}'.")
                        except Exception as exc:
                            log_error(f"Failed to run Snap installer: {exc}")

        if not is_silent:
            log_success("Restoration cycle completed successfully.")
            if rollback_location:
                log_success(f"Rollback files are stored at: {rollback_location}")
                
        return {
            "is_successful": True,
            "restored_items": restored_components,
            "rollback_path": rollback_location,
            "error_message": None
        }
