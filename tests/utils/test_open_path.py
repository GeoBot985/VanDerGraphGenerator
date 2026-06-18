"""Tests for the cross-platform open_in_os helper."""

from __future__ import annotations

from pathlib import Path

import pytest

from semantic_visual_builder.utils import open_path as open_path_module


def test_open_in_os_windows_calls_startfile(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    called = {}

    class FakeOs:
        @staticmethod
        def startfile(target):
            called["target"] = target

    import sys

    monkeypatch.setattr(open_path_module.platform, "system", lambda: "Windows")
    monkeypatch.setitem(sys.modules, "os", FakeOs())
    result = open_path_module.open_in_os(tmp_path / "file.html")
    assert "Opened" in result
    assert called["target"].endswith("file.html")


def test_open_in_os_macos_calls_open(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    captured = {}

    def fake_run(args, check=False):
        captured["args"] = list(args)
        captured["check"] = check

    monkeypatch.setattr(open_path_module.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(open_path_module.subprocess, "run", fake_run)
    result = open_path_module.open_in_os(tmp_path / "report.html")
    assert "Opened" in result
    assert captured["args"][0] == "open"
    assert captured["check"] is False


def test_open_in_os_linux_calls_xdg_open(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    captured = {}

    def fake_run(args, check=False):
        captured["args"] = list(args)

    monkeypatch.setattr(open_path_module.platform, "system", lambda: "Linux")
    monkeypatch.setattr(open_path_module.subprocess, "run", fake_run)
    result = open_path_module.open_in_os(tmp_path / "exports")
    assert "Opened" in result
    assert captured["args"][0] == "xdg-open"


def test_open_in_os_handles_failure_gracefully(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(args, check=False):
        raise OSError("no handler")

    monkeypatch.setattr(open_path_module.platform, "system", lambda: "Linux")
    monkeypatch.setattr(open_path_module.subprocess, "run", fake_run)
    result = open_path_module.open_in_os("/nonexistent/path")
    assert "Could not open" in result
