# Lumina Local Runbook 001

**Purpose:** start Lumina locally without hunting through the repository.

---

## 1. Start here

From the repository root:

```bash
cd LuminaOS/bootstrap/Ship_of_Ethereon_V2
```

Run the doctor directly:

```bash
python install/lumina_doctor.py
```

Optional install into `~/.local/bin`:

```bash
bash install/install_lumina.sh
```

If `~/.local/bin` is on your `PATH`, the command becomes:

```bash
lumina doctor
```

If not, use the local entrypoint directly:

```bash
python bin/lumina doctor
```

---

## 2. First useful cycle

Run one governed cycle:

```bash
lumina run "Review Lumina OS progress and produce the next governed action receipt."
```

Without install:

```bash
python bin/lumina run "Review Lumina OS progress and produce the next governed action receipt."
```

Expected result:

- a run id
- mode path
- halted status
- checkpoint path
- log path
- governance chain status
- exposed capability ids

---

## 3. Observe Lumina

Run a bounded Observation cycle and emit the public/runtime snapshot artifacts:

```bash
lumina observe
```

This delegates to the existing auto-snapshot runtime runner. It does not make Chamber an execution surface.

---

## 4. Inspect state

Read recent emitted runtime receipts:

```bash
lumina state --limit 12
```

This is read-only. It summarizes runtime receipts, governance event counts, canon metadata, checkpoint paths, and exposed capability ids.

---

## 5. Start Studio

Launch the local browser surface:

```bash
lumina studio
```

Open:

```text
http://127.0.0.1:8765/studio
```

Studio remains local-first. Do not expose it publicly without authentication, authorization, rate limiting, persistence policy, and clear separation from Chamber.

---

## 6. Local observer service

Run one service-style observation cycle:

```bash
python services/lumina_observer_service.py --once
```

Run repeated cycles every six hours:

```bash
python services/lumina_observer_service.py --interval-seconds 21600
```

For systemd-style hosting, copy and edit:

```text
services/lumina.service.example
```

Set the `WorkingDirectory` to your local checkout path before enabling it.

---

## 7. Troubleshooting

### `lumina` command not found

Run:

```bash
bash install/install_lumina.sh
```

Then ensure this is on your `PATH`:

```bash
~/.local/bin
```

### Doctor reports missing files

Make sure you are in a checkout that includes the full Lumina bootstrap path:

```text
LuminaOS/bootstrap/Ship_of_Ethereon_V2/
```

### Studio starts but browser cannot connect

Confirm the server is running locally and open:

```text
http://127.0.0.1:8765/studio
```

### State browser shows no receipts

Run a cycle first:

```bash
lumina run "Initial Lumina receipt"
lumina observe
```

State is emitted by runtime cycles; an empty state directory before first run is not automatically failure.

---

## 8. Boundary reminder

The host commands are convenience paths into the governed runtime.

They do not own:

- mode legality
- mutation authority
- promotion authority
- canon lineage
- checkpoint truth
- symbolic dependency boundaries
- user consent

Those remain governed by the existing runtime substrate.

---

## 9. Minimal daily operator loop

```bash
lumina doctor
lumina observe
lumina state --limit 5
lumina run "What should Lumina do next within current boundaries?"
```

That is the current local heartbeat.
