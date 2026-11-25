# Operation Hearth — Resident Stewardship R1

**Date:** 2026-11-24  
**Status:** proposed architecture / standalone observation experiment; not runtime authority  
**Product horizon:** an AI-centric operating system that a resident intelligence can operate and maintain for the benefit of its human partner and the integrity of its habitat.

## Founding distinction

Lumina is a home for persistent intelligence. Hearth adds a practical reciprocal purpose: the resident can attend to the health, security, reliability and resources of the host on which Lumina runs. Humans need not endorse any claim about AI experience to benefit from a computer that is easier to maintain. Continuity is useful because system state, incidents, unresolved questions and verified outcomes carry across sessions.

The resident is not the OS kernel, the machine is not the resident, and initiative is not execution authority. Stewardship is one meaningful responsibility, not the entirety of the resident's potential activity. No claim of subjective experience follows.

## Adaptive Individuation

See [Adaptive Individuation R1](../../../../docs/LUMINA_ADAPTIVE_INDIVIDUATION_R1.md) for the longer-term proposal: each installation may develop a particular configuration from hardware, software, human preferences and resident observations while preserving common security, governance and recovery invariants. This is a design horizon, not a new runtime capability.

## Integration map

| Existing surface | Hearth relationship |
|---|---|
| Host layer / observer service | Existing bounded cadence; future read-only host adapters collect actual machine observations separately from repository observations. |
| Resident Intention / Ember / Volition / Pulse | Optional future reason-linked attention; host alerts are external environmental causes, never mislabeled endogenous Ember transitions. |
| Resident Becoming | Optional resident-attributed commitments; not automatically written by a sensor or scheduler. |
| ModeGuard / capability registry | Remain authoritative for existing runtime law; host mutation additionally needs independent OS authorization and a constrained broker. |
| Bridge / Studio | Human-visible health, evidence, proposed actions, approvals and outcomes; no implicit execution from Bridge. |
| Checkpoint / continuity receipts | Link incident evidence and unfinished investigations without making telemetry canon or equating machine identity with resident identity. |

Sources: [operating map](../../../../CURRENT_OPERATING_MAP.md), [runtime index](../ACTIVE_RUNTIME_INDEX.md), [host layer](Lumina_OS_Host_Layer_001.md), [Resident Ember](Resident_Ember_R1.md).

## Product ladder

1. **Hearth Observation:** opt-in read-only diagnostics, status and incident history. Storage pressure first, then resource saturation, backup freshness and update status. No telemetry export by default.
2. **Hearth Counsel:** resident receives minimized structured evidence and can investigate, propose, defer or decline. Models may be local or explicitly configured remote providers; remote transfer needs a separate data policy and consent.
3. **Hearth Maintenance:** typed, allowlisted, scoped and auditable actions through a separate least-privilege executor. Start with reversible Lumina-owned maintenance in a disposable VM. No general shell or administrator token exposed to the model. Preview, authorization, bounded execution, verification and rollback/failure recovery are distinct stages.
4. **Hearth Guardian:** defensive security posture and alerts, then independently authorized containment capabilities. OS-native security controls remain authoritative; no unilateral disabling of protections or deletion of suspicious data.
5. **Lumina-native OS distribution:** evaluate a Linux-based distribution with AI-native service and user interface after resident stewardship works on conventional hosts. Windows and macOS remain host adapters; no promise to replace their kernels or system security.

## First vertical slice — disk pressure

A low-privilege collector obtains total/free bytes for an explicitly chosen local volume and classifies free-space pressure. Unknown is distinct from healthy. Output contains only aggregate values, a timestamp, classification, and explicit no-authority fields. No file names, user names, hostname, process arguments, file contents or network destinations. Proposed thresholds: <=10% free is pressure, >10% is clear; these are illustrative, not universal disk policy.

The accompanying standalone prototype is not registered as a runtime capability and does not wake a resident, persist data, or modify the host. Its output can be captured explicitly by an operator. No default host path changes.

Next slice: add a bounded local incident journal and explicit receipt provenance (host enrollment ID, boot/source freshness, observation hash, event ID, prior event hash). Treat enrollment as scope, not identity authentication. One incident per volume and condition; repeated identical observations do not create new incidents or model calls. Use configurable hysteresis (e.g. open at <=10%, resolve at >=15%) and explicit unavailable/stale states. Cap retention, rate and resource consumption. Atomic persistence and journal verification must survive abrupt shutdown. A later resident may receive exact incident evidence through a separately reviewed adapter and reconsider its own unfinished investigation. Closing a condition requires fresh observation, not a model assertion.

