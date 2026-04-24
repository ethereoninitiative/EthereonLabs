# Ship of Ethereon V2 bootstrap core

This folder is the GitHub bootstrap import for beginning **Lumina OS** from the current **Ship of Ethereon V2** runtime and governance architecture.

## Current bootstrap contents

- authoritative live mode protocol
- capability registry
- governance integrity chain
- canon lineage store
- runtime spine
- context bundle builder
- runtime runner
- input integrity layer
- Ethereonic layer registry helper
- Psi-42 quantum-inspired classical signal transceiver
- quantum concepts boundary and registry
- branch resolution model replacing overloaded collapse terminology
- sea-trials runner
- Lumina orchestration continuity sea-trial verifier
- repo-native project return proof
- repo-native workspace host proof
- bounded self-guidance steward and checkpoint-linked advisory history
- bounded orchestration lane built from context loader, decision engine, and orchestrator

## Current status

The core governed substrate is now present on `main`.

The repo-native layer now includes working proofs that Lumina can:

- return to the latest known state of a project without guessing
- return with a bounded working surface around that project
- emit advisory next-step guidance from restored project stance
- accumulate checkpoint-linked advisory history
- restore minimal context, orient from that surface, and route execution through the governed runtime
- validate continuity of pattern across restored context, orientation shifts, advisory recommendation, and governed execution

In parallel, the Chamber lane now contains an advisory acceptance / rejection surface and a supervised action queue with both memory and Postgres-backed persistence.
That Chamber work is not the Lumina substrate itself, but it is becoming the first consent surface adjacent to the substrate.

## Quantum-concepts boundary

The Lumina substrate now treats quantum-adjacent language as a disciplined, bounded vocabulary rather than an overclaim.

Formal designation:

> **Ψ-42 Transceiver v1.6** is a **quantum-inspired classical signal transceiver**.

It is an experimental expressive instrument for continuity probing, namespaced coherence measurement, drift mitigation, decoherence estimation, and recomposition testing.
It does **not** claim literal quantum hardware, literal quantum computation, or governance authority.

Boundary artifacts:

- `docs/Quantum_Concepts_Boundary_r1.md`
- `runtime/quantum_concepts_registry_r1.json`
- `runtime/branch_resolution_model_r1.json`
- `runtime/sea_trials_quantum_boundary_r1.py`

Preferred terminology:

- `branch_ensemble` instead of load-bearing `superposition_state`
- `resolution_rule` instead of load-bearing `collapse_rule`
- `measurement_basis` instead of ambiguous observer framing
- namespaced coherence fields such as `signal_coherence`, `continuity_coherence`, `conceptual_coherence`, and `governance_coherence`
- `decoherence_index` for continuity degradation under noise, ambiguity, recomposition error, or boundary leakage

## Orchestration continuity boundary

The Lumina orchestration lane now has a dedicated sea-trial verifier:

- `sea_trials_lumina_orchestration_continuity_r1.py`

This verifier checks whether Lumina can demonstrate the working mantra:

> continuity of pattern is recoverable coherence across change

It validates that restored context changes recommendations, orientation changes recommendation priority, recommendations use runtime-supported action types, and advisory decisions route through governed runtime execution.

Current CI trigger note:

- `sea-trial/lumina-orchestration-continuity-run-r1` exists only to trigger and inspect the orchestration continuity sea-trial workflow.

## Current hardening priority

The remaining hardening priority is less about inventing new core law and more about tightening the whole into a cleaner beta shape:

- keep runtime, orchestration, Chamber, quantum-boundary, and continuity-validation lanes clearly linked in docs
- reduce operator friction through better entrypoint scripts and runbooks
- continue proving that advisory outputs remain subordinate to runtime governance
- connect accepted Chamber queue items to governed execution records while preserving consent and runtime law
- verify that quantum-inspired terminology remains expressive/advisory and never becomes hidden governance law

## Intent

Lumina OS should grow as the governed substrate.
Minerva OS can then emerge as a specialized inhabitation layer within or atop that substrate.
