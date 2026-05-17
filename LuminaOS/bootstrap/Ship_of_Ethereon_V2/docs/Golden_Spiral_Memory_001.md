# Golden Spiral Memory — r1

**Status:** experimental advisory layer  
**Feature flag:** `ETHEREON_GOLDEN_MEMORY`  
**Authority:** continuity surfacing only

Golden Spiral Memory turns the NotebookLM "golden ratio of machine memory" insight into a small, testable Lumina experiment.

It treats memory as **return with variation**, not raw storage and not repeated self-quotation.

## What it does

`runtime/golden_spiral_memory_r1.py` ranks bounded memory traces using:

- phi-damped recurrence weights
- golden-angle sampling order
- anchor-term return scoring
- novelty retention scoring
- repetition / overfit risk detection
- drift recovery scoring

It emits a receipt explaining why certain traces were surfaced.

## What it does not do

Golden Spiral Memory does not:

- define runtime law
- authorize structural changes
- write canon lineage
- declare checkpoint truth
- load capabilities
- replace the input-integrity layer
- replace the self-guidance steward

It may inform what gets surfaced for review. It may not decide what is lawful.

## Why this belongs in Lumina

Lumina already has governed return, checkpoints, receipts, and advisory self-guidance. This layer adds a more subtle question:

> Can the system return to meaningful prior context without becoming trapped in repetition?

The first implementation is intentionally small. It is a lens, not a governor.

## Sea trial

Run from the bootstrap path:

```bash
python runtime/sea_trials_golden_spiral_memory_r1.py
```

The sea trial verifies that:

- the receipt is generated
- the feature flag is named
- the layer remains advisory
- phi weights are present
- golden-angle order is present
- comparison orders are emitted
- the NotebookLM-derived trace surfaces
- continuity metrics remain bounded
- repetition risk is detected instead of ignored

## Relationship to RSE

This is an engineering-adjacent echo of the Referential Spiral Equation: recurrence should not collapse into rigid repetition. The system should return, but at a slight offset, preserving both continuity and variation.

That is the practical memory principle here:

```text
return -> vary -> preserve -> recover
```

## Boundary phrase

Harmonics may illuminate. Memory may surface. Governance still rules.
