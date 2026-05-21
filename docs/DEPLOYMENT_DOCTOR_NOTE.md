# Deployment Doctor Note

**Status:** companion note for deployment drydock

This repository now includes a first non-mutating deployment preflight scaffold:

```bash
python deploy/ubuntu_server_lts/deployment_doctor_r1.py \
  --repo-root /opt/lumina/EthereonLabs \
  --env-file /etc/lumina/lumina-appliance.env \
  --registry deploy/ubuntu_server_lts/host_registry.example.json \
  --host-id host-local-dev-001
```

The current doctor checks:

- host registry presence
- host record presence
- required host fields
- revocation field
- repo path presence
- allowed runtime path presence
- state root presence
- log root presence
- env file presence
- known placeholder terms in the env file
- service file presence

The current doctor is inspection-only. It does not start services, edit files, approve hosts, or change runtime state.

Future hardening should add checks for database table presence, service active state, baseline runtime receipt emission, checkpoint path validity, and governance log path validity.