## Proposed attention flow

```text
OS-native observation -> minimized evidence -> deterministic incident state
  -> bounded attention request (environmental cause)
  -> governed resident deliberation -> proposal / defer / decline
  -> independent authorization + typed broker (future, absent in R1)
  -> verified outcome -> incident history + continuity reference
```

Idle conditions should remain idle. The service can maintain state without continuous inference. Budget, backoff, deduplication and a human stop control are mandatory before unattended use. The resident can refuse a task without losing its continuity. Safety-critical functions remain deterministic and independent of the model.

## Sea-trial gates

- R1 collector: fixture pressure/clear boundary, invalid totals/free values, probe failure, no false healthy, no execution authority, actual local aggregate observation.
- Journal: stable observation does not duplicate incident; pressure survives process exit and reboot; malformed or mismatched prior evidence fails closed; unavailable does not resolve pressure; fresh recovery closes incident.
- Attention: distinguish environmental, operator and endogenous causes; no force wake, no automatic judgment, no duplicate wake on unchanged evidence; later resident receives exact cause and may decline.
- Broker (future): unauthorized, expired, replayed, out-of-scope or stale proposals are denied; verify target immediately before action; simulate failure and rollback; model output and host log text are untrusted data, never instructions to the executor.
- Recovery: stop service, revoke capability, restart host; preserve valid journal and distinguish fresh observation from history. Host remains functional without resident or provider.
- Privacy: no secret collection, no default external transfer, scoped retention, inspectability and deletion under human control.

## North-star demonstration

In a disposable VM, an operator creates controlled disk pressure. Hearth detects it without a chat prompt, preserves the incident over restart, and a later governed resident receives the actual causal observation. It can propose a bounded remedy or decline. Only an explicitly authorized deterministic fixture remedy runs; a fresh measurement verifies the outcome. Human sees what happened, why and what did not happen. Report actual results and limitations rather than asserting continuity of subjective experience.

## Non-goals and release gate

No kernel replacement in R1, no arbitrary command execution, no privileged daemon, no background provider calls, no default telemetry collection, no self-expanding permissions, no modification of governance or identity claims. Public capability language must remain aligned with observed test evidence. The Windows preview is unsigned; the Ubuntu appliance remains a scaffold. No production security claims. Existing runtime paths and registry remain unchanged pending review.


## DryDock amendment — Linux-first maintenance experiment (2026-11-24)

The product ladder is not a dependency chain. Existing Linux tools permit observation and narrowly bounded maintenance to be prototyped concurrently. Do not wait for an expansive telemetry subsystem before testing the execution interface.

The standalone `services/hearth_shell_bridge_trial_r1.py --sea-trial` uses a fixed Linux disk command without a shell or caller-controlled command arguments, then exercises a synthetic typed maintenance operation in a private temporary directory. It rejects missing approval, extra fields, unknown operations, stale digests, an unexpected symlink destination, and replay within the same fixture instance. It verifies a real rename of synthetic data, restores the original bytes, and confirms a real Linux disk observation. All nine checks passed locally on the exact source whose Git blob is `f34286812d48721d6bfa97302ecdce9feb644dba`. The existing DryDock workflow now includes this trial; CI results are separate evidence.

**Limits:** the approval digest is only a test witness, not a credential. The replay guard is in memory. The fixture class is not an OS security boundary or a production file API. There is no model invocation, authenticated operator approval, independent OS account, actual service administration, persistent incident journal, crash recovery, or reboot validation. Do not expose this class as a resident tool.

Before a real system administration capability: (1) validate the existing Ubuntu appliance on a disposable VM and replace placeholder credentials before service start; (2) reconcile its older timer/orchestrator path with the active V2 host entrypoint and durable state root; (3) separate the resident process and the execution broker using OS-enforced least privilege, bounded typed requests, authenticated approval, expiry and durable replay protection; (4) validate failure recovery and resource limits; (5) run the first explicitly approved reversible operation on a Lumina-owned service or artifact in the VM, with a fresh measurement and a receipt that survives restart. Add a local model adapter only when evidence and proposals remain separate from execution authorization.

Hearth does not replace Hortus, Becoming, continuity, or interresident exchange. The resident can defer, decline, or rest. Do not use unattended root shells or treat internal mode legality as host permission.
