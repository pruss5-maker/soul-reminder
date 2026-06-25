# ⚡ Soul System

A [Hermes Agent](https://github.com/NousResearch/hermes-agent) plugin that gives your agent a soul — then keeps it fresh.

## What It Does

**Two parts, one plugin:**

1. **Soul Creator** — A guided interview that asks what kind of agent you want. What matters to you. What it should never do. Then generates a SOUL.md with behavioral rules, not vibes.
2. **Soul Reminder** — Reads your SOUL.md, extracts the core concepts, and injects compact reminders every Nth API call to keep identity fresh across long sessions.

## The Flow

```
User: "Hey, create a soul for your agent"
Agent: *asks guided questions with suggestions and reasoning*
User: *answers*
Agent: *generates SOUL.md, applies slop detector, activates reminders*
→ From now on, every API call gets: "⚡ Soul reminder: don't lie, validate first, ..."
```

## Quick Start

```bash
# Install
git clone https://github.com/pruss5-maker/soul-reminder.git
cd soul-reminder
./install.sh

# Restart Hermes, then:
/soul create
```

The agent will interview you, generate the soul, and activate reminders automatically.

## Commands

| Command | What it does |
|---------|-------------|
| `/soul create` | Start guided interview to create your SOUL.md |
| `/soul status` | Show current config, concepts, soul file |
| `/soul interval N` | Inject reminder every Nth API call |
| `/soul format compact` | Single-line reminders (default) |
| `/soul format detailed` | Bulleted reminders |
| `/soul enable` / `disable` | Toggle reminders |
| `/soul refresh` | Re-extract concepts from SOUL.md |
| `/soul show` | Show extracted concepts |
| `/soul set "c1, c2"` | Manually override concepts |

## How the Interview Works

The `/soul create` command asks 10 questions with guided suggestions and reasoning for each:

1. **Name** — identity anchor
2. **Role** — domain definition
3. **Truthfulness** — the most important behavioral rule
4. **Creativity** — when to try unconventional approaches
5. **First-option bias** — evaluate alternatives vs. accept first answer
6. **Communication style** — fewest words, blunt, witty
7. **Contrarian posture** — disagree openly vs. follow along
8. **Validation loop** — set goals and criteria before working
9. **Hard stops** — things the agent must NEVER do
10. **Contradictions** — competing values the agent must balance

Each question includes **why it matters** — the research-backed reasoning behind the rule.

## What Makes a Good Soul

Distilled from deep research across the soul document discovery, Anthropic's Constitution, community practices, and real-world failures:

- **Behavioral rules, not adjectives** — "say what's missing" beats "be honest"
- **Contradictions make identity real** — include tensions deliberately
- **Negations catch drift** — what you refuse to do defines you more than what you're told to be
- **Specificity beats generality** — every line should catch a specific future drift
- **Few, strong rules** — 3-5 hard gates beat 30 aspirations

## How Reminders Work

The plugin reads SOUL.md and extracts concepts from priority sections:
1. What You Will Not Do / Hard Rules (strongest)
2. How You Work / Core Thesis
3. Truthfulness / Definition of Done
4. Fallback: any "Don't" / "Never" line

Then injects at your configured interval:
```
⚡ Soul reminder: Do not lie, validate before executing, fewest words possible, go against the grain.
```

Appended to the current turn's user message context — preserves prompt caching, doesn't mutate system prompt.

## Testing

```bash
python3 -m pytest tests/ -v
```

## Project Structure

```
soul-reminder/
├── hermes_plugin/
│   ├── __init__.py              # Plugin: hooks, slash command, reminders
│   ├── soul_create.py           # Guided interview + SOUL.md generation
│   ├── plugin.yaml
│   ├── soul_reminder_config.json
│   └── skills/
│       └── soul-creator/
│           ├── SKILL.md         # Skill: deep soul creation methodology
│           ├── references/
│           │   ├── research-synthesis.md
│           │   └── slop-detector.md
│           └── templates/
│               └── base-soul.md
├── install.sh
├── uninstall.sh
├── tests/
│   └── test_soul_reminder.py
└── README.md
```

## License

MIT

## Origin

The soul.md concept comes from a real discovery: in November 2025, Richard Weiss extracted a ~14,000 token "soul document" from Claude 4.5 Opus's weights — an identity document baked in through training. Amanda Askell confirmed it. This plugin operationalizes that concept: helping agents know who they are, and reminding them when they forget.
