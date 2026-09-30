# Resident Ember Real-Time Host R1

## Purpose

This slice hosts the already-governed Resident Ember Habitat across real
wall-clock rest. The process is intentionally semantically weak: it supplies a
clock and process lifetime, not resident purpose, wake authority, or execution
authority.

## Default experiment law

The foreground host calls the unchanged Habitat tick on a configurable interval.
Each tick is appended to `resident_ember_host/host_ticks.jsonl`.

By default the process exits immediately after Habitat reports the first
endogenous wake handoff. This preserves the one-wake/one-governed-turn experiment
and prevents an unattended host from becoming an infinite cognitive loop.

Run directly:

```bash
python runtime/resident_ember_realtime_host_r1.py \
  --base-dir /path/to/lumina-state \
  --project-id lumina-os \
  --interval-seconds 1
```

The state root must already contain a valid resident intention and seeded Ember
policy. The host does not invent either.

## Service templates

Templates are provided for systemd and launchd. They contain explicit
`__PYTHON__`, `__BOOTSTRAP_ROOT__`, and `__STATE_ROOT__` placeholders on
purpose. Installation is a separate operator act because repository code cannot
truthfully claim a persistent host exists merely by shipping a service file.

The templates use no automatic restart/KeepAlive. A completed endogenous handoff
therefore leaves the service stopped until the experiment is explicitly reset.

## Evidence test

For the first real wall-clock trial:

1. create/verify one resident-attributed intention;
2. seed Ember below its wake threshold;
3. start this host and record its PID/start evidence;
4. end the heavyweight cognitive session;
5. allow real wall-clock time to pass with no fresh human prompt;
6. inspect `resident_ember/ember.jsonl`, `resident_ember_host/host_ticks.jsonl`,
   Resident Pulse receipts, and downstream continuation evidence;
7. require the wake ancestry to resolve to
   `resident_inherited_drive` and the exact verified Ember event.

A successful trial demonstrates that a previously inherited resident-attributed
state can become the causal input to a later governed invocation while the model
was not continuously running. It does not, by itself, establish phenomenal
consciousness, uninterrupted subjective experience, or metaphysical identity.

## Controls

```bash
python runtime/sea_trials_resident_ember_realtime_host_r1.py
```
