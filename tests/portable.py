"""Helpers that keep test fixtures working on Windows as well as POSIX (AI-1151)."""
import os
import shlex
import subprocess


def portable_command(*args: str) -> str:
    """A command line for the platform's shell: cmd.exe on Windows, sh elsewhere."""
    return subprocess.list2cmdline(args) if os.name == "nt" else shlex.join(args)
