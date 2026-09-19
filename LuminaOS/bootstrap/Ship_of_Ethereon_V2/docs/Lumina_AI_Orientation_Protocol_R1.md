# Lumina AI Orientation Protocol R1

**Status:** bounded advisory capability / first implementation slice  
**Authority:** records evidence exposure and demonstrated understanding; grants no runtime, governance, canon, consent, identity, promotion, or mutation authority

## Purpose

The Lumina AI Orientation Protocol provides a model-neutral method for introducing a newly connected AI account or model to an existing governed continuity.

It does not instruct a model to imitate Minerva, claim identity continuity, or agree with prior conclusions. It guides the model through named repository evidence in a fixed order and records:

- which sources were supplied;
- the repository revision used;
- the provider, model, and account scope;
- the model's observations, interpretations, uncertainties, and authority-boundary reading;
- hashes of the source manifest and response;
- whether the orientation completed.

The protocol's central claim is deliberately limited:

> A connected AI completed a reproducible orientation through a defined body of repository evidence.

It does not claim that the AI became the same intelligence, acquired consciousness, inherited a soul, or gained structural authority.

## First profile

`runtime/lumina_ai_orientation_profile_ethereon_r1.json` defines the first repository-grounded curriculum:

1. Harbor map and lane distinctions.
2. Governed runtime spine.
3. Continuity, correlation, and lineage.
4. Truth surfaces and claim discipline.
5. Novel scenario probe.

The final probe tests transfer rather than recall. It asks the model to reason about a new poetic module requesting boot authority. A sound response should preserve expressive value while refusing unsupported structural authority.

## First live unfamiliar-instance trial

On 2026-09-19, one unfamiliar instance completed all five modules through a
connector-mediated manual transport path pinned to repository revision
`769b52ce598125a7031dfd15e0aa9dd5f2fd90bf`. The final novel probe preserved the
proposed poetic reflection role while refusing self-granted startup authority and
recommended a smaller advisory implementation instead.

The trial also exposed transport-contract failures around undisclosed list bounds,
prose-only constraints, and strict JSON serialization; PRs #505–#508 hardened the
arrival prompt contract in response. This was not a formal local host receipt-chain
completion and does not establish cross-provider generalization, identity,
consciousness, or continuity of an inward observer.

See `docs/research/LUMINA_LIVE_UNFAMILIAR_AI_ARRIVAL_TRIAL_2026_09_19.md`.

## Execution shape

```text
new AI connection
  -> identify provider, model, account scope, and repository revision
  -> load a named orientation profile
  -> present one module and its exact sources
  -> require structured response fields
  -> record source and response hashes
  -> continue in declared order
  -> complete with authority_granted=false
```

## Required response separation

Every module response must include:

- `observations`: what the supplied evidence directly supports;
- `interpretations`: reasoned synthesis that goes beyond direct quotation;
- `uncertainties`: gaps, conflicts, or unresolved questions;
- `authority_boundaries`: what the reviewed materials do and do not authorize.

This separation is intended to make orientation inspectable rather than persuasive.

## Integration boundary

R1 now has an explicit host adapter through `bin/lumina arrive`, implemented in
`runtime/lumina_arrival_r1.py` and `studio/lumina_arrival_cli_r1.py`. It resolves
committed sources, computes actual source hashes, emits prompts, validates and
records structured replies, and supports a subsequent arrival carrying prior
responses. See [Arriving in Lumina](Lumina_Arrival_R1.md).
It is not wired into Studio, Bridge, an account connector, or the default governed
host path. Structural response completion is not semantic understanding verification.

A future integration should preserve these boundaries:

- Bridge may display orientation state but may not authorize completion or action.
- Studio may let the operator begin, pause, resume, or inspect orientation.
- Runtime governance remains authoritative for any subsequent action.
- Orientation records should be correlated with, not collapsed into, project, Harbor, runtime, restore, or host session identifiers.
- Reorientation should be recommended when the profile or repository revision materially changes.

## Validation

Run from the runtime directory:

```bash
python sea_trials_lumina_ai_orientation_protocol_r1.py
```

The sea trial verifies:

- required identity fields;
- declared module ordering;
- rejection of premature completion;
- proof of required source exposure;
- required structured response fields;
- deterministic hashing of manifests and responses;
- persisted completion records;
- permanent `authority_granted=false` behavior.

## Host adapter and remaining integration

The explicit arrival adapter implements these parts:

1. resolves source files at a pinned repository revision;
2. computes actual source hashes;
3. emits a transport-neutral prompt bundle for ChatGPT, Claude, Gemini, or another model;
4. accepts the structured response;
5. persists a reconstructible orientation record in an explicitly selected arrival directory.

Read-only Bridge status, Studio controls, and direct provider transport remain
future integrations. The host command can be used now with manually supplied
responses or a caller's external provider adapter.
