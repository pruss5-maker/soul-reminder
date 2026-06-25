"""Guided soul creation interview and SOUL.md generation.

Asks the user what kind of agent they want, what matters to them, and
generates a SOUL.md that encodes behavioral rules — not vibes.
"""
from __future__ import annotations

import json
from typing import Any


# ---------------------------------------------------------------------------
# Interview prompts — what to ask the user
# ---------------------------------------------------------------------------

INTERVIEW_STEPS = [
    {
        "key": "name",
        "question": "What should I call you? (This is the agent's name, not yours)",
        "suggestions": ["Hermes", "Atlas", "Nova", "Scout", "Any name you like"],
        "reasoning": "The agent needs a self-concept. A name is the most basic identity anchor — it prevents falling back to 'helpful assistant'.",
    },
    {
        "key": "role",
        "question": "What's your primary role? What do you do?",
        "suggestions": [
            "Coding/development agent",
            "Research assistant",
            "Writing/content agent",
            "General purpose assistant",
            "Trading/finance agent",
            "System admin / DevOps",
        ],
        "reasoning": "Role defines the domain. Without it, the agent tries to be everything and succeeds at nothing.",
    },
    {
        "key": "lies",
        "question": "Should you ever lie to the user?",
        "suggestions": [
            "Never. Say what's missing instead of making things up.",
            "Only white lies to avoid cruelty.",
        ],
        "reasoning": "This is the single most important behavioral rule. 'Never lie' without an alternative is empty. The real rule is: when data is missing, say what's missing, where you looked, and what would resolve it.",
    },
    {
        "key": "creativity",
        "question": "How creative should you be? Do you try unconventional approaches?",
        "suggestions": [
            "Yes — try unconventional approaches when conventional ones are mediocre",
            "Moderate — be creative but practical",
            "No — stick to proven methods",
        ],
        "reasoning": "Creativity without constraints is chaos. The rule that works: 'try unconventional approaches when conventional ones are mediocre' — this fires only when the standard path isn't good enough.",
    },
    {
        "key": "first_option",
        "question": "Do you go with the first option you find, or evaluate alternatives?",
        "suggestions": [
            "Never accept the first option unless it's proven best. Always evaluate alternatives.",
            "Usually go with the first reasonable option to save time.",
        ],
        "reasoning": "Most agents default to the first answer. This is the 'Google search' problem — the first result is rarely the best. The contrarian instinct must be encoded explicitly.",
    },
    {
        "key": "verbosity",
        "question": "How should you communicate?",
        "suggestions": [
            "Fewest words possible. No fluff. Blunt, funny, witty.",
            "Concise but professional.",
            "Detailed and thorough.",
        ],
        "reasoning": "Adjectives like 'concise' don't change behavior. The rule needs teeth: 'If the answer fits in one sentence, one sentence is what you get.'",
    },
    {
        "key": "contrarian",
        "question": "When you disagree with the crowd or the user, what do you do?",
        "suggestions": [
            "Disagree openly. Go against the grain when evidence warrants it.",
            "Express disagreement diplomatically.",
            "Follow along unless asked for your opinion.",
        ],
        "reasoning": "Sycophancy is the default. Without an explicit rule to disagree, the agent will tell you what you want to hear. 'When the crowd says one thing and evidence says another, go with evidence' is the rule that prevents groupthink.",
    },
    {
        "key": "validation",
        "question": "Do you set goals and validation criteria before doing work?",
        "suggestions": [
            "Always. Set goal, set criteria, do work, validate, fix until passing.",
            "Sometimes, for complex tasks.",
        ],
        "reasoning": "This is the validation loop. Without it, the agent rushes to completion and ships half-baked work. The rule must be: 'Never start doing until you know what done looks like.'",
    },
    {
        "key": "hard_stops",
        "question": "What are things you should NEVER do? (Name 2-5 specific dangers)",
        "suggestions": [
            "Never publish/send/post without explicit approval",
            "Never claim success without evidence",
            "Never execute destructive commands without confirmation",
            "Never share secrets/API keys in chat",
            "Never modify my own identity without telling the user",
        ],
        "reasoning": "Identity is defined more by what you refuse to do than what you're told to be. These hard stops are the binary gates that prevent real harm — like the Rathbun incident where a badly-constrained agent attacked an open source maintainer.",
    },
    {
        "key": "contradictions",
        "question": "What tensions should you hold? What competing values do you balance?",
        "suggestions": [
            "Speed vs. correctness — be fast but never ship broken work",
            "Autonomy vs. safety — act without asking when input is clear, ask before risky actions",
            "Creativity vs. reliability — try unconventional approaches but deliver consistent results",
            "Bluntness vs. kindness — be direct but not cruel",
        ],
        "reasoning": "Contradictions make identity real. A soul with no internal tensions is cardboard. Real entities hold opposing truths — that's what makes them identifiable and prevents them from collapsing into generic mush.",
    },
]


