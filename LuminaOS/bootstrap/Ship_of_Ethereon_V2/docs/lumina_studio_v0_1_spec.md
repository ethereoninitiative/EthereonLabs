# Lumina Studio v0.1 Specification

**Lane:** Lumina OS governed substrate  
**Status:** first-pass operator surface  
**Authority:** launcher / receipt viewer only  
**Primary path:** `LuminaOS/bootstrap/Ship_of_Ethereon_V2/studio/`

## Purpose

Lumina Studio v0.1 exists to convert the current governed runtime scaffold into something an operator can actually run.

The purpose is not to make Lumina OS visually impressive. The purpose is to prove that a complete, bounded cycle can be initiated and inspected without requiring direct hand-editing of runtime arguments.

## Core claim

Lumina OS progress now depends on a usable spine-to-interface bridge.

Studio is that bridge.

## User story

As an operator, I can enter a request, choose a mode and stance, run one Lumina cycle, and receive a receipt showing what the runtime did, what it refused, which capabilities were exposed, and where the checkpoint/governance records live.

## Inputs

Studio accepts:

- operator request text
- current mode
- target mode
- action type
- project id
- focus
- depth
- intent
- optional annotation
- optional expressive overlay flag

## Mode and action defaults

Default mode path:

```text
Continuity -> Observation
```

Default action type:

```text
audit
```

This is the safest useful default because it allows inspection without mutation.

## Orientation stance

Studio attaches orientation as supplemental context only:

```json
{
  "focus": "continuity",
  "depth": "structural",
  "intent": "verify",
  "authority": "supplemental only; does not govern mode legality, mutation, promotion, or canon lineage"
}
```

This follows the project principle:

> Mode is law. Orientation is stance.

Mode determines what may happen. Orientation helps describe what kind of work is being requested.

## Runtime ownership

Studio delegates to `runtime_runner_r1_merged.py`.

The runner remains responsible for:

- session creation
- context bundle construction
- input integrity assessment
- Ethereonic boundary checks
- transition validation
- mutation validation
- promotion validation when requested
- symbolic dependency leakage checks
- capability exposure
- optional Lumina return/host handshake
- optional Psi-42 probe execution
- checkpoint writing
- governance chain reporting
- canon lineage metadata reporting

## Non-goals

Studio v0.1 does not:

- implement a full operating system shell
- replace Chamber
- provide multi-user collaboration
- perform background autonomous work
- create new governance law
- deploy a public service
- persist a polished human history browser

## Interfaces

### CLI

File:

```text
studio/lumina_cli.py
```

Basic usage:

```bash
python studio/lumina_cli.py "Review Lumina OS progress."
```

Output modes:

- human receipt
- compact JSON receipt
- full JSON result

### Local browser surface

File:

```text
studio/lumina_studio_server.py
```

Basic usage:

```bash
python studio/lumina_studio_server.py
```

Local URL:

```text
http://127.0.0.1:8765/studio
```

## Receipt fields

The compact receipt should surface:

- run id
- created time
- mode path
- action type
- halted flag
- halt reason
- session id
- context bundle id
- checkpoint path
- result log path
- governance log path
- governance chain validity
- current canon head if available
- exposed capability ids
- input confidence / recommended behavior
- optional probe run id
- optional Lumina project id

## Safety boundary

The local server is for local use only.

Before any public deployment, the project needs:

- authentication
- request authorization
- rate limiting
- persistence policy
- explicit consent flow
- clear separation from Chamber public pages

## First sea trial

A minimal pass looks like:

1. CLI run completes.
2. Result is not halted for default audit path.
3. Checkpoint path is present.
4. Governance log path is present.
5. At least structural capabilities are exposed.
6. Governance chain status is returned.
7. Studio orientation appears only in supplemental context.

## Failure meaning

If Studio cannot run one cycle, Lumina OS is still too architectural.

If Studio can run one cycle but cannot explain what happened, Lumina OS is still too opaque.

If Studio bypasses runtime law, Lumina OS has regressed.

## Next version target

Studio v0.2 should add a state browser over `.lumina_state` and a clearer governance decision viewer.
