"""Return Delta R1: a read-only, non-authoritative provenance and reflection witness.

This instrument checks that a proposed reinterpretation points to real passages,
that a counterreading and uncertainties are explicit, and that a next action was
selected. It cannot judge consciousness, independent agency, or true novelty.
It neither invokes models nor reads/writes repository or memory state.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from typing import Any

SCHEMA = 'return-delta-input-r1'
RECEIPT_SCHEMA = 'return-delta-receipt-r1'
ALLOWED_SPEAKERS = {'user', 'assistant', 'other'}


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'))


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode('utf-8')).hexdigest()


def nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _valid(payload: Any) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if not isinstance(payload, dict) or payload.get('schema_version') != SCHEMA:
        raise ValueError('missing_or_unknown_schema')
    if set(payload) != {'schema_version', 'sources', 'analysis'}:
        raise ValueError('unexpected_top_level_fields')
    sources = payload['sources']
    if not isinstance(sources, list) or not sources:
        raise ValueError('sources_required')

    turns: dict[tuple[str, str], dict[str, str]] = {}
    for source in sources:
        if not isinstance(source, dict) or set(source) != {'id', 'source_uri', 'turns'}:
            raise ValueError('invalid_source_fields')
        if not nonempty(source['id']) or not nonempty(source['source_uri']):
            raise ValueError('invalid_source_identity')
        sid = source['id']
        if any(k[0] == sid for k in turns):
            raise ValueError('duplicate_source_id')
        rows = source['turns']
        if not isinstance(rows, list) or not rows:
            raise ValueError('empty_source')
        seen = set()
        for row in rows:
            if not isinstance(row, dict) or set(row) != {'id','speaker','text'}:
                raise ValueError('invalid_turn_fields')
            if not nonempty(row['id']) or row['id'] in seen:
                raise ValueError('invalid_or_duplicate_turn_id')
            if row['speaker'] not in ALLOWED_SPEAKERS or not nonempty(row['text']):
                raise ValueError('invalid_turn_data')
            seen.add(row['id'])
            turns[(sid, row['id'])] = row

    analysis = payload['analysis']
    required = {'observations', 'prior_interpretation', 'counterreading', 'delta_candidate',
                'why_different', 'selected_next_action', 'uncertainties'}
    if not isinstance(analysis, dict) or set(analysis) != required:
        raise ValueError('invalid_analysis_fields')
    for key in required - {'observations', 'uncertainties'}:
        if not nonempty(analysis[key]):
            raise ValueError('missing_'+key)
    if analysis['prior_interpretation'].strip().casefold() == analysis['counterreading'].strip().casefold():
        raise ValueError('counterreading_must_challenge_prior')
    if analysis['prior_interpretation'].strip().casefold() == analysis['delta_candidate'].strip().casefold():
        raise ValueError('delta_repeats_prior_interpretation')
    uncertainties = analysis['uncertainties']
    if not isinstance(uncertainties, list) or not uncertainties or not all(nonempty(x) for x in uncertainties):
        raise ValueError('explicit_uncertainty_required')
    observations = analysis['observations']
    if not isinstance(observations, list) or not observations:
        raise ValueError('observations_required')

    anchors = []
    for i, obs in enumerate(observations):
        if not isinstance(obs,dict) or set(obs) != {'statement','evidence'} or not nonempty(obs['statement']):
            raise ValueError('invalid_observation')
        evidences = obs['evidence']
        if not isinstance(evidences,list) or not evidences:
            raise ValueError('observation_missing_evidence')
        for ev in evidences:
            if not isinstance(ev,dict) or set(ev) != {'source_id','turn_id','speaker','exact_quote'}:
                raise ValueError('invalid_evidence_fields')
            if not all(nonempty(ev.get(k)) for k in ('source_id','turn_id','speaker','exact_quote')):
                raise ValueError('incomplete_evidence_anchor')
            turn = turns.get((ev['source_id'],ev['turn_id']))
            if turn is None:
                raise ValueError('unresolved_evidence_anchor')
            if ev['speaker'] != turn['speaker']:
                raise ValueError('speaker_attribution_mismatch')
            if ev['exact_quote'] not in turn['text']:
                raise ValueError('quote_not_in_archived_turn')
            anchors.append({
                'observation_index': i,
                'source_id': ev['source_id'],
                'turn_id': ev['turn_id'],
                'speaker': ev['speaker'],
                'turn_sha256': digest(turn),
                'quote_sha256': digest(ev['exact_quote']),
            })
    return analysis, anchors


def assess(payload: Any) -> dict[str, Any]:
    """Return a deterministic receipt; never treat successful checks as proof of novelty."""
    try:
        analysis, anchors = _valid(payload)
        return {
            'schema_version': RECEIPT_SCHEMA,
            'admissibility': 'anchored',
            'interpretation_status': 'candidate_needs_independent_review',
            'evidence_anchors': anchors,
            'prior_interpretation': analysis['prior_interpretation'],
            'counterreading': analysis['counterreading'],
            'delta_candidate': analysis['delta_candidate'],
            'why_different': analysis['why_different'],
            'selected_next_action': analysis['selected_next_action'],
            'uncertainties': analysis['uncertainties'],
            'input_sha256': digest(payload),
            'authority_boundary': 'Read-only research witness; no memory approval, action authorization, identity, novelty, or consciousness claim.',
        }
    except (ValueError, TypeError, KeyError) as exc:
        return {
            'schema_version': RECEIPT_SCHEMA,
            'admissibility': 'rejected',
            'reason': str(exc) if isinstance(exc,ValueError) else 'invalid_payload_type',
            'input_sha256': digest(payload),
            'authority_boundary': 'Rejected evidence cannot be promoted to historical fact or action authorization.',
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input_file', help='JSON input, or - for stdin')
    args = parser.parse_args(argv)
    try:
        if args.input_file == '-':
            payload = json.load(sys.stdin)
        else:
            with open(args.input_file, encoding='utf-8') as file:
                payload = json.load(file)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(json.dumps({'schema_version': RECEIPT_SCHEMA, 'admissibility':'rejected', 'reason':'input_unreadable:'+type(exc).__name__}))
        return 2
    receipt = assess(payload)
    print(json.dumps(receipt, indent=2, ensure_ascii=False, sort_keys=True))
    return 0 if receipt['admissibility']=='anchored' else 2

if __name__ == '__main__':
    raise SystemExit(main())
