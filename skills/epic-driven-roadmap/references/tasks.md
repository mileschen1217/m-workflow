# Scaffold a task

Tasks are finer-grained execution units within an epic phase. They produce L0 artifacts (`result.json`, optional `review.md`) per the multi-vendor dispatch convention.

1. Pick a task-id — `T<NN>-<short-slug>`, lowercase, hyphen-separated. NN is sequence within the epic (T01, T02, ...).
2. Resolve concrete path from project CLAUDE.md § Doc Routing — typically `.touchstone/epics/<slug>/tasks/<task-id>/`. <!-- phase-2-carve-out -->
3. Copy `templates/task-contract.md` to `<epics-dir>/<slug>/tasks/<task-id>/contract.md`. Fill in: `task_id`, `epic` slug, `role`, `runtime`, `created`. <!-- phase-2-carve-out -->
4. (optional) Copy `templates/task-result.json` to the same dir as `result.json` initialized with `status: pending`. <!-- phase-2-carve-out -->
5. Commit.

## Task contract scope

A task contract is a unit of cohesive change that an executor (CC subagent, Codex, human) can hold in mind, complete, and have reviewed as one decision. Scoping is judgment — these heuristics resolve the "is this one task or two?" question.

**Default scope of one contract:** all changes that share *all* of these properties:

- **One repo / one runtime.** Different repos and different language runtimes (Rust core vs Python tests vs C plugin) are separate review surfaces and separate executors; do not bundle.
- **One responsibility.** A single named change in the spec's "Interfaces / Contracts" or "Architecture" section. Adding a function and updating its callers is one responsibility; adding two unrelated functions is two.
- **One review boundary.** A reviewer can sensibly evaluate the diff as a unit without needing to context-switch between unrelated concerns.
- **One acceptance criterion bundle.** The contract's acceptance criteria are co-satisfied by the same change. ACs that are satisfied by *different* changes belong in *different* contracts even if they touch the same file.

**One contract may bundle multiple file edits when:**

- Edits are tightly coupled (signature change ripples through callers; rename and its references; struct field add and its serializer).
- The pattern is the same across all files (e.g., "add stacking-aware bound to plugin schema, applied identically to `config_ifmib.rs` and `config_mxport.rs`"). Treat as one contract with the pattern stated once and the file list as a parameter.
- Local helper plus its only caller — no point splitting if the helper has no other client.

**Split into multiple contracts when:**

- A decision artifact (ADR) must land before code — the ADR is its own (CC-owned) task; the consuming implementation is a separate (potentially Codex-owned) task. Sequential dependency on a *decision*, not on code.
- One implementation must land and be verified before another can be written or tested (sequential code dependency where the second can't even be specified without the first).
- The runtime is a CC-vs-Codex split — Codex contracts are mechanical implementation; CC handles work needing project-specific tooling (build orchestration, multi-repo commit discipline, bench access, on-device verification).
- Total scope is large (rule of thumb: more than ~10 file edits, or work that wouldn't fit in one focused execution session) — split along the strongest natural seam (repo, module, layer).
- Different parts of the change need different reviewers / different vendor (e.g. Rust core change goes to a Rust reviewer; Python test goes to a Python reviewer).

**Cross-repo work is NOT automatically a split.** If a small cohesive feature touches 3-4 repos with 1-2 files each, and one executor can hold it all in mind, one contract listing the per-repo edits is correct. The /nos-commit-per-repo ceremony is the orchestrator's responsibility (CC plan tasks), not the contract's. Split per-repo only when the change is large enough that splitting along the repo seam aids reviewability or unblocks parallelism.

**Anti-pattern: one task per file edit.** Splitting along file lines without semantic justification produces high-volume, low-cohesion contracts that obscure the change's intent and inflate review overhead. Bundle by responsibility, not by file count.

**Anti-pattern: one task per AC.** ACs in the spec are observable contracts, not always implementation units. A single contract can satisfy several ACs simultaneously when the underlying change is one cohesive thing (e.g., adding the role gate satisfies AC-REJECT-1 and AC-REJECT-3 with one code change).

**Distribution across executors.** When the plan mixes CC orchestration and Codex implementation:

- Code change with clear contract + standard tooling (cargo build inside repo) → Codex (`codex-implementer` or `codex-tdd`).
- Code change requiring out-of-sandbox tooling (project-specific build wrappers like `/nos-build-buildroot`, multi-repo commit discipline like `/nos-commit`, live-bench verification) → CC (sonnet hybrid implementer or human).
- Decision artifacts (ADR, spec revision, retrospective) → CC.
- Test authoring against live infrastructure → CC (executor needs test-infra context that lives in CC memory).
- Verification / build / commit → CC orchestrator regardless of who wrote the code.

The plan markdown sequences contracts and CC tasks together; contracts live under `tasks/`, CC tasks live as plan steps. Both reference each other by ID so the plan reads end-to-end.

## Close a task

1. Mark contract.md frontmatter `status: done` (or `failed`). <!-- phase-2-carve-out -->
2. Update result.json with completion fields: `status`, `summary`, `files_changed`, `commands_run`, `tests_passed`, `risks`, `handoff_notes`, `completed_at`, `duration_ms`, `fallback_reason`.
3. (optional) If a cross-provider review ran, ensure `review.md`, `raw_cc.md`, `raw_codex.jsonl` are present.
4. Commit.

## Task status vocabulary

`pending | in-flight | blocked | done | failed`. Distinct from epic status (`proposed | active | paused | done | cancelled`) because tasks are finer-grained.
