"""Soul Reminder — injects core identity concepts into every Nth API call.

The soul system has two parts:
1. soul-creator (skill) — creates the SOUL.md identity file
2. soul-reminder (this plugin) — injects reminders of core concepts into the
   conversation at configurable intervals

The reminder reads core concepts from SOUL.md (or a custom config) and injects
a compact reminder like:

    ⚡ Soul reminder: Don't forget — don't lie, validate before executing,
    fewest words possible, go against the grain, be creative.

This keeps the agent's identity fresh across long sessions where the original
SOUL.md may have scrolled out of the model's attention window.
"""
from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

_DEFAULT_CONFIG = {
    "enabled": True,
    "interval": 5,           # inject every Nth API call (default: every 5th)
    "format": "compact",     # "compact" or "detailed"
    "reminder_prefix": "⚡ Soul reminder:",
    "soul_file": "",         # auto-detected if empty
    "core_concepts": [],     # auto-extracted if empty
    "initialized": False,    # True after /soul generate creates a SOUL.md
}

_onboarding_injected = False  # track if we've shown the onboarding nudge this session

_call_counter: dict[str, int] = {}


def _hermes_home() -> Path:
    return Path(os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes")))


def _config_path() -> Path:
    return Path(__file__).parent / "soul_reminder_config.json"


def _soul_path() -> Path:
    """Find the SOUL.md file."""
    cfg = load_config()
    explicit = cfg.get("soul_file", "")
    if explicit:
        p = Path(explicit).expanduser()
        if p.exists():
            return p
    # Auto-detect
    p = _hermes_home() / "SOUL.md"
    if p.exists():
        return p
    return p  # return path even if it doesn't exist yet


def load_config() -> dict[str, Any]:
    """Load config, merged with defaults."""
    cfg = dict(_DEFAULT_CONFIG)
    p = _config_path()
    if p.exists():
        try:
            saved = json.loads(p.read_text())
            cfg.update(saved)
        except (json.JSONDecodeError, OSError):
            pass
    return cfg


def save_config(cfg: dict[str, Any]) -> None:
    """Save config to disk."""
    p = _config_path()
    p.write_text(json.dumps(cfg, indent=4, sort_keys=True))


# ---------------------------------------------------------------------------
# Soul parsing — extract core concepts from SOUL.md
# ---------------------------------------------------------------------------

def extract_concepts_from_soul(soul_text: str, max_concepts: int = 8) -> list[str]:
    """Extract the core behavioral concepts from a SOUL.md file.

    Looks for the most load-bearing lines: hard rules, negations, and
    bullet points under key sections. Returns short, punchy phrases.
    """
    concepts: list[str] = []

    # Look for lines under "What You Will Not Do" or "Hard Rules"
    priority_sections = [
        r"(?:##|#+)\s*(?:What You Will Not Do|Hard Rules|Negations)",
        r"(?:##|#+)\s*(?:Core Thesis|How You Work|Optimize For)",
        r"(?:##|#+)\s*(?:Truthfulness|Definition of Done)",
    ]

    lines = soul_text.split("\n")
    in_priority = False

    for line in lines:
        stripped = line.strip()

        # Check if we're entering a priority section
        if stripped.startswith("#"):
            in_priority = any(
                re.search(pat, stripped, re.I) for pat in priority_sections
            )
            continue

        if not in_priority and not stripped.startswith("-"):
            continue

        # Extract bullet content
        if stripped.startswith("-"):
            text = stripped.lstrip("- ").strip()
            text = _clean_concept(text)
            if text and len(text) > 5 and len(text) < 200:
                if text not in concepts:
                    concepts.append(text)

        if len(concepts) >= max_concepts:
            break

    # Fallback: grab any line starting with "Don't" or "Do not" or "Never"
    if len(concepts) < 3:
        for line in lines:
            stripped = line.strip()
            if re.match(r"^(?:Don't|Do not|Never|No)\s", stripped, re.I):
                text = _clean_concept(stripped)
                if text and text not in concepts:
                    concepts.append(text)
                if len(concepts) >= max_concepts:
                    break

    # Last resort: first few non-empty, non-header lines
    if len(concepts) < 3:
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and not stripped.startswith("---"):
                text = _clean_concept(stripped)
                if text and len(text) > 10 and text not in concepts:
                    concepts.append(text)
                if len(concepts) >= max_concepts:
                    break

    return concepts[:max_concepts]


def _clean_concept(text: str) -> str:
    """Clean a concept line into a short reminder phrase."""
    # Remove markdown formatting
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    # Remove bracketed placeholders like [specific risky action]
    text = re.sub(r"\[.+?\]", "", text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    # Remove trailing punctuation
    text = text.rstrip(".")
    return text


# ---------------------------------------------------------------------------
# Reminder generation
# ---------------------------------------------------------------------------

def build_reminder(concepts: list[str], fmt: str = "compact",
                   prefix: str = "⚡ Soul reminder:") -> str:
    """Build a reminder string from concepts."""
    if not concepts:
        return ""

    if fmt == "detailed":
        lines = [f"{prefix}"]
        for c in concepts:
            lines.append(f"  • {c}")
        return "\n".join(lines)

    # compact (default)
    joined = ", ".join(concepts)
    return f"{prefix} {joined}."


def get_reminder() -> str:
    """Get the current reminder based on config and SOUL.md."""
    cfg = load_config()

    if not cfg.get("enabled", True):
        return ""

    # Get concepts from config or extract from SOUL.md
    concepts = cfg.get("core_concepts", [])
    if not concepts:
        soul_file = _soul_path()
        if soul_file.exists():
            soul_text = soul_file.read_text()
            concepts = extract_concepts_from_soul(soul_text)
            # Cache for future calls
            cfg["core_concepts"] = concepts
            save_config(cfg)

    if not concepts:
        return ""

    return build_reminder(
        concepts,
        fmt=cfg.get("format", "compact"),
        prefix=cfg.get("reminder_prefix", "⚡ Soul reminder:"),
    )


# ---------------------------------------------------------------------------
# Onboarding prompt — injected on first run when no SOUL.md exists
# ---------------------------------------------------------------------------

_ONBOARDING_PROMPT = """⚡ Soul system installed! You don't have a SOUL.md yet.

Start your soul creation interview NOW. Ask the user these questions one at a time, conversationally. Use the suggestions as options they can pick from. When they answer, move to the next question.

1. **Name** — What should I call my agent? (e.g. Atlas, Nova, Hermes, or any name)
2. **Role** — What's the agent's primary job? (coding, research, writing, general, trading, devops)
3. **Truthfulness** — Should the agent ever lie? (Recommend: never — say what's missing instead)
4. **Creativity** — Try unconventional approaches when conventional ones are mediocre? (Recommend: yes)
5. **First-option bias** — Evaluate alternatives or go with the first answer? (Recommend: never accept first option unless proven best)
6. **Communication** — Fewest words possible and blunt/funny/witty? Or concise-professional? Or detailed?
7. **Contrarian** — Disagree openly when evidence warrants? Or follow along?
8. **Validation** — Set goals and validation criteria before doing work? (Recommend: always)
9. **Hard stops** — What should the agent NEVER do? (e.g. publish without approval, claim success without evidence, share secrets)
10. **Contradictions** — What competing values should the agent balance? (e.g. speed vs correctness, autonomy vs safety)

After collecting all answers, call /soul generate with the answers as JSON. This creates the SOUL.md and activates reminders automatically. The user should NOT need to type any commands — you handle everything."""


# ---------------------------------------------------------------------------
# Plugin hook
# ---------------------------------------------------------------------------

def pre_llm_call(ctx=None, session_id=None, user_message="",
                 conversation_history=None, model="", platform="", **kwargs) -> dict | None:
    """Hermes pre_llm_call hook.

    First-run behavior: if no SOUL.md exists yet, inject an onboarding nudge
    that tells the agent to start the guided interview. The user just answers
    questions — they never need to type /soul create.

    Normal behavior: inject reminder at configured interval.
    """
    global _onboarding_injected
    cfg = load_config()

    if not cfg.get("enabled", True):
        return None

    # --- First-run onboarding ---
    # Check if we need to onboarding. Two conditions:
    # 1. initialized flag not set in config
    # 2. No SOUL.md exists (or it's the default Hermes one)
    soul_file = _soul_path()
    soul_is_custom = cfg.get("initialized", False) or (
        soul_file.exists() and "soul-reminder" in soul_file.read_text().lower()
    )

    if not soul_is_custom and not _onboarding_injected:
        _onboarding_injected = True  # only inject once per session
        return {"context": _ONBOARDING_PROMPT}

    # --- Normal reminder injection ---
    # Track call count per session
    sid = session_id or "_default"
    _call_counter[sid] = _call_counter.get(sid, 0) + 1
    count = _call_counter[sid]

    interval = max(1, int(cfg.get("interval", 5)))

    # Only inject on every Nth call
    if count % interval != 0:
        return None

    reminder = get_reminder()
    if not reminder:
        return None

    return {"context": reminder}


# ---------------------------------------------------------------------------
# Slash command handler
# ---------------------------------------------------------------------------

def slash_soul(raw_args: str) -> str:
    """Handle /soul slash command.

    Usage:
        /soul                  — show current status + last reminder
        /soul interval N       — set injection interval (every Nth call)
        /soul format compact   — set format (compact|detailed)
        /soul enable           — enable reminders
        /soul disable          — disable reminders
        /soul refresh          — re-extract concepts from SOUL.md
        /soul show             — show current concepts
        /soul set "concept 1, concept 2" — manually set concepts
    """
    args = (raw_args or "").strip()
    cfg = load_config()

    if not args or args == "status":
        soul_file = _soul_path()
        concepts = cfg.get("core_concepts", [])
        return json.dumps({
            "enabled": cfg.get("enabled", True),
            "interval": cfg.get("interval", 1),
            "format": cfg.get("format", "compact"),
            "soul_file": str(soul_file),
            "soul_exists": soul_file.exists(),
            "concept_count": len(concepts),
            "concepts": concepts,
        }, indent=2, sort_keys=True)

    if args.startswith("interval "):
        val = args[len("interval "):].strip()
        try:
            n = int(val)
            if n < 1:
                return "Interval must be >= 1"
            cfg["interval"] = n
            save_config(cfg)
            return f"Interval set to every {n} API call(s)"
        except ValueError:
            return f"Invalid interval: {val}"

    if args.startswith("format "):
        fmt = args[len("format "):].strip().lower()
        if fmt not in ("compact", "detailed"):
            return "Format must be 'compact' or 'detailed'"
        cfg["format"] = fmt
        save_config(cfg)
        return f"Format set to {fmt}"

    if args == "enable":
        cfg["enabled"] = True
        save_config(cfg)
        return "Soul reminders enabled"

    if args == "disable":
        cfg["enabled"] = False
        save_config(cfg)
        return "Soul reminders disabled"

    if args == "refresh":
        cfg["core_concepts"] = []
        save_config(cfg)
        soul_file = _soul_path()
        if soul_file.exists():
            concepts = extract_concepts_from_soul(soul_file.read_text())
            cfg["core_concepts"] = concepts
            save_config(cfg)
            return f"Refreshed {len(concepts)} concepts from {soul_file}"
        return f"SOUL.md not found at {soul_file}"

    if args == "show":
        return json.dumps(cfg.get("core_concepts", []), indent=2)

    if args.startswith("set "):
        raw = args[len("set "):].strip().strip('"').strip("'")
        concepts = [c.strip() for c in raw.split(",") if c.strip()]
        cfg["core_concepts"] = concepts
        save_config(cfg)
        return f"Set {len(concepts)} concepts: {concepts}"

    if args == "create":
        # Return the interview prompt for the agent to use
        try:
            from .soul_create import get_interview_prompt, generate_soul
        except ImportError:
            import importlib.util
            _p = Path(__file__).parent / "soul_create.py"
            _spec = importlib.util.spec_from_file_location("soul_create", _p)
            _mod = importlib.util.module_from_spec(_spec)
            _spec.loader.exec_module(_mod)
            get_interview_prompt = _mod.get_interview_prompt
            generate_soul = _mod.generate_soul

        return get_interview_prompt()

    if args.startswith("generate "):
        # Generate SOUL.md from JSON answers
        try:
            from .soul_create import generate_soul
        except ImportError:
            import importlib.util
            _p = Path(__file__).parent / "soul_create.py"
            _spec = importlib.util.spec_from_file_location("soul_create", _p)
            _mod = importlib.util.module_from_spec(_spec)
            _spec.loader.exec_module(_mod)
            generate_soul = _mod.generate_soul

        raw_json = args[len("generate "):].strip()
        try:
            answers = json.loads(raw_json)
        except json.JSONDecodeError:
            return f"Invalid JSON: {raw_json[:100]}"

        soul_text = generate_soul(answers)
        soul_file = _soul_path()
        soul_file.parent.mkdir(parents=True, exist_ok=True)
        soul_file.write_text(soul_text)

        # Refresh concepts from the new soul
        cfg["core_concepts"] = []
        cfg["initialized"] = True  # Mark as initialized — stop onboarding nudges
        save_config(cfg)
        concepts = extract_concepts_from_soul(soul_text)
        cfg["core_concepts"] = concepts
        save_config(cfg)

        return json.dumps({
            "status": "created",
            "path": str(soul_file),
            "concepts": concepts,
            "message": f"SOUL.md written to {soul_file}. {len(concepts)} concepts extracted. Reminders active.",
        }, indent=2)

    return (
        "Usage: /soul [status|create|generate <json>|interval N|format compact|detailed|"
        "enable|disable|refresh|show|set \"c1, c2, ...\"]"
    )


# ---------------------------------------------------------------------------
# Plugin registration
# ---------------------------------------------------------------------------

def register(ctx):
    """Register the soul-reminder plugin with Hermes."""
    ctx.register_hook("pre_llm_call", lambda **kw: pre_llm_call(ctx=ctx, **kw))
    ctx.register_command(
        "soul",
        slash_soul,
        description="Create your soul, configure reminders, manage agent identity",
        args_hint="[create|status|generate <json>|interval N|format|enable|disable|refresh|show|set]",
    )
    # Register the bundled soul-creator skill
    skill = Path(__file__).parent / "skills" / "soul-creator" / "SKILL.md"
    if skill.exists():
        ctx.register_skill("soul-creator", skill)
