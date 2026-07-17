# Lumina Return — Build Week 2026

This directory is the bounded contest workspace for **Lumina Return**.

## Product promise

Lumina Return gives developers an inspectable way to resume AI-assisted project work across sessions. It restores bounded context, checks authority before action, records an allow/refuse decision, emits a receipt, and preserves a resumable checkpoint.

## Primary user

A developer or small team using AI assistance on a project that lasts longer than one conversation.

## Problem

After a session boundary, it is often unclear:

- what project context was actually restored;
- which source is authoritative;
- whether a requested action is permitted;
- what the agent changed or refused;
- what durable evidence remains for the next session.

## Required judge journey

The complete demo must be understandable in under three minutes and operable without repository archaeology.

1. **Return** — load the bundled sample project and show current state, evidence, authority boundaries, and next supported action.
2. **Request** — accept a plain-language developer request.
3. **Govern** — display known, uncertain, allowed, and blocked conditions.
4. **Act or refuse** — complete one lawful request and halt one ambiguous or unauthorized request.
5. **Receipt** — show a readable receipt with evidence references.
6. **Resume** — restart and reconstruct the project from preserved state.

## Build Week deliverables

- [ ] one-command or one-click judge launch
- [ ] bundled sample project
- [ ] plain-language project-return view
- [ ] visible governance decision
- [ ] lawful action path
- [ ] blocked/clarification path
- [ ] human-readable receipt
- [ ] restart-and-resume demonstration
- [ ] automated judge-path test
- [ ] supported-platform and installation instructions
- [ ] Build Week provenance ledger
- [ ] Codex `/feedback` session ID recorded after the primary build thread
- [ ] public demo video under three minutes

## Existing foundation versus new work

### Pre-existing foundation

The following classes of capability existed before this branch:

- governed runtime and mode boundaries;
- project-return and workspace-host scaffolding;
- input-integrity assessment;
- capability exposure rules;
- checkpoints and governance receipts;
- continuity-correlation machinery;
- Bridge and Studio surfaces;
- repository-native and Windows developer-preview paths.

### Build Week contribution

Only code, tests, interfaces, fixtures, documentation, and evidence committed after the recorded baseline belong to the contest-period extension. The final submission must name those changes precisely rather than attributing the whole repository to Build Week.

Baseline commit:

```text
d0436260d8b5ee097561ed2dbd690de85f44c4fc
```

## Planned directory map

```text
build-week-2026/lumina-return/
├── README.md
├── demo/                 # judge-facing launch and presentation surface
├── sample-project/       # deterministic bounded fixture
├── evidence/             # baseline, receipts, screenshots, provenance
├── tests/                # focused judge-path validation
└── docs/                 # installation, video script, submission notes
```

## Product language

Default judge-facing labels should favor plain language:

- Known
- Uncertain
- Allowed
- Blocked
- Evidence
- Receipt
- Resume

Ethereonic language may remain as secondary identity and expression, but it may not obscure the mechanism or become runtime authority.

## Success criteria

A fresh evaluator should be able to understand the problem, launch the experience, complete the full journey, inspect the receipt, and see a successful resume without reading the wider EthereonLabs architecture first.

## Deliberate non-goals during the sprint

- no new grand architecture layer;
- no custom Linux distribution work;
- no website-wide redesign;
- no metaphysical claim as part of the primary product pitch;
- no feature that cannot be shown meaningfully in the contest demo;
- no duplicate standalone repository during the sprint.

## Development rule

Receipts before reverence. The demo must remain subordinate to executable behavior, tests, and reproducible artifacts.
