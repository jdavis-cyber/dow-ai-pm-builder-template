"""Send Ctrl-C or Ctrl-Break to an isolated Windows test console."""
import ctypes
from ctypes import wintypes
import sys
import threading


if __name__ == "__main__":
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    if not kernel.AttachConsole(int(sys.argv[1])):
        raise ctypes.WinError(ctypes.get_last_error())
    # The sender shares the target's console. Consume its own copy of the
    # event, including Ctrl-Break, which cannot be ignored with a NULL handler.
    delivered = threading.Event()

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.DWORD)
    def callback(event):
        delivered.set()
        return True

    if not kernel.SetConsoleCtrlHandler(callback, True):
        raise ctypes.WinError(ctypes.get_last_error())
    if not kernel.SetConsoleCtrlHandler(None, False):
        raise ctypes.WinError(ctypes.get_last_error())
    if not kernel.GenerateConsoleCtrlEvent(int(sys.argv[2]), 0):
        raise ctypes.WinError(ctypes.get_last_error())
    if not delivered.wait(5):
        raise RuntimeError("console control event was not delivered")
