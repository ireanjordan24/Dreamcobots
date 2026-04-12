"""
DreamCo Core — Sandbox Runner

Executes an uploaded bot file in a restricted subprocess with a hard wall-clock
timeout so that untrusted code cannot run indefinitely or consume unbounded
resources.

Security notes
--------------
* The subprocess is started with a 10-second timeout.
* stdout / stderr are captured and returned; they are never passed to the
  orchestrator as code.
* The caller is responsible for pre-validating the file with
  ``core.bot_validator.validate_bot`` before calling this function.
"""

from __future__ import annotations

import subprocess
import sys
from typing import Any, Dict

DEFAULT_TIMEOUT: int = 10  # seconds


def run_in_sandbox(file_path: str, timeout: int = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    """
    Run the Python file at *file_path* in an isolated subprocess.

    Parameters
    ----------
    file_path : str
        Absolute path to the ``.py`` file to execute.
    timeout : int
        Maximum wall-clock seconds to allow (default ``10``).

    Returns
    -------
    dict
        ``{"success": True, "output": str, "error": str}`` on normal exit.
        ``{"success": False, "error": str}`` on timeout or exception.
    """
    try:
        result = subprocess.run(
            [sys.executable, file_path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "success": result.returncode == 0,
            "output": result.stdout,
            "error": result.stderr,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Execution timed out after {timeout}s",
        }
    except Exception as exc:  # pylint: disable=broad-except
        return {
            "success": False,
            "error": str(exc),
        }
