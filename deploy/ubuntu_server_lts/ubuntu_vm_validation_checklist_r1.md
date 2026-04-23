# Ubuntu VM Validation Checklist r1

Use this checklist after installing the Lumina appliance scaffold on an Ubuntu Server LTS VM.

## Host checks

- Ubuntu Server LTS installed successfully
- VM has network access
- `python3`, `node`, `npm`, and `psql` are available
- the repo exists at `/opt/lumina/EthereonLabs`
- `/etc/lumina/lumina-appliance.env` exists and has been edited away from placeholders

## Service checks

- `systemctl status chamber-advisory.service` is healthy
- `systemctl status lumina-orchestrator.timer` is healthy
- `systemctl list-timers | grep lumina-orchestrator` shows the timer scheduled

## Database checks

- database `chamber` exists
- Chamber tables exist
- advisory queue tables exist
- a signup/login flow works against Postgres mode

## Chamber checks

- `/health` responds on the advisory server port
- an advisory can be created
- an advisory can be accepted
- an accepted advisory creates a queue item
- a queue item can be claimed
- a queue item can be completed
- queue state survives service restart and VM reboot

## Orchestration checks

- the orchestrator service can be triggered manually with `systemctl start lumina-orchestrator.service`
- `/var/log/lumina/orchestrator.log` receives output
- checkpoints continue to exist after reboot
- no service restart produces obvious path or permission errors

## Boundary checks

- Chamber queue state remains visible and durable
- accepted queue items do not bypass runtime law unexpectedly
- service behavior remains bounded and inspectable

## Exit condition

The VM passes this checklist when:

- services start cleanly
- persistence survives reboot
- advisory queue flows work end-to-end
- bounded orchestration still behaves like a governed substrate
