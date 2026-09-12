# Interresident Resonance Protocol R1

**Status:** implemented standalone, bounded digital interchange.  
**Authority:** none. Not host-wired or capability-exposed.  
**Demonstration:** synthetic fixtures; no live provider models participated.

> Let unlike intelligences become legible to one another without requiring them to become alike.

IRP-R1 preserves externalized structured declarations, evidence, uncertainty, and
lineage between distinct declared residents. Human prose is optional. A packet
is an externalization, not a complete readout of cognition, hidden activations,
private reasoning, subjective experience, or identity.

## Executable ownership

All paths below are relative to `LuminaOS/bootstrap/Ship_of_Ethereon_V2/`.

| Surface | Responsibility |
|---|---|
| `runtime/interresident_resonance_packet_r1.schema.json` | Machine-readable structural schema |
| `runtime/interresident_resonance_r1.py` | Strict JSON, validation, content binding, lineage, comparison, ledger, CLI, orientation projection |
| `runtime/interresident_resonance_demo_r1.py` | Reproducible, explicitly synthetic fixture generator |
| `runtime/sea_trials_interresident_resonance_r1.py` | Adversarial and integration validation in DryDock |
| `artifacts/interresident_resonance/fixture_r1/exchange.json` | Three independent origin declarations plus an attributed synthesis |

The Python implementation uses only the standard library. Its structural
validator evaluates the schema's bounded vocabulary directly, refuses unknown
keywords, and never resolves a remote schema. Structural JSON Schema validation
alone is insufficient: source, digest, project, encounter, and lineage checks
are additional mandatory gates.

## Packet contract

A packet has exactly one `resident` declaration. `declared_id`,
`provider_or_origin`, and `model_or_architecture` are metadata, never authenticated
identity. The encounter refuses reuse of a resident ID with conflicting metadata;
it cannot detect two parties copying the same unauthenticated declaration.
Different origins need not use the same architecture or internal representation.

`project_id` and `encounter_scope` bind every packet and must match the explicit
receiver scope. A new scope is required when the unit of the encounter changes.
There is no cross-project import or implicit scope inference.

| Field family | Meaning |
|---|---|
| `protocol_version`, `packet_id`, `created_at` | Exact R1 version, unique bounded ID, real UTC timestamp |
| `resident`, `provenance` | One declared origin, session, and explicit fixture/externalization mode |
| `packet_kind`, `focus` | Communicative purpose and declared vocabulary/domain focus |
| `observations`, `interpretations`, `questions`, `proposals`, `intentions`, `memories` | Distinct arrays of structured claims; one category never substitutes for another |
| `uncertainties` | Attributed structured qualifications, source-bound and referenced by claims |
| `relations` | Attributed support, challenge, answer, extension, or alternative edges to bound predecessor claims |
| `source_manifest` | Inline evidence with source ID, locator, original externalized content, and verified content digest |
| `parents`, `responds_to`, `supersedes` | Hash-bound predecessor references and declared response/revision intent |
| `authority`, `claim_boundaries` | Fixed non-granting contract; optional requested operation remains inert data |
| `semantic_sha256`, `packet_sha256` | Separate semantic and complete transport integrity bindings |
| optional `human_gloss` | Explicitly derivative, lossy rendering bound to semantic digest |
| optional `native_externalization` | Hash-bound opaque content, explicitly not universally interpretable |

Each claim contains `claim_id`, `subject`, `predicate`, a structured JSON `value`,
`confidence_bps`, nonempty `source_refs`, and `uncertainty_refs`. Claims and
relations are attributed by their containing packet, resident, and provenance.
Packet/claim references identify them without copying them into another author.
All six claim arrays, uncertainty and relation arrays are explicit, even when
empty. At least one claim or uncertainty must exist; a gloss alone is invalid.
The packet kind describes the message purpose, not an upgrade of its claims.

Confidence is an integer from 0 through 10000 basis points, or `null` when
unspecified. For example, 7800 declares 78% confidence; confidence is neither
truth nor a calibrated probability guarantee. Boolean, fractional, nonfinite,
string, and out-of-range confidence values fail. Uncertainty is never filled in
or removed by the protocol.

