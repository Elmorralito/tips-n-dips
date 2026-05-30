# Config Migrator

`config_migrator` exports and imports workstation configuration archives across supported OS adapters (`macOS`, `Linux`).

## Quick Start

From repository root:

```bash
bash config_migrator/src/bash/installer.sh install
```

Then verify CLI:

```bash
PYTHONPATH="config_migrator/src/python" python3 -m config_migrator --help
```

## Installer Script (Detailed)

The bootstrap script is:

- `config_migrator/src/bash/installer.sh`

It supports three commands:

- `install` - install runtime dependencies
- `export` - create a migration backup archive
- `import` - restore from a migration archive

### 1) Download the script from repository

Replace `<owner>` and `<repo>` with your GitHub repository location.

Using `curl`:

```bash
curl -fsSL "https://raw.githubusercontent.com/<owner>/<repo>/main/config_migrator/src/bash/installer.sh" -o installer.sh
chmod +x installer.sh
```

Using `wget`:

```bash
wget -q "https://raw.githubusercontent.com/<owner>/<repo>/main/config_migrator/src/bash/installer.sh" -O installer.sh
chmod +x installer.sh
```

### 2) Install dependencies

```bash
./installer.sh install
```

What `install` does:

- Validates expected repo structure for `config_migrator`
- Verifies `python3` is installed (installs if missing)
- On macOS:
  - checks if `brew` exists
  - installs Homebrew if missing
  - installs Python with Homebrew if needed
- On Linux:
  - uses available package manager (`apt-get`, `dnf`, `pacman`) to install Python/pip
- Installs Python package dependencies required by the migrator

### 3) Export a backup

Basic export:

```bash
./installer.sh export
```

Export to custom directory:

```bash
./installer.sh export --output-dir ./backup
```

Dry run export:

```bash
./installer.sh export --dry-run
```

Export with secrets (explicit opt-in):

```bash
./installer.sh export --include-secrets
```

macOS-specific examples:

```bash
./installer.sh export --os macos --macos-skip-brew-packages
./installer.sh export --os macos --macos-include-home-credentials
```

Linux-specific examples:

```bash
./installer.sh export --os linux --linux-skip-packages
./installer.sh export --os linux --linux-skip-desktop-settings --linux-skip-cron-jobs
```

### 4) Import a backup

Basic import:

```bash
./installer.sh import --archive-path ./backup/system_migration_backup_*.tar.gz
```

Import without interactive prompts:

```bash
./installer.sh import --archive-path ./backup/system_migration_backup_*.tar.gz --yes-to-all
```

Dry run import:

```bash
./installer.sh import --archive-path ./backup/system_migration_backup_*.tar.gz --dry-run
```

macOS-specific import example:

```bash
./installer.sh import --os macos --archive-path ./backup/osx_migration_backup_*.tar.gz --macos-skip-tool-installation
```

Linux-specific import examples:

```bash
./installer.sh import --os linux --archive-path ./backup/system_migration_backup_*.tar.gz --linux-skip-system-packages
./installer.sh import --os linux --archive-path ./backup/system_migration_backup_*.tar.gz --linux-skip-flatpak --linux-skip-snap
```

## Direct CLI Usage (without installer wrapper)

You can also invoke the Python module directly:

```bash
PYTHONPATH="config_migrator/src/python" python3 -m config_migrator export --output-dir ./backup
PYTHONPATH="config_migrator/src/python" python3 -m config_migrator import --archive-path ./backup/<archive>.tar.gz
```

## Security Notes

- Secrets are not exported unless explicitly enabled.
- If you enable secret export, the archive may include private credentials and keys.
- Treat produced archives as sensitive artifacts:
  - avoid uploading to public storage
  - encrypt at rest
  - restrict file permissions
