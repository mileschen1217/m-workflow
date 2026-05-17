# Coverage matrix protocol

The §0 matrix is the operational completeness contract for a discovery doc. Rows = features. Columns = lenses (L1–L16, plus optional L17/L18). Each cell carries one of five states. The matrix is not a checklist — it is the audit trail of how the discovery converged.

## Cell-state vocabulary

| State | Meaning | Cell text format |
|---|---|---|
| `unset` | Never visited. Default state at scaffold time. | `unset` |
| `gap` | Visited; the lens question is real for this feature; nobody has answered it yet. | `gap` |
| `investigating` | Sweep dispatched a helper (Explore / grep / `/m-arch-review` / Context7 / web). Awaiting result. | `investigating` |
| `partial` | A section *touches* this (feature, lens) intersection but does not fully answer the lens question. Cite the partial-coverage section AND name what's still missing. | `partial (§X.Y; missing <what>)` |
| `covered` | The lens question is fully answered in a specific section, and the cell points there. | `covered (§X.Y)` |
| `deferred` | The question is real, but answering it is out of scope for this discovery. Pointer to where it will be resolved. | `deferred (→ <path or skill>)` |
| `N/A` | The lens does not apply to this feature. One-sentence rationale required. | `N/A (<rationale>)` |

**Forbidden cell content:** "yes", "ok", "✓", "see doc", "see §X" without a `§Y` anchor. These are gaps in disguise.

**`partial` exists to prevent over-claiming.** If the cited section *mentions* the feature in passing — e.g. lists it in a state-inventory table without walking its lifecycle, or names it in a flow without the per-step detail — that's `partial`, not `covered`. The cell text must name what's missing so a sweep pass can resolve to either `covered` (by expanding the section) or genuinely `gap` (by acknowledging the partial mention as too thin). Without `partial`, the matrix has only "fully covered" or "not at all," and authors will round up — producing a green matrix that overstates the doc.

## Cell-state transitions

```
unset ──(scaffold complete)──> gap
gap ──(sweep: investigate)──> investigating
gap ──(sweep: defer)──> deferred
gap ──(sweep: N/A)──> N/A
gap ──(section touches feature but doesn't fully answer)──> partial
investigating ──(finding written into §X.Y, fully answers)──> covered (§X.Y)
investigating ──(finding written but only touches the question)──> partial (§X.Y; missing …)
investigating ──(no signal; punt)──> deferred
partial ──(sweep: expand the cited section)──> covered (§X.Y)
partial ──(sweep: drop the partial mention as too thin)──> gap
covered ──(review surfaces the section doesn't fully answer)──> partial
covered ──(section content invalidated)──> gap        # rare; happens when a finding contradicts an earlier section
deferred ──(scope expanded)──> gap                    # then re-sweep
N/A ──(scope expanded)──> gap                         # then re-sweep
```

`investigating` is the only transient state — it should not persist between sessions. If a sweep ends with `investigating` cells, write the partial finding (or revert to `gap`) before stopping.

`partial` is also a working state — it should converge to `covered` or `gap` over time, not become a permanent "we kind of did this" hideout.

## Matrix-complete definition

A discovery is **matrix-complete** when every cell is in `covered`, `deferred`, or `N/A`. No `unset`, no `gap`, no `investigating`.

Status header transitions when matrix-complete:
> `Status: Discovery (in progress)` → `Status: Discovery (matrix-complete)`

After end-of-discovery audit (via `/m-design-review`) clears Critical/High:
> `Status: Discovery (matrix-complete)` → `Status: Discovery (reviewed)`

## Sweep protocol

Codified procedure for `/m-arch-discovery <slug> sweep`:

```
1. Read §0 matrix.
2. Enumerate cells in (`unset` ∪ `gap`) order, row-major (feature × lens).
3. For each cell:
   a. Print: <feature> × <lens-name> — <lens question>
   b. Decide (interactive or autonomous):
      - investigate now → mark `investigating`, dispatch helper
      - defer            → ask for pointer, mark `deferred (→ <pointer>)`
      - N/A              → ask for rationale, mark `N/A (<rationale>)`
      - skip             → leave as `gap`, continue
   c. On `investigate now` complete:
      - Write finding into the right section (per lens-to-section map below)
      - Update cell to `covered (§X.Y)`
4. Loop until no `unset`/`gap` remain, OR user halts.
5. If matrix-complete: prompt user to flip status header.
```

