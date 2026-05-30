"""Utility functions for command execution and OS/system detection."""

import asyncio
import shutil
import sys

from .logger import log_debug
from .types import CommandExecutionError, CommandOptions, CommandResult


async def run_shell_command(options: CommandOptions) -> CommandResult:
    """Execute a system command asynchronously."""
    cmd = options.get("cmd")
    is_shell = options.get("is_shell", False)
    cwd = options.get("cwd")
    timeout_seconds = options.get("timeout_seconds", 30.0)

    if not cmd:
        raise CommandExecutionError("Invalid command: command cannot be empty.")

    log_debug(f"Executing command: {cmd} (shell={is_shell}, cwd={cwd})")

    try:
        if is_shell:
            cmd_str = " ".join(cmd) if isinstance(cmd, list) else cmd
            process = await asyncio.create_subprocess_shell(
                cmd_str,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
            )
        else:
            cmd_args = cmd.split() if isinstance(cmd, str) else cmd
            process = await asyncio.create_subprocess_exec(
                cmd_args[0],
                *cmd_args[1:],
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
            )

        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(process.communicate(), timeout=timeout_seconds)
        except asyncio.TimeoutError:
            process.kill()
            stdout_bytes, stderr_bytes = await process.communicate()
            return {
                "stdout": stdout_bytes.decode(errors="replace"),
                "stderr": f"TIMEOUT ERROR: Command exceeded {timeout_seconds}s.\n{stderr_bytes.decode(errors='replace')}",
                "exit_code": -1,
                "is_successful": False,
            }

        return {
            "stdout": stdout_bytes.decode(errors="replace").strip(),
            "stderr": stderr_bytes.decode(errors="replace").strip(),
            "exit_code": process.returncode if process.returncode is not None else -1,
            "is_successful": process.returncode == 0,
        }
    except Exception as exc:
        raise CommandExecutionError(f"Execution failed for command {cmd}: {exc}") from exc


def has_command(cmd_name: str) -> bool:
    """Return True when command exists in PATH."""
    return shutil.which(cmd_name) is not None


def detect_package_manager() -> str:
    """Detect package manager for the current system."""
    if has_command("apt-get"):
        return "apt"
    if has_command("pacman"):
        return "pacman"
    if has_command("dnf"):
        return "dnf"
    if has_command("brew"):
        return "brew"
    return "unknown"


def detect_os_family() -> str:
    """Best effort OS family detection."""
    if sys.platform.startswith("linux"):
        return "linux"
    if sys.platform == "darwin":
        return "macos"
    return "unknown"
