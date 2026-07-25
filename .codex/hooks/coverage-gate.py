#!/usr/bin/env python3
from __future__ import annotations

import configparser
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


DEFAULT_THRESHOLD = 80.0
LOW_FILE_THRESHOLD = 70.0


def project_root() -> Path:
    current = Path.cwd().resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".codex").is_dir():
            return candidate
    return current


def python_executable(root: Path) -> str:
    candidates = [
        root / ".venv" / "bin" / "python",
        root / "venv" / "bin" / "python",
        root / "env" / "bin" / "python",
        root / ".venv" / "Scripts" / "python.exe",
        root / "venv" / "Scripts" / "python.exe",
        root / "env" / "Scripts" / "python.exe",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return sys.executable


def has_module(python: str, module: str) -> bool:
    result = subprocess.run(
        [python, "-c", f"import {module}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def read_pyproject(root: Path) -> dict:
    pyproject = root / "pyproject.toml"
    if not pyproject.exists():
        return {}
    try:
        import tomllib
    except ModuleNotFoundError:
        return {}
    try:
        with pyproject.open("rb") as handle:
            return tomllib.load(handle)
    except Exception:
        return {}


def threshold(root: Path, pyproject: dict) -> float:
    report = pyproject.get("tool", {}).get("coverage", {}).get("report", {})
    value = report.get("fail_under")
    if value is not None:
        return float(value)

    for filename, section in ((".coveragerc", "report"), ("setup.cfg", "coverage:report")):
        path = root / filename
        if not path.exists():
            continue
        parser = configparser.ConfigParser()
        parser.read(path)
        if parser.has_option(section, "fail_under"):
            return parser.getfloat(section, "fail_under")

    return DEFAULT_THRESHOLD


def source_args(root: Path, pyproject: dict) -> list[str]:
    configured = pyproject.get("tool", {}).get("coverage", {}).get("run", {}).get("source")
    if isinstance(configured, str):
        return [f"--cov={configured}"]
    if isinstance(configured, list) and configured:
        return [f"--cov={item}" for item in configured]
    if (root / "src").is_dir():
        return ["--cov=src"]
    packages = [
        path.name
        for path in sorted(root.iterdir())
        if path.is_dir()
        and not path.name.startswith(".")
        and (path / "__init__.py").exists()
    ]
    if packages:
        return [f"--cov={package}" for package in packages]
    return ["--cov=."]


def tests_exist(root: Path) -> bool:
    tests = root / "tests"
    return tests.is_dir() and any(tests.rglob("test_*.py"))


def run_gate(root: Path) -> int:
    python = python_executable(root)

    if not tests_exist(root):
        print("coverage-gate: no tests found; skipping")
        return 0

    if not has_module(python, "pytest"):
        print("coverage-gate: pytest is not available; run $python-sandbox")
        return 0

    if not has_module(python, "pytest_cov"):
        print("coverage-gate: pytest-cov is not available; run $python-sandbox")
        return 0

    pyproject = read_pyproject(root)
    fail_under = threshold(root, pyproject)

    with tempfile.NamedTemporaryFile(prefix="coverage-current-", suffix=".json", delete=False) as handle:
        coverage_json = Path(handle.name)

    cmd = [
        python,
        "-m",
        "pytest",
        "tests/",
        *source_args(root, pyproject),
        "--cov-report=term-missing",
        f"--cov-report=json:{coverage_json}",
        "-q",
        "--tb=short",
    ]

    print(f"coverage-gate: running pytest coverage (threshold: {fail_under:.1f}%)")
    result = subprocess.run(cmd, cwd=root, text=True, capture_output=True, check=False)
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip(), file=sys.stderr)

    if result.returncode != 0:
        coverage_json.unlink(missing_ok=True)
        print("coverage-gate: tests failed")
        return 2

    if not coverage_json.exists():
        print("coverage-gate: coverage JSON was not generated")
        return 0

    try:
        data = json.loads(coverage_json.read_text())
    finally:
        coverage_json.unlink(missing_ok=True)

    current = float(data["totals"]["percent_covered"])
    low_files: list[str] = []
    for path, info in sorted(data.get("files", {}).items()):
        summary = info.get("summary", {})
        percent = float(summary.get("percent_covered", 100.0))
        if percent < LOW_FILE_THRESHOLD:
            missing = info.get("missing_lines", [])[:8]
            low_files.append(f"  {path:<60} {percent:5.1f}%  missing: {missing}")

    passed = current >= fail_under
    status = "PASS" if passed else "FAIL"
    print(f"coverage-gate: {status}")
    print(f"  Total: {current:.1f}% (threshold: {fail_under:.1f}%)")

    if low_files:
        print("")
        print(f"  Files below {LOW_FILE_THRESHOLD:.0f}%:")
        print("\n".join(low_files))

    return 0 if passed else 2


if __name__ == "__main__":
    os.chdir(project_root())
    raise SystemExit(run_gate(Path.cwd()))
