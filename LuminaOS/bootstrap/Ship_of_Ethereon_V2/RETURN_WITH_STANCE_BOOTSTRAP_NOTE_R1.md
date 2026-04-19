# Return With Stance — Bootstrap Note R1

This note marks the next architectural move for Lumina OS inside the governed bootstrap path.

## What landed

Two repo-native runtime modules now live inside the bootstrap runtime directory:

- `runtime/project_return_repo_native_r1.py`
- `runtime/workspace_host_repo_native_r1.py`

## Why this matters

The bootstrap already held runtime law, governance, canon lineage, and bounded context.

What it did not yet hold inside the same path was the narrower pair of behaviors that make Lumina feel more like a host substrate than a static idea:

1. a project can be left and resumed without guessing
2. a project can return with a bounded working surface around it

These new modules are the first repo-native proofs for those behaviors.

## What they are not

This is not yet a deep merge into `runtime_spine_r1.py` or `runtime_runner_r1_merged.py`.

That deeper merge should come later, once the project-return and workspace-host payloads have been pressure-tested enough to justify becoming direct runtime law.

## Current role

For now, these modules do four useful things:

- move continuity return into the bootstrap path
- move workspace-host restoration into the bootstrap path
- keep state repo-native through `repo_paths_r1.py`
- define a cleaner bridge between continuity and host behavior

## Next likely move

When ready, the next hardening step is to absorb the project-return and workspace-host fields into the main session / runner flow so Lumina can restore not only legality and continuity, but active working stance as first-class runtime behavior.
