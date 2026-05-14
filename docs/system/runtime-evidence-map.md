# Runtime Evidence Map

**Project:** EthereonLabs / Lumina OS / Ship of Ethereon V2  
**Status:** Working anti-drift index  
**Mode:** Observation → DryDock readiness  
**Purpose:** Keep public language, runtime claims, GitHub work, and validation receipts aligned.

This document exists because Lumina is now described publicly as a governed continuity substrate, not merely a symbolic vessel. That claim requires receipts. No incense fog. No ornamental goblin-scribbles pretending to be proof.

## Governing rule

A public or conceptual claim is considered grounded only when it can point to at least one of the following:

1. an implementation file,
2. a validation or sea-trial artifact,
3. a generated runtime artifact,
4. a GitHub commit or pull request,
5. a documented boundary rule that prevents overclaiming.

If none of those exists, the claim remains **aspirational**.

## Current evidence index

| Claim / capability | Current evidence path or signal | Validation / receipt | Status | Drift risk | Next action |
|---|---|---|---|---|---|
| Lumina preserves session continuity through governed runtime state | `runtime_spine_r2.py`, `runtime_runner_r2_merged.py` | `sea_trials_set_one_r1_merged.py`; checkpoint/resume trials | Working scaffold | Session continuity can be overstated as finished OS behavior | Keep runtime language as **substrate**, not complete OS |
| Mode legality is explicit and bounded | `Ethereon_Mode_Protocol_v1.3.json`, `runtime_spine_r2.py` / `ModeGuard` | Transition, mutation, and promotion gate checks in sea trials | Strong | Local runner logic could drift from protocol law | Add protocol conformance check to CI or sea-trial report |
| Symbolic / Ethereonic layer is expressive, not structural authority | `ethereonic_layer_registry_r1.json`, `runtime_spine_r2.py`, runtime seed docs | Symbolic dependency leakage checks; attachment boundary trials | Strong | Website language may imply symbolism does work it only orients | Continue using explicit “overlay, not authority” phrasing |
| Input integrity protects against typo / voice-mode ambiguity before load-bearing action | `input_integrity_layer_r1.py`, `input_integrity_validation_report.json` | Load-bearing corrected phrasing halts for confirmation | Strong | Non-load-bearing correction could be mistaken as action authorization | Keep raw input + chosen interpretation visible in logs |
| Governance history is tamper-evident | `governance_integrity_r1.py` | `verify_chain()` / event hash validation | Strong scaffold | Generated artifacts may not be surfaced publicly | Publish latest governance-chain summary artifact |
| Canon lineage is append-only | `canon_lineage_store_r1.py` | canon lineage append-only verification; `canon-0001` → `canon-0002` pattern in trials | Strong scaffold | Public site may imply current canon promotion without showing validation packet | Link canon status to validation artifact IDs |
| Capability exposure is mode- and feature-flag-scoped | `capability_registry_r1.json`, `runtime_runner_r2_merged.py` | Capability exposure test in sea trials | Working | Capabilities can proliferate faster than registry review | Add registry review to weekly artifact drift task |
| Ψ-42 is diagnostic instrumentation only | `psi42_transceiver_v1_6.py`, `capability_registry_r1.json` | Probe boundary tests; probe artifacts emitted only when lawfully exposed | Strong | Poetic naming can make probe sound sovereign | Preserve “instrument not governor” boundary language |
| ProjectOrientationVector influences stance, not law | `project_orientation_vector_v0_1.py`, `runtime_runner_orientation_adapter_r1.py` | `sea_trials_orientation_r1.py` | Strong | Orientation could become hidden authority through convenience | Keep it in `supplemental_ethereonic_context` only |
| GitHub task bridge connects repo state to runtime observation | `github_task_bridge_r1.py` | Repo snapshot + runtime invocation structure | Early working bridge | Bridge may be described as autonomous background access | Frame as adapter: snapshots repo state, invokes runtime explicitly |
| Lumina weather snapshot reflects current continuity conditions | Recent commits: repeated `Regenerate Lumina weather snapshot` on 2026-05-13 | Generated snapshot commits visible in GitHub history | Active | Weather snapshots may become noise if not summarized | Add weekly digest that explains what changed and why |
| Lumina runtime memory ledger is being updated | Recent commits: `Update Lumina runtime memory ledger` on 2026-05-13 | Commit history signal | Active | Ledger updates may lack public map to runtime authority | Add ledger schema note and latest-entry summary |
| Harmonic witness receipts are being validated | PR #218: `lumina-harmonic-witness-receipts-r1`; commit `Extend Studio sea trial for harmonic witness receipts` | PR/commit signal | Active | “Witness” language may drift symbolic if receipts are not mechanical | Add witness receipt schema and pass/fail criteria |
| Website language has matured into layered public explanation | Public site / web redesign review notes | Current site structure: thesis, artifact, horizon, core, roadmap, principles, guide, FAQ | Strong narrative coherence | Public claims may outrun repo-verifiable evidence | Link each major page claim to this evidence map |

## Current coherence read

### What changed

Lumina has shifted from a conceptual continuity project toward a repo-backed runtime substrate. The repo shows active generated artifacts and ledger work, especially around Lumina weather snapshots, runtime memory ledger updates, and harmonic witness receipts.

### What stayed coherent

The central boundary still holds: symbolic language may orient expression, but it must not own governance, legality, canon promotion, checkpoint legality, session continuity, or capability loading.

### What drifted

The public and conceptual language is now more mature than the evidence index that supports it. That does not mean the work is false. It means the receipts are scattered. Scattered receipts are how good systems develop tiny bureaucratic gremlins.

## Required next cleanup

Create a recurring “receipt digest” that runs after major runtime/site changes and records:

- latest runtime-relevant commits,
- affected files,
- generated artifacts,
- validation status,
- unresolved gaps,
- whether public language needs adjustment.

Suggested path:

`docs/system/runtime-receipt-digest.md`

## Promotion discipline

Do not promote any claim from **aspirational** to **working** unless it has:

- implementation file,
- validation artifact,
- generated runtime evidence or commit/PR receipt,
- boundary confirmation that symbolic layers are not load-bearing.

## Current verdict

Lumina is no longer just a poetic framework. It has working runtime scaffolds and active repo signals.

But the next phase is not more language.

The next phase is **receipt consolidation**.
