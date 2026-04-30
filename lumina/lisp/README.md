# Lumina Lisp Layer

The Lumina Lisp layer is a small, non-executable notation practice for preserving meaning, state, intent, and governance in a compact human-readable form.

It is not a runtime dependency, parser target, agent language, or source of authority.

## Purpose

Use `.lx` files to capture moments that have stabilized enough to deserve preservation:

- session truth
- navigation intent
- system state
- governance boundaries
- dry-dock findings
- sea-trial outcomes
- reflection after meaningful change

## Boundaries

- Lisp files are not executable.
- Lisp files do not override Python, JSON, JavaScript, governance logs, or runtime state.
- Lisp files may summarize decisions, but they do not authorize decisions.
- Symbolic language may clarify meaning, but it must not become hidden runtime law.

## Suggested structure

```text
lumina/lisp/
  sessions/
  inspections/
  governance/
  flows/
```

## Naming pattern

Use descriptive names with a numeric suffix:

```text
session_website_mobile_stabilization_001.lx
dry_dock_lisp_opportunities_001.lx
governance_symbolic_boundary_001.lx
flow_public_site_pathways_001.lx
```

## When to use Lisp

Use Lisp when a moment has become clear:

```lisp
(session
  (topic website-mobile-header)
  (result stable)
  (next observe)
)
```

Use Lisp sparingly. It should appear less often than ordinary notes, but when it appears, it should feel obviously useful.

## When not to use Lisp

Avoid Lisp for:

- raw brainstorming
- fast iteration
- unsettled design exploration
- anything that still needs ordinary prose
- anything that must be executable or authoritative

## Current role

The Lisp layer currently acts as a practice of symbolic continuity. It may later inform dashboards, summaries, or inspection tooling, but only after it proves useful as a manual notation layer.
