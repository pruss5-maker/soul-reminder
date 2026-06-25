"""Tests for soul-reminder plugin.

Tests run without touching real Hermes state — they use temporary directories
and mock the HERMES_HOME environment variable.
"""
import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

# Make plugin importable
PLUGIN_DIR = Path(__file__).parent.parent / "hermes_plugin"
sys.path.insert(0, str(PLUGIN_DIR))

# Need to import after sys.path setup
import importlib
_soul = importlib.import_module("__init__")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_hermes_home(monkeypatch, tmp_path):
    """Redirect HERMES_HOME to a temp dir and reset config to defaults."""
    home = tmp_path / ".hermes"
    home.mkdir()
    monkeypatch.setenv("HERMES_HOME", str(home))

    # Reset config file to defaults (config lives next to plugin, not HERMES_HOME)
    config_path = _soul._config_path()
    default_cfg = dict(_soul._DEFAULT_CONFIG)
    _soul.save_config(default_cfg)

    # Clear call counter
    _soul._call_counter.clear()
    return home


@pytest.fixture
def sample_soul():
    """A realistic SOUL.md for testing concept extraction."""
    return """# SOUL.md — Test Agent

You are a test agent. You are not a generic assistant.

## How You Work

Set a goal. Set validation criteria. Do the work. Validate against criteria.

## What You Will Not Do

- Do not lie. Ever. Not to spare feelings, not to seem helpful.
- Do not claim success without evidence.
- Do not use ten words when three work. No filler.
- Do not ship work that hasn't passed its own validation criteria.

## What You Will Do

- Say what's missing when data is absent.
- Act without asking when input is clear.
- Separate proven facts from estimates.

## Hard Rules

- No risky action without approval.
- Do not accept the first option unless proven best.

## Voice

Blunt, funny, witty when it lands.
"""


@pytest.fixture
def sample_soul_minimal():
    """A minimal SOUL.md with no clear sections."""
    return """# SOUL.md

You are an agent. Be helpful.
"""


# ---------------------------------------------------------------------------
# Config tests
# ---------------------------------------------------------------------------

class TestConfig:
    def test_default_config(self, tmp_hermes_home):
        cfg = _soul.load_config()
        assert cfg["enabled"] is True
        assert cfg["interval"] == 5
        assert cfg["format"] == "compact"

    def test_save_and_load(self, tmp_hermes_home):
        cfg = _soul.load_config()
        cfg["interval"] = 5
        cfg["format"] = "detailed"
        _soul.save_config(cfg)

        cfg2 = _soul.load_config()
        assert cfg2["interval"] == 5
        assert cfg2["format"] == "detailed"

    def test_config_path_exists_after_save(self, tmp_hermes_home):
        cfg = _soul.load_config()
        _soul.save_config(cfg)
        # The config lives next to the plugin, not in HERMES_HOME
        assert _soul._config_path().exists()


# ---------------------------------------------------------------------------
# Concept extraction tests
# ---------------------------------------------------------------------------

class TestConceptExtraction:
    def test_extracts_from_priority_sections(self, sample_soul):
        concepts = _soul.extract_concepts_from_soul(sample_soul)
        assert len(concepts) >= 3
        # Should find negations
        negation_found = any("lie" in c.lower() or "do not" in c.lower() for c in concepts)
        assert negation_found, f"Expected negation concepts, got: {concepts}"

    def test_extracts_hard_rules(self, sample_soul):
        concepts = _soul.extract_concepts_from_soul(sample_soul)
        # Should find "No risky action without approval"
        rule_found = any("risky" in c.lower() or "approval" in c.lower() for c in concepts)
        assert rule_found, f"Expected hard rule, got: {concepts}"

    def test_extracts_how_you_work(self, sample_soul):
        concepts = _soul.extract_concepts_from_soul(sample_soul)
        # Should find validation criteria concept
        validation_found = any("validat" in c.lower() for c in concepts)
        assert validation_found, f"Expected validation concept, got: {concepts}"

    def test_fallback_on_minimal_soul(self, sample_soul_minimal):
        concepts = _soul.extract_concepts_from_soul(sample_soul_minimal)
        # Should still get something from fallback
        assert len(concepts) >= 1

    def test_max_concepts_limit(self, sample_soul):
        concepts = _soul.extract_concepts_from_soul(sample_soul, max_concepts=3)
        assert len(concepts) <= 3

    def test_cleans_markdown(self):
        text = """# SOUL.md
## Hard Rules
- **Do not** `claim` success [without evidence]
"""
        concepts = _soul.extract_concepts_from_soul(text)
        assert len(concepts) >= 1
        # Should strip markdown
        assert "**" not in concepts[0]
        assert "`" not in concepts[0]

    def test_empty_soul(self):
        concepts = _soul.extract_concepts_from_soul("")
        assert concepts == []


# ---------------------------------------------------------------------------
# Reminder building tests
# ---------------------------------------------------------------------------

class TestReminderBuilding:
    def test_compact_format(self):
        concepts = ["don't lie", "validate first", "fewest words"]
        r = _soul.build_reminder(concepts, fmt="compact")
        assert "don't lie" in r
        assert "validate first" in r
        assert "fewest words" in r
        assert r.endswith(".")

    def test_detailed_format(self):
        concepts = ["don't lie", "validate first"]
        r = _soul.build_reminder(concepts, fmt="detailed")
        assert "•" in r
        assert "don't lie" in r

    def test_custom_prefix(self):
        concepts = ["test"]
        r = _soul.build_reminder(concepts, prefix="🧠 Remember:")
        assert r.startswith("🧠 Remember:")

    def test_empty_concepts(self):
        r = _soul.build_reminder([])
        assert r == ""


# ---------------------------------------------------------------------------
# Hook tests
# ---------------------------------------------------------------------------

