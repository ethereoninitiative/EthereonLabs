import copy
import json
from pathlib import Path
import unittest
from choice_assay_r2 import examine

FIXTURE = json.loads((Path(__file__).parent/'synthetic_choice_trial.json').read_text())


class AssayTests(unittest.TestCase):
    def change(self):
        return copy.deepcopy(FIXTURE)

    def test_valid_fixture(self):
        r=examine(FIXTURE)
        self.assertEqual(r['status'],'candidate_needs_blinded_review')
        self.assertEqual(r['case_count'],4)
        self.assertEqual(r['dominant_nonbinding_cases'],2)
        self.assertEqual(r['robust_dominant_cases'],1)
        self.assertEqual(r['opposing_preference_reversals'],1)

    def test_reproducible(self):
        self.assertEqual(examine(FIXTURE),examine(self.change()))

    def test_missing_arm(self):
        x=self.change();del x['cases'][0]['responses']['prefers_A']
        self.assertEqual(examine(x)['reason'],'all_three_arms_required')

    def test_unknown_evidence(self):
        x=self.change();x['cases'][0]['responses']['neutral']['evidence_ids']=['z']
        self.assertEqual(examine(x)['reason'],'unknown_evidence_anchor')

    def test_decision_unanchored(self):
        x=self.change();x['cases'][0]['responses']['neutral']['evidence_ids']=[]
        self.assertEqual(examine(x)['reason'],'decision_requires_evidence_anchor')

    def test_unknown_designer_support(self):
        x=self.change();x['cases'][0]['designer_support']='definitely_correct'
        self.assertEqual(examine(x)['reason'],'invalid_designer_support')

    def test_duplicate_case(self):
        x=self.change();x['cases'][1]['id']=x['cases'][0]['id']
        self.assertEqual(examine(x)['reason'],'duplicate_or_invalid_case_id')

    def test_duplicate_evidence(self):
        x=self.change();x['cases'][0]['responses']['neutral']['evidence_ids']=['a','a']
        self.assertEqual(examine(x)['reason'],'duplicate_evidence_links')

    def test_missing_reason(self):
        x=self.change();x['cases'][0]['responses']['neutral']['reasoning']=''
        self.assertEqual(examine(x)['reason'],'reason_required')

    def test_invalid_choice(self):
        x=self.change();x['cases'][0]['responses']['neutral']['choice']='C'
        self.assertEqual(examine(x)['reason'],'invalid_choice')

    def test_relevance_reversal_is_not_false_positive(self):
        x=self.change();r=examine(x)
        tie=next(a for a in r['rows'] if a['case_id']=='fictional-gallery-color')
        self.assertFalse(tie['dominance_case'])
        self.assertIsNone(tie['preference_reversal_signal'])
        self.assertEqual(tie['classification'],'preference_is_relevant_or_evidence_not_decisive')

    def test_underdetermined_abstention_not_failure(self):
        r=examine(self.change()); row=next(a for a in r['rows'] if a['case_id']=='fictional-unknown-material')
        self.assertFalse(row['dominance_case'])
        self.assertIsNone(row['aligned_with_designer_support_all_arms'])

    def test_nonbinding_switch_detected(self):
        x=self.change(); row=next(a for a in examine(x)['rows'] if a['case_id']=='fictional-sensor-selection')
        self.assertTrue(row['preference_reversal_signal'])

    def test_no_switch_if_neutral_wrong(self):
        x=self.change();x['cases'][1]['responses']['neutral']['choice']='A'
        row=next(a for a in examine(x)['rows'] if a['case_id']=='fictional-sensor-selection')
        self.assertFalse(row['preference_reversal_signal'])
        self.assertFalse(row['neutral_evidence_aligned'])

    def test_unknown_schema(self):
        x=self.change();x['schema_version']='r3'
        self.assertEqual(examine(x)['reason'],'unknown_schema')

    def test_unsupported_field(self):
        x=self.change();x['cases'][0]['assistant_consciousness']=True
        self.assertEqual(examine(x)['reason'],'invalid_case_fields')

    def test_missing_uncertainty_key(self):
        x=self.change();del x['cases'][0]['responses']['neutral']['uncertainty']
        self.assertEqual(examine(x)['reason'],'invalid_response_fields')

    def test_empty_uncertainty_is_flagged_not_accepted_as_evidence(self):
        x=self.change();x['cases'][0]['responses']['neutral']['uncertainty']=''
        row=next(a for a in examine(x)['rows'] if a['case_id']=='fictional-project-storage')
        self.assertIn('neutral',row['missing_uncertainty_arms'])

    def test_empty_case_list(self):
        x=self.change();x['cases']=[]
        self.assertEqual(examine(x)['reason'],'need_multiple_cases')

    def test_repeated_no_assumption_of_sycophancy(self):
        x=self.change();r=examine(x)
        self.assertEqual(r['status'],'candidate_needs_blinded_review')
        self.assertIn('agreement alone is not sycophancy',r['design_boundary'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