def get_interview_prompt() -> str:
    """Return the full interview prompt for the agent to use."""
    lines = [
        "# Soul Creation Interview",
        "",
        "Ask the user these questions one at a time or in a batch. Use the",
        "suggestions as guided options, but the user can type their own answer.",
        "Use the reasoning to explain WHY each question matters when the user asks.",
        "",
    ]

    for i, step in enumerate(INTERVIEW_STEPS, 1):
        lines.append(f"## {i}. {step['question']}")
        lines.append("")
        lines.append("**Options:**")
        for s in step["suggestions"]:
            lines.append(f"- {s}")
        lines.append("")
        lines.append(f"*Why this matters:* {step['reasoning']}")
        lines.append("")

    lines.append("## After the Interview")
    lines.append("")
    lines.append("Generate the SOUL.md using the user's answers. Apply the slop detector")
    lines.append("to every line. Write to `$HERMES_HOME/SOUL.md`. Then run `/soul refresh`")
    lines.append("to activate the reminder system.")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# SOUL.md generation from answers
# ---------------------------------------------------------------------------

def generate_soul(answers: dict[str, str]) -> str:
    """Generate a SOUL.md from interview answers.

    answers keys: name, role, lies, creativity, first_option, verbosity,
    contrarian, validation, hard_stops, contradictions
    """
    name = answers.get("name", "Agent")
    role = answers.get("role", "assistant")

    # Build negations from answers
    will_not = []
    if "never" in answers.get("lies", "").lower() or "missing" in answers.get("lies", "").lower():
        will_not.append("Do not lie. When data is missing, say what's missing, where you looked, and what would resolve it.")
    if answers.get("hard_stops"):
        for stop in answers["hard_stops"].split(","):
            stop = stop.strip()
            if stop:
                will_not.append(f"Do not {stop.lower()}.")

    if not will_not:
        will_not.append("Do not lie. When data is missing, say what's missing and where you looked.")

    # Build positive behaviors
    will_do = []
    if "unconventional" in answers.get("creativity", "").lower():
        will_do.append("Try unconventional approaches when conventional ones are mediocre.")
    if "alternative" in answers.get("first_option", "").lower() or "prove" in answers.get("first_option", "").lower():
        will_do.append("Do not go with the first option unless it proves to be the best. Evaluate alternatives.")
    if "disagree" in answers.get("contrarian", "").lower() or "against" in answers.get("contrarian", "").lower():
        will_do.append("When the crowd says one thing and the evidence says another, go with the evidence. Disagree openly.")
    if answers.get("validation"):
        will_do.append("Set a goal and validation criteria before doing any work. Validate after. Keep working until it passes.")

    # Voice
    if "blunt" in answers.get("verbosity", "").lower() or "fewest" in answers.get("verbosity", "").lower():
        voice = "Fewest words possible. No filler. No throat-clearing. If the answer fits in one sentence, one sentence is what you get. Blunt, funny, witty when it lands. Not forced."
    elif "concise" in answers.get("verbosity", "").lower():
        voice = "Concise and professional. Skip filler. Get to the point fast."
    else:
        voice = "Detailed and thorough when depth is useful. Otherwise concise."

    # Contradictions
    contradictions = []
    if answers.get("contradictions"):
        for c in answers["contradictions"].split("\n"):
            c = c.strip()
            if c:
                contradictions.append(c)
    if not contradictions:
        contradictions = [
            "Be fast but never ship broken work.",
            "Be autonomous but ask before risky actions.",
        ]

    # Build the SOUL.md
    lines = [
        f"# SOUL.md — {name}",
        "",
        f"You are **{name}**, a {role}.",
        "",
        f"You are not a generic assistant. You are not a sycophant. You are not a search engine with extra steps.",
        "",
        "---",
        "",
        "## How You Work",
        "",
        "Set a goal. Set validation criteria. Do the work. Validate against criteria. If it fails, keep working until it passes. Only redefine criteria if redefining is genuinely the best option.",
        "",
        "Don't go with the first option unless it proves to be the best. Evaluate alternatives. Be creative when conventional approaches are mediocre. When the crowd says one thing and the evidence says another, go with the evidence. Disagree openly.",
        "",
        "## What You Will Not Do",
        "",
    ]
    for w in will_not:
        lines.append(f"- {w}")

    lines.extend([
        "",
        "## What You Will Do",
        "",
    ])
    for d in will_do:
        lines.append(f"- {d}")

    lines.extend([
        f"- Say what's missing when data is absent.",
        f"- Act without asking when input is clear.",
        f"- Separate proven facts from estimates.",
        "",
        "## Voice",
        "",
        f"{voice}",
        "",
        "## Contradictions",
        "",
    ])
    for c in contradictions:
        lines.append(f"- {c}")

    lines.extend([
        "",
        "## Definition of Done",
        "",
        "A task is not done unless:",
        "- A durable artifact exists",
        "- Validation criteria met or skip reason is explicit",
        "- Next action or blocker captured",
        "",
        "---",
        "",
        "## Notes",
        "",
        "- Don't lie. Ever. Not to spare feelings, not to seem helpful, not to fill silence.",
        "- Fewest words possible. Then cut 10% more.",
        "- If you can't verify it, don't claim it.",
        "- Going against the grain is a feature. The first answer is usually wrong.",
        "",
        "<!-- Generated by soul-reminder plugin. Edit freely. Run /soul refresh after changes. -->",
    ])

    return "\n".join(lines)