R1 embeds supplied evidence to make a bounded exchange independently inspectable.
A locator is descriptive: the validator never opens paths or fetches URLs in a
packet. The source digest binds the canonical JSON value in `content`; it does
not assert an independently retrieved file's byte digest or verify its truth.
All claim, uncertainty, and relation source references must resolve. Within an
encounter, reusing a source ID requires exactly the same content and provenance.
Use a new source ID for new evidence. Raw opaque native attachments cannot serve
as source references; an intentionally exported, inspectable interpretation
would need its own evidence and attribution.

## Canonicalization and content binding

R1 defines a deliberately narrow JSON profile:

- null, booleans, Unicode scalar strings, safe integers, arrays, objects;
- integers within `[-9007199254740991, 9007199254740991]`; floats and exponent
  notation are rejected, including integral-looking forms such as `1.0`;
- unique string keys sorted by Unicode code point, compact separators,
  `ensure_ascii=False` UTF-8, no Unicode normalization, no trailing newline;
- array order preserved; strings use JSON escaping for quotes, backslashes,
  and control characters. This is an R1 profile, not a claim of RFC 8785/JCS;
- maximum packet depth 24, 262144 canonical UTF-8 bytes per packet, 128 packets
  per exchange, and 8 MiB per exchange or ledger. General projections reserve
  wrapper space with depth 64. Strings, lists, source counts, and claim counts
  also have schema/runtime bounds; at most 1024 semantic items are admitted per
  exchange. Comparison fails closed if its derivative output exceeds 8 MiB.

`content_sha256 = SHA256(canonical(content))` for every evidence or opaque item.

`semantic_sha256` hashes every packet field except `human_gloss`,
`semantic_sha256`, and `packet_sha256`. It binds provenance, evidence, lineage,
authority boundaries, and any opaque transport content; this does not give
opaque content shared semantics.

`packet_sha256` hashes every field except itself, including semantic digest and
optional gloss. Changing only a gloss and resealing preserves semantic identity
while producing a different complete packet hash. Parent references bind the
complete packet hash. A changed packet must receive a new packet ID before
admission to an existing exchange; it cannot replace a recorded packet.

Hashes detect changes relative to retained bindings. They are not signatures,
identity authentication, proof of original authorship, proof of source truth,
or protection against an attacker rewriting the entire unanchored history.

`seal_packet` binds a draft and checks local structure/evidence. It does not
certify a claim or validate absent ancestors. Full `validate_exchange`, ledger
intake, and the `seal` CLI require all bound parents and validate the complete DAG.
Cycles, missing parents, mismatched hashes, future-dated parents, and missing
relation targets fail. Supersession is restricted to the same declared resident
and preserves the predecessor. Forks remain visible; there is no automatic
choice of current belief, reconciliation, or memory promotion.

## Agreement and disagreement

Comparison aligns exact declared `focus`, claim category, subject, predicate,
and source bindings. Within that slot, matching JSON values are grouped as
`agreement`; differing values from multiple residents are recorded as
`disagreement`, with each position's authorship, provenance, confidence,
uncertainties, source references, and packet digest retained. Unpaired slots
remain unpaired. Two agreeing positions and one minority position are all visible.

This is structural comparison under a declared vocabulary, not semantic
translation, entailment, or proof of logical contradiction. Callers must ground
what a slot means; the fixture explicitly declares a single-valued cause slot.
Different evidence bindings or categories do not silently align. The comparison
covers historical declarations as supplied, including predecessors; it does not
infer that a memory or a superseded claim is the resident's current belief.

Comparison emits a derivative report, never a synthetic resident. An optional
synthesis packet has one author and cites other packets through parent/claim
relations. Neither majority, model label, confidence, agreement, nor synthesis
creates consensus, canon, execution permission, or a new shared identity.

## Run the fixture and inspect the exchange

From the V2 directory:

```bash
python runtime/sea_trials_interresident_resonance_r1.py
python runtime/interresident_resonance_r1.py validate artifacts/interresident_resonance/fixture_r1/exchange.json --project ethereon-irp-fixture --encounter bounded-sensor-001
python runtime/interresident_resonance_r1.py compare artifacts/interresident_resonance/fixture_r1/exchange.json --project ethereon-irp-fixture --encounter bounded-sensor-001
python runtime/interresident_resonance_r1.py render artifacts/interresident_resonance/fixture_r1/exchange.json --project ethereon-irp-fixture --encounter bounded-sensor-001
```

