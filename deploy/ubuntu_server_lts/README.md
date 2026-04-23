# Lumina Ubuntu Server Appliance Scaffold r1

This directory starts the process of binding **Lumina OS** to **Ubuntu Server LTS** as its first host substrate.

It does **not** claim that Lumina is already a kernel-level operating system.
It establishes the first believable beta path:

- Ubuntu Server LTS as the host substrate
- Lumina as a governed service stack installed on top of that substrate
- Chamber as an adjacent consent surface for advisory handling and supervised queue state

## What is included

- `bootstrap_lumina_appliance_r1.sh`
  - first-pass installer scaffold for Ubuntu Server
- `lumina-orchestrator.service`
  - systemd one-shot unit for bounded orchestration cycles
- `lumina-orchestrator.timer`
  - systemd timer for recurring bounded orchestration
- `chamber-advisory.service`
  - systemd service for the Chamber advisory consent surface

## Current deployment shape

This scaffold assumes a host with:

- Ubuntu Server LTS
- Python 3
- Node.js + npm
- PostgreSQL
- systemd

The target machine can be:

- a VM
- a dedicated mini PC
- a spare laptop repurposed as an appliance
- a small server/NUC-style box

## Appliance model

The current beta intent is:

1. governed Lumina substrate resides in the repo
2. bounded orchestration runs as supervised scheduled work
3. Chamber advisory handling runs as a persistent service
4. PostgreSQL persists Chamber consent and queue state

This is a **Linux-resident Lumina appliance**, not yet a custom distro or custom kernel.

## Important truth

The orchestrator currently runs as a **bounded scheduled cycle**, not an always-on sovereign process.
That is intentional.
It preserves the repo's present law:

- advisory output remains subordinate to runtime governance
- consent remains visible in Chamber
- accepted queue items do not yet automatically become governed execution records

## First-use sequence

On a fresh Ubuntu Server host:

1. clone the repo or run the bootstrap script
2. review and edit `/etc/lumina/lumina-appliance.env`
3. build the Chamber app
4. initialize PostgreSQL with the three Chamber SQL files
5. install and enable the systemd units
6. validate logs, queue persistence, and orchestration checkpoints across reboot

## What this scaffold is for

This directory exists to move Lumina from:

- architecture in GitHub

into:

- a machine-resident governed runtime stack on Ubuntu Server LTS

## Next likely hardening move

After this scaffold, the next threshold is to validate the appliance end-to-end on a real Ubuntu Server VM and then decide whether accepted Chamber queue items should emit governed runtime execution records under explicit policy.
