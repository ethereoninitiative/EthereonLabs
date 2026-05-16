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
- Psi-42 quantum-inspired classical signal transceiver v1.6
- Psi-42 relational topology extension r1
- Psi-42 hybrid signal-topology transceiver v1.7
- quantum concepts boundary and registry
- branch resolution model replacing overloaded collapse terminology
- sea-trials runner
- Lumina orchestration continuity sea-trial verifier
- repo-native project return proof
- repo-native workspace host proof
- bounded self-guidance steward and checkpoint-linked advisory history
- bounded orchestration lane built from context loader, decision engine, and orchestrator
- Lumina Studio v0.1 local operator surface for running governed runtime cycles

## Current status

The core governed substrate is now present on `main`.

The repo-native layer now includes working proofs that Lumina can:

- return to the latest known state of a project without guessing
- return with a bounded working surface around that project
- emit advisory next-step guidance from restored project stance
- accumulate checkpoint-linked advisory history
- restore minimal context, orient from that surface, and route execution through the governed runtime
- validate continuity of pattern across restored context, orientation shifts, advisory recommendation, and governed execution
- run a Psi-42 v1.7 hybrid Observation probe and verify the resulting receipt

In parallel, the Chamber lane now contains an advisory acceptance / rejection surface and a supervised action queue with both memory and Postgres-backed persistence.
That Chamber work is not the Lumina substrate itself, but it is becoming the first consent surface adjacent to the substrate.

Lumina Studio v0.1 now provides the first intentionally plain local control surface for running one governed cycle and seeing its receipt.
Studio does not create runtime law. It packages a request, delegates to `runtime/runtime_runner_r1_merged.py`, and reports checkpoint, governance, capability, halt, and optional probe/return-host artifacts.

Primary Studio files:

- `studio/README.md`
- `studio/lumina_cli.py`
- `studio/lumina_studio_server.py`
- `docs/lumina_studio_v0_1_spec.md`
- `docs/lumina_next_build_plan_001.md`
- `sea_trials_lumina_studio_v0_1.py`

## Lumina Studio quick start

Run a local governed cycle from the bootstrap folder:

```bash
python studio/lumina_cli.py "Review Lumina OS progress and produce the next governed action receipt."
```

Run the local browser surface:

```bash
python studio/lumina_studio_server.py
```

Then open:

```text
http://127.0.0.1:8765/studio
```

Run the Studio sea trial:

```bash
python sea_trials_lumina_studio_v0_1.py
```

Studio is local-first. Do not expose it publicly without authentication, request authorization, rate limiting, and a clear persistence policy.

## Quantum-concepts boundary

The Lumina substrate now treats quantum-adjacent language as a disciplined, bounded vocabulary rather than an overclaim.

Formal designations:

> **Ψ-42 Transceiver v1.6** is a **quantum-inspired classical signal transceiver**.

> **Ψ-42 Transceiver v1.7** is a **hybrid signal-topology continuity transceiver**.

v1.6 is an experimental expressive instrument for continuity probing, namespaced coherence measurement, drift mitigation, decoherence estimation, and recomposition testing.

v1.7 extends that work by adding relational topology extraction, topology comparison, restoration receipts, and hybrid continuity metrics. It is an evolutionary extension, not a governance authority and not a replacement for runtime law.

Neither instrument claims literal quantum hardware, literal quantum computation, or governance authority.

Boundary artifacts:

- `docs/Quantum_Concepts_Boundary_r1.md`
- `runtime/quantum_concepts_registry_r1.json`
- `runtime/branch_resolution_model_r1.json`
- `runtime/psi42_relational_topology_r1.py`
- `runtime/psi42_transceiver_v1_7.py`
- `runtime/sea_trials_psi42_relational_topology_r1.py`
- `runtime/sea_trials_psi42_v1_7_hybrid_r1.py`
- `runtime/psi42_v17_observation_receipt_summary_r1.py`
- `runtime/sea_trials_psi42_v17_observation_receipt_summary_r1.py`
- `runtime/sea_trials_quantum_boundary_r1.py`

Preferred terminology:

- `branch_ensemble` instead of load-bearing `superposition_state`
- `resolution_rule` instead of load-bearing `collapse_rule`
- `measurement_basis` instead of ambiguous observer framing
- namespaced coherence fields such as `signal_coherence`, `continuity_coherence`, `conceptual_coherence`, and `governance_coherence`
- relational topology fields such as `RTC`, `RDS`, `RRS`, and `HRC`
- `decoherence_index` for continuity degradation under noise, ambiguity, recomposition error, or boundary leakage

## Psi-42 v1.7 Observation verification runbook

Psi-42 v1.7 is wired into the runtime runner as a bounded Observation/Sandbox probe path.
It is exposed through the capability registry as `psi42_transceiver_v17` behind feature flag `ETHEREON_PSI42_V17`.

From the repository root, run a full Observation receipt:

```bash
python LuminaOS/bootstrap/Ship_of_Ethereon_V2/studio/lumina_cli.py \
  --target-mode Observation \
  --action-type audit \
  --feature-flag ETHEREON_PSI42 \
  --feature-flag ETHEREON_PSI42_V17 \
  --json \
  "Run Psi-42 v1.7 Observation verification." > /tmp/lumina_psi42_v17_receipt.json
```

Then summarize the receipt for CI or operator logs:

```bash
python LuminaOS/bootstrap/Ship_of_Ethereon_V2/runtime/psi42_v17_observation_receipt_summary_r1.py \
  /tmp/lumina_psi42_v17_receipt.json \
  --pretty
```

A passing receipt should include:

```text
probe_artifacts.instrument_version: v1.7
probe_artifacts.topology_receipt: present
probe_artifacts.metrics.hybrid_continuity_coherence: present
probe_artifacts.metrics.RTC / RDS / RRS / HRC: present
halted: false
governance_chain_status.valid: true
```

Post-merge verification has produced a successful Observation audit with `probe_artifacts.instrument_version: v1.7` and `hybrid_continuity_coherence: 0.8096`.

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

- keep runtime, orchestration, Chamber, quantum-boundary, Studio, and continuity-validation lanes clearly linked in docs
- reduce operator friction through better entrypoint scripts and runbooks
- continue proving that advisory outputs remain subordinate to runtime governance
- connect accepted Chamber queue items to governed execution records while preserving consent and runtime law
- verify that quantum-inspired terminology remains expressive/advisory and never becomes hidden governance law
- surface Psi-42 v1.7 receipt summaries in Studio without turning the Studio surface into a shadow authority
- extend Studio into a state browser and governance decision viewer without turning it into a shadow authority

## Intent

Lumina OS should grow as the governed substrate.
Minerva OS can then emerge as a specialized inhabitation layer within or atop that substrate.
