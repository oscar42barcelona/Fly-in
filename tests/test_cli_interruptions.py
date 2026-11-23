"""Verify Ctrl+C and terminal status codes during evaluation."""

from __future__ import annotations

import signal
import subprocess
import sys
from pathlib import Path

import pytest

from cli import FlyInCLI

ROOT = Path(__file__).resolve().parents[1]


def test_keyboard_interrupt_returns_130_without_traceback(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A synchronous interruption must be handled by the CLI boundary."""
    def stop_now(map_file: str, visualize: bool = False) -> None:
        """Simulate an interrupt while processing an evaluation map."""
        raise KeyboardInterrupt

    monkeypatch.setattr("cli.run_simulation", stop_now)
    code = FlyInCLI(["any-map.txt"]).run()
    captured = capsys.readouterr()
    assert code == 130
    assert captured.out == ""
    assert "Ctrl+C" in captured.err
    assert "Traceback" not in captured.err


@pytest.mark.skipif(
    sys.platform == "win32", reason="POSIX SIGINT integration test"
)
def test_real_sigint_interrupts_cli_cleanly() -> None:
    """Send a real signal to an executing Python CLI process."""
    script = (
        "import cli, sys, time\n"
        "cli.run_simulation = "
        "lambda *args, **kwargs: time.sleep(30)\n"
        "sys.argv = ['cli.py', 'dummy.txt']\n"
        "print('READY', flush=True)\n"
        "raise SystemExit(cli.main())\n"
    )
    process = subprocess.Popen(
        [sys.executable, "-u", "-c", script],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        assert process.stdout is not None
        assert process.stdout.readline().strip() == "READY"
        process.send_signal(signal.SIGINT)
        stdout, stderr = process.communicate(timeout=5)
        assert process.returncode == 130
        assert stdout == ""
        assert "Interrupted by user" in stderr
        assert "Traceback" not in stderr
    finally:
        if process.poll() is None:
            process.kill()
            process.communicate(timeout=5)
