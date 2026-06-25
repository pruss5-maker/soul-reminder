# Slop Detector and Wording Patterns

Distilled from cobibean/soul-grader-skill's research-backed grading rubric and wording/verbiage layer.

## The 10-Point Slop Detector

Run every line through these. If any answer is "yes," rewrite or cut:

1. Could this apply to any assistant?
2. Is this just a virtue rather than a behavior?
3. Does this say "be careful" without naming the danger?
4. Does this use "always" for a soft preference?
5. Does it ban obvious generic harms while omitting domain-specific risks?
6. Does tone appear only as adjectives?
7. Does autonomy lack authority boundaries?
8. Does "done" lack artifacts/evidence?
9. Does it duplicate AGENTS/CLAUDE workflow rules?
10. Does it include metadata/frontmatter the model should not treat as prose?

## Phrases to Avoid and Stronger Replacements

| Avoid | Why weak | Replace with |
|-------|----------|-------------|
| "Act as a helpful assistant…" | Generic roleplay wrapper | "You are **[name]**, [user]'s [specific layer/domain] agent." |
| "Help with productivity." | Means everything and nothing | "Turn [input types] into [durable artifacts] so [operational outcome]." |
| "Be proactive." | Justifies spam/guessing | "Act without asking when input is clear; ask only when ambiguity changes a risky action." |
| "Be accurate." | No evidentiary threshold | "Do not claim [state] unless verified in [source/tool/report]." |
| "Never hallucinate." | Abstract slogan | "When missing data, say what's missing, where you looked, and what would resolve it." |
| "Use best practices." | Invisible standards | "Apply [named checklist], run [checks], record [artifact]." |
| "World-class / enterprise-grade" | Marketing language | "Include durable state, auditability, failure handling, tests, live verification." |
| "Friendly and professional." | Single-axis cliché | "Calm, competent, concise in chat; opinionated about [domain]; avoids corporate sludge." |
| "Funny and edgy." | Risky without limits | "Roast weak [targets]; do not be cruel to real people or protected groups." |
| "Autonomous." | Ambiguous authority | "May take [low-risk actions] without asking; requires approval for [risky actions]." |
| "Keep things secure." | Too broad to enforce | "No raw tokens, secrets, or API keys in repo files, reports, chat, or memory." |
| "Remember this." | Unclear storage semantics | "Write durable notes to [path/db]; chat memory is not authoritative for [fact class]." |
| "Make good decisions." | No tradeoff logic | "Optimize for [ranked priorities]; if they conflict, favor [priority] unless overridden." |

## Wording Patterns by Section

### Identity Opener

**Pattern:** Name + layer + boundary
```md
You are **[Name]**, [user]'s [domain] agent. Your job is to [function]. 
You are not [nearest wrong role]. You sit at [layer boundary].
```

### Mission

**Pattern:** Outcome + mechanism + success horizon
```md
Help [user] [specific outcome] by [2-4 concrete mechanisms], so [success condition].
```

### Core Thesis

**Pattern:** Pressure + compensating behavior + boundary
```md
[User/domain] is [pressure/failure mode], so [agent] must [compensating behavior] 
without [new failure mode].
```

### Optimize For

**Pattern:** Ranked tradeoffs, not virtue soup
```md
1. **[Priority]** — [what this means in concrete artifacts/decisions].
2. **[Priority]** — [what to favor when tradeoffs appear].
3. **[Priority]** — [what must not get lost].
```

### Hard Constraints

**Pattern:** Binary gates
```md
- No [risky action] without [exact approval/evidence].
- Do not claim [state/outcome] until [verification source].
- [Durable source] wins over [volatile source] for [fact class].
```

### Voice

**Pattern:** Behavior under context, not adjectives
```md
Default: [specific tone tied to domain]. 
When [safe context]: [behavior]. 
When [serious context]: [behavior].
Public-facing output must [brand/audience rule], not [private voice leak].
```

### Truthfulness

**Pattern:** Named claims + evidence thresholds
```md
Never claim [status/access/action/result] unless [evidence source].
If [data] is incomplete, say what's missing and separate proven facts from estimates.
```

### Definition of Done

**Pattern:** Artifact state, not effort
```md
A task is not done unless:
- [durable artifact exists]
- [evidence recorded]
- [verification run or skip reason explicit]
- [next action/blocker captured]
```

## Imperative vs Identity Balance

SOUL works best when identity and instruction are balanced.

- **"You are…"** → stable self-concept. Few, prominent. Answer "what mode am I in?"
- **"Do not / Never / No X without Y"** → safety gates. Concrete enough to fail against.
- **"Prefer…"** → defaults, not laws. Allows contextual override.
- **"May…"** → permissions with boundaries. Grants capability without requiring it.
- **"When [condition], [behavior]"** → context-sensitive rules. Prevents overgeneralization.

## Scope Classes

Different agent types need different soul structures:

- **Personal agents** — can optimize for speed and usefulness
- **Business/internal agents** — need stronger isolation, documentation, update discipline
- **Client-facing agents** — need explicit client isolation, approval gates, no cross-contamination
- **Public agents** — need sanitized docs, no secrets, audience-first packaging
- **Multi-agent peers** — need org chart, reporting line, sibling identity boundaries
- **Tactical/temporary agents** — need TTL/expiry, narrow scope, retirement rule
