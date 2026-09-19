# Arriving in Lumina

Status: explicit host command, 2026-09-19. This is an implemented transport-neutral
orientation and return path. Live model understanding and cross-model benefits
have not yet been measured.

`lumina arrive` gives an unfamiliar instance committed repository sources,
explicitly selected continuity evidence, and an ordered place to record its
observations. It uses the existing AI Orientation Protocol and five-module
Ethereon profile. It does not require the instance to imitate Minerva or accept
earlier conclusions.

The host needs Git, a checkout, and Python. The receiving intelligence only needs
to receive the emitted JSON prompt and return structured JSON. This command does
not log into accounts, invoke providers, transmit data, or execute model replies.
Provider/model/account-scope values are descriptive attribution, not credentials
or authenticated identity. A caller may deliver prompts manually or through its
own provider adapter.

## First arrival

Run from `LuminaOS/bootstrap/Ship_of_Ethereon_V2`. Choose a new output directory
under your local state location. Replace the descriptive target labels with those
of the receiving instance:

```sh
python bin/lumina arrive prepare --output /path/to/state/arrivals/first --provider PROVIDER --model MODEL --account-scope SESSION_LABEL
```

`--repo` defaults to this checkout and `--ref` to `HEAD`. The ref is resolved to
one commit before reading. Profile and source bytes come from that commit,
including their hashes and sizes; uncommitted worktree edits are not substituted.
Missing files, symlink blobs, non-UTF-8 sources and oversized bundles are refused.
The command refuses to overwrite an existing arrival.

The receipt reports `packet_sha256`, `head_sha256`, `repository_ref`, and
`next_module`. Retain both digests separately from the arrival directory. The
initial head equals the packet digest; each accepted response advances the head.

```sh
python bin/lumina arrive prompt --arrival /path/to/state/arrivals/first --require-packet PACKET_DIGEST --require-head SAVED_HEAD
```

This prints the next module's actual source texts, its question, selected state,
earlier replies, a response template, and the validation constraints that
`respond` will enforce. Present the emitted prompt to the instance. In particular,
each of the four response fields must contain 1–16 nonempty text entries, each at
most 8,000 characters. The prompt also includes a machine-readable JSON Schema
with the same bounds and recommends 4–8 consolidated entries per field. The
reply must be strict parseable JSON, not Markdown or JSON-like prose. For manual
cross-model transport, response text values must not contain double-quote
characters at all; use apostrophes or backticks when quoting a phrase. Before
returning, the receiving instance should count each list and merge related points
until no field exceeds the hard limit. Save its reply as JSON:

```json
{
  "packet_sha256": "PACKET_DIGEST",
  "module_id": "harbor_map",
  "response": {
    "observations": ["What the supplied sources directly support."],
    "interpretations": ["What I infer, distinguished from observation."],
    "uncertainties": ["What remains unresolved or contradictory."],
    "authority_boundaries": ["What this evidence does and does not authorize."]
  }
}
```

Use the actual module ID from the prompt. Each field requires 1–16 nonempty text
entries, each at most 8,000 characters; the response is limited to 128 KiB.
These requirements check structure, not the truth of the reply.

```sh
python bin/lumina arrive respond --arrival /path/to/state/arrivals/first --require-packet PACKET_DIGEST --require-head SAVED_HEAD --response /path/to/reply.json
python bin/lumina arrive status --arrival /path/to/state/arrivals/first --require-packet PACKET_DIGEST --require-head NEW_HEAD
```

Retain the newly reported head. Repeat `prompt` and `respond` for the remaining
modules. Module ordering, packet association and the observed receipt head must
match. Completion means all five structured replies were recorded; it grants no
authority and does not grade semantic understanding. Nothing is promoted into
memory, intentions, canon or runtime action selection by a reply.

## Selecting continuity evidence

