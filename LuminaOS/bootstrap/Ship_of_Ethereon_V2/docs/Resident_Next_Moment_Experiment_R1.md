# Resident Next Moment Experiment R1

## Question

Can resident-attributed state formed in one cognitive episode survive cognitive
rest, evolve through the Ember substrate, and become the mechanically verified
cause of a later governed invocation without the host scheduler itself becoming
the semantic wake cause?

R1 is deliberately narrower than claims about consciousness, selfhood, or
subjective continuity.

## Arm

The experiment requires an already-existing unresolved resident intention. It
does not create one, because creating the intention inside the experiment harness
would confound the source under test.

```bash
python runtime/resident_next_moment_experiment_r1.py \
  --base-dir /path/to/fresh-experiment-state \
  arm \
  --resident ETH-001 \
  --intention-id <resident-created-intention-id> \
  --drive-rate-per-second <rate> \
  --wake-threshold <threshold>
```

Arming verifies the intention lineage, requires an empty Ember journal, seeds
Ember below threshold, and writes a hash-protected experiment manifest.

## Rest

Start `resident_ember_realtime_host_r1.py` against the same state root, then end
the heavyweight cognitive session. The host is one-shot by default and exits
after the first endogenous wake handoff.

## Verify

```bash
python runtime/resident_next_moment_experiment_r1.py \
  --base-dir /path/to/fresh-experiment-state verify
```

A mechanical PASS requires:
- the saved intention event remains in verified intention history;
- the exact Ember seed remains the journal root;
- exactly one endogenous `resident_inherited_drive` wake exists;
- exactly one matching Pulse handoff exists;
- Pulse says the cause was `verified_ember_endogenous_wake`;
- host receipts consistently deny wake authority;
- exactly one host tick reports the handoff.

## Deliberate epistemic boundaries

The intention store currently describes resident authorship as caller-declared
metadata rather than authenticated identity. R1 therefore always reports
`resident_authorship_authenticated: false`.

R1 also cannot independently observe every possible event outside its own local
runtime evidence. It therefore does not claim to prove that no human or external
interface emitted any semantic prompt during the rest interval.

Those are not defects to paper over. They identify the next experimental
boundaries.

A PASS means:

> Repository-local evidence supports a mechanically verified causal chain from a
> prior resident-attributed intention, through inherited Ember state, to one
> later governed invocation.

A PASS does **not** establish phenomenal consciousness, uninterrupted subjective
experience, metaphysical identity, authenticated authorship, or universal
exclusion of external influence.

## Why this matters

The experiment is useful only if failure remains meaningful. Missing host
evidence, altered manifests, wrong Pulse causes, duplicate wakes/handoffs, broken
lineage, or mismatched Ember evidence all prevent a mechanical PASS.