The sweep is observable — at any halt point, the matrix shows exactly what is done, what is in flight, and what is left. This is the deliberate-process property the matrix exists to provide.

## Lens → section map (default)

When a sweep produces a finding, it lands in the section that owns the lens. The template's section-to-lens cross-reference is the source of truth; this is the inverse view.

| Lens | Primary section |
|---|---|
| L1 Functional | §1.1, §4 |
| L2 Ownership | §1.2 |
| L3 Invariants | §1.3 |
| L4 State | §3 |
| L5 Info flow / config plane | §4.1 |
| L6 Config model | §4.1 + §7 |
| L7 Data plane | §4.3, §4.4 |
| L8 Control plane events | §4.2 |
| L9 Platform capabilities | §2.1, §2.4 |
| L10 Platform constraints | §2.2, §2.5 |
| L11 Platform forced behaviors | §2.3 |
| L12 Failure modes | §6 |
| L13 Lifecycle | §1.4, §5 |
| L14 Interfaces | §7 |
| L15 Decisions | §9 |
| L16 Open questions | §8 |

A single finding may land in multiple sections; in that case all matching cells get `covered (§X.Y)` citations.

## Worked example

Discovery slug: `l3-stacking-behavior`. Initial features: `vlan`, `arp`, `svi`, `connected-route`, `failover`. Below is the §0 matrix at three time points during a discovery's life. Only L1–L4 columns shown for brevity.

### T0 — after Setup Mode (matrix bootstrapped)

| Feature \ Lens | L1 Func | L2 Own | L3 Inv | L4 State |
|---|---|---|---|---|
| vlan | unset | unset | unset | unset |
| arp | unset | unset | unset | unset |
| svi | unset | unset | unset | unset |
| connected-route | unset | unset | unset | unset |
| failover | unset | unset | unset | unset |

### T1 — after first authoring session (§1 system model drafted)

| Feature \ Lens | L1 Func | L2 Own | L3 Inv | L4 State |
|---|---|---|---|---|
| vlan | covered (§4.1.1) | covered (§1.2) | gap | covered (§3.1) |
| arp | gap | covered (§1.2) | gap | gap |
| svi | covered (§4.3.2) | covered (§1.2) | covered (§1.3) | gap |
| connected-route | gap | covered (§1.2) | gap | gap |
| failover | gap | gap | gap | gap |

§1 ownership claims happened to cover most of L2 in one pass — that's why all but `failover` flipped together. `failover` is still `gap` for L2 because the role-election story was not yet written.

### T2 — after sweep on (`arp`, L1) and (`svi`, L4)

| Feature \ Lens | L1 Func | L2 Own | L3 Inv | L4 State |
|---|---|---|---|---|
| vlan | covered (§4.1.1) | covered (§1.2) | gap | covered (§3.1) |
| arp | covered (§4.3.4) | covered (§1.2) | gap | deferred (→ ADR-0007) |
| svi | covered (§4.3.2) | covered (§1.2) | covered (§1.3) | covered (§3.2) |
| connected-route | gap | covered (§1.2) | gap | gap |
| failover | gap | gap | gap | gap |

`arp` × L4 was deferred because the SHM layout for ARP cache replication is being settled in a separate ADR. Pointer captured. Discovery doesn't need to re-derive it.

The matrix is now actionable: 7 cells remain (`gap`/`unset`), and they are the explicit work. No surprise gaps surface later, because the lens × feature grid forced every intersection to be considered.

## Anti-patterns

- **`covered` without `§Y` anchor.** "covered" by itself is identical to "yes" — meaningless. Always cite a section.
- **`N/A` without rationale.** A bare `N/A` reads as "I don't want to think about this." One sentence forces the thinking.
- **`deferred` without pointer.** A defer that doesn't say where the answer goes is a black hole. Even `deferred (→ next epic)` is better than bare `deferred`.
- **Letting `investigating` persist.** It's a transient. End-of-session, every `investigating` must resolve to `covered` or revert to `gap`.
- **Splitting the matrix per feature.** Rows = features is intentional. The whole point is the cross-feature visibility — splitting kills it.
- **Adding lens columns ad-hoc.** L1–L16 is the contract. L17/L18 are the only optional additions. New lenses → propose at the skill level (edit `lenses.md`), don't fork per-doc.
