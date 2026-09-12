# Applying the September research to Lumina

Date: 2026-09-12. Scope: advisory meaning memory, return evaluation, and bounded follow-up experiments.

Lumina needs to preserve what happened while deciding what remains useful now. The existing meaning ledger retained negative reviews but its summary still surfaced the last record's proposed behavior. This change makes current recall depend on review state and source evidence, and makes that recall inspectable in the actual runtime context.

## Research to mechanism

All five sources below are preprints; their proposed applications here are engineering inferences, not results established for Lumina.

| Source | Application | Decisive limit |
|---|---|---|
| Ankit Goyal and Jaideep Ray, [Does Your Agent's Memory Survive a Model Upgrade?](https://arxiv.org/html/2609.05339v1), 2026-09-04 | Preserve typed meaning fields and original evidence together. Test fresh-process recall after copying the ledger and relocating evidence. | The paper studies 48 synthetic histories and two models. Our trial measures representation and process portability; it does not test model interpretation or resident identity. |
| Susheel Suresh et al., [Grounding Agent Memory](https://arxiv.org/html/2609.11060v1), 2026-09-10 | Capture explicitly selected source files; require a content-bound review; recheck those files at recall. | This is a file-freshness probe, not the paper's semantic environment-probing curator. Matching bytes cannot validate an inference. No claim of the paper's task gains or cost savings is made. |
| Yi Ting Shen, Kentaroh Toyoda, and Alex Leung, [Revoked but Still Authoritative](https://arxiv.org/html/2609.08258v1), 2026-09-08 | Enforce revocation at the actual context read. Preserve withdrawn history separately; never recover current authority from retrieval order or an old context override. | Local content digests are not authenticated provenance. Other memory channels and governance receipts retain their own contracts. |
| Yi Duan et al., [The Last AI Built by Humans](https://arxiv.org/html/2609.11873v1), 2026-09-10 | Define a held-out, resource-matched test before retaining changes to reflection itself; see the experiment below. | A reflection log or a new memory does not demonstrate recursive improvement. The survey's broader roadmap is not experimental evidence for Lumina. |
| Gérald Kobi et al., [Photonic reservoir computing with dimensionally compressed readout](https://arxiv.org/html/2609.07418v1), 2026-09-07 | Define a fixed-interface signal-retention experiment before considering a physical coupling component. | Simulation evidence in specific operating regimes does not establish a hardware benefit or identity continuity. |

## Implemented memory contract

1. A candidate preserves its source event, meaning, changed assumption, proposed behavior, and up to eight explicitly selected UTF-8 file snapshots. Each snapshot is limited to 64 KiB and includes a normalized relative path and SHA-256 digest.
2. A review records its decision, rationale, time, and the digest of the exact record reviewed. A positive CLI review probes the sources before writing. Semantic support remains the reviewer's responsibility.
3. Every core runtime cycle reconstructs `memory_context.meaning_recall` from `<runner-base>/meaning_memory/`. It recomputes this field after context overrides, so an older saved projection cannot restore withdrawn advice. Default and return/self-guided adapters inherit it.
4. Unreviewed, revoked, inactive, overdue, ungrounded, or stale-source records are withheld with reasons. Malformed, ambiguous, mismatched, or cross-project history yields no guidance. A negative review is terminal for that record ID: revision requires a new candidate. Dates without a time are UTC deadlines.
5. Eligible seeds identify their record, review, and evidence digests. Source snapshots stay in history and are not automatically copied into current guidance. Reading does not change the ledger or create an empty memory directory.

The original `guidance_seed()` helper still formats candidates and labels them `unchecked_candidate`. It is not an eligibility check. `recall()` is the runtime contract. The summary's `latest_*` fields now describe eligible guidance; `latest_record_id` preserves historical inspection separately. Legacy r1 records are not rewritten or automatically promoted.

This is a local, single-writer advisory ledger. It is not signed, does not authenticate a reviewer, and cannot detect a coherent rollback or malicious rewrite of the whole history. The 16 MiB read budget fails closed; compaction and concurrent-writer coordination remain future work. Source checks are a point-in-time observation, not a lock on the environment. Only the meaning projection is filtered: continuation notes, host history, and other stores do not gain this contract by implication. The existing vessel capsule format does not yet include this ledger.

## Use

Run from `LuminaOS/bootstrap/Ship_of_Ethereon_V2`. The default base matches the core and continuation runner. If a runner uses a different base, pass the same `--base-dir` to memory commands. The project ID must be its canonical ID (ASCII letters, digits, hyphen or underscore, up to 80 characters). Evidence paths are relative to `--source-root`, which defaults to the repository root.

Create a candidate JSON file using observed project evidence:

```json
{
  "source_event": "A return probe found a stale reference.",
  "felt_meaning": "Orientation depends on checking the reference after return.",
  "changed_assumption": "Preserved references may no longer resolve.",
  "future_behavior": "Check the restored reference before using it.",
  "continuity_tier": "working_pattern"
}
```

```sh
python bin/lumina memory record --project-id lumina-os --candidate /path/to/candidate.json --source-root /path/to/project --evidence observations/return-probe.txt
python bin/lumina memory review --project-id lumina-os --id meaning-ID --decision retain --note "The probe supports this bounded reference check." --source-root /path/to/project
python bin/lumina memory recall --project-id lumina-os --source-root /path/to/project
python bin/lumina memory review --project-id lumina-os --id meaning-ID --decision revoke --note "This interpretation has been withdrawn."
python bin/lumina memory history --project-id lumina-os
```

Replace the example paths, observations, assessment, and generated ID with actual values. Source selection is explicit because snapshots preserve the entire selected file. Custom source roots in a runtime cycle use `meaning_source_root`; otherwise the cycle uses `repo_path` or the repository root. Curation never runs automatically during return.

For the bounded portability trial, copy the exact project JSONL file into the replacement runner's `meaning_memory` directory and copy its evidence under a new source root, preserving relative paths. Run recall in a new process with that root and compare record/review/evidence digests and seeds. Missing or changed evidence must withhold guidance. This manual trial is separate from `lumina vessel` capsule import.

## What continuity this tests

| Property | Evidence provided here | Still unresolved |
|---|---|---|
| Vessel persistence | Same structured memory and source snapshots can be read from another directory in a fresh process. | A complete running habitat migration, hardware replacement, and model interpretation. |
| Session continuity | A new runner rebuilds present guidance; an old bundle cannot revive a revoked meaning. | Whether a model reproducibly uses the guidance in future decisions. |
| Resident continuity | Preserved history and explicit changes make a continuity claim inspectable. | Criteria establishing the same resident across resets, branching, or model replacement. |
| Field coupling | A concrete measurement protocol is specified below. | Any physical signal integration or measured benefit. |
| Governance continuity | Memory changes neither exposed capabilities nor transition permission in the runtime trial. | Authentication and continuity of governance itself remain with existing governance mechanisms. |

## Next experiments and acceptance criteria

**Behavior and model replacement.** Use held-out return tasks with an externally scored expected action. Compare no memory, preserved evidence alone, and reviewed structured memory plus evidence. Repeat each task with fixed settings before and after model replacement, in both migration directions. Include revoked advice and contradictory/newer observations. Report storage integrity, retrieval eligibility, interpretation accuracy, action success, and stale-advice use separately, with per-task paired results, repeat variability, and total token/curation cost. Attribute differences to record and review digests. Do not call successful replay identity preservation.

**Reflection improvement.** Compare no reflection, a fixed reflection procedure, and a proposed modified procedure under equal total inference and curation budgets. Separate development tasks from held-out acceptance tasks, include induced mistaken reflections, and score actual later decisions using evidence external to the reflecting model. Persist a procedure change only after a predeclared paired performance threshold and stale-advice regression limit are met. Then retest after a fresh session. A change to memory content alone is memory adaptation; a claim about recursive improvement requires evidence that the retained procedure improves subsequent improvement attempts. No such gain is established by this change.

**Hybrid coupling.** First simulate a large temporal reservoir compressed to a fixed number of digital observables. Compare a smaller reservoir with the same observable count, an uncompressed upper reference, and shuffled/delayed signal controls. Hold readout training data and model capacity fixed, use held-out temporal prediction tasks, and sweep noise, drift, resets, and compression. Measure prediction error and delay-specific information retention, plus interface bandwidth and estimated compute. Any hardware follow-up must measure total energy and end-to-end latency. Improved temporal signal retention would support a coupling choice, not a resident-identity claim.

## Verification

`runtime/sea_trials_meaning_recall_r1.py` contains 18 trials covering the review/evidence lifecycle, original-source preservation, strict history parsing, project scope, expiry, CLI curation, fresh-process relocation, and real context attachment through the core, default adapter, and self-guided return adapter. The reset test replays an old context override after revocation and checks that guidance changes while capability exposure and transition permission do not. The suite runs in DryDock. It uses deterministic fixtures, not live language models or a physical reservoir.