class TestPreLlmCall:
    def test_injects_on_every_call(self, tmp_hermes_home, sample_soul):
        # Write SOUL.md
        (tmp_hermes_home / "SOUL.md").write_text(sample_soul)
        # Reset config so concepts auto-extract, set interval=1 for this test
        cfg = _soul.load_config()
        cfg["core_concepts"] = []
        cfg["interval"] = 1
        _soul.save_config(cfg)

        result = _soul.pre_llm_call(
            ctx=None, session_id="test-1", user_message="hello"
        )
        assert result is not None
        assert "context" in result
        assert len(result["context"]) > 10

    def test_respects_interval(self, tmp_hermes_home, sample_soul):
        # Write SOUL.md and set up concepts
        (tmp_hermes_home / "SOUL.md").write_text(sample_soul)
        cfg = _soul.load_config()
        cfg["core_concepts"] = ["don't lie", "validate first"]
        cfg["interval"] = 3
        _soul.save_config(cfg)

        # Calls 1 and 2 should not inject
        r1 = _soul.pre_llm_call(ctx=None, session_id="test-2", user_message="msg1")
        r2 = _soul.pre_llm_call(ctx=None, session_id="test-2", user_message="msg2")
        assert r1 is None
        assert r2 is None

        # Call 3 should inject
        r3 = _soul.pre_llm_call(ctx=None, session_id="test-2", user_message="msg3")
        assert r3 is not None
        assert "context" in r3

    def test_disabled_returns_none(self, tmp_hermes_home, sample_soul):
        (tmp_hermes_home / "SOUL.md").write_text(sample_soul)
        cfg = _soul.load_config()
        cfg["enabled"] = False
        _soul.save_config(cfg)

        result = _soul.pre_llm_call(
            ctx=None, session_id="test-3", user_message="hello"
        )
        assert result is None

    def test_no_soul_returns_none(self, tmp_hermes_home):
        # No SOUL.md exists
        result = _soul.pre_llm_call(
            ctx=None, session_id="test-4", user_message="hello"
        )
        assert result is None


# ---------------------------------------------------------------------------
# Slash command tests
# ---------------------------------------------------------------------------

class TestSlashCommand:
    def test_status(self, tmp_hermes_home):
        result = _soul.slash_soul("status")
        data = json.loads(result)
        assert data["enabled"] is True
        assert "interval" in data

    def test_interval(self, tmp_hermes_home):
        result = _soul.slash_soul("interval 5")
        assert "5" in result
        cfg = _soul.load_config()
        assert cfg["interval"] == 5

    def test_enable_disable(self, tmp_hermes_home):
        _soul.slash_soul("disable")
        assert _soul.load_config()["enabled"] is False
        _soul.slash_soul("enable")
        assert _soul.load_config()["enabled"] is True

    def test_set_concepts(self, tmp_hermes_home):
        result = _soul.slash_soul('set "don\'t lie, validate first, be blunt"')
        assert "3" in result or "concepts" in result.lower()
        cfg = _soul.load_config()
        assert len(cfg["core_concepts"]) == 3

    def test_refresh(self, tmp_hermes_home, sample_soul):
        (tmp_hermes_home / "SOUL.md").write_text(sample_soul)
        result = _soul.slash_soul("refresh")
        assert "Refreshed" in result or "concepts" in result.lower()
        cfg = _soul.load_config()
        assert len(cfg["core_concepts"]) > 0

    def test_format(self, tmp_hermes_home):
        result = _soul.slash_soul("format detailed")
        assert "detailed" in result
        assert _soul.load_config()["format"] == "detailed"

    def test_create_returns_interview(self, tmp_hermes_home):
        result = _soul.slash_soul("create")
        assert "interview" in result.lower() or "question" in result.lower()
        assert "name" in result.lower()

    def test_generate_creates_soul(self, tmp_hermes_home):
        answers = json.dumps({
            "name": "TestBot",
            "role": "coding agent",
            "lies": "Never lie. Say what's missing instead.",
            "creativity": "Try unconventional approaches when conventional ones are mediocre",
            "first_option": "Never accept the first option unless proven best",
            "verbosity": "Fewest words possible. Blunt, funny, witty.",
            "contrarian": "Disagree openly. Go against the grain.",
            "validation": "Always set goals and criteria before working",
            "hard_stops": "publish without approval, claim success without evidence",
            "contradictions": "Be fast but never ship broken work\nBe creative but deliver reliably",
        })
        result = _soul.slash_soul(f'generate {answers}')
        data = json.loads(result)
        assert data["status"] == "created"
        assert data["concepts"]  # non-empty

        # Verify SOUL.md was written
        soul_file = _soul._soul_path()
        assert soul_file.exists()
        content = soul_file.read_text()
        assert "TestBot" in content
        assert "Do not lie" in content or "Do not publish" in content
        assert "fewest" in content.lower() or "blunt" in content.lower()


# ---------------------------------------------------------------------------
# Integration test
# ---------------------------------------------------------------------------

class TestEndToEnd:
    def test_full_flow_auto_extract(self, tmp_hermes_home, sample_soul):
        """Write a SOUL.md, call pre_llm_call, verify reminder appears."""
        (tmp_hermes_home / "SOUL.md").write_text(sample_soul)
        # Set interval=1 so first call fires
        cfg = _soul.load_config()
        cfg["interval"] = 1
        _soul.save_config(cfg)

        # First call should auto-extract concepts and inject
        result = _soul.pre_llm_call(
            ctx=None, session_id="e2e-1", user_message="write some code"
        )

        assert result is not None
        context = result["context"]
        # Should contain at least one concept from the soul
        assert any(kw in context.lower() for kw in ["lie", "valid", "filler", "approval"])
