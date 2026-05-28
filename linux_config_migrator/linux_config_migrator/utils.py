"""Utility functions for shell command execution, logging, and system detection.

Designed with strict sanitization, secure command defaults, and RORO support.
"""

import asyncio
import os
import shutil
import sys
from typing import Optional
from .types import CommandOptions, CommandResult, CommandExecutionError

from .logger import (
    log_info,
    log_success,
    log_warning,
    log_error,
    log_debug,
    set_show_traceback,
    should_show_traceback,
)


async def run_shell_command(options: CommandOptions) -> CommandResult:
    """Execute a system shell command asynchronously with strict safety controls.
    
    Adheres strictly to the Receive an Object, Return an Object (RORO) pattern.
    
    Args:
        options: A TypedDict containing 'cmd', 'is_shell', 'cwd', and 'timeout_seconds'.
        
    Returns:
        A TypedDict containing stdout, stderr, exit_code, and success boolean.
        
    Raises:
        CommandExecutionError: If system execution context fails.
    """
    cmd = options.get("cmd")
    is_shell = options.get("is_shell", False)
    cwd = options.get("cwd")
    timeout_seconds = options.get("timeout_seconds", 30.0)

    # Guard clause: ensure valid command input is provided
    if not cmd:
        raise CommandExecutionError("Invalid target command: Command string/list cannot be empty.")

    log_debug(f"Executing command: {cmd} (shell={is_shell}, cwd={cwd})")

    try:
        if is_shell:
            # If executing via shell, enforce string type
            if isinstance(cmd, list):
                cmd_str = " ".join(cmd)
            else:
                cmd_str = cmd
                
            # Create the subprocess with shell interpreter
            process = await asyncio.create_subprocess_shell(
                cmd_str,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
            )
        else:
            # Safe execution: list of arguments, avoids shell command injections
            if isinstance(cmd, str):
                cmd_args = cmd.split()
            else:
                cmd_args = cmd

            process = await asyncio.create_subprocess_exec(
                cmd_args[0],
                *cmd_args[1:],
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
            )

        # Wait for command completion with timeout limit
        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                process.communicate(), timeout=timeout_seconds
            )
        except asyncio.TimeoutError:
            process.kill()
            stdout_bytes, stderr_bytes = await process.communicate()
            log_warning(f"Command timed out after {timeout_seconds} seconds: {cmd}")
            return {
                "stdout": stdout_bytes.decode(errors="replace"),
                "stderr": f"TIMEOUT ERROR: Command execution exceeded {timeout_seconds}s limit.\n" + stderr_bytes.decode(errors="replace"),
                "exit_code": -1,
                "is_successful": False,
            }

        stdout_decoded = stdout_bytes.decode(errors="replace").strip()
        stderr_decoded = stderr_bytes.decode(errors="replace").strip()
        exit_code = process.returncode if process.returncode is not None else -1
        is_successful = (exit_code == 0)

        return {
            "stdout": stdout_decoded,
            "stderr": stderr_decoded,
            "exit_code": exit_code,
            "is_successful": is_successful,
        }

    except Exception as exc:
        raise CommandExecutionError(f"System execution failed for command {cmd}: {str(exc)}") from exc


def detect_package_manager() -> str:
    """Identify which primary package manager is installed on the current system.
    
    Returns:
        One of 'apt', 'pacman', 'dnf', or 'unknown'.
    """
    if shutil.which("apt-get"):
        return "apt"
    if shutil.which("pacman"):
        return "pacman"
    if shutil.which("dnf"):
        return "dnf"
    return "unknown"


def has_command(cmd_name: str) -> bool:
    """Check if a specific binary command exists in the user's path.
    
    Args:
        cmd_name: Name of the binary utility to look for.
        
    Returns:
        True if the command exists and is executable.
    """
    return shutil.which(cmd_name) is not None
