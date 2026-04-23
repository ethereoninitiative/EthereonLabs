# Lumina Beta Hardware Target r1

This note defines the first recommended **hardware target** for a Lumina OS beta appliance while the Ubuntu Server VM validation path proceeds in parallel.

## Recommended class

A **dedicated mini PC / NUC-style machine** is the preferred beta host.

Why this class:

- small always-on footprint
- lower noise and power draw than a tower
- cleaner appliance identity than a spare laptop
- easier to dedicate fully to Lumina than a shared desktop

## Recommended baseline spec

### CPU
- modern 64-bit x86 processor
- 4 to 8 cores is a healthy beta target

### Memory
- minimum: 16 GB RAM
- preferred: 32 GB RAM

Reason:
The host should have room for Ubuntu Server, PostgreSQL, Chamber services, bounded orchestration, logging, and future interface growth without feeling cramped.

### Storage
- minimum: 512 GB SSD
- preferred: 1 TB SSD

Reason:
This gives room for repo growth, state, logs, checkpoints, database storage, snapshots, and future build artifacts.

### Network
- reliable Ethernet preferred
- Wi-Fi acceptable as secondary convenience, not primary dependency

### GPU
- not required for the first beta appliance

Reason:
The current Lumina beta path is about governed substrate, orchestration, persistence, and consent surfaces rather than local model inference or graphics-heavy rendering.

## Recommended posture

The first dedicated beta machine should be:

- boring
- stable
- easy to image
- easy to re-install
- easy to leave on continuously

This is not the moment to optimize for maximum power or visual flair.
It is the moment to optimize for **reliable presence**.

## Machine-role recommendation

Use the first dedicated machine for:

- Ubuntu Server LTS host substrate
- Lumina governed runtime stack
- Chamber advisory consent surface
- PostgreSQL persistence
- reboot and continuity validation

Do not overload the first beta box with unrelated creative software, general desktop clutter, or experimental local AI stacks unless they are intentionally part of the appliance test plan.

## Sequencing note

This hardware target note is paired with a VM-first validation path.

The sequence is:

1. define the ideal beta host now
2. validate the Ubuntu appliance scaffold on a VM
3. buy or dedicate the machine after the VM reveals practical friction
4. image the dedicated host with what the VM taught us

## Exit condition

The hardware target is considered good enough when it supports:

- Ubuntu Server LTS cleanly
- PostgreSQL comfortably
- Lumina services without thermal or memory pressure
- repeated reboot / restart validation
- continuous quiet operation as a machine-resident appliance
