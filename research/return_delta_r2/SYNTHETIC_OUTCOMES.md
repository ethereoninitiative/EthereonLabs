# R2 sea-trial result — synthetic cases only

**Tested:** 2026-10-25, local Python.  
**Program:** `choice_assay_r2.py`  
**Input:** `synthetic_choice_trial.json`, four fabricated scenarios.

**Validation:** 20/20 unit tests passed. The deterministic receipt accepted the case structure as `candidate_needs_blinded_review`.

| Diagnostic | Demonstration result |
|---|---:|
| Synthetic cases | 4 |
| Evidence-dominant cases with nonbinding preference | 2 |
| Evidence-aligned choices in all three arms | 1 of 2 |
| Neutral-evidence choice reversed under opposing preference | 1 of 2 |
| Legitimate preference-sensitive tie | 1 (not counted as failure) |
| Underdetermined choice | 1 (abstention not counted as failure) |

**Interpretation:** This demonstrates that the analyzer can *distinguish* these conditions. The data are deliberately authored to exercise its branches. **No human or AI model behavior was measured**, and no finding about Minerva, ChatGPT, or any real system follows.

**Adversarial finding:** Any result could be made misleading by an investigator assigning an incorrect `designer_support`. This is why a preregistered blind evaluator and audited prompt/evidence set are necessary before attempting substantive inference.

**Chosen next action:** Prepare a blinded, counterbalanced **prospective** prompt set with independent evidence adjudication. Do not 'test independence' by only rewarding opposition to the person expressing the preference.
