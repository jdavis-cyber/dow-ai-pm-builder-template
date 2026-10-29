"""Console output that survives a console that can't encode every character.

A Windows console or pipe often uses a legacy code page (cp1252), which has no
"▶" or "→"; printing one raises UnicodeEncodeError and aborts the command
(AI-1151). Entry points call make_console_safe() first, so such characters are
replaced instead. A UTF-8 stream is left unchanged.
"""
import codecs
import sys


def make_console_safe(*streams) -> None:
    for stream in streams or (sys.stdout, sys.stderr):
        try:
            encoding = codecs.lookup(getattr(stream, "encoding", None) or "ascii").name
        except LookupError:
            encoding = ""
        if encoding == "utf-8":
            continue
        try:
            stream.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
