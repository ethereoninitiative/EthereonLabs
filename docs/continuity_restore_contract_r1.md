# Continuity Restore Contract R1

This is the first narrow continuity-restore proof for Lumina.

It does not attempt full orchestration.
It proves one simpler thing instead:

> a person can leave a project, return later, and the system can resolve the latest known working state for that project without guessing.

## Core additions

- `project_id` becomes part of session state
- explicit checkpoints become restore capture points
- each checkpoint writes a project-scoped restore record
- the latest restore for a project can be resolved directly
- project resume routes through the stored checkpoint path

## Restore payload shape

A restore point carries:

- project id
- session id
- checkpoint path
- captured timestamp
- current mode
- artifacts in scope
- pending next action
- last completed action
- workspace state
- continuation notes
- optional linked host bundle path

## Why this matters

Before this step, the runtime could resume a checkpoint if you already knew where it was.
After this step, the runtime can answer a more Lumina-native question:

- what is the latest state of project X?

That is the first believable doorway into continuity restore.

## Workspace host handshake

With `lumina_workspace_host_spike_r1.py` present, continuity restore may now also resolve an optional host bundle for the same project id.

That does **not** turn continuity restore into full host orchestration.
It simply means project return can now distinguish between:

- `checkpoint_only`
- `checkpoint_plus_host`

The continuity layer still owns checkpoint truth.
The host layer still owns the bounded workspace surface.

## Deliberate limits

This version does **not** yet include:

- automatic background capture
- multi-project ranking
- cross-application orchestration
- adaptive layout behavior
- inference-heavy next-step prediction
- real UI rendering

Those can come later.
The current aim is structural clarity, lawful capture, and reproducible project return.
