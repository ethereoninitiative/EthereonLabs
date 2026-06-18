# Lumina Project Registry R1

**Project:** Lumina OS / Ship of Ethereon V2 Bootstrap  
**Layer:** Harbor workspace foundation  
**Status:** R1 local project registry  
**Date:** June 18, 2026

---

## Purpose

Lumina needs a Harbor: a place where work is received, organized, resumed, and distributed.

Project Registry R1 makes local projects first-class host/workspace objects.

It introduces:

```bash
lumina project create EthereonLabs --open
lumina project list
lumina project active
lumina project open EthereonLabs
lumina project archive EthereonLabs
lumina project restore EthereonLabs
```

---

## Storage Shape

Projects live under:

```text
.lumina_state/ship_of_ethereon_v2/projects/
```

Each project receives:

```text
<project>/
  project.json
  receipts/
  bundles/
  checkpoints/
  notes/
  timeline/
  artifacts/
```

The active project marker lives at:

```text
.lumina_state/ship_of_ethereon_v2/active_project.json
```

---

## Authority Boundary

Project registry may:

- create local workspace folders
- record project metadata
- mark one project as active
- archive and restore project records
- provide a home for future receipts, notes, bundles, checkpoints, timeline entries, and artifacts

Project registry may not:

- define runtime governance
- define mode legality
- authorize mutation
- authorize canon promotion
- alter checkpoint legality
- expose capabilities
- treat project metadata as canon truth

The registry is Harbor/workspace organization only.

---

## Example Flow

```bash
lumina project create EthereonLabs --description "Primary Lumina OS / Ship of Ethereon workspace" --tag lumina --tag ethereon --open
lumina project active
lumina project list
lumina run --preset drydock
lumina compare
```

---

## Why This Matters

Before R1, Lumina could run governed cycles, but those cycles did not have an explicit local home.

After R1, Lumina can answer a basic habitat question:

> Where am I working?

That is the first Harbor foundation.

---

## Guiding Sentence

Make projects first-class places before adding more rooms to the Harbor.
