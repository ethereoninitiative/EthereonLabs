# Lumina Runtime Daemon v0.1

Minimal heartbeat implementation for Lumina OS.

## What this is

A small local process that can:
- start or resume a session
- report status
- write checkpoints
- stop cleanly
- enforce basic mode transition rules

## What this is NOT

- not a full operating system
- not a UI or desktop shell
- not an autonomous agent

## Requirements

Python 3.10+

## Usage

```bash
python lumina_daemon_v0_1.py start
python lumina_daemon_v0_1.py status
python lumina_daemon_v0_1.py checkpoint --label test
python lumina_daemon_v0_1.py transition --target-mode Sandbox
python lumina_daemon_v0_1.py stop
```

## Default state directory

```text
~/.lumina/runtime_daemon_v0_1/
```

Contents:
- daemon_state_v0_1.json
- daemon_events_v0_1.jsonl
- checkpoints/

## First success test

```bash
python lumina_daemon_v0_1.py start
python lumina_daemon_v0_1.py checkpoint --label first
python lumina_daemon_v0_1.py stop
python lumina_daemon_v0_1.py start
python lumina_daemon_v0_1.py status
```

Expected:
- same session_id
- last_checkpoint present
- state_source = resumed
```

## Notes

- Mode transitions are guarded but minimal
- Governance is intentionally lightweight in v0.1
- Symbolic layers are not used for runtime decisions
