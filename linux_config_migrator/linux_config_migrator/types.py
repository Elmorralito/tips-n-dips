"""Type definitions and exception schemas for the Linux Configuration Migrator.

This file enforces the Receive an Object, Return an Object (RORO) pattern.
"""

from typing import TypedDict, Optional


# =====================================================================
# Custom Exceptions
# =====================================================================

class MigratorError(Exception):
    """Base exception for all configuration migrator errors."""
    pass


class CommandExecutionError(MigratorError):
    """Raised when a system shell command execution fails."""
    pass


class ArchiveError(MigratorError):
    """Raised when creating or extracting migration backup tarballs fails."""
    pass


class CompatibilityError(MigratorError):
    """Raised when restoring settings on an incompatible system."""
    pass


# =====================================================================
# Structured Types (RORO Pattern Interfaces)
# =====================================================================

class CommandOptions(TypedDict):
    """Configuration options for executing a system command.
    
    Attributes:
        cmd: List of command arguments.
        is_shell: If True, execute via shell interpreter.
        cwd: Directory path to execute the command in.
        timeout_seconds: Optional max runtime.
    """
    cmd: list[str] | str
    is_shell: bool
    cwd: Optional[str]
    timeout_seconds: Optional[float]


class CommandResult(TypedDict):
    """Structured response from executing a system command.
    
    Attributes:
        stdout: Standard output text string.
        stderr: Standard error text string.
        exit_code: Exit status code of the process.
        is_successful: True if command executed with status code 0.
    """
    stdout: str
    stderr: str
    exit_code: int
    is_successful: bool


class ExportOptions(TypedDict):
    """Parameters received by the export execution routine.
    
    Attributes:
        output_dir: Directory where the generated tarball is written.
        is_dry_run: If True, simulate backup without writing files.
        is_silent: If True, suppress console logs.
        include_secrets: If True, backup sensitive SSH/GPG folders.
    """
    output_dir: str
    is_dry_run: bool
    is_silent: bool
    include_secrets: bool


class ExportResult(TypedDict):
    """Response returned by the export execution routine.
    
    Attributes:
        is_successful: True if backup archive is successfully generated.
        archive_path: Complete absolute path to the output tarball.
        manifest: Dictionary containing metadata of what was backed up.
        error_message: Error explanation if the export fails.
    """
    is_successful: bool
    archive_path: Optional[str]
    manifest: Optional[dict]
    error_message: Optional[str]


class ImportOptions(TypedDict):
    """Parameters received by the import execution routine.
    
    Attributes:
        archive_path: Absolute path to the migration backup tarball.
        is_dry_run: If True, preview restoration without modifying active system files.
        is_silent: If True, suppress stdout logging.
        yes_to_all: If True, automatically confirm prompts (non-interactive mode).
    """
    archive_path: str
    is_dry_run: bool
    is_silent: bool
    yes_to_all: bool


class ImportResult(TypedDict):
    """Response returned by the import execution routine.
    
    Attributes:
        is_successful: True if import process completes without fatal errors.
        restored_items: List of components successfully restored.
        rollback_path: Location of previous config backups if files were overwritten.
        error_message: Detailed error string if import fails.
    """
    is_successful: bool
    restored_items: list[str]
    rollback_path: Optional[str]
    error_message: Optional[str]


class ArchiveOptions(TypedDict):
    """Configuration options for archiving and compression tasks.
    
    Attributes:
        source_dir: Directory containing items to compress.
        output_filepath: Output destination path for the tarball.
    """
    source_dir: str
    output_filepath: str


class ArchiveResult(TypedDict):
    """Output results of compressing or extracting processes.
    
    Attributes:
        is_successful: True if operation completed successfully.
        file_count: Number of files packed or extracted.
        size_bytes: Size of the compression archive.
    """
    is_successful: bool
    file_count: int
    size_bytes: int
