"""Unit tests for dbtest.load_config. These never connect to Neo4j."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import pytest

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from dbtest import REQUIRED_ENV, load_config  # noqa: E402

REQUIRED = ("NEO4J_URI", "NEO4J_USERNAME", "NEO4J_PASSWORD")
DUMMY_PASSWORD = "unit-test-not-a-real-secret"


@pytest.fixture(autouse=True)
def clear_neo4j_env(monkeypatch):
    for key in list(os.environ):
        if key.startswith("NEO4J_"):
            monkeypatch.delenv(key, raising=False)
    yield


def test_required_env_tuple():
    assert REQUIRED_ENV == REQUIRED


def test_missing_all_exits_2(capsys):
    with pytest.raises(SystemExit) as ei:
        load_config()
    assert ei.value.code == 2
    err = capsys.readouterr().err
    for key in REQUIRED:
        assert key in err


def test_partial_env_exits_2(monkeypatch, capsys):
    monkeypatch.setenv("NEO4J_URI", "bolt://127.0.0.1:17687")
    monkeypatch.setenv("NEO4J_USERNAME", "unit-test-user")
    with pytest.raises(SystemExit) as ei:
        load_config()
    assert ei.value.code == 2
    err = capsys.readouterr().err
    assert "NEO4J_PASSWORD" in err
    assert DUMMY_PASSWORD not in err


def test_load_config_from_dummy_env(monkeypatch):
    monkeypatch.setenv("NEO4J_URI", "bolt://127.0.0.1:17687")
    monkeypatch.setenv("NEO4J_USERNAME", "unit-test-user")
    monkeypatch.setenv("NEO4J_PASSWORD", DUMMY_PASSWORD)
    cfg = load_config()
    assert cfg["uri"] == "bolt://127.0.0.1:17687"
    assert cfg["user"] == "unit-test-user"
    assert cfg["password"] == DUMMY_PASSWORD
    assert cfg["database"] is None
    assert cfg["name"] == "Neo4j"


def test_optional_database_and_name(monkeypatch):
    monkeypatch.setenv("NEO4J_URI", "neo4j://127.0.0.1:17687")
    monkeypatch.setenv("NEO4J_USERNAME", "unit-test-user")
    monkeypatch.setenv("NEO4J_PASSWORD", DUMMY_PASSWORD)
    monkeypatch.setenv("NEO4J_DATABASE", "testdb")
    monkeypatch.setenv("NEO4J_NAME", "Local")
    cfg = load_config()
    assert cfg["database"] == "testdb"
    assert cfg["name"] == "Local"


def test_empty_database_is_none(monkeypatch):
    monkeypatch.setenv("NEO4J_URI", "bolt://127.0.0.1:17687")
    monkeypatch.setenv("NEO4J_USERNAME", "unit-test-user")
    monkeypatch.setenv("NEO4J_PASSWORD", DUMMY_PASSWORD)
    monkeypatch.setenv("NEO4J_DATABASE", "")
    cfg = load_config()
    assert cfg["database"] is None


def test_dbtest_source_has_no_hardcoded_password():
    source = (BACKEND / "dbtest.py").read_text()
    assert 'os.environ["NEO4J_PASSWORD"]' in source
    for i, line in enumerate(source.splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith('"""') or stripped.startswith("'''"):
            continue
        if re.search(r"""password\s*=\s*['\"]""", stripped, re.I):
            pytest.fail(f"hard-coded password literal on line {i}")
