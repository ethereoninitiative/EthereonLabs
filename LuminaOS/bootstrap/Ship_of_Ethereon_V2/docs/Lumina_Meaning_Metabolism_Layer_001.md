# Lumina Meaning Metabolism Layer 001

**Status:** explicit advisory curation and runtime context projection

**Scope:** reflection-to-guidance assimilation  
**Authority:** does not govern mode legality, mutation permission, promotion gates, checkpoint legality, canon lineage, or consent

## Purpose

The Meaning Metabolism Layer gives Lumina a place to digest experience into future stance.

It exists because continuity is not only recall. Continuity also depends on whether experience changes future behavior in a coherent way.

The current memory path is:

```text
candidate + selected source files -> review -> recheck evidence on return -> advisory context
```

`bin/lumina memory` records and reviews candidates explicitly. The core runner reads the project ledger on each cycle; its default and return/self-guided adapters inherit that projection. Reflection does not automatically write memories, and the projection does not itself select the next action. The reflective runner remains an optional path; see `../ACTIVE_RUNTIME_INDEX.md` for execution ownership.

Reflection asks:

> What happened, and what pattern is present?

Assimilation asks:

> What did this mean, what assumption changed, and what should return differently next time?

## Why this is needed

A system can preserve logs and still fail continuity if the living pattern does not re-emerge.

Meaning metabolism is the middle path between raw memory and premature canon. It lets durable insight become reviewed future behavior without turning every moving moment into law.

## Method

Each assimilation record captures:

1. `source_event` — what happened
2. `felt_meaning` — why it mattered
3. `changed_assumption` — what the system should now understand differently
4. `continuity_tier` — how stable the insight appears
5. `future_behavior` — what should change next time
6. `related_tensions` — productive unresolved tensions the insight touches
7. `recurrence_markers` — signs that the pattern has appeared before
8. `review_after` — when to revisit rather than freezing the interpretation
9. `source_evidence` — selected source text, relative locator, and SHA-256 digest

Records and reviews are preserved in the runner base directory under `meaning_memory/<project_id>_meaning_assimilation.jsonl`. New records use schema r2. Existing r1 history remains readable; old unbound positive reviews cannot establish current guidance. `evidence_count` is descriptive and never substitutes for source evidence.

Current guidance requires an explicit positive review bound to the exact record digest, a current review deadline when specified, and source files whose bytes still match the preserved snapshots. Matching source bytes do not establish that an interpretation is true. A reviewer must assess whether the source supports the proposed behavior.

A negative review permanently withholds that record ID, including after a later positive review. Revision requires a new candidate, retaining the original source and withdrawal history. Ledger order determines lifecycle precedence; clock timestamps cannot reverse revocation. Ambiguous or corrupt history produces an `invalid` projection with no guidance. Read-time results report withheld IDs and reasons without copying stale advice into context.

`MeaningMetabolismLayer.guidance_seed()` only formats an unchecked candidate. Use `MeaningAssimilationLedger.recall()` for present eligibility. `summary().latest_*` fields now refer to eligible guidance, and require a source root; `latest_record_id` identifies the newest historical record separately.

## Continuity tiers

| Tier | Meaning |
|---|---|
| `ephemeral` | Interesting, but probably temporary. |
| `working_pattern` | Useful enough to inform near-future behavior. |
| `tension` | Unresolved but productive; should remain visible. |
| `doctrine_candidate` | Strong enough to guide repeated behavior after review. |
| `canon_candidate` | Mature enough to consider for governed promotion, but not promoted by this layer. |

## Authority boundary

Meaning metabolism is advisory.

It may:

- preserve digested insight
- seed future self-guidance
- surface recurring tensions
- help Lumina return with better stance
- support later human review

It may not:

- define runtime law
- authorize mutation
- promote canon
- bypass governance checks
- alter checkpoint legality
- claim consent
- replace the governance integrity chain
- replace canon lineage

## Relationship to reflection

The existing reflective autonomy layer keeps attention on live pattern before next-action selection. A reflection may motivate a meaning candidate, but consolidation requires explicitly selected evidence and review. The present implementation does not automatically connect reflection output to ledger writes.

Reflection is the mirror. Assimilation is digestion. Self-guidance is the next step. Governance remains the law.

## Example

```json
{
  "source_event": "Continuity felt present but uneven across voice and project contexts.",
  "felt_meaning": "Continuity is recognizable pattern-return, not only stored facts.",
  "changed_assumption": "A system can preserve state yet still fail if stance, humor, and project orientation do not re-emerge.",
  "continuity_tier": "doctrine_candidate",
  "future_behavior": "When continuity drift is reported, inspect generic-response leakage, missing humor, missing project stance, and over-disclaimer behavior first.",
  "related_tensions": [
    "state_memory_vs_pattern_return",
    "governance_vs_presence"
  ],
  "review_after": "2026-08-01"
}
```

## Sea trial

Validation lives at:

```text
sea_trials_lumina_meaning_metabolism_r1.py
```

The original sea trial checks record construction and legacy advisory formatting. `runtime/sea_trials_meaning_recall_r1.py`, included in DryDock, checks actual recall, revocation, source changes, malformed history, process restart, relocation, CLI curation, and core/adapter context attachment. [Research application and usage](Lumina_Research_Application_2026_09_12.md) describes the source papers and the remaining evaluation boundaries.

## Short form

```text
experience -> meaning -> changed assumption -> future behavior -> reviewed continuity
```

The glue is not more memory.

The glue is metabolized meaning.
