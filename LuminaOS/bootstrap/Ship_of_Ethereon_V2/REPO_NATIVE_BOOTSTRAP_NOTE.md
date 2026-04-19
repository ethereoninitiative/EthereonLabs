# Repo-native bootstrap note

These repo-native files supersede the earlier bootstrap-only imports when you want the Lumina OS substrate to behave like a real repository checkout rather than a ChatGPT container snapshot.

## Added repo-native layer

- `runtime/runtime_spine_repo_native_r1.py`
- `runtime/runtime_runner_repo_native_r1.py`
- `runtime/psi42_transceiver_v1_6_full_local.py`
- `runtime/sea_trials_set_one_repo_native_r1.py`
- `runtime/project_return_repo_native_r1.py`
- `runtime/workspace_host_repo_native_r1.py`
- `runtime/lumina_return_host_repo_native_bridge_r1.py`
- `runtime/runtime_runner_return_host_bridge_r1.py`

## Why they exist

They preserve the earlier bootstrap work while correcting practical gaps:

1. repo-relative state and artifact paths
2. a fuller local Ψ-42 implementation
3. package-oriented import behavior inside the repository
4. project return without guessing
5. bounded workspace-host restoration
6. bridge-based activation of the repo-native return/host layer without risky surgery to the main runner

## Guidance

Use the repo-native runner and repo-native sea-trials files as the preferred entry points for ongoing Lumina OS work on this branch.
Use the return/host bridge runner when the task is about restoring active project stance through the bootstrap-local repo-native layer rather than the older spike path.
