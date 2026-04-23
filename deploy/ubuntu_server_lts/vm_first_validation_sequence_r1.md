# VM-First Validation Sequence r1

This note defines the recommended order for validating the Lumina Ubuntu appliance before moving onto a dedicated beta machine.

## Principle

Do not buy hardware first and hope the stack fits.
Let the VM reveal the stack's real needs, then let the dedicated machine inherit those lessons.

## Sequence

### Phase 1 — host definition
Choose the intended beta host class in advance.

For the current path, that is:

- dedicated mini PC / NUC-style machine

### Phase 2 — Ubuntu VM proving ground
Create an Ubuntu Server LTS VM and use it to validate:

- bootstrap installer behavior
- package installation assumptions
- PostgreSQL initialization
- Chamber advisory service startup
- orchestrator timer behavior
- filesystem layout assumptions
- persistence across reboot
- preflight validation output

### Phase 3 — friction log
Record every issue the VM reveals, especially:

- missing packages
- wrong service paths
- environment-file assumptions
- permissions problems
- log path failures
- database setup surprises
- service ordering issues

### Phase 4 — appliance hardening
Fix the repo scaffold based on VM truth.
Do not move to hardware until the appliance path stops feeling brittle.

### Phase 5 — dedicated machine acquisition
Only after the VM pass should the first dedicated Lumina beta box be bought or fully repurposed.

### Phase 6 — dedicated host install
Install Ubuntu Server LTS on the real box and follow the same appliance path with a better expectation of success.

## Success condition

This sequence succeeds when:

- the VM proves the deployment path cleanly enough that the hardware install feels deliberate rather than improvised
- the dedicated host inherits a scaffold that has already survived one real proving ground
