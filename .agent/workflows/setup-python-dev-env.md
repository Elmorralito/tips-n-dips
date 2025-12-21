---
description: Set up the Python development environment using pyenv and your preferred package manager.
---

This workflow guides you through setting up a robust Python development environment. It uses `pyenv` for Python version management and supports Poetry, pip (with venv), and uv.

1.  **Check Prerequisites**: Ensure `pyenv` is installed and initialized.

    ```bash
    if ! command -v pyenv &> /dev/null; then
        read -p "pyenv not found. Install it? (y/N) " INSTALL_PYENV
        if [[ "$INSTALL_PYENV" =~ ^[Yy]$ ]]; then
            echo "Installing pyenv..."
            curl https://pyenv.run | bash

            # Add pyenv to PATH for this session
            export PYENV_ROOT="$HOME/.pyenv"
            [[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
            eval "$(pyenv init -)"

            if ! command -v pyenv &> /dev/null; then
                 echo "Automatic installation failed or PATH update needed."
                 echo "Please check https://github.com/pyenv/pyenv#installation"
                 exit 1
            fi
        else
            echo "pyenv is required for this workflow. Exiting."
            exit 0
        fi
    fi
    echo "pyenv found: $(pyenv --version)"
    ```

2.  **Select and Install Python Version**
    Select the Python version you want to use for this project.

    ```bash
    echo "Available Python versions (short list):"
    pyenv install --list | grep -E "^\s*3\.\d+\.\d+$" | tail -n 5

    read -p "Enter desired Python version (e.g., 3.12.1): " PYTHON_VERSION

    if ! pyenv versions | grep -q "$PYTHON_VERSION"; then
        echo "Installing Python $PYTHON_VERSION..."
        pyenv install "$PYTHON_VERSION"
    else
        echo "Python $PYTHON_VERSION is already installed."
    fi

    pyenv local "$PYTHON_VERSION"
    echo "Set local Python version to $PYTHON_VERSION"
    ```

3.  **Choose Package Manager**
    Select your preferred package manager: Poetry, Pip (standard venv), or uv.

    ```bash
    echo "Select Package Manager:"
    echo "1) Poetry (Recommended for managing dependencies)"
    echo "2) Pip + Virtualenv (Standard)"
    echo "3) uv (Fastest)"

    read -p "Enter choice [1-3]: " PM_CHOICE

    case $PM_CHOICE in
        1)
            echo "Setting up with Poetry..."
            if ! command -v poetry &> /dev/null; then
                 echo "Poetry not found. Installing via pipx..."
                 pipx install poetry
            fi
            poetry env use $(pyenv which python)
            poetry install
            echo "Setup complete! Run 'poetry shell' to activate."
            ;;
        2)
            echo "Setting up with Pip + Virtualenv..."
            python -m venv .venv
            source .venv/bin/activate
            pip install --upgrade pip
            if [ -f "requirements.txt" ]; then
                pip install -r requirements.txt
            fi
            echo "Setup complete! Run 'source .venv/bin/activate' to activate."
            ;;
        3)
            echo "Setting up with uv..."
            if ! command -v uv &> /dev/null; then
                echo "uv not found. Installing..."
                curl -LsSf https://astral.sh/uv/install.sh | sh
            fi
            uv venv
            source .venv/bin/activate
            if [ -f "requirements.txt" ]; then
                uv pip install -r requirements.txt
            elif [ -f "pyproject.toml" ]; then
                 # Basic sync if supported or just pip sync
                 uv pip install -r <(uv pip compile pyproject.toml)
            fi
            echo "Setup complete! Run 'source .venv/bin/activate' to activate."
            ;;
        *)
            echo "Invalid choice. Exiting."
            exit 1
            ;;
    esac
    ```
