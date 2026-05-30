#!/usr/bin/env bash
set -euo pipefail

# Config Migrator installer/runner
#
# Download examples:
#   curl -fsSL "https://raw.githubusercontent.com/<owner>/<repo>/main/config_migrator/src/bash/installer.sh" -o installer.sh
#   wget -q "https://raw.githubusercontent.com/<owner>/<repo>/main/config_migrator/src/bash/installer.sh" -O installer.sh
#
# Usage:
#   bash installer.sh install
#   bash installer.sh export [--include-secrets] [--output-dir <dir>] [extra config_migrator args]
#   bash installer.sh import --archive-path <archive.tar.gz> [extra config_migrator args]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
PACKAGE_DIR="${ROOT_DIR}/config_migrator"
PYTHON_PACKAGE_DIR="${PACKAGE_DIR}/src/python"

log() { printf '[*] %s\n' "$*"; }
warn() { printf '[!] %s\n' "$*" >&2; }
fail() { printf '[-] %s\n' "$*" >&2; exit 1; }

command_exists() { command -v "$1" >/dev/null 2>&1; }

usage() {
  cat <<'EOF'
Config Migrator installer/runner

Commands:
  install                    Install dependencies required by config_migrator
  export [args...]           Run migration export
  import [args...]           Run migration import

Examples:
  bash installer.sh install
  bash installer.sh export --output-dir ./backup
  bash installer.sh import --archive-path ./backup/system_migration_backup.tar.gz

Notes:
  - 'export' and 'import' pass all additional arguments to:
      python3 -m config_migrator <command> ...
  - If you need command options, inspect:
      python3 -m config_migrator --help
EOF
}

validate_structure() {
  [[ -d "$PACKAGE_DIR" ]] || fail "Expected package directory not found: $PACKAGE_DIR"
  [[ -d "$PYTHON_PACKAGE_DIR" ]] || fail "Expected Python source directory not found: $PYTHON_PACKAGE_DIR"
}

install_brew_macos() {
  if command_exists brew; then
    log "Homebrew detected."
    return 0
  fi

  warn "Homebrew not found. Installing Homebrew (required package manager on macOS)."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

  if [[ -x /opt/homebrew/bin/brew ]]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
  elif [[ -x /usr/local/bin/brew ]]; then
    eval "$(/usr/local/bin/brew shellenv)"
  fi

  command_exists brew || fail "Homebrew installation failed or brew not available in PATH."
  log "Homebrew installed successfully."
}

install_python_for_platform() {
  local os_name
  os_name="$(uname -s)"

  if command_exists python3; then
    log "python3 detected: $(python3 --version)"
    return 0
  fi

  case "$os_name" in
    Darwin)
      install_brew_macos
      log "Installing python via Homebrew..."
      brew install python
      ;;
    Linux)
      if command_exists apt-get; then
        log "Installing python3 and pip with apt-get..."
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip python3-venv
      elif command_exists dnf; then
        log "Installing python3 and pip with dnf..."
        sudo dnf install -y python3 python3-pip
      elif command_exists pacman; then
        log "Installing python and pip with pacman..."
        sudo pacman -Sy --noconfirm python python-pip
      else
        fail "No supported Linux package manager found (apt-get, dnf, pacman)."
      fi
      ;;
    *)
      fail "Unsupported OS: ${os_name}"
      ;;
  esac

  command_exists python3 || fail "python3 could not be installed."
  log "python3 installed successfully: $(python3 --version)"
}

install_python_dependencies() {
  local requirements_file="${PACKAGE_DIR}/requirements.txt"

  python3 -m pip install --upgrade pip

  if [[ -f "$requirements_file" ]]; then
    log "Installing Python dependencies from requirements.txt..."
    python3 -m pip install -r "$requirements_file"
  else
    log "requirements.txt not found; installing core runtime dependency directly..."
    python3 -m pip install "pydantic[email,secret,extra-types]>=2.3.0,<3.0"
  fi
}

run_migrator() {
  local command="$1"
  shift || true
  validate_structure
  PYTHONPATH="${PYTHON_PACKAGE_DIR}" python3 -m config_migrator "$command" "$@"
}

main() {
  local command="${1:-}"
  if [[ -z "$command" ]]; then
    usage
    exit 1
  fi
  shift || true

  case "$command" in
    install)
      log "Starting Config Migrator bootstrap install..."
      validate_structure
      install_python_for_platform
      install_python_dependencies
      log "Install complete."
      log "Run: PYTHONPATH=\"config_migrator/src/python\" python3 -m config_migrator --help"
      ;;
    export)
      run_migrator export "$@"
      ;;
    import)
      run_migrator import "$@"
      ;;
    -h|--help|help)
      usage
      ;;
    *)
      fail "Unknown command: $command (use: install, export, import)"
      ;;
  esac
}

main "$@"
