# Return With Stance — Bootstrap Note

This note records the next architectural threshold for Lumina OS inside the governed bootstrap path.

## What landed

The repo-native return / host layer now feeds the main runtime path more directly.

Core runtime files now carry:

- `project_id` through session state and context bundles
- bounded `working_stance` through session state and context bundles
- resolved project-return summaries in the context path when a prior project surface exists
- resolved host-bundle summaries in the context path when a bounded workspace surface exists

The repo-native modules remain:

- `runtime/project_return_repo_native_r1.py`
- `runtime/workspace_host_repo_native_r1.py`

## Why this matters

The earlier bridge work proved two believable Lumina-native behaviors:

1. a project can be left and resumed without guessing
2. a project can return with a bounded working surface around it

The next necessary move was to stop treating those behaviors as merely adjacent proofs.

Lumina now carries project stance inside the main session / context flow itself.
That makes the governed runtime feel more like a host substrate and less like a shell that happens to call host-like modules on the side.

## What still remains bounded

This does **not** make workspace state into governance law.

The continuity layer still owns:
- session continuity
- checkpoints
- resume legality

The host layer still owns:
- panels
- tool bindings
- reference surfaces
- host bundles

Governance still owns:
- transitions
- mutation legality
- promotion legality
- canon lineage

## Current role

At this stage, the return / host layer does five useful things:

- preserves project-scoped return without guessing
- preserves bounded workspace-host restoration
- keeps those artifacts repo-native
- projects their stance into the main runtime flow
- keeps authority boundaries explicit

## Next likely move

The next hardening step is not “make stance exist.”
That threshold is crossed.

The next step is to deepen:

- checkpoint-triggered stance capture
- richer stance resolution from prior project history
- clearer orchestration behavior around the bounded workspace surface
- future UI/runtime consumption of host bundles

without letting any of that become hidden governance authority.
