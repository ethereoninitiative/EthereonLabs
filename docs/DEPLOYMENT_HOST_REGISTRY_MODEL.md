# Deployment Host Registry Model

**Status:** proposed structural model  
**Authority:** deployment documentation and future implementation guide only  
**Scope:** hosted Lumina appliance work, Ubuntu Server scaffold, shared runtime experiments, and any future non-local runtime surface

## Purpose

The Ubuntu Server appliance scaffold makes deployment real enough to need a keel.

Local execution has an implicit host boundary: a known checkout, a known operator, and a known machine. A hosted or shared Lumina appliance cannot rely on that implicit boundary.

This document defines the first host-of-record model.

## Core distinction

| Rail | Question |
|---|---|
| Chamber consent | May this advisory become a queued action? |
| Runtime governance | May this requested action pass mode, mutation, promotion, and capability rules? |
| Deployment host record | Is this environment approved to operate this Lumina runtime scope? |

These rails must remain separate.

## Host-of-record fields

A future registry can be implemented as JSON, SQL, or a governed runtime state file. Minimum fields:

```text
host_id
host_label
host_type
runtime_scope
approved_by_user_id
operator_user_ids
allowed_runtime_paths
allowed_action_types
state_root
log_root
service_user
created_at
review_after
revoked_at
notes
```

## Field meanings

| Field | Meaning |
|---|---|
| `host_id` | Stable id for the environment. |
| `host_label` | Human-readable name. |
| `host_type` | `local`, `vm`, `mini_pc`, `server`, `cloud_instance`, or other documented value. |
| `runtime_scope` | `development`, `drydock`, `public_chamber`, or `release_candidate`. |
| `approved_by_user_id` | User id or local operator id that approved this host record. |
| `operator_user_ids` | Users/operators allowed to administer this host context. |
| `allowed_runtime_paths` | Runtime paths allowed to operate from this host. |
| `allowed_action_types` | `audit`, `transition`, `mutation`, and/or `promotion`. |
| `state_root` | Expected state directory, such as `/var/lib/lumina`. |
| `log_root` | Expected log directory, such as `/var/log/lumina`. |
| `service_user` | Expected service account, such as `lumina`. |
| `created_at` | Creation timestamp. |
| `review_after` | Review timestamp or null. |
| `revoked_at` | Revocation timestamp or null. |
| `notes` | Human-readable notes. |

## Example record

```json
{
  "host_id": "host-local-spencer-001",
  "host_label": "Local Spencer development host",
  "host_type": "local",
  "runtime_scope": "development",
  "approved_by_user_id": "spencer",
  "operator_user_ids": ["spencer"],
  "allowed_runtime_paths": ["/opt/lumina/EthereonLabs/LuminaOS/bootstrap/Ship_of_Ethereon_V2"],
  "allowed_action_types": ["audit", "transition"],
  "state_root": "/var/lib/lumina",
  "log_root": "/var/log/lumina",
  "service_user": "lumina",
  "created_at": "2026-05-20T00:00:00Z",
  "review_after": null,
  "revoked_at": null,
  "notes": "Initial local development host model."
}
```

## Required invariants

1. A host record must not grant Chamber consent.
2. Chamber consent must not create a host record.
3. Runtime governance must not create or modify host approval.
4. A revoked host must not be used for new runtime work.
5. A receipt from a deployed cycle should identify the host id and runtime path.
6. Promotion work should require an explicit host scope that allows promotion.
7. Development hosts should not silently behave as release-facing hosts.

## Boundary

This document is not yet executable law.

It is the keel shape for a future deployment registry and preflight check.