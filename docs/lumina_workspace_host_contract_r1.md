# Lumina Workspace Host Contract R1

## Status
First host-environment proof for Lumina inside the repository.

## Intent

The continuity-restore spike proved that a project can be left and later resumed through an explicit checkpoint path.

This contract proves the next narrower and more Lumina-native thing:

> a project can return with a bounded host workspace around it, not just with a checkpoint pointer.

That means the system can restore:
- the active layout
- the visible panel set
- the tool palette for the current project
- reference surfaces
- the current focus target
- continuation notes that belong to the working surface itself

This is **not** yet full Lumina orchestration.
It is the first believable host-layer proof.

## Why this addition exists

The repository now has:
- a strong public site
- a real Chamber threshold-space
- a backend scaffold for shared social interaction
- a narrow continuity-restore proof

What it still lacks is a more tangible sign that **Lumina itself** is becoming a host environment rather than remaining only a page on the site.

This addition fills that gap without pretending the whole operating layer already exists.

## Core additions

- `project_id` remains the continuity anchor
- a host session now carries:
  - active layout id
  - panel states
  - tool bindings
  - reference surfaces
  - focus target
  - continuation notes
- explicit host snapshots become project-scoped host restore points
- the latest host snapshot for a project can be resolved directly
- a host bundle can be emitted for later interface/runtime consumption

## Host payload shape

A host snapshot carries:

- project id
- host session id
- captured timestamp
- current mode
- active layout id
- panels
- tool bindings
- references
- focus target
- continuation notes
- optional restore checkpoint path
- optional artifact scope

## Deliberate limits

This version does **not** yet include:

- automatic cross-application launching
- adaptive panel inference
- ranked tool suggestion
- autonomous background capture
- provider orchestration
- real UI rendering
- multi-user workspace coordination

Those can come later.

The purpose of R1 is simpler:
to make Lumina's host logic visible as code and data instead of leaving it implied.

## Relationship to continuity restore

`continuity_restore_spike_r1.py` proves:
- latest state for project X can be found lawfully

`lumina_workspace_host_spike_r1.py` proves:
- latest state for project X can be returned with a bounded working surface around it

That is the more believable bridge from continuity into host environment behavior.

## Success criteria

This addition succeeds if:

- a project-scoped host session can be created
- panels, tools, references, and focus target can be updated explicitly
- a host snapshot can be written reproducibly
- the latest host snapshot can be resolved by project id
- a bounded host bundle can be emitted for later runtime use
- the implementation stays honest about being a host proof, not a finished Lumina OS
