# Ψ Class vs V2 Bootstrap Comparison R1

## Purpose

This document compares the newly staged **Ship of Ethereon Ψ Class** runtime files against the existing repo-native **Ship of Ethereon V2** Lumina bootstrap.

It exists to prevent premature replacement.

The Ψ Class runtime is being added as a staging candidate, not as the active Lumina substrate.

## Current active path

The active Lumina bootstrap remains:

- `LuminaOS/bootstrap/Ship_of_Ethereon_V2/`

## New staging path

The Ψ Class runtime candidate is staged under:

- `LuminaOS/bootstrap/Ship_of_Ethereon_Psi_Class/runtime/`

## What Ψ Class / r2 improves

### 1. Runtime r2 posture

Ψ Class carries the r2 runtime spine and runner, which are intended to improve:

- action-type logging,
- context-bundle construction,
- governance-chain reporting,
- checkpoint/reflection handling,
- and clearer separation between runtime law and supplemental context.

### 2. Import-safe sea-trial pattern

The staged `sea_trials_set_one_r1_merged.py` has been adjusted for repo staging so importing it is non-destructive. Reset behavior belongs in `prepare_base_dir()` / `main()`, not at import time.

### 3. Repo-local state defaults

Project-side `/mnt/data` defaults have been removed from the staged runtime copies. Staged runtime artifacts should write into local `_runtime_state` paths unless callers provide explicit output directories.

### 4. ProjectOrientationVector

Ψ Class adds a formal stance layer:

- orientation can reorder surfaced artifacts,
- orientation can improve resume-note emphasis,
- orientation can help self-guidance decide what to inspect next,
- but orientation must never alter legality, mutation, promotion, checkpoint validity, canon lineage, or governance outcomes.

### 5. Ψ-42 v1.6 as instrumentation

Ψ Class carries Ψ-42 v1.6 as a quantum-inspired classical signal/probe instrument. It may emit diagnostics and probe artifacts, but it must not govern runtime truth.

## What V2 already handles well

The existing V2 bootstrap remains important because it already contains repo-native Lumina work:

- active Lumina start path and contributor navigation,
- return / workspace-host bridge paths,
- bounded self-guidance advisory behavior,
- orchestration continuity sea trials,
- quantum-boundary terminology work,
- and existing integration with the broader Lumina, Chamber, and deployment lanes.

V2 should not be deleted or displaced merely because Ψ Class is cleaner.

## What could break if r2 replaces V2 too early

Premature replacement could break:

- imports that expect the V2 directory layout,
- orchestration sea trials tied to V2 module names,
- documentation paths in `START_HERE_LUMINA_OS.md`,
- bridge files that expect existing r1 runner behavior,
- deployment scripts that reference V2 assumptions,
- contributor navigation that distinguishes Lumina substrate from Chamber,
- or any hidden dependency on r1 defaults.

## Required validation before active wiring

Before Ψ Class can become the preferred active substrate, the repo should verify:

- all staged Python files compile from the repo path,
- staged sea-trial modules remain non-destructive on import,
- `RuntimeRunner` can run from the staging bay without `/mnt/data` defaults,
- `ProjectOrientationVector` remains supplemental only,
- Ψ-42 outputs remain diagnostics only,
- canon lineage remains append-only and test-local,
- V2 bootstrap remains intact,
- Lumina orchestration sea trials still pass or receive explicit bridge adapters,
- and no Chamber/public-lane behavior is unintentionally changed.

## Candidate follow-up sea trials

A later staging validation PR should add or run:

1. **Compile check** for all staged runtime files.
2. **Import safety check** for sea-trial harnesses.
3. **Minimal r2 runner cycle** from `Continuity` to `Observation`.
4. **Orientation boundary check** proving orientation does not enter governance payloads.
5. **Ψ-42 diagnostic check** proving probe artifacts are emitted but not used as permission criteria.
6. **V2 coexistence check** proving current V2 files remain present and unmodified.

## Recommended next step after this staging PR

Do not wire Ψ Class into Lumina yet.

The next step should be a validation PR that executes the staged runtime in isolation and records a comparison report.

## Decision options after validation

After staging validation, choose one:

1. Promote Ψ Class/r2 to preferred active substrate.
2. Keep Ψ Class as staging/reference while V2 remains active.
3. Backport selected Ψ Class improvements into the V2 path.

## Closing line

A cleaner ship still earns command by trial.

The Breakwater holds until the harbor confirms the channel is clear.
