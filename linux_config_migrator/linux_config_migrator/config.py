"""Configuration defaults and settings for the Linux Configuration Migrator."""

import os
from typing import Final

# Default list of dotfiles and configuration directories relative to the user's home folder.
# These will be backed up during a standard backup.
DEFAULT_DOTFILES: Final[list[str]] = [
    # Shell configuration files
    ".bashrc",
    ".bash_aliases",
    ".bash_profile",
    ".bash_logout",
    ".profile",
    ".zshrc",
    ".zshenv",
    ".zprofile",
    ".zlogin",
    ".zlogout",
    ".zsh_aliases",
    ".zshrc_aliases",
    ".p10k.zsh",
    ".inputrc",
    
    # Modern terminal and multiplexer configurations
    ".config/alacritty",
    ".config/kitty",
    ".config/tmux",
    ".tmux.conf",
    
    # Core developer tools and editors
    ".config/nvim",
    ".config/git",
    ".gitconfig",
    ".config/fish",
    ".config/gh",
    ".config/mise",
    ".config/rtx",
    ".config/htop",
    
    # User-level service configurations
    ".config/systemd/user",
]

# Sensitive credentials and secret key configurations.
# These will ONLY be backed up if the explicit --include-secrets flag is enabled.
DEFAULT_SECRETS: Final[list[str]] = [
    ".ssh/config",
    ".ssh/authorized_keys",
    ".ssh/known_hosts",
    ".gnupg",
    ".aws/credentials",
    ".aws/config",
]

# Default backup archive name prefix.
DEFAULT_ARCHIVE_PREFIX: Final[str] = "system_migration_backup"

# Default subdirectory name for local rollbacks.
DEFAULT_ROLLBACK_PREFIX: Final[str] = "import_rollback"