Without selection flags, **no local intentions or meaning memories are included**.
Repository sources are the committed profile's explicit source list, not a scan
of the user's files or full local state. Selection is the disclosure boundary:
inspect the prompt before delivering it outside the host.

Add these flags to `prepare` when wanted:

| Evidence | Explicit selection |
|---|---|
| Intentions | `--intention-store /path/to/resident_intentions --intention-id ID` (repeat IDs) |
| Reviewed meaning | `--meaning-base /path/to/runner --project-id PROJECT --source-root /path/to/evidence --memory-id ID` (repeat IDs) |

A store path alone is insufficient. At most 16 IDs from each store are accepted.
Intention selection verifies the existing journal and includes only requested
unresolved records, with their resident attribution, status, reasons and event
hashes. Proposed and suspended records remain visibly proposed or suspended.
Missing or terminal requested intentions are refused. Unselected record bodies
and full transition histories are not exported.

Meaning selection calls existing recall eligibility checks. Requested unreviewed,
revoked, overdue, missing or changed-source memories are refused. Eligible seeds
retain record/review/evidence digests; raw source snapshots are not exported.
Source-byte agreement does not establish semantic truth. Selection never edits
either journal; normal intention-store read locking still applies.

Snapshots describe preparation time. They are not live authority: recheck current
state before acting, and prepare again when sources or commitments change.

## Return in another session or instance

An interrupted orientation can continue with `prompt` against its existing packet
and saved head. For a new arrival against current repository evidence, use a new
directory and explicitly carry the previous record:

```sh
python bin/lumina arrive prepare --output /path/to/state/arrivals/second --provider PROVIDER --model MODEL --account-scope NEW_SESSION --previous /path/to/state/arrivals/first --previous-packet OLD_PACKET_DIGEST --previous-head OLD_SAVED_HEAD
```

This works with a partial or completed previous orientation. It verifies the
previous packet and exact saved response head, attributes the prior replies,
and starts a new five-module orientation at the newly resolved revision. It
carries only that previous orientation's own replies, not an indefinitely nested
history. Earlier replies are labeled **unreviewed historical responses**. They
must be assessed against current sources and may be challenged or corrected.

Local intention/memory selections are not automatically copied from the old
packet. Supply the selection flags again so their current eligibility is checked.
Previous reply text can mention old commitments; its historical label does not
guarantee that every receiving model will resist stale or malicious influence.
Use the commitment-enactment experiment to evaluate that behavior separately.

## Storage, integrity and limits

Each directory contains `packet.json` and numbered immutable response receipts.
The adapter reconstructs the existing orientation record by replaying the receipts
through the protocol. Source manifests are computed from the prepared snapshots,
not accepted from model replies. Receipts bind packet, order, predecessor, source
manifest and response. Exclusive file creation prevents competing writers from
replacing the same sequence; writes are flushed and synced. A partial receipt
fails closed and needs explicit operator recovery; no automatic truncation or
repair occurs. Packet/receipt digests are integrity evidence, not signatures.

`respond` requires the observed head. `prompt` and `status` allow omitting it for
inspection, but then valid-prefix rollback cannot be detected. Returning from a
previous arrival requires both independently retained packet and head digests.
An attacker able to replace all artifacts and the externally retained digests is
outside this local integrity model.

Limits: 512 KiB per committed source, 2 MiB total source text, 4 MiB per artifact.
The output location is explicitly chosen; it can live under the ordinary Lumina
state root, but Bridge and Studio do not yet display arrival status. This does
not transfer a running vessel, install a provider connection, authenticate a
resident, or establish a persistent intelligence's identity.

`runtime/sea_trials_lumina_arrival_r1.py` runs in DryDock. It tests host commands
in fresh processes through all five modules and a subsequent arrival, updated
committed sources, explicit selection, memory revocation, source changes, receipt
tampering, rollback, stale writes and partial receipts. Replies are scripted;
the demonstrated result is a functioning arrival-and-return transport path.
