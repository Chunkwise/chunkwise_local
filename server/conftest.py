"""Pytest configuration for the server package tests.

This makes the repository root importable so tests can import the `server`
package using absolute imports (e.g. `from server.utils import ...`).
"""

import sys
from pathlib import Path

# Add the repository root (one level up from `server/`) to sys.path so that
# `server` is importable regardless of the current working directory when
# pytest is invoked.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
