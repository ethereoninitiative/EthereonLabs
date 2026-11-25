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
- `host_registry.example.json`
  - example host-of-record registry for deployment drydock
- `deployment_doctor_r1.py`
  - non-mutating preflight checker for host boundary, env, path, and service-file readiness
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

## Deployment keel guardrails

This scaffold is now paired with a deployment keel documentation set:

- `../../docs/DEPLOYMENT_HOST_REGISTRY_MODEL.md`
- `../../docs/DEPLOYMENT_RUNTIME_RECEIPT_CONTRACT.md`
- `../../docs/DEPLOYMENT_DRYDOCK_CHECKLIST.md`

These documents define the host-of-record model, deployed receipt expectations, and drydock checks that should be satisfied before this appliance is treated as ordinary hosted operation.

The short rule:

```text
host boundary -> appliance preflight -> governed runtime receipt -> Chamber bridge
```

Do not treat accepted Chamber queue items as executable work until both the Chamber bridge discipline and deployment host discipline hold.

## First-use sequence

Use a disposable Ubuntu Server LTS VM first. Preparation and activation are intentionally separate.

1. Review the exact checkout and take a VM snapshot. Run the bootstrap with explicit `--prepare` only; this installs packages, prepares the repository, builds Chamber and writes an environment template. It does not provision the Chamber database or install, enable or start Lumina units. OS package installation may start dependency services such as PostgreSQL.
2. Have the operator configure real database credentials and a private (0600) regular environment file. Provision the database and apply the SQL migrations separately under reviewed instructions; never use placeholder passwords.
3. Create a real host-of-record file outside the repository from the example. Do not pass the checked-in example as proof of enrollment.
4. Run the deployment doctor and resolve all halt conditions. It exits 1 on reported halt conditions and 0 on a passing structural report.
5. Treat a passing report only as readiness for the next DryDock, not authorization or proof of working services. Validate database connectivity, unit contents and service account isolation, verify the updated governed-cycle service on an actual systemd host, and review actual state ownership before any separate operator-approved activation.
6. Validate receipts, logs, queue persistence and restart/reboot behavior in the VM before considering a dedicated host.

Example non-mutating preflight (replace the host ID and registry path with real operator-maintained values):

```bash
python3 deploy/ubuntu_server_lts/deployment_doctor_r1.py \
  --repo-root /opt/lumina/EthereonLabs \
  --env-file /etc/lumina/lumina-appliance.env \
  --registry /etc/lumina/host_registry.json \
  --host-id my-reviewed-host
```

Offline structural fixture trial (does not run `--prepare` or start services):

```bash
python3 deploy/ubuntu_server_lts/sea_trials_deployment_preflight_r1.py
```

The host registry is an operator declaration, not authenticated host identity. The doctor checks selected structural conditions, not actual database connectivity, process isolation, ownership, OS authorization, or readiness for a privileged resident.

## What this scaffold is for

This directory exists to move Lumina from:

- architecture in GitHub

into:

- a machine-resident governed runtime stack on Ubuntu Server LTS

## Next likely hardening move

After this scaffold, the next threshold is to validate the appliance end-to-end on a real Ubuntu Server VM, emit a deployment drydock receipt, and then decide whether accepted Chamber queue items should emit governed runtime execution records under explicit policy.


## Governed observation cycle R1

The proposed Ubuntu timer now invokes `governed_appliance_cycle_r1.py`, which invokes the existing V2 `bin/lumina run` host entrypoint with a fixed Observation/audit request and explicit runtime base beneath `/var/lib/lumina`. It requires an affirmative governance-chain witness, a non-halted result, the expected action/mode, and existing receipt evidence paths within the chosen state root before reporting success. A halted runtime result is a failed appliance cycle even if the CLI process exits zero. No arbitrary shell command, model call, system mutation, or privilege escalation is added.

The core runner, project/session registries, state browser and Bridge state now honor explicitly configured `LUMINA_STATE_ROOT`, preserving their previous behavior when unset. This is a targeted alignment, not proof that every experimental or legacy surface honors it. The service no longer receives Chamber database credentials; systemd's StateDirectory, LogsDirectory and read-only system mounts constrain this service. These are proposed unit settings, not a tested isolation boundary. The service account is still shared with Chamber; separation and authenticated authorization remain required before host maintenance.

Offline integration trial from a complete checkout:

```bash
python3 deploy/ubuntu_server_lts/sea_trials_governed_appliance_cycle_r1.py
```

The trial invokes two fresh CLI processes against one temporary state root, checks evidence retention and shared governance log, and checks the state browser sees both runs. This is not an OS reboot, concurrent-writer test or systemd execution. Do not activate the timer until the existing deployment preflight and real Ubuntu VM checks are satisfied.


## Hearth read-only execution boundary R1

This opt-in prototype accepts a single fixed request (`disk_status`) over a local Unix stream socket and returns aggregate root filesystem capacity only. It uses Linux SO_PEERCRED to compare the actual connecting UID against a separately configured account, not a caller-supplied identity. No arbitrary command, path, environment, mutation, privilege or model interface is exposed. It bounds request length and reading time. The client must half-close its write side; the exact request frame is defined by the Python module.

The staged systemd socket and per-connection unit are **not installed or enabled** by the bootstrap. Before considering activation in a disposable VM, an operator must provision a distinct unprivileged `lumina-hearth` service account and group, review the permitted `lumina` client account (currently shared with other services), and install verified broker code under root-owned, non-client-writable `/usr/local/lib/lumina-hearth/`. Never execute broker code from the existing service-user-writable checkout. Verify the complete ownership chain, installed unit settings, Unix socket permissions, process identities, timeout behavior, and aggregate measurement against the actual VM. The kernel credential check authenticates a local account, not a resident identity; root remains a trusted OS administrator and can bypass OS boundaries. The current account is not resident-exclusive. Do not activate on a production or personal machine.

Offline test from checkout: `python3 deploy/ubuntu_server_lts/sea_trials_hearth_broker_r1.py`. Local Linux testing passed all nine protocol checks. A separate sandbox experiment passed a real accepted Unix stream from UID 65534 to a broker subprocess running as UID 1, and rejected a UID 0 client. These are sandbox tests, not systemd activation or Ubuntu appliance validation. No host mutation or persistent authorization has been implemented. Before any write capability, isolate the resident account from Chamber, implement independently authenticated scoped approvals, persistent replay protection, recovery and receipts, and test against adversarial requests.
