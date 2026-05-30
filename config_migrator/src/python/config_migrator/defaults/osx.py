"""Configuration defaults for the macOS Configuration Migrator."""

from typing import Final

DEFAULT_DOTFILES: Final[list[str]] = [
    ".zshrc",
    ".zprofile",
    ".zshenv",
    ".p10k.zsh",
    ".gitconfig",
    ".config/nvim",
    ".config/git",
    ".config/gh",
    ".config/tmux",
    ".tmux.conf",
]

DEFAULT_SECRETS: Final[list[str]] = [
    # High-risk secrets are opt-in only via --include-secrets.
    # These folders can contain private keys, cloud credentials, and host trust data.
    ".ssh",
    ".gnupg",
    ".aws",
]

DEFAULT_ARCHIVE_PREFIX: Final[str] = "osx_migration_backup"
DEFAULT_ROLLBACK_PREFIX: Final[str] = "osx_import_rollback"
