# Lumina Continuity Correlation R1

## Purpose

Lumina currently creates several valid but distinct references during one work episode:

- a persistent Harbor project
- a persistent Harbor session
- a governed runtime session
- a continuity-restore session
- a workspace-host session

These references must be linked without being collapsed into one object.

## Correlation Envelope

```text
project_slug
harbor_session_id
runtime_session_id
restore_session_id
host_session_id
correlation_id
```

The Harbor session is the primary human-facing work episode.

The runtime, restore, and host references describe specialized instances attached to that episode.

## Resolution Rule

Project resolution should proceed in this order:

1. explicit project argument
2. active Harbor project marker
3. active Harbor session project
4. clearly labeled projectless execution or halt

Raw prompt text should not silently become a project identifier.

## Mismatch Rule

If the active project marker and active session marker name different projects, correlation must fail rather than guessing.

## Authority Boundary

Correlation coordinates references only.

It does not transfer:

- governance authority
- canon authority
- checkpoint legality
- mode legality
- capability authority

## Next Integration

A later runner bridge should emit the correlation envelope into runtime receipts and active-session receipt storage.
