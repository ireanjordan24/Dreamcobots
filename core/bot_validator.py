"""
DreamCo Core — Bot Validator

Performs lightweight static-analysis safety checks on uploaded bot files
before they are executed in the sandbox.  Rejects files that contain
dangerous patterns.
"""

from __future__ import annotations

import os
from typing import Tuple

# Keywords that must not appear in uploaded bot code
_BLOCKED_PATTERNS: tuple[str, ...] = (
    "os.system",
    "subprocess",
    "rm -rf",
    "__import__",
    "eval(",
    "exec(",
    "shutil",
)


def validate_bot(file_path: str) -> Tuple[bool, str]:
    """
    Validate the Python source file at *file_path*.

    Parameters
    ----------
    file_path : str
        Absolute path to the ``.py`` file to validate.

    Returns
    -------
    (bool, str)
        ``(True, "Safe")`` when the file passes all checks.
        ``(False, reason)`` when a blocked pattern is found.

    Raises
    ------
    FileNotFoundError
        If *file_path* does not exist.
    ValueError
        If *file_path* is not an absolute path.
    """
    resolved = os.path.realpath(file_path)
    if not os.path.isfile(resolved):
        raise FileNotFoundError(f"File not found: {file_path!r}")

    with open(resolved, "r", encoding="utf-8") as fh:
        code = fh.read()

    for pattern in _BLOCKED_PATTERNS:
        if pattern in code:
            return False, f"Blocked pattern detected: {pattern!r}"

    return True, "Safe"
