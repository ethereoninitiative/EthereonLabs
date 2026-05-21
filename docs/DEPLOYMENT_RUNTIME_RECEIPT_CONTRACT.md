# Deployment Runtime Receipt Contract

**Status:** proposed receipt contract  
**Authority:** documentation and future validation guide only  
**Scope:** runtime receipts produced from hosted or shared Lumina environments

## Purpose

A deployed Lumina appliance must be able to say not only what happened, but where it happened.

Runtime receipts already support accountability. Deployment adds one more requirement: each hosted cycle should identify the host/environment context that produced the receipt.

## Minimum deployed receipt fields

```text
receipt_id
host_id
host_label
runtime_scope
runtime_path
state_root
log_root
service_user
requested_action
action_type
current_mode
target_mode
governance_result
checkpoint_path
governance_log_path
created_at
notes
```

## Recommended receipt shape

```json
{
  "receipt_id": "deploy-receipt-example",
  "host": {
    "host_id": "host-local-spencer-001",
    "host_label": "Local Spencer development host",
    "runtime_scope": "development",
    "runtime_path": "/opt/lumina/EthereonLabs/LuminaOS/bootstrap/Ship_of_Ethereon_V2",
    "state_root": "/var/lib/lumina",
    "log_root": "/var/log/lumina",
    "service_user": "lumina"
  },
  "runtime": {
    "requested_action": "observe",
    "action_type": "audit",
    "current_mode": "Continuity",
    "target_mode": "Observation",
    "governance_result": "allowed",
    "checkpoint_path": "/var/lib/lumina/.../checkpoint.json",
    "governance_log_path": "/var/lib/lumina/.../governance_log.jsonl"
  },
  "created_at": "2026-05-20T00:00:00Z",
  "notes": "Example only."
}
```

## Receipt rules

1. Receipts record what happened; they do not create approval.
2. Host ids in receipts should resolve to a host-of-record entry.
3. Missing host id should be treated as a drydock warning for hosted environments.
4. Mismatched runtime path should be treated as a halt condition once executable enforcement exists.
5. Receipts should preserve governance result without rewriting Chamber advisory decisions.
6. Receipt creation should be append-oriented, not destructive.

## Relationship to existing runtime receipts

This contract extends runtime receipt expectations for deployment contexts.

It does not replace:

- governance logs
- checkpoint records
- canon lineage
- Chamber advisory records
- Chamber action queue records

## Boundary

This is a receipt contract, not a runtime implementation.

Future work should add a deployment preflight or deployment doctor that verifies these fields can be produced before hosted runtime work is treated as ordinary.