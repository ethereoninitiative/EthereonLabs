# Deployment DryDock Checklist

**Status:** proposed checklist  
**Authority:** deployment validation guidance only  
**Scope:** Ubuntu Server appliance scaffold and future hosted Lumina runtime work

## Purpose

This checklist defines the first deployment drydock pass for the Lumina Ubuntu Server appliance lane.

The goal is simple: before the appliance is treated as ordinary hosted operation, verify that the host boundary, runtime path, service account, database shape, logs, and receipts are all inspectable.

## Preflight checks

| Check | Expected result |
|---|---|
| host record exists | host id, label, scope, operator ids, service user, state root, and log root are present |
| host record active | `revoked_at` is null and review date has not expired |
| service user matches | systemd units use the expected service user |
| env file exists | `/etc/lumina/lumina-appliance.env` exists and is readable by the service context |
| placeholder credentials removed | default placeholder database credentials are not still active |
| state root exists | state root exists and is owned by the service user |
| log root exists | log root exists and is writable by the service user |
| repo path exists | expected repo checkout exists |
| runtime path exists | expected Lumina runtime path exists |
| Chamber SQL initialized | core Chamber tables, session extension, and advisory queue extension exist |
| Chamber advisory service defined | systemd unit exists and points at the expected server path |
| orchestrator timer defined | timer exists and runs bounded cycles |
| baseline runtime receipt possible | one observation/audit cycle can emit a receipt |
| governance log path recorded | receipt points to governance log path |
| checkpoint path recorded | receipt points to checkpoint path |

## Halt conditions

Treat the deployment as not ready if any of the following are true:

- host record is missing
- host record is revoked
- env file still contains placeholder credentials
- service user differs from the host record without explanation
- repo path differs from the host record without explanation
- database initialization is incomplete
- runtime cycle cannot produce a receipt
- receipt does not identify host id or runtime path

## Recommended first drydock command

Future implementation should provide a command such as:

```bash
lumina deployment doctor
```

or:

```bash
python deploy/ubuntu_server_lts/deployment_doctor_r1.py
```

That command should emit a JSON report with:

```text
host_id
check_results
halt_conditions
receipt_paths
recommendation
created_at
```

## Relationship to Chamber bridge

Deployment drydock comes before the Chamber to runtime bridge becomes active.

The Chamber bridge answers: can an accepted advisory become governed runtime work?

Deployment drydock answers: is this host allowed and prepared to run the governed work at all?

Both must hold before public-facing supervised action is treated as real.

## Boundary

This checklist is not an implementation. It defines the inspection shape future implementation should satisfy.