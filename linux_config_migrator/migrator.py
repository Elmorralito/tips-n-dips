#!/usr/bin/env python3
"""Backward-compatibility wrapper for the Linux Configuration Migrator.

Forwards all commands and CLI arguments to the python package module:
`python3 -m linux_config_migrator`.
"""

import sys
import runpy
from pathlib import Path

if __name__ == "__main__":
    # Locate package folder and add it to sys.path
    package_root = Path(__file__).parent.resolve()
    sys.path.insert(0, str(package_root))
    
    # Run the module in the __main__ namespace dynamically
    runpy.run_module("linux_config_migrator", run_name="__main__")
