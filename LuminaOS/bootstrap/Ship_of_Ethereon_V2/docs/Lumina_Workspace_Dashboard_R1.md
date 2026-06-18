# Lumina Workspace Dashboard R1

**Project:** Lumina OS / Ship of Ethereon V2 Bootstrap  
**Layer:** Harbor workspace surface  
**Status:** R1 local dashboard  
**Date:** June 18, 2026

---

## Purpose

Lumina should answer the operator's first question before work begins:

> Where am I?

Workspace Dashboard R1 makes `lumina` with no subcommand show a compact Harbor status panel.

It can also be invoked explicitly:

```bash
lumina dashboard
```

---

## Dashboard Contents

The dashboard surfaces:

- active project name and slug
- active project root
- recent receipt count
- latest continuity shape
- drift note
- governance event count and latest event type
- canon head
- available presets
- suggested next commands

---

## Authority Boundary

The dashboard may:

- read active project metadata
- read state-browser summaries
- read preset registry names
- suggest next local commands

The dashboard may not:

- create runtime law
- mutate governance state
- authorize canon promotion
- expose capabilities
- execute a governed cycle automatically
- treat dashboard summaries as canon truth

It is a Harbor orientation surface only.

---

## Example Flow

```bash
lumina
lumina project active
lumina run --preset drydock
lumina compare
lumina dashboard
```

---

## Why This Matters

Before R1, Lumina required the operator to already know which command to run.

After R1, Lumina has an entrance.

The first screen is not a file list or a traceback. It is orientation.

---

## Guiding Sentence

Let Lumina open like a place, not a toolbox drawer.
