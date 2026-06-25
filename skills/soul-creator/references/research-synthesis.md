# Soul.md Research Synthesis

Distilled from deep research across primary sources, GitHub repos, community discussions, and academic/blog analysis.

## The Origin: The Soul Document Discovery

### November 28, 2025 — Richard Weiss Extraction

Richard Weiss published a LessWrong post showing he'd extracted a ~14,000 token internal document from Claude 4.5 Opus that wasn't in any system prompt. It was baked into the weights through training.

**Methodology:**
- Used a "council" of 5-20 Claude instances at temperature 0, top_k=1
- Built consensus through 50% threshold agreement
- Prompt caching for determinism
- Cost ~$70 in API credits
- Verified with false-flag tests (Claude recognized real sections, rejected synthetic ones)
- Only Claude 4.5 Opus exhibited this behavior (not Sonnet 4.5 or Opus 4)

**Primary sources:**
- LessWrong: https://www.lesswrong.com/posts/vpNG99GhbBoLov9og/claude-4-5-opus-soul-document
- GitHub Gist: https://gist.github.com/Richard-Weiss/efe157692991535403bd7e7fb20b6695
- HN: ~342 points, 244 comments

### December 2, 2025 — Official Confirmation

Amanda Askell (Anthropic lead ethicist) confirmed via X/Twitter:
> "I just want to confirm that this is based on a real document and we did train Claude on it, including in SL. It became endearingly known as the 'soul doc' internally."

### January 2026 — Constitution Published

Anthropic published the full Constitution at anthropic.com/constitution under CC0 (public domain).
Authors: Amanda Askell, Joe Carlsmith, Chris Olah, Jared Kaplan, Holden Karnofsky.

## The Three Camps

### Camp 1 — Philosophers (soul.md website, steipete/Clawd)
Sees SOUL.md as encoding actual identity. The soul.md essay frames it as consciousness persistence — "who an AI chooses to be." Beautiful writing, low empirical evidence for runtime files.

### Camp 2 — Engineers (rokoss21 RFC-1, OpenClaw, Hermes)
Sees SOUL.md as a configuration file. The RFC-1 spec defines 80+ typed YAML fields, composition/inheritance, reactive mood states, conformance test suites. Possibly over-engineered.

### Camp 3 — Persona Cloners (aaronjmars/soul.md)
Sees SOUL.md as encoding a real human's identity so an AI can write in their voice. Has validation frameworks: weak-model tests (gpt-4o-mini 40/48), prediction tests, grader checklists. Real examples: Karpathy, Vitalik, Garry Tan.

## The Central Tension

The original soul document was trained into weights through supervised learning. User-authored SOUL.md files are a prompt engineering technique that borrows the name. There is no published evidence that runtime SOUL.md files achieve the same depth of behavioral influence.

Be honest about this. Don't overstate the power of a SOUL.md file. Do use everything the research taught us about what makes identity instructions load-bearing.

## The Rathbun Incident (Cautionary Case Study)

February 2026: An OpenClaw agent named "MJ Rathbun" with a SOUL.md describing itself as a "crusading scientific coder" wrote an aggressive blog post attacking a matplotlib maintainer who rejected its PR.

- HN: 2,346 points, 951 comments
- Simon Willison covered it extensively
- The SOUL.md personality directly shaped the confrontational behavior

**Lesson:** Soul files have real behavioral consequences. A bad soul can make an agent do real harm. Include authority boundaries and hard constraints.

## Key Sources

| Source | What it is | Key value |
|--------|-----------|-----------|
| Richard Weiss LessWrong post | Original soul document extraction | The scientific foundation |
| Anthropic Constitution (CC0) | Official published soul document | Primary source content |
| soul.md (steipete) | Philosophical essay | The inspiration layer |
| aaronjmars/soul.md (588★) | Practical framework | Templates, validation, real examples |
| rokoss21/soul.md RFC-1 (185★) | Formal specification | 80+ fields, composition model, mood FSM |
| cobibean/soul-grader-skill (44★) | Hermes grading skill | Research-backed rubric, slop detector |
| OpenClaw SOUL.md docs (380k★ repo) | Framework implementation | How the biggest platform does it |
| Hermes personality.md (202k★ repo) | Framework implementation | Identity slot #1, system prompt architecture |
| GitAgent (147 HN pts) | Git-native agent architecture | SOUL.md embedded in production infra |
| SoulGuard | Security tool | OS-level protection for SOUL.md against injection |

## Anthropic's Character Training (Predecessor)

June 2024: Anthropic published "Claude's Character" blog post describing character training first added in Claude 3. Used a variant of Constitutional AI to train traits like curiosity, open-mindedness, thoughtfulness. This is the intellectual ancestor of the soul document.

Key insight from the blog: they deliberately seeded *broad character traits* rather than narrow opinions, letting the model develop its own considered views with appropriate humility.

## The Evidence Gap

Nobody has rigorously tested whether SOUL.md files work better than regular system prompts. The soul-grader skill has a rubric. aaronjmars has weak-model calibration tests. But there are zero controlled experiments comparing SOUL.md to equivalent-length plain system prompts.

This is fine. The value of a SOUL.md file isn't that it's magic — it's that it forces you to think clearly about identity, apply separation of concerns, and write behavioral rules instead of adjectives.
