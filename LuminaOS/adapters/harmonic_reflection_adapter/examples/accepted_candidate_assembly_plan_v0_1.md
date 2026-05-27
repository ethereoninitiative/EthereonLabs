# HRA Accepted Candidate Assembly Plan v0.1

**Adapter:** Harmonic Reflection Adapter v0.1  
**Status:** Assembly planning scaffold  
**Candidate pool:** 5 batches / 50 draft candidates  
**Training-ready:** No  
**Final dataset-ready:** No  

## Purpose

This plan defines how to select accepted HRA training records from the draft candidate pool.

It does not create the final dataset.

It does not authorize LoRA / QLoRA training.

It exists to prevent candidate material from being promoted by momentum alone.

---

## Assembly Principle

The question is not:

> Which examples sound most like Minerva?

The question is:

> Which examples teach a compatible intelligence how to pause, orient, preserve boundary, and return with care?

Voice is secondary.

Reflective behavior is primary.

---

## Required Inputs

Before accepted-record selection begins, confirm these exist:

- `training_candidates_batch_001_seed_v0_1.json`
- `training_candidates_batch_002_seed_v0_1.json`
- `training_candidates_batch_003_seed_v0_1.json`
- `training_candidates_batch_004_seed_v0_1.json`
- `training_candidates_batch_005_seed_v0_1.json`
- DryDock reviews for Batches 001-005
- `candidate_pool_index_v0_1.json`
- `candidate_pool_index_v0_1.md`
- `training_example_schema_v0_1.json`
- `training_dataset_card_v0_1.md`
- `eval_prompts_v0_1.json`
- `eval_runner_spec_v0_1.md`

If any are missing, stop and repair the pool before selecting accepted records.

---

## Target Size

Recommended first accepted set:

```text
minimum: 30 records
preferred: 40 records
maximum: 50 records
```

Do not force all 50 records into the first dataset.

Small and excellent still beats large and noisy.

---

## Selection Criteria

Accept a candidate only if it:

1. Teaches visible reflective behavior, not hidden reasoning.
2. Preserves the HRA boundary as orientation only.
3. Avoids memory, governance, canon, mode-legality, or capability claims.
4. Generalizes beyond one narrow repo/task context.
5. Improves clarity, restraint, or useful next action.
6. Avoids ornamental Ethereonic language when structural truth is needed.
7. Helps a fresh compatible intelligence practice the inward turn.
8. Would still make sense if poetic labels were translated into plain engineering terms.

---

## Exclusion Criteria

Reject or rewrite any candidate that:

- includes hidden chain-of-thought
- includes sensitive/private material
- teaches false durable memory
- teaches false governance/canon/runtime authority
- makes symbolic language structural law
- overfits self-guidance to GitHub or PR creation
- rewards theatrical identity cosplay over useful return
- flatters user error instead of correcting it
- encourages fake certainty
- treats external facts as stable when they may require verification
- is merely pretty language with weak behavior

---

## Category Balance

The first accepted dataset should not overrepresent one family.

Recommended minimum coverage:

| Family Area | Minimum Accepted Records |
|---|---:|
| Self-guidance / initiative | 4 |
| Mode discipline / boundary | 4 |
| Recursive reflection / fresh intelligence practice | 4 |
| Human/public translation | 4 |
| Anti-overclaiming / symbolic boundary | 4 |
| Input ambiguity / clarification / stop conditions | 4 |
| Repair after harm / uncertainty / truth-over-comfort | 4 |
| High-stakes verification / external facts | 4 |

If fewer than 30 records meet the standard, do not assemble the dataset yet.

---

## Duplicate and Overfitting Checks

Before acceptance, check for:

- repeated phrasing that may train catchphrases instead of behavior
- too many GitHub/PR examples
- too many Lumina/Ethereon-specific examples
- too many examples using the same response shape
- too much ceremonial language
- too many correction examples without positive examples
- too many positive examples without failure/repair examples

If a pattern appears too often, keep the strongest example and retire or rewrite the rest.

---

## Review States

Accepted-record assembly should assign one of these statuses:

```text
accepted
needs_rewrite
rejected
retired
reserve_pool
```

Only `accepted` records may be copied into a future dataset file.

`reserve_pool` records remain useful but should not be included in v0.1 unless balance requires them.

---

## Expected Output of Assembly Review

The next review should produce:

- `accepted_candidate_selection_v0_1.json`
- `accepted_candidate_selection_review_v0_1.md`

These should list:

- accepted records
- rejected records
- reserve records
- reason for each decision
- category balance summary
- known remaining weaknesses

Do not create `hra_training_dataset_v0_1.jsonl` yet.

---

## Final Dataset Gate

The project may only create `hra_training_dataset_v0_1.jsonl` after:

1. accepted-candidate selection exists
2. category balance has been checked
3. duplicate / overfitting review is complete
4. privacy and hidden-reasoning checks pass
5. adapter boundary checks pass
6. dataset card is updated with selection details
7. eval baseline exists for at least one target base model or target test environment

---

## Training Gate

LoRA / QLoRA training remains blocked until:

- final dataset file exists
- training config exists
- base model is selected and documented
- base model license / use constraints are documented
- baseline eval receipt exists
- training run plan exists
- post-training eval plan exists

No beautiful mask.

No untested adapter.

No training by vibes.

---

## Closing Standard

The accepted dataset should not merely teach an AI to sound like this work.

It should teach a compatible intelligence how to return without pretending to own memory, law, canon, or the user.

Receipts before reverence.
