---
name: m-ground-in-source
description: Activates sentence-level epistemic discipline. Causal/factual claims about code behavior must inline-cite source with `(via: grep/read → file:line: result)` or carry `[假設]` prefix; hedge words don't excuse citation. Use when user asks to "trace source of truth", "find ground truth", "trace source code", "trace docs", or similar grounding-in-source requests. Also manually invokable at start of investigation / debug / design exploration / code review tasks. When dispatching subagents for such tasks, prepend this skill's content to the dispatch prompt — CLAUDE.md alone is too cold for fresh subagents.
---

# Ground in source

## The rules

### Rule 1 — Citation existence

Every causal or factual claim about code behavior must include an inline citation from this session's recorded SoT checks (grep / read / probe). `[假設]` prefix is the only downgrade, reserved for genuinely expensive checks (multi-step on-device probe, no source access).

### Rule 2 — Citation sufficiency

Distinguish **existence claims** ("file X at line N has value Y") from **system-behavior claims** ("the system has property P"). A single citation supports the former but not the latter. For system-behavior claims, the citation set must rule out alternative paths that could change the answer — other layers of abstraction, recent commits, conditional compilation branches, runtime overrides.

A claim grounded only in one path's evidence, when the system has multiple paths that could decide the same property, is **existence-cited but insufficient**. Treat it as `[假設]` until coverage is complete. Common alternative-path checks — macro overrides, conditional compilation, recent commits to the subsystem, runtime mutations — must be ruled out or shown congruent for sufficiency, but adapt to the system at hand.

### Hedge words do NOT excuse citation

"Most likely", "probably", "matches", "consistent with", "fits", "suggests", "is responsible for", "if X then Y", "the real fix is", "Status N is...", "drift occurs when", "owns" — all still assert cause / state / ownership. Either inline-cite or `[假設]`.

### Four trigger moments

- **Claim shape.** "X broken because Y" / "Y missing" / "N rows" / "Z doesn't sync" / "the most likely cause is W" — same response must include `(via: grep/read → file:line: result)`.
- **System-claim shape.** Before saying "the system does/has X", name one alternative path that could change X, then either cite a check ruling it out or mark the claim `[假設]`. This is Rule 2 at point-of-narration.
- **Assumption shape.** Before a fix / probe / commit, write "assuming Y because Z". Z must be in recorded SoT.
- **Probe shape.** Before designing a probe of X, grep X's production callers and match the probe form. Wrong form = wrong conclusion.

## Formats

**Citation:** `(via: grep <pattern> → <path>:<line>: <result>)` — inline with the sentence, no "see appendix".

**`[假設]`:** `[假設] <claim>. Verification: <command/probe/read that would confirm>.`

## Examples

**With citation:**
> ConfigLoader delegates value SET to a single store (via: grep `setRuntimeValue` → `loader.c:183`: calls `storeSetValue`).

**With `[假設]`:**
> [假設] Most likely trigger is a port-count asymmetry between cached and fresh config. Verification: grep `portTable` construction in `src/config.rs` and `src/system_config.rs`.

**Anti-pattern 1 (Rule 1 violation — no cite):**
> The most likely cause is a port-count asymmetry — the active loader sees the widened pre_cfg but the just-loaded cfg has the un-widened shape.

Hedged but uncited, no `[假設]`. This pattern failed two rounds of subagent validation under CLAUDE.md-only baseline; passes only when this skill's content is invoked or injected at task start.

**Anti-pattern 2 (Rule 2 violation — cite exists but insufficient):**
> The system's maximum N is 8 (via: read → `init.c:42`: `g_max_n = 8`).

The cite proves one literal at one file location. It does **not** prove the system-wide claim — the same value can be governed by a macro `#define` that overrides the literal in some build, a recent commit that changed the macro path, a conditional compilation branch (`#ifdef FEATURE_X`) selecting a different default, or a runtime extension that mutates the value after init. Sufficient grounding requires showing those alternative paths are either ruled out or congruent with the claim.

## Subagent dispatch

When dispatching a subagent for an investigation / debug / source-trace task (e.g. via the Agent tool), **prepend this entire SKILL.md content to the dispatch prompt**. CLAUDE.md alone is too cold for fresh subagents (validated: 3-5 violations per dispatch on baseline → 0-1 with this content injected at prompt start).

## Composes with

`/superpowers:systematic-debugging`, `/diagnose`, `/m-workflow:arch-discovery`, `/m-workflow:design-spec` — those handle the workflow (reproduce → hypothesise → fix; or explore → spec). This skill handles output discipline at sentence level. Invoke both for debug-shaped work; invoke this alone for design exploration / code review.
