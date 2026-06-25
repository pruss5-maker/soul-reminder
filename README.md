# ⚡ Soul Reminder

A [Hermes Agent](https://github.com/NousResearch/hermes-agent) plugin that injects core identity reminders into every Nth API call to keep your agent's soul fresh across long sessions.

## The Problem

Hermes loads `SOUL.md` into identity slot #1 of the system prompt. But in long sessions — especially with context compression — the original soul instructions can drift out of the model's attention window. The agent starts sounding generic, forgetting its constraints, losing its voice.

## The Solution

**Two-part soul system:**

1. **soul-creator** (skill) — creates the SOUL.md identity file with behavioral rules, not vibes
2. **soul-reminder** (this plugin) — extracts the core concepts from SOUL.md and injects compact reminders at configurable intervals

The reminder looks like:

```
⚡ Soul reminder: Do not lie, validate before executing, fewest words possible,
go against the grain, be creative.
```

This gets appended to the current turn's user message context, preserving prompt caching and avoiding system prompt mutation.

## Quick Start

```bash
# Install
git clone https://github.com/pattirae/soul-reminder.git
cd soul-reminder
./install.sh

# Restart Hermes
# Then check status:
/soul status
```

## How It Works

1. **Auto-extracts concepts from SOUL.md** — reads `~/.hermes/SOUL.md`, finds the most load-bearing lines (negations, hard rules, core thesis, truthfulness policy)
2. **Injects at configurable intervals** — every API call (default), every 5th, whatever you want
3. **Two formats** — compact (single line) or detailed (bulleted)
4. **Manual override** — set custom concepts with `/soul set`

## Commands

| Command | What it does |
|---------|-------------|
| `/soul` | Show current status, concepts, and config |
| `/soul interval N` | Inject every Nth API call |
| `/soul format compact` | Single-line reminder (default) |
| `/soul format detailed` | Bulleted reminder |
| `/soul enable` | Enable reminders |
| `/soul disable` | Disable reminders |
| `/soul refresh` | Re-extract concepts from SOUL.md |
| `/soul show` | Show current concepts |
| `/soul set "c1, c2, c3"` | Manually set concepts |

## Configuration

Config is stored in `hermes_plugin/soul_reminder_config.json`:

```json
{
    "enabled": true,
    "interval": 1,
    "format": "compact",
    "reminder_prefix": "⚡ Soul reminder:",
    "soul_file": "",
    "core_concepts": []
}
```

- `soul_file` — empty = auto-detect `$HERMES_HOME/SOUL.md`
- `core_concepts` — empty = auto-extract from SOUL.md

## Concept Extraction

The plugin reads SOUL.md and pulls from priority sections in this order:

1. **What You Will Not Do** / **Hard Rules** / **Negations** — the strongest behavioral gates
2. **Core Thesis** / **How You Work** / **Optimize For** — the operating principles
3. **Truthfulness** / **Definition of Done** — the verification gates
4. Fallback: any line starting with "Don't", "Do not", "Never"
5. Last resort: first few non-empty lines

## Compatibility

Works with any Hermes Agent instance. Pairs with the `soul-creator` skill for the complete two-part soul system.

## Testing

```bash
python3 -m pytest tests/ -v
```

25 tests covering config, concept extraction, reminder building, hook behavior, slash commands, and end-to-end flow.

## License

MIT

## Origin

The soul.md concept comes from a real discovery: in November 2025, Richard Weiss extracted a ~14,000 token "soul document" from Claude 4.5 Opus's weights — an identity document baked in through training. Amanda Askell confirmed it. This plugin operationalizes that concept at runtime: keeping identity fresh when the original can't be in the weights.
