# Lumina Runtime Daemon v0.1 Contract

## Purpose

Lumina Runtime Daemon v0.1 defines the first inside-out heartbeat of Lumina OS.

This is not a full operating system, desktop shell, or visual interface. It is the smallest persistent runtime process that can wake, load state, expose status, route requests through governance, and preserve continuity across restart.

## Core Thesis

Build Lumina from the inside out.

1. inner law
2. persistent state
3. runtime heartbeat
4. human interface
5. host integration
6. appliance / distro packaging

This contract covers step 3 while depending on steps 1 and 2.

## Goals

The daemon should:

- start as a local process
- load an existing session state or create a new one
- expose a simple status surface through CLI and/or local endpoint
- report current mode, session id, checkpoint path, and uptime
- route load-bearing actions through governance checks
- write lifecycle events to a durable log
- write checkpoints on request and at controlled lifecycle moments
- resume from saved state after restart
- keep Ethereonic overlays supplemental and non-load-bearing

## Non-Goals

The daemon must not:

- act as a full operating system
- replace the host OS process manager
- operate as an autonomous unsupervised agent
- mutate canonical artifacts without explicit governed action
- treat symbolic, poetic, or Ethereonic language as runtime law
- require RSE, harmonic signatures, Toki Pona, binary, or light-language layers for legality or resume behavior
- expose destructive host operations in v0.1

## Required Runtime Responsibilities

### 1. Lifecycle

The daemon must support:

- `start`
- `status`
- `checkpoint`
- `stop`
- `resume`

A minimal implementation may expose these as CLI commands before adding any local HTTP endpoint.

### 2. Session State

The daemon must maintain or delegate to a session state object containing at least:

- session id
- created timestamp
- current mode
- last checkpoint
- turn or cycle count
- last lifecycle event

### 3. Governance Routing

All load-bearing requests must pass through the existing governance path before execution.

Load-bearing actions include:

- mode transition
- mutation
- promotion
- checkpoint authority changes
- capability exposure changes

### 4. Checkpointing

The daemon must be able to write a checkpoint that captures:

- active session state
- current mode
- last lifecycle event
- timestamp
- checkpoint hash or equivalent integrity marker when available

### 5. Resume Behavior

On restart, the daemon must attempt to resume from the latest valid checkpoint or saved session state.

If no valid state exists, it may create a new session, but must record that a fresh session was created rather than silently pretending continuity was preserved.

### 6. Status Surface

The daemon status response should include:

```json
{
  "daemon": "lumina-runtime-daemon",
  "version": "0.1",
  "status": "running",
  "session_id": "...",
  "current_mode": "Continuity",
  "last_checkpoint": "...",
  "uptime_seconds": 0,
  "state_source": "resumed|fresh",
  "governance_available": true
}
```

### 7. Boundary Rules

The daemon may load supplemental Ethereonic context for expression or interface purposes.

It may not allow that context to define:

- mode legality
- mutation permission
- promotion gates
- checkpoint legality
- capability loading
- session continuity authority

## First Success Test

The first successful daemon sea trial is:

1. start daemon
2. create or load session
3. request status
4. write checkpoint
5. stop daemon
6. restart daemon
7. request status again
8. confirm session id, mode, and checkpoint state are preserved or honestly reported as fresh if resume fails

Pass condition:

The daemon resumes or reports failure truthfully without symbolic dependency, hidden state invention, or governance bypass.

## Suggested File Targets

Future implementation may live under:

- `LuminaOS/runtime/daemon/lumina_daemon_v0_1.py`
- `LuminaOS/runtime/daemon/README.md`
- `LuminaOS/runtime/daemon/tests/`

Exact location may be adjusted after inspecting current runtime layout.

## DND Principle

Do not drift.

- Do not drift into fog.
- Do not drift into flattening.
- Preserve depth while improving legibility.

For daemon work, this means: build the heartbeat cleanly before building the skin.
