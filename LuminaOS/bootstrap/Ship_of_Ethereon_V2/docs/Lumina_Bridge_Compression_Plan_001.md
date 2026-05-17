# Lumina Bridge Compression Plan 001

**Status:** planning document  
**Scope:** runner / bridge architecture cleanup  
**Authority:** advisory implementation plan, not runtime law

## Why this exists

A NotebookLM external read correctly surfaced a structural pressure in the current Lumina stack: **bridge accumulation**.

Lumina has grown through careful isolated bridges:

- repo-native project return bridge;
- workspace-host bridge;
- self-guided runner bridge;
- reflective self-guided bridge;
- orchestration continuity bridge patterns;
- Studio / host-layer entry surfaces.

This was the right way to build safely. Each bridge allowed a new idea to be tested without rewriting the entire runtime spine.

But enough bridges become a dockyard maze.

The next refinement is not more bridge proliferation. The next refinement is compression.

## Goal

Compress bridge behavior into a cleaner runner architecture while preserving every authority boundary that makes Lumina safe.

Target pattern:

```text
return -> host context -> reflect -> advise -> govern -> record
```

The runner should make those phases explicit without requiring a separate bespoke bridge for every new advisory layer.

## Non-goals

This plan does not propose:

- weakening ModeGuard;
- allowing advisory layers to authorize action;
- letting reflection mutate runtime state;
- turning Ethereonic context into structural law;
- bypassing human consent;
- deleting working bridges before equivalent behavior is covered by sea trials.

## Current pressure points

### 1. Duplicate orchestration shape

Several bridges wrap `run_cycle` to attach extra context, history, reflection, or orientation. The behavior is useful, but the wrapping pattern is becoming repetitive.

### 2. Advisory layers have similar lifecycle needs

Self-guidance, reflective autonomy, Golden Spiral Memory, orientation vectors, and future supervised action queues all need some version of:

1. read bounded context;
2. generate advisory receipt;
3. attach advisory summary to artifact or memory context;
4. log that the advisory was produced;
5. ensure advisory did not gain authority.

That lifecycle should become a reusable contract.

### 3. Host / Studio / CLI entrypoints should converge

Local command, Studio, and future Chamber-supervised queues should all hit the same governed runner phases rather than each assembling partial behavior differently.

## Proposed compressed architecture

### Phase 1 — Advisory contract

Create a small interface / convention for advisory modules.

Suggested file:

```text
runtime/lumina_advisory_contract_r1.py
```

Suggested contract:

```text
Advisory modules may:
- read context bundle summaries;
- read checkpoint-linked history;
- emit advisory receipts;
- recommend next steps;
- produce confidence / risk / continuity scores.

Advisory modules may not:
- validate mode legality;
- authorize mutation;
- write canon lineage;
- declare checkpoint truth;
- expose capabilities;
- execute tools;
- override user consent.
```

The contract should be intentionally simple and boring.

### Phase 2 — Advisory pipeline

Create a runner-side advisory pipeline that can execute registered advisory modules in order.

Suggested file:

```text
runtime/lumina_advisory_pipeline_r1.py
```

Possible pipeline order:

```text
project return summary
workspace host summary
reflective autonomy receipt
self-guidance advisory
Golden Spiral Memory receipt
supervised action queue proposal
```

Each item should attach its result under clearly named artifact or memory context keys.

### Phase 3 — Unified enhanced runner

Replace bridge stacking with a single enhanced runner that composes the advisory pipeline before the governed runtime cycle.

Suggested file:

```text
runtime/runtime_runner_lumina_enhanced_r1.py
```

This runner should remain subordinate to the existing core runner and ModeGuard.

It should not become a new hidden authority.

### Phase 4 — Bridge deprecation map

Once equivalent behavior is covered by tests, mark older bridges as compatibility wrappers.

Potential docs update:

```text
docs/Lumina_Runner_Bridge_Stack_001.md
```

Add a section:

```text
Bridge status:
- active bridge
- compatibility wrapper
- replaced by advisory pipeline
- deprecated after sea trial coverage
```

No bridge should be removed until sea trials prove the compressed path preserves its behavior.

## Proposed sea trials

Suggested file:

```text
runtime/sea_trials_lumina_bridge_compression_r1.py
```

Checks:

1. compressed runner produces same or richer context than bridge stack;
2. self-guidance remains advisory;
3. reflective autonomy remains advisory;
4. Golden Spiral Memory remains advisory;
5. project orientation vector remains supplemental only;
6. ModeGuard still owns transition legality;
7. mutation denial still halts;
8. canon promotion still requires full gate;
9. capability exposure remains mode/flag scoped;
10. governance log records advisory production without treating it as authority;
11. checkpoint still writes with hash reference;
12. compressed path output includes a clear receipt.

## Migration sequence

### Step 1 — Inventory

List every current runner bridge and what it adds.

### Step 2 — Contract

Add `lumina_advisory_contract_r1.py`.

### Step 3 — Pipeline

Add `lumina_advisory_pipeline_r1.py` with self-guidance and Golden Spiral Memory as first participants.

### Step 4 — Enhanced runner

Add `runtime_runner_lumina_enhanced_r1.py` as an opt-in runner, not default.

### Step 5 — Sea trial

Add bridge-compression sea trial and compare against current bridge behavior.

### Step 6 — Index update

Update `ACTIVE_RUNTIME_INDEX.md` and `START_HERE_LUMINA_OS.md` only after the sea trial passes.

### Step 7 — Compatibility note

Mark older bridges as active compatibility wrappers, not dead code.

## Acceptance criteria

Bridge compression is successful only if:

- no advisory module gains authority;
- no existing bridge behavior is lost;
- ModeGuard remains the single owner of legality decisions;
- governance receipts stay intact;
- the active runtime index becomes easier to read;
- future advisory modules can plug in without another bespoke runner bridge.

## Guiding phrase

```text
Fewer bridges. Clearer river. Same law.
```

## Working conclusion

Bridge accumulation is not failure. It is evidence of careful experimental growth.

But Lumina is moving from scaffold into inhabitable system. The next maturity step is to compress repeated bridge patterns into a clean advisory pipeline and enhanced runner while preserving the strict authority separation that makes the project trustworthy.
