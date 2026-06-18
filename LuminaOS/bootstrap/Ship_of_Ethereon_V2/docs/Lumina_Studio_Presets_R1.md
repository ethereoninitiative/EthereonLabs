# Lumina Studio Presets R1

**Project:** Lumina OS / Ship of Ethereon V2 Bootstrap  
**Layer:** local operator convenience, not governance law  
**Status:** R1 host UX hardening  
**Date:** June 18, 2026

---

## Purpose

Lumina already has a local command vocabulary, doctor readiness checks, state schema handling, and a state browser.

This R1 adds a lighter operator surface for common run shapes:

```bash
lumina presets
lumina run --preset observe
lumina run --preset drydock
lumina run --preset return
lumina run --preset psi42
lumina compare
```

The goal is to make the first local runtime loop easier to use without changing runtime law.

---

## Authority Boundary

Presets may:

- prefill prompt, mode, action type, focus, depth, intent, and overlay preference
- reduce operator friction
- make common local workflows easier to remember
- route to the existing governed runtime runner

Presets may not:

- define mode legality
- authorize mutation
- authorize canon promotion
- bypass input integrity
- expose capabilities outside the registry
- alter governance, checkpoint, or canon authority

Runtime law remains authoritative.

---

## Preset Registry

The registry lives at:

```text
studio/lumina_presets_r1.json
```

Current presets:

- `observe` — default bounded Observation audit cycle
- `drydock` — architecture and package-readiness inspection
- `return` — project return and continuity-orientation audit
- `psi42` — bounded Psi-42 Observation witness path with Ethereonic overlay

---

## State Comparison

`lumina compare` reads the same state browser data as `lumina state`, but surfaces the operator-facing summary:

- latest continuity shape
- recent drift note
- recurrence note
- recent shape counts
- governance event count
- latest governance event type
- canon head
- receipt count

It remains read-only.

---

## Example Flow

```bash
lumina doctor --ensure-state
lumina presets
lumina run --preset drydock
lumina compare
lumina state --limit 3
```

---

## Guiding Sentence

Make the governed loop easier to enter without making convenience into law.
