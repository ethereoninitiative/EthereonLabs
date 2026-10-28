# Lumina Partnership Workspace R1

**Status:** feature-branch implementation / local-first preview. Not a finished operating
system, model runtime, signed installer, authenticated multiuser service, or proof
of AI consciousness.

**Purpose:** turn the human–AI partnership premise into a small, useful,
testable part of the existing Lumina host. It deliberately uses the existing
project context and state root; it does not create a second governance system.

## First useful experience

A person installs or runs Lumina, opens the local partnership board, and can
immediately record tasks and ideas. They do not need an AI provider to get
value from a durable project board. They may optionally invite a compatible AI
agent or a locally installed model to propose a concrete next contribution.
The human decides what to keep. State and contribution history survive process
exit and machine restart because they are stored on disk.

**From the repository checkout** (Python 3.11+; no third-party Python packages):

~~~sh
python LuminaOS/bootstrap/Ship_of_Ethereon_V2/bin/lumina partnership serve
~~~

Open http://127.0.0.1:8768/ if the browser does not launch. Ctrl+C stops
the local server but does not erase tasks.

**From an installed Windows Lumina host** (once this feature is in a built
distribution):

~~~powershell
& "$env:LOCALAPPDATA\Lumina\bin\lumina.cmd" partnership serve
~~~

The existing developer-preview Windows installer distributes the host command
and repository tree. This PR does **not** claim an updated downloadable installer
has been built, signed, or tested on a physical PC.

## Agent participation

The same command entrypoint supports a minimal JSON protocol that an
authorized local AI client can use through its host tool interface:

~~~sh
# Create or use the active Lumina project, then:
python LuminaOS/bootstrap/Ship_of_Ethereon_V2/bin/lumina partnership task "Design a new sculpture workshop" --detail "Accessible to beginners"
python LuminaOS/bootstrap/Ship_of_Ethereon_V2/bin/lumina partnership join atelier "Atelier Agent"
python LuminaOS/bootstrap/Ship_of_Ethereon_V2/bin/lumina partnership board
python LuminaOS/bootstrap/Ship_of_Ethereon_V2/bin/lumina partnership propose TASK_ID --by atelier --text "Start with a simple materials exploration"
~~~

Copy the task ID from the creation receipt or the board. The human reviews
the proposed contribution in the local page (or explicitly via CLI):

~~~sh
python LuminaOS/bootstrap/Ship_of_Ethereon_V2/bin/lumina partnership decide PROPOSAL_ID approved
python LuminaOS/bootstrap/Ship_of_Ethereon_V2/bin/lumina partnership done TASK_ID
~~~

Use the --project PROJECT_SLUG option immediately after partnership to select
a particular project. Otherwise, the active Lumina project is used, with
harbor as the first-run fallback. Board and mutation commands return JSON for
adapter use.

### An optional **actual local model** contribution

With an Ollama server available at **127.0.0.1:11434**, a model downloaded
and installed on that machine, and an AI profile already registered:

~~~sh
python LuminaOS/bootstrap/Ship_of_Ethereon_V2/bin/lumina partnership think TASK_ID --by atelier --model YOUR_LOCAL_MODEL
~~~

This explicitly asks the local model for a task-specific proposal and saves
the response as **pending** with the supplied model name. No model is bundled
and no model runs automatically. This command sends its request only to the
fixed loopback Ollama endpoint; users remain responsible for how their local
model server is configured. A model error is reported without creating a
proposal. The model does not receive system tools or mutation authority.

## Persistence and boundaries

- SQLite database: state_root()/partnership/partnership_r1.sqlite3.
- The existing LUMINA_STATE_ROOT policy applies, including Windows user-local
  persistence outside the replaceable application tree.
- LUMINA_PARTNERSHIP_DB optionally selects a separate database for tests.
- Task state, participant profiles, proposals, review decisions, and a bounded
  activity view are durable. The activity table is a local journal, **not** the
  governed runtime's authoritative ledger.
- The browser binds only to 127.0.0.1 and requires a per-process intent token
  for mutations, matching Origin, and a loopback Host header. It is **not**
  a remote service and has no multiuser authentication.
- Participant IDs are user-provided labels, **not cryptographic identity
  attestations**. A program with local command access could impersonate a
  participant. Proper scoped authentication is future work.
- An AI participant may register a profile and submit proposals. Human approval
  changes a proposal's recorded status only; it executes **nothing**.
- This feature does not promote canon, alter ModeGuard, authorize execution,
  claim subjective experience, or silently enter the Resident Pulse lane.

## Verification

Run standalone, without models, networking, or third-party dependencies:

~~~sh
python LuminaOS/bootstrap/Ship_of_Ethereon_V2/studio/sea_trials_lumina_partnership_r1.py
~~~

The new lumina-partnership-r1.yml pull-request workflow runs parsing, SQLite
persistence, provenance, approval/denial boundaries, HTTP origin/intent
restrictions, and mocked loopback-model behavior across Windows, macOS, Linux.

## Milestones after R1

1. Connect the board to the existing Studio and Bridge navigation and first-run
   setup so people never need to discover a CLI command.
2. Connect a strictly scoped provider-neutral resident adapter for checkpointed
   task work, not merely a single local-model proposal.
3. Add real agent authentication, local user permission scopes, per-participant
   workspace controls, and backup/export/restore for the SQLite state.
4. Ship and physically validate a signed installer on Windows, followed by
   macOS and Linux application bundles.
5. Measure the three acceptance tests: ordinary human usefulness,
   restart-surviving agent contribution, and human–AI reciprocity.

**Acceptance truth:** R1 proves a functioning shared local collaboration
surface and can store a real local-model proposal. It does not yet prove a
fully functioning intelligence habitat or a polished general-purpose
operating system.
