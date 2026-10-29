"""AI-1151: adapter process handling and environment work on Windows too (NSR-01).

The Windows branches are exercised here by patching the platform check and the
process calls; the Windows and macOS CI jobs run the real thing.
"""
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "automation"))

import governed_factory as gf  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent))
from portable import portable_command  # noqa: E402

WINDOWS_NAMES = ("SYSTEMROOT", "COMSPEC", "PATHEXT", "WINDIR", "TEMP", "TMP",
                 "USERPROFILE", "APPDATA", "LOCALAPPDATA")


class ProcessGroupTests(unittest.TestCase):
    def test_windows_starts_the_adapter_in_a_new_process_group(self):
        with mock.patch.object(gf, "_on_windows", return_value=True):
            kwargs = gf.adapter_popen_options()
        self.assertEqual(kwargs, {"creationflags": gf.CREATE_NEW_PROCESS_GROUP})
        self.assertEqual(gf.CREATE_NEW_PROCESS_GROUP, 0x00000200)

    def test_posix_starts_the_adapter_in_a_new_session(self):
        with mock.patch.object(gf, "_on_windows", return_value=False):
            self.assertEqual(gf.adapter_popen_options(), {"start_new_session": True})

    def test_windows_kills_the_whole_tree_with_taskkill(self):
        proc = mock.Mock(pid=4242)
        proc.poll.return_value = None
        done = subprocess.CompletedProcess([], 0)
        with mock.patch.object(gf, "_on_windows", return_value=True), \
                mock.patch.object(gf.subprocess, "run", return_value=done) as run, \
                mock.patch.object(gf.os, "killpg", create=True) as killpg:
            gf.kill_adapter_tree(proc)
        run.assert_called_once_with(["taskkill", "/T", "/F", "/PID", "4242"], capture_output=True)
        killpg.assert_not_called()
        proc.kill.assert_not_called()

    def test_windows_falls_back_to_kill_when_taskkill_fails(self):
        proc = mock.Mock(pid=4242)
        proc.poll.return_value = None
        failed = subprocess.CompletedProcess([], 128)
        with mock.patch.object(gf, "_on_windows", return_value=True), \
                mock.patch.object(gf.subprocess, "run", return_value=failed):
            gf.kill_adapter_tree(proc)
        proc.kill.assert_called_once_with()

    def test_windows_taskkill_missing_falls_back_to_kill(self):
        proc = mock.Mock(pid=4242)
        proc.poll.return_value = None
        with mock.patch.object(gf, "_on_windows", return_value=True), \
                mock.patch.object(gf.subprocess, "run", side_effect=OSError("no taskkill")):
            gf.kill_adapter_tree(proc)
        proc.kill.assert_called_once_with()

    def test_posix_kills_the_process_group(self):
        proc = mock.Mock(pid=4242)
        # Windows has no SIGKILL; supply it so the POSIX branch runs on every CI platform.
        with mock.patch.object(gf, "_on_windows", return_value=False), \
                mock.patch.object(gf.signal, "SIGKILL", getattr(signal, "SIGKILL", 9), create=True), \
                mock.patch.object(gf.os, "killpg", create=True) as killpg:
            gf.kill_adapter_tree(proc)
        killpg.assert_called_once_with(4242, getattr(signal, "SIGKILL", 9))
        proc.kill.assert_not_called()

    def test_exit_status_is_not_read_as_a_signal_on_windows(self):
        with mock.patch.object(gf, "_on_windows", return_value=True):
            self.assertEqual(gf.adapter_signal(137), 0)
            self.assertEqual(gf.adapter_signal(1), 0)
        with mock.patch.object(gf, "_on_windows", return_value=False):
            self.assertEqual(gf.adapter_signal(137), 9)
            self.assertEqual(gf.adapter_signal(-15), 15)

    def test_real_timeout_kills_the_adapter_tree(self):
        # Runs on every CI platform: the adapter starts a child and both are stopped.
        # One line: cmd.exe ends a command line at a newline.
        script = ("import subprocess, sys, time; "
                  "subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)']); "
                  "time.sleep(60)")
        code, _out, _err, timed_out = gf._run_adapter(portable_command(sys.executable, "-c", script),
                                                      "", gf.adapter_environment(), 2)
        self.assertTrue(timed_out)
        self.assertEqual(code, gf.ADAPTER_TIMEOUT_EXIT)


