# Bootstrap a new project

## Step 0 — Check m-workflow config

Read `.claude/m-workflow.yaml` in the project root.

**Absent** → invoke `/m-workflow:init` now. Pass explicit path defaults so config is written deterministically even if the context is non-interactive:

    /m-workflow:init --specs-dir .swarm/specs --adr-dir .swarm/docs/adr \
      --epics-dir .swarm/epics --plans-dir .swarm/plans \
      --archive-specs-dir .swarm/archive/specs

In a non-interactive context `adopted_disciplines` will be left empty; print the notice:
> `source-as-truth available but not adopted — run /m-workflow:init interactively to add`

Then continue to step 1.

**Present AND `source-as-truth` NOT in `adopted_disciplines`** → print:
> `source-as-truth available but not adopted — run /m-workflow:init to add`

Continue to step 1. Do NOT re-prompt paths; do NOT silently skip the notice.

**Present AND `source-as-truth` already in `adopted_disciplines`** → continue silently.

Discipline-menu logic stays solely in `init`; bootstrap never duplicates it.

## Steps

1. Copy `templates/ROADMAP.md` to the project root.
2. Create `.swarm/epics/README.md` with the binding rule (copy from this skill's "The Rule" section).
3. Add `## Doc Routing` to project CLAUDE.md using the path schema below.
4. Scaffold the first epic (above).
