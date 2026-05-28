"""Unit tests for the Linux Configuration Migrator utility module.

Designed with robust async mocks to eliminate OS side-effects and test edge cases.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from linux_config_migrator.linux_config_migrator.types import CommandExecutionError
from linux_config_migrator.linux_config_migrator.utils import (
    detect_package_manager,
    has_command,
    run_shell_command,
)


@pytest.mark.asyncio
async def test_run_shell_command_success_exec() -> None:
    """Test nominal success of run_shell_command using exec (non-shell mode).
    
    Verifies that commands are passed as lists and outputs are parsed correctly.
    """
    # Arrange: Mock the process object returned by create_subprocess_exec
    mock_process = MagicMock()
    mock_process.communicate = AsyncMock(return_value=(b"my_package\nanother_pkg\n", b""))
    mock_process.returncode = 0
    
    with patch("asyncio.create_subprocess_exec", AsyncMock(return_value=mock_process)) as mock_exec:
        options = {
            "cmd": ["apt-mark", "showmanual"],
            "is_shell": False,
            "cwd": "/tmp",
            "timeout_seconds": 10.0
        }
        
        # Act
        result = await run_shell_command(options)
        
        # Assert
        assert result["is_successful"] is True
        assert result["exit_code"] == 0
        assert result["stdout"] == "my_package\nanother_pkg"
        assert result["stderr"] == ""
        mock_exec.assert_called_once_with(
            "apt-mark", "showmanual",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd="/tmp"
        )


@pytest.mark.asyncio
async def test_run_shell_command_success_shell() -> None:
    """Test nominal success of run_shell_command using a shell string.
    
    Ensures shell string commands are piped correctly.
    """
    mock_process = MagicMock()
    mock_process.communicate = AsyncMock(return_value=(b"pkg_1\npkg_2\n", b""))
    mock_process.returncode = 0
    
    with patch("asyncio.create_subprocess_shell", AsyncMock(return_value=mock_process)) as mock_shell:
        options = {
            "cmd": "snap list | awk '{print $1}'",
            "is_shell": True,
            "cwd": None,
            "timeout_seconds": 5.0
        }
        
        # Act
        result = await run_shell_command(options)
        
        # Assert
        assert result["is_successful"] is True
        assert result["stdout"] == "pkg_1\npkg_2"
        mock_shell.assert_called_once_with(
            "snap list | awk '{print $1}'",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=None
        )


@pytest.mark.asyncio
async def test_run_shell_command_timeout() -> None:
    """Test boundary edge case where a subprocess execution times out.
    
    Verifies that the process is safely terminated and reports a timeout.
    """
    mock_process = MagicMock()
    mock_process.communicate = AsyncMock(side_effect=asyncio.TimeoutError())
    mock_process.kill = MagicMock()
    
    # communicate is called again during kill phase
    mock_process.communicate = AsyncMock(
        side_effect=[asyncio.TimeoutError(), (b"", b"Terminated due to timeout")]
    )
    mock_process.returncode = -1
    
    with patch("asyncio.create_subprocess_exec", AsyncMock(return_value=mock_process)):
        options = {
            "cmd": ["sleep", "10"],
            "is_shell": False,
            "cwd": None,
            "timeout_seconds": 0.1
        }
        
        # Act
        result = await run_shell_command(options)
        
        # Assert
        assert result["is_successful"] is False
        assert result["exit_code"] == -1
        assert "TIMEOUT ERROR" in result["stderr"]
        mock_process.kill.assert_called_once()


@pytest.mark.asyncio
async def test_run_shell_command_invalid_input() -> None:
    """Test invalid input behavior when command is empty.
    
    Ensures a CommandExecutionError is raised.
    """
    options = {
        "cmd": [],
        "is_shell": False,
        "cwd": None,
        "timeout_seconds": 10.0
    }
    
    # Act & Assert
    with pytest.raises(CommandExecutionError) as exc_info:
        await run_shell_command(options)
        
    assert "Invalid target command" in str(exc_info.value)


@pytest.mark.asyncio
async def test_run_shell_command_os_error() -> None:
    """Test failure state when internal OS execution exception occurs.
    
    Ensures custom CommandExecutionError is cleanly raised.
    """
    with patch("asyncio.create_subprocess_exec", AsyncMock(side_effect=OSError("Permission denied"))):
        options = {
            "cmd": ["unprivileged_bin"],
            "is_shell": False,
            "cwd": None,
            "timeout_seconds": 10.0
        }
        
        # Act & Assert
        with pytest.raises(CommandExecutionError) as exc_info:
            await run_shell_command(options)
            
        assert "System execution failed" in str(exc_info.value)


def test_detect_package_manager_apt() -> None:
    """Test package manager identification logic when apt-get is present."""
    with patch("shutil.which", side_effect=lambda name: "/usr/bin/apt-get" if name == "apt-get" else None):
        pm = detect_package_manager()
        assert pm == "apt"


def test_detect_package_manager_pacman() -> None:
    """Test package manager identification logic when pacman is present."""
    with patch("shutil.which", side_effect=lambda name: "/usr/bin/pacman" if name == "pacman" else None):
        pm = detect_package_manager()
        assert pm == "pacman"


def test_detect_package_manager_unknown() -> None:
    """Test fallback package manager identification logic when none match."""
    with patch("shutil.which", return_value=None):
        pm = detect_package_manager()
        assert pm == "unknown"


def test_has_command_checks() -> None:
    """Test command existence checking wrapper."""
    with patch("shutil.which", side_effect=lambda name: "/usr/bin/curl" if name == "curl" else None):
        assert has_command("curl") is True
        assert has_command("wget") is False
