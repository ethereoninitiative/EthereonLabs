# Artifact Truth Contract

**Purpose:** prevent drift between executable runtime truth, capability exposure, public documentation, and website claims.

## Source of truth hierarchy

1. Executable runtime behavior
2. Capability registry
3. Sea-trial validation receipts
4. Start-here / operating-map documentation
5. Public website messaging

If a higher layer changes, lower layers must be reconciled.

## Drift checklist

When runtime structure changes, inspect:

- capability_registry_r1.json
- CURRENT_OPERATING_MAP.md
- START_HERE_LUMINA_OS.md
- relevant bootstrap README files
- public website claims about Lumina / continuity / OS behavior

## Red flags

- docs describe deprecated runtime paths
- website claims capabilities not exposed by registry
- sea trials validate behavior not explained anywhere
- exploratory spikes presented as current substrate
- symbolic framing accidentally described as structural law

## Rule

Poetic framing may orient.
Executable architecture defines truth.
