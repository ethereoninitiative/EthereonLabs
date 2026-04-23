# Lumina Appliance Layout r1

This note defines the first suggested filesystem layout for a Lumina OS beta appliance hosted on Ubuntu Server LTS.

## Proposed layout

### Repository checkout
- `/opt/lumina/EthereonLabs`

This keeps the repo in a stable system location owned by the service user.

### Environment and service configuration
- `/etc/lumina/lumina-appliance.env`

This file should hold host-local environment values for Chamber and service configuration.

### Persistent state root
- `/var/lib/lumina`

Suggested child paths:
- `/var/lib/lumina/runtime`
- `/var/lib/lumina/checkpoints`
- `/var/lib/lumina/governance`
- `/var/lib/lumina/advisory-history`
- `/var/lib/lumina/chamber`

### Log root
- `/var/log/lumina`

Suggested log files:
- `/var/log/lumina/orchestrator.log`
- `/var/log/lumina/chamber-advisory.log`

## Why this shape

This separates:

- mutable host config in `/etc`
- persistent operational state in `/var/lib`
- service logs in `/var/log`
- repo code in `/opt`

That is a conventional Linux service layout and makes the Lumina appliance easier to reason about, back up, and restore.

## Current truth

The repo itself still contains internal runtime state conventions of its own.
This layout note does not override runtime law.
It gives the Ubuntu appliance a cleaner outer operating envelope.
