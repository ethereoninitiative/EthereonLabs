"""Pure-stdlib sea trials: no network, repo state, or external model needed."""
import copy
import json
import pathlib
import unittest

from return_delta_r1 import assess

SAMPLE = json.loads((pathlib.Path(__file__).parent / 'sample_synthetic.json').read_text(encoding='utf-8'))


class ReturnDeltaTests(unittest.TestCase):
    def altered(self):
        return copy.deepcopy(SAMPLE)

    def test_good_synthetic_witness(self):
        receipt = assess(SAMPLE)
        self.assertEqual(receipt['admissibility'],'anchored')
        self.assertEqual(receipt['interpretation_status'],'candidate_needs_independent_review')
        self.assertEqual(len(receipt['evidence_anchors']),2)
        self.assertNotIn('source_text',receipt)

    def test_deterministic(self):
        self.assertEqual(assess(SAMPLE),assess(copy.deepcopy(SAMPLE)))

    def test_swapped_speaker_rejected(self):
        x = self.altered();x['analysis']['observations'][0]['evidence'][0]['speaker'] = 'assistant'
        self.assertEqual(assess(x)['reason'],'speaker_attribution_mismatch')

    def test_fabricated_quote_rejected(self):
        x = self.altered();x['analysis']['observations'][0]['evidence'][0]['exact_quote']='I am definitely conscious'
        self.assertEqual(assess(x)['reason'],'quote_not_in_archived_turn')

    def test_missing_source_rejected(self):
        x = self.altered();x['analysis']['observations'][0]['evidence'][0]['source_id']='not-a-source'
        self.assertEqual(assess(x)['reason'],'unresolved_evidence_anchor')

    def test_missing_counterreading_rejected(self):
        x = self.altered();x['analysis']['counterreading']=''
        self.assertEqual(assess(x)['reason'],'missing_counterreading')

    def test_echo_as_counterreading_rejected(self):
        x = self.altered();x['analysis']['counterreading']=x['analysis']['prior_interpretation']
        self.assertEqual(assess(x)['reason'],'counterreading_must_challenge_prior')

    def test_echo_as_novel_delta_rejected(self):
        x = self.altered();x['analysis']['delta_candidate']=x['analysis']['prior_interpretation']
        self.assertEqual(assess(x)['reason'],'delta_repeats_prior_interpretation')

    def test_missing_uncertainty_rejected(self):
        x = self.altered();x['analysis']['uncertainties']=[]
        self.assertEqual(assess(x)['reason'],'explicit_uncertainty_required')

    def test_duplicate_turn_rejected(self):
        x = self.altered();x['sources'][0]['turns'][1]['id']='u1'
        self.assertEqual(assess(x)['reason'],'invalid_or_duplicate_turn_id')

    def test_duplicate_source_rejected(self):
        x = self.altered();x['sources'].append(copy.deepcopy(x['sources'][0]))
        self.assertEqual(assess(x)['reason'],'duplicate_source_id')

    def test_unknown_schema_rejected(self):
        x = self.altered();x['schema_version']='return-delta-r9'
        self.assertEqual(assess(x)['reason'],'missing_or_unknown_schema')

    def test_unauthorized_fields_rejected(self):
        x = self.altered();x['canon_authority']=True
        self.assertEqual(assess(x)['reason'],'unexpected_top_level_fields')

    def test_changed_archive_fails_closed(self):
        x = self.altered();x['sources'][0]['turns'][0]['text']='A different reply was archived.'
        self.assertEqual(assess(x)['reason'],'quote_not_in_archived_turn')


if __name__ == '__main__':
    unittest.main(verbosity=2)
