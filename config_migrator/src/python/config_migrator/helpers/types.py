"""Shared type definitions and exceptions for config migrator."""

from typing import Optional, TypedDict


class MigratorError(Exception):
    """Base exception for all migrator-specific errors."""


class CommandExecutionError(MigratorError):
    """Raised when command execution fails."""


class ArchiveError(MigratorError):
    """Raised when backup archive operations fail."""


class CompatibilityError(MigratorError):
    """Raised when backup and target systems are incompatible."""


class CommandOptions(TypedDict):
    """Configuration options for command execution."""

    cmd: list[str] | str
    is_shell: bool
    cwd: Optional[str]
    timeout_seconds: Optional[float]


class CommandResult(TypedDict):
    """Structured response from command execution."""

    stdout: str
    stderr: str
    exit_code: int
    is_successful: bool


class ExportOptions(TypedDict, total=False):
    """Parameters accepted by exporters."""

    output_dir: str
    is_dry_run: bool
    is_silent: bool
    include_secrets: bool


class ExportResult(TypedDict):
    """Structured exporter result."""

    is_successful: bool
    archive_path: Optional[str]
    manifest: Optional[dict]
    error_message: Optional[str]


class ImportOptions(TypedDict, total=False):
    """Parameters accepted by importers."""

    archive_path: str
    is_dry_run: bool
    is_silent: bool
    yes_to_all: bool


class ImportResult(TypedDict):
    """Structured importer result."""

    is_successful: bool
    restored_items: list[str]
    rollback_path: Optional[str]
    error_message: Optional[str]
