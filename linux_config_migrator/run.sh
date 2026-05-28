#!/usr/bin/env bash
# =====================================================================
# Linux Configuration Migrator - Bash Launcher Script
# =====================================================================
# This script performs target system environment verification and 
# executes the config migrator as a Python module cleanly.
# =====================================================================

# Color configurations
RED='\033[31m'
GREEN='\033[32m'
YELLOW='\033[33m'
BLUE='\033[34m'
BOLD='\033[1m'
RESET='\033[0m'

# Resolve absolute path of this script's parent folder
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${SCRIPT_DIR}:${PYTHONPATH}"

# Print banner
echo -e "${BLUE}${BOLD}====================================================${RESET}"
echo -e "${BLUE}${BOLD}        Linux Configuration Migrator Launcher       ${RESET}"
echo -e "${BLUE}${BOLD}====================================================${RESET}"

# 1. Verify system environment requirements
echo -e "${BLUE}[*]${RESET} Verifying target system environment..."

# Check Python 3 availability
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}${BOLD}[-] Error: Python 3 is not installed or not in the PATH.${RESET}"
    echo -e "${YELLOW}[!] Install Python 3 using your package manager and try again.${RESET}"
    echo -e "${YELLOW}    Example: sudo apt install python3${RESET}"
    exit 1
fi

# Retrieve Python version
PYTHON_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo -e "${GREEN}[+]${RESET} Python 3 detected (v${PYTHON_VER})"

# 2. Inform user about dependencies
echo -e "${BLUE}[*]${RESET} Verifying library requirements..."
echo -e "${GREEN}[+]${RESET} Zero-Dependency Architecture: Utilizing Python Standard Library."
echo -e "${GREEN}[+]${RESET} No pip packages or virtual environments needed."

echo -e "${BLUE}[*]${RESET} Booting migrator package...\n"

# 3. Execute the module, forwarding all command-line arguments
python3 -m linux_config_migrator "$@"
exit_code=$?

echo -e "\n${BLUE}${BOLD}====================================================${RESET}"
if [ $exit_code -eq 0 ]; then
    echo -e "${GREEN}${BOLD}     Migration process finished successfully!       ${RESET}"
else
    echo -e "${RED}${BOLD}     Migration process terminated with errors.      ${RESET}"
fi
echo -e "${BLUE}${BOLD}====================================================${RESET}"

exit $exit_code
