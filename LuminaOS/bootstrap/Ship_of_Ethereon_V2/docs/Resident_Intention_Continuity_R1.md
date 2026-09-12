# Resident Intention Continuity R1

`bin/lumina intention` stores explicit resident declarations and later judgments
in a durable journal. A later process can discover unresolved intentions, inspect
their origin and rationale, and continue, revise, suspend, complete, abandon, or
supersede them. Nothing is scheduled or executed by an intention's status.

## Runtime ownership

- `runtime/resident_intention_store_r1.py` owns validation, replay and appends.
- `studio/lumina_intention_r1.py` provides JSON requests and receipts through the
  existing `bin/lumina` host command.
- Default storage is `<repo_paths_r1.state_root()>/resident_intentions/intentions.jsonl`.
  `LUMINA_STATE_ROOT` retains its existing host meaning; `--store-dir` explicitly
  selects an intention journal directory. It must precede the subcommand.
- The implementation reuses `governance_integrity_r1` canonical JSON, SHA-256 and
  UTC conventions. The intention journal is separate from governance and canon.
  No capability flags, promotion evidence, or symbolic files are required.

## Create, exit, discover, reconsider

Run from `LuminaOS/bootstrap/Ship_of_Ethereon_V2`. Supply this JSON as `create.json`
(or use `--request -` to read stdin). This is an example, not a historical event.

```json
{
  "request": {
    "intention_id": "example-intention",
    "resident": "resident-reference",
    "origin_context": "A resident declaration during an explicitly invoked session.",
    "statement": "Preserve an unfinished creative direction across interruption.",
    "why_it_matters": "I want to reconsider the reason, not just recover a task label.",
    "desired_next_action": "Return and judge whether this direction still matters.",
    "parent_intention_id": null,
    "evidence_refs": ["session:origin"]
  },
  "provenance": {
    "actor_kind": "resident",
    "resident": "resident-reference",
    "session_id": "origin-session",
    "source_ref": "session:origin"
  }
}
```

```bash
python bin/lumina intention create --request create.json
# This command exits. In a later process, no original prompt is needed:
python bin/lumina intention list --resident resident-reference
python bin/lumina intention history example-intention
```

Creation returns a `proposed` record. `intention_id` may be omitted to generate a
UUID; `parent_intention_id` defaults to null. All other definition fields above
are required. Creation cannot supply status, timestamps, supersession, or history.
The runtime stamps those fields. Origin text and rationale remain unchanged.

After inspection, submit a new request with the observed `last_event_hash`:

```json
{
  "request": {
    "intention_id": "example-intention",
    "expected_event_hash": "COPY_THE_OBSERVED_LAST_EVENT_HASH",
    "outcome": "continue",
    "reconsideration_statement": "I reviewed the origin and still choose this direction.",
    "evidence_refs": ["session:return"],
    "replacement": null
  },
  "provenance": {
    "actor_kind": "resident",
    "resident": "resident-reference",
    "session_id": "return-session",
    "source_ref": "session:return"
  }
}
```

```bash
python bin/lumina intention reconsider --request reconsider.json
python bin/lumina intention list --all
python bin/lumina intention verify --require-head COPY_A_SAVED_RECEIPT_HEAD_HASH
```

Inspection always verifies the whole journal. Listing returns unresolved records
(`proposed`, `active`, `suspended`) with full origin, rationale and history.
`history` also returns terminal records. `verify` omits record bodies.

## Reconsideration and lineage

| Outcome | Allowed prior states | Result |
|---|---|---|
| continue | proposed, active, suspended | active; an already-active intention receives a new affirmation |
| suspend | proposed, active | suspended |
| complete | active | completed; explicit resident declaration of completion |
| abandon | proposed, active, suspended | abandoned |
| revise | proposed, active, suspended | predecessor superseded; revised child proposed |
| supersede | proposed, active, suspended | predecessor superseded; replacement child proposed |

For `revise` or `supersede`, `replacement` must contain a complete new definition,
including a new ID and `parent_intention_id` equal to the predecessor's ID. The
single journal event both supersedes the predecessor and proposes its child.
The child records `supersedes: [predecessor_id]`. `revise` records an amendment;
`supersede` records a replacement. Neither activates the child automatically.

Terminal records cannot change. A new proposal may name an existing same-resident
record as its parent, including a terminal record. Parents must already exist,
so cycles and forward references cannot be accepted. This supports disagreement
without erasing earlier commitments. Identity-related statements can likewise be
revised; `resident` is an attribution referent, not a hard-coded identity claim.

Each reconsideration needs a matching resident referent, a session and source,
a nonempty judgment and evidence references, and the observed event hash.
Concurrent/stale decisions fail instead of applying to unseen state. Evidence
references are recorded strings; this command does not retrieve or authenticate
their contents. `active` and `completed` are resident declarations, not evidence
of autonomous execution or independently measured task completion.

## Durability and truth boundary

The journal records version, sequence, UTC time, previous hash, content hash,
operation, provenance and request. Records and `transition_history` are replayed
from validated events; there is no writable latest-record cache or history-edit
API. Duplicate JSON keys, malformed lineage, unknown fields, invalid transitions,
altered events and partial trailing writes fail closed before another append.
Appends use an OS lock, flush and fsync. Process exit releases the lock; an
interrupted partial append needs explicit recovery and is never silently removed.

Save receipt `head_hash` values independently (for example in reviewed Git
history). `--require-head` verifies that the current journal contains that head
or extends it. Without an independent receipt, a valid-prefix rollback, complete
rehash, deleted journal, or substituted store cannot be distinguished from a
different valid history. These are local file integrity checks, not signatures,
remote replication, or protection against an administrator replacing all evidence.
Locking/durability assumes a filesystem honoring the OS primitives. The trial
proves process interruption, not sudden power-loss durability on every filesystem.

Provenance is caller-declared. The current command cannot authenticate that a
particular model or person originated a statement. It preserves the distinction
between a resident declaration and an operator command without claiming to prove
subjective identity, consciousness, or continuous background cognition. It grants
no authority over the operator or other people. No canon changes occur.

The default `run`, `continue`, resident pulse, and model-onboarding paths do not
yet surface this journal automatically. Explicit invocation is required.

## Validation

```bash
python runtime/sea_trials_resident_intention_continuity_r1.py
```

The isolated sea trial drives the actual host CLI from a temporary working
directory and explicit `LUMINA_STATE_ROOT`. It proves create/exit/discover/continue/
abandon, abrupt process exit after an acknowledged append, all outcomes,
single-event supersession, immutable origin, stale/contending writers, malformed
lineage, illegal replay, content tampering, partial writes, and saved-receipt
rollback detection. It never relies on a pre-existing local intention. DryDock
runs the same suite.