class AdapterEnvironmentTests(unittest.TestCase):
    ENV = {**{name: f"value-{name}" for name in WINDOWS_NAMES},
           "PATH": "p", "HOME": "h", "SECRET_TOKEN": "s", "AWS_SECRET_ACCESS_KEY": "s"}

    def test_windows_keeps_what_cmd_exe_needs_and_nothing_secret(self):
        with mock.patch.object(gf, "_on_windows", return_value=True), \
                mock.patch.dict(gf.os.environ, self.ENV, clear=True):
            env = gf.adapter_environment()
        for name in WINDOWS_NAMES + ("PATH",):
            self.assertEqual(env.get(name), f"value-{name}" if name != "PATH" else "p", name)
        self.assertNotIn("SECRET_TOKEN", env)
        self.assertNotIn("AWS_SECRET_ACCESS_KEY", env)

    def test_windows_matches_names_without_regard_to_case(self):
        with mock.patch.object(gf, "_on_windows", return_value=True), \
                mock.patch.dict(gf.os.environ, {"SystemRoot": "C:\\Windows", "Path": "p"}, clear=True):
            env = gf.adapter_environment()
        # Real Windows upper-cases os.environ keys; compare without case.
        self.assertEqual({k.upper(): v for k, v in env.items()}, {"SYSTEMROOT": "C:\\Windows", "PATH": "p"})

    def test_posix_does_not_add_windows_names(self):
        with mock.patch.object(gf, "_on_windows", return_value=False), \
                mock.patch.dict(gf.os.environ, self.ENV, clear=True):
            env = gf.adapter_environment()
        self.assertEqual(set(env), {"PATH", "HOME"})

    def test_passthrough_still_works_on_both(self):
        for windows in (True, False):
            with self.subTest(windows=windows), mock.patch.object(gf, "_on_windows", return_value=windows), \
                    mock.patch.dict(gf.os.environ, {**self.ENV, gf.ADAPTER_ENV_PASSTHROUGH: "SECRET_TOKEN"},
                                    clear=True):
                self.assertEqual(gf.adapter_environment()["SECRET_TOKEN"], "s")


class StopHandlerTests(unittest.TestCase):
    def test_posix_stops_on_sigterm(self):
        with mock.patch.object(gf, "_on_windows", return_value=False), \
                mock.patch.object(gf.signal, "signal") as install:
            self.assertEqual(gf.install_stop_handlers(), [signal.SIGTERM])
        install.assert_called_once_with(signal.SIGTERM, gf._raise_interrupted)

    def test_windows_also_stops_on_ctrl_break(self):
        with mock.patch.object(gf, "_on_windows", return_value=True), \
                mock.patch.object(gf.signal, "SIGBREAK", 21, create=True), \
                mock.patch.object(gf.signal, "signal") as install:
            self.assertEqual(gf.install_stop_handlers(), [signal.SIGTERM, 21])
        install.assert_any_call(21, gf._raise_interrupted)

    def test_windows_adapter_identity_has_no_process_group(self):
        with mock.patch.object(gf, "_on_windows", return_value=True), \
                mock.patch.object(gf, "_windows_process", return_value=(True, 77)):
            self.assertEqual(gf.adapter_identity(mock.Mock(pid=4242)),
                             {"pid": 4242, "pgid": None, "start_time": 77})


class DispatchLockTests(unittest.TestCase):
    def lock(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return Path(tmp.name) / "anchor" / "dispatch.lock"

    def test_the_lock_is_exclusive_on_this_platform(self):
        # Real fcntl on POSIX, real msvcrt on the Windows CI job.
        path = self.lock()
        first, second = gf.DispatchLock(path), gf.DispatchLock(path)
        self.assertTrue(first.acquire())
        try:
            self.assertFalse(second.acquire())
        finally:
            first.release()
        self.assertTrue(second.acquire())
        second.release()

    def test_windows_locks_with_msvcrt(self):
        fake = mock.Mock(LK_NBLCK=2, LK_UNLCK=0)
        path = self.lock()
        with mock.patch.object(gf, "_on_windows", return_value=True), \
                mock.patch.dict(sys.modules, {"msvcrt": fake}):
            lock = gf.DispatchLock(path)
            self.assertTrue(lock.acquire())
            lock.release()
            fake.locking.side_effect = OSError("locked")
            self.assertFalse(gf.DispatchLock(path).acquire())
        self.assertEqual([c.args[1:] for c in fake.locking.call_args_list], [(2, 1), (0, 1), (2, 1)])


if __name__ == "__main__":
    unittest.main()
