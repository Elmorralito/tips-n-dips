# Linux Configuration Migrator 🚀

A highly robust, zero-dependency, asynchronous Python utility designed to backup and restore system packages, repositories, desktop settings, cron jobs, and user configuration dotfiles when migrating to a new PC. 

Built entirely with the **Python Standard Library** (`asyncio`, `tarfile`, `argparse`, `pathlib`, `shutil`), this tool is guaranteed to work out-of-the-box on a fresh OS installation without requiring any bootstrapping or package installs.

---

## Key Features

- **Zero External Dependencies**: Standard library Python only—no `pip` installs required.
- **Asynchronous Execution**: High performance asynchronous package scanning and compression utilizing `asyncio`.
- **Intelligent Package Delta Analysis**: On restoration, the migrator scans your target system and calculates *exactly* which packages, flatpaks, and snaps are missing, prompting you to install only what you need.
- **Safety Rollback Engine**: Automatically archives any conflicting configurations into a designated backup directory (e.g., `~/backups/import_rollback_<timestamp>`) before importing, enabling 100% safe rollbacks.
- **Desktop Environment Adaptability**: Gracefully skip settings (like GNOME `dconf` configurations) if restoring on a different or headless environment.
- **Granular Security Controls**: Excludes highly sensitive secret keys (`.ssh/config`, `.gnupg`, etc.) by default, with an explicit opt-in `--include-secrets` CLI flag for power users.

---

## What We Migrate

| Component | Description | Export Method |
| :--- | :--- | :--- |
| **System Packages** | Manually installed APT (Debian/Ubuntu), Pacman (Arch), or DNF (Fedora) packages. | `apt-mark showmanual` / `pacman -Qqe` / `dnf repoquery --userinstalled` |
| **Third-Party Repos** | Saved external package repositories (Ubuntu sources). | Copies files from `/etc/apt/sources.list.d/` |
| **Flatpak Apps** | Installed Flatpak application IDs. | `flatpak list --app --columns=application` |
| **Snap Apps** | Installed snap application IDs. | `snap list` |
| **Desktop Settings** | GNOME shell settings, terminal profiles, layouts, and keyboard shortcuts. | `dconf dump /` |
| **Cron Jobs** | User cron automations. | `crontab -l` |
| **User Dotfiles** | Standard config directories like `.config/nvim`, `.config/git`, shell profiles (`.bashrc`, `.zshrc`), and editor environments. | Secure hierarchical copy relative to `~/` |

---

## Installation & Setup

1. Copy the `linux_config_migrator` directory onto your machine.
2. The script can be run directly using the bash launcher or Python module:

```bash
# Using the Bash Launcher (Recommended)
./run.sh --help

# Or run directly via Python 3 module syntax
python3 -m linux_config_migrator --help
```

---

## Command Reference

### 1. Exporting Configurations (Backup)

Create a compressed tarball of your system configuration.

```bash
# Export configs into the current folder
./run.sh export

# Export configs to a specific target folder
./run.sh export --output-dir /path/to/backup_folder

# Export standard configurations AND sensitive keys (SSH/GPG/AWS credentials)
./run.sh export --include-secrets

# Dry-run (Preview what files and categories will be archived)
./run.sh export --dry-run
```

The export command will generate an archive named in the format:  
`system_migration_backup_<hostname>_<date_time>.tar.gz`

### 2. Importing Configurations (Restore)

Extract and restore your packages and configurations on your new machine.

```bash
# Dry-run restoration (Preview what will be overwritten and what packages are missing)
./run.sh import --archive ./system_migration_backup_oldpc_20260528.tar.gz --dry-run

# Restore interactively (Recommended)
./run.sh import --archive ./system_migration_backup_oldpc_20260528.tar.gz

# Automated restoration (Answer 'Yes' to all prompts automatically)
./run.sh import --archive ./system_migration_backup_oldpc_20260528.tar.gz --yes
```

---

## Safety & Rollbacks

If a migration restoration accidentally overwrites a shell config or Neovim setup that you wanted to keep, don't worry! 

Every time you run the `import` command:
1. The tool identifies all conflicting configuration files.
2. It copies your current configuration items to a designated directory under `~/backups/import_rollback_<timestamp>/`.
3. It then safely extracts the migration archive files over the home directory.

To undo an import, simply copy the contents of the generated rollback folder back to your home directory:

```bash
# Example Rollback Restore
cp -r ~/backups/import_rollback_20260528_153000/. ~
```

---

## File Structure of Staging Workspace

The exported archive packs the stage directory in the following layout:

```text
├── manifest.json            # Migration details (source OS, hostname, included components, file index)
├── packages/
│   ├── system_packages.txt  # Native package selections list
│   ├── apt_sources/         # Copied external apt repository entries
│   ├── flatpak_packages.txt # List of Flatpak app IDs
│   └── snap_packages.txt    # List of Snap app IDs
├── desktop/
│   └── dconf_dump.ini       # Gnome/dconf shell settings
├── cron/
│   └── crontab.txt          # Exported user crontab schedule
└── dotfiles/                # Hierarchical mirror of your back-up configuration files
    ├── .bashrc
    ├── .zshrc
    └── .config/
        ├── nvim/
        └── git/
```

---

## Architectural Guidelines Compliance (`python-cybersec.md`)

This utility adheres strictly to defensive secure-coding standards:
- **Input Sanitization**: External commands are invoked as argument lists avoiding shell spawns, eliminating shell injection vulnerabilities.
- **RORO (Receive an Object, Return an Object)**: Functions receive standardized `TypedDict` configs and return structured output dictionaries for high developer predictability.
- **No Classes**: The entire workspace is functional, declarative, and modular.
- **Deep Guard Clauses**: Quick returns on errors and structural validation prevent nested conditional traps and race conditions.