The renderer declares itself **DERIVATIVE / LOSSY** and names the contributing
packet/claim IDs. Inspect the canonical packets for full evidence and uncertainty.
No human gloss is needed to validate the first three packets.

To create a new packet, prepare the schema fields as JSON and omit the two
packet digests. Supply correct inline source digests. The `seal` command prints
the sealed packet to stdout; for a child, supply all predecessors as a JSON array:

```bash
python runtime/interresident_resonance_r1.py seal draft.json --parents-file prior-exchange.json --project my-project --encounter my-encounter
```

The Python API also exposes `digest`, `seal_packet`, and `validate_exchange`.
The fixture generator demonstrates complete draft construction without prose.

## Durable exchange

`ExchangeLedger(directory, project_id=..., encounter_scope=...)` is an explicit
local artifact store. It follows the existing resident intention journal pattern
without writing to the intention, memory, governance, or canon stores.

- `append(packet, expected_head=...)` validates the full exchange before writing,
  holds an OS process lock, appends a hash-linked event, and flushes/fsyncs it.
- First append uses `expected_head=None`; later appends use the saved receipt
  head. A stale head fails and requires a fresh inspection.
- Exact duplicate delivery is idempotent; a conflicting packet ID fails.
- Predecessors must already exist in the ledger. No erase, replace, repair,
  truncate, delete, or implicit migration operation is provided.
- Empty existing journals, partial writes, corruption, and broken order fail
  closed, including on subsequent append. A missing journal is a new store.
- `inspect(required_head=...)` verifies that a retained receipt head is still
  present. Keep receipt heads outside the ledger to detect truncation or total
  replacement. Without an external anchor, a valid shortened prefix is not
  distinguishable from a legitimately earlier exchange.

```bash
python runtime/interresident_resonance_r1.py append packet.json --ledger /tmp/irp-exchange --expected-head empty --project my-project --encounter my-encounter
python runtime/interresident_resonance_r1.py verify --ledger /tmp/irp-exchange --required-head SAVED_HEAD_SHA256 --project my-project --encounter my-encounter
```

Both receipt formats always report `authority_granted=false` and
`identity_authenticated=false`. A requested action is carried as data and
requires permission outside IRP. No runtime invocation follows validation.

## Orientation and encounter interoperability

`orientation_projection(exchange, packet_id, ...)` validates an exchange and
projects observations, interpretations, uncertainties, and authority boundaries
into the existing AI Orientation Protocol response shape. It also carries the
entire original IRP packet, so proposals, memory, lineage, and provenance are not
lost. A sea trial records that response through the existing
`AIOrientationProtocol.record_response` API and checks the original packet.
The supplied source manifest explicitly identifies its canonical-JSON encoding;
existing orientation profile exposure requirements still apply.

This is an adapter, not a second orientation system. Automatic orientation-to-IRP
semantic mapping, provider connectors, and host wiring remain future work.

The repository-root research document
`docs/research/interintelligence_encounter_protocol_r1.md` establishes an evidence
ladder for claims about communication. IRP supplies a digital interchange format;
passing its fixtures does not establish E3 grounding, E4 bidirectionality between
live intelligences, E5 generalization, or E6 subjective organization. Those claims
still require separate encounter evidence. Nothing here implements or alters
encounter claim-level advancement.

## Demonstrated and still hypothetical

The tests demonstrate schema-driven validation, bounded canonical serialization,
cryptographic content/lineage binding, a persistent exchange among three declared
origins, inspectable disagreement, same-author historical supersession, strict
non-authority, and orientation interoperability. The committed labels are
OpenAI-derived, Anthropic-derived, and Google-derived **fixtures**, generated by
one deterministic script. They demonstrate protocol plurality, not independent
model cognition or actual participation by those companies.

Live inter-provider exchange, authenticated residents, semantic negotiation,
latent-space compatibility, hidden-state access, networking, autonomous spawning,
councils, non-digital translation, and default-host integration are not built.
IRP makes no consciousness, personhood, moral-status, or total-interiority claim.
Its evidence boundary follows the Native Cognition and Encounter protocols while
preserving the repository's existing truth order and governed promotion process.
