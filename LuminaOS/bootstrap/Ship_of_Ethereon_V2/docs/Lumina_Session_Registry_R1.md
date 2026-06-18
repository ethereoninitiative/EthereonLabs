# Lumina Session Registry R1

**Project:** Lumina OS / Ship of Ethereon V2 Bootstrap  
**Layer:** Harbor workspace continuity  
**Status:** R1 local session registry  
**Date:** June 18, 2026

---

## Purpose

Lumina needs more than projects. It needs work episodes.

Session Registry R1 makes local sessions first-class host/workspace objects so later PRs can support resume, timeline, notes, and receipt linking.

It introduces:

```bash
lumina session create "Initial Harbor session" --open
lumina session list
lumina session active
lumina session open session-0001
lumina session archive session-0001
lumina session restore session-0001
```

---

## Storage Shape

If a project is active, sessions live under that project:

```text
.lumina_state/ship_of_ethereon_v2/projects/<project>/sessions/
```

Each session receives:

```text
session-0001/
  session.json
  receipts/
  notes/
  artifacts/
  context/
```

If no project is active, projectless sessions live under:

```text
.lumina_state/ship_of_ethereon_v2/sessions/
```

The active session marker lives at:

```text
.lumina_state/ship_of_ethereon_v2/active_session.json
```

---

## Authority Boundary

Session registry may:

- create local session folders
- record session metadata
- mark one session as active
- archive and restore session records
- provide a home for future receipts, notes, artifacts, and context

Session registry may not:

- define runtime governance
- define mode legality
- authorize mutation
- authorize canon promotion
- alter checkpoint legality
- expose capabilities
- treat session metadata as canon truth

The registry is Harbor/workspace organization only.

---

## Dashboard Integration

The Harbor dashboard now shows active session alongside active project:

```bash
lumina
```

If no session is active, the dashboard suggests:

```bash
lumina session create "Initial Harbor session" --open
```

---

## Example Flow

```bash
lumina project create EthereonLabs --open
lumina session create "Initial Harbor session" --open
lumina
lumina run --preset drydock
lumina compare
```

---

## Guiding Sentence

Make work episodes visible before trying to resume them.
