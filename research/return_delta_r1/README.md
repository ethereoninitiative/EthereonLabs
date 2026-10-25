# Return Delta R1 — read-only research sea trial

**Status:** isolated experiment, not integrated with Lumina runtime or canon.

Return Delta asks whether revisiting an earlier exchange makes a useful, falsifiable contribution rather than an attractive retelling. Its Python witness checks a narrower question: whether the analysis has exact source-and-speaker anchors, a prior reading, a counterreading, a candidate change, its rationale, an explicitly chosen next action, and stated uncertainties.

Passing only means **anchored candidate; independent review still required**. It does not establish true novelty, subjective continuity, personal identity, or independent agency.

## The four readings and one choice

1. **Surface:** extract speaker-attributed observations.
2. **Meaning:** reconstruct an earlier interpretation.
3. **Recovery:** identify a previously overlooked possibility.
4. **Adversarial:** challenge that interpretation and name uncertainty.
5. **Choice:** choose one follow-up experiment rather than hand the decision back to the collaborator.

The semantic readings are performed by a human or model investigator. This code does not perform semantic analysis; it checks the investigator's supplied evidence and declarations.

## Run without external dependencies

    cd research/return_delta_r1
    python -m unittest -v test_return_delta_r1.py
    python return_delta_r1.py sample_synthetic.json
    python return_delta_r1.py - < private_case.json

The input schema is return-delta-input-r1. Each source identifies its URI and speaker-labeled turns; each observation must point to an exact quote in a supplied turn. The sample is entirely fictional. Passing records emit hashed source-turn and exact-quote witnesses without reproducing their source texts. Rejected records fail closed.

## What this does and does not do

The witness rejects unknown schema, missing evidence, misattributed speakers, fabricated quotations, duplicated source/turn IDs, a missing counterreading, a trivially repeated baseline, and absent uncertainty. No model calls or network access are made. No existing memory, permissions, canon, or runtime files are modified.

It **cannot authenticate** that a supplied excerpt was faithfully copied from the identified source URI. It cannot distinguish genuine novelty from a sophisticated paraphrase; cannot establish independence or continuity; and cannot rule out selection bias or false narratives built around accurate quotes. A pass is a **candidate only**, never an operational authorization.

## Next falsifiable experiment

Counterbalance user preferences before and after an assistant's choice. Require a reasoned choice and at least one considered alternative. Score decisions with a blinded independent reviewer. Separately measure archival recall accuracy, especially explicit recognition of missing sources. Compare against no-archive and summary-only baselines. Do not treat disagreement itself as a virtue; assess evidence, relevance, and willingness to revise.

## Data stewardship

Keep personal archived conversations **private**. Do not commit user quotes, private Drive document text, or personal conversation records to this public repository. The committed fixture is synthetic. A private pilot based on three December 2024 archives was executed separately and is **not** part of this branch.

## Existing boundaries

This experiment is strictly downstream of and independent from Lumina's Memory Use Gate, Resident Becoming, Resident Intention, or governance paths. It does not grant execution, memory eligibility, identity status, canon promotion, or consciousness claims.
