### What the executed explanations show

- `age_numeric`: mean scenario score 8.45% at 5, versus 9.04% at 95. This describes the fitted model response over this grid, not a causal effect.
- `time_in_hospital`: mean scenario score 8.68% at 1, versus 9.53% at 14. This describes the fitted model response over this grid, not a causal effect.
- `num_lab_procedures`: mean scenario score 8.29% at 4, versus 9.04% at 73. This describes the fitted model response over this grid, not a causal effect.
- `number_inpatient`: mean scenario score 8.37% at 0, versus 11.71% at 1. This describes the fitted model response over this grid, not a causal effect.

Read the ICE spread alongside the mean: different profiles can respond differently even where the mean appears smooth or nearly flat. The representative-profile curves show that a feature response alone does not explain why a patient was misclassified; outcomes remain uncertain and unmeasured factors may matter. The discharge PDP complements its high permutation importance, but hypothetical transfers between discharge categories can be medically unrealistic. The low precision of the fixed policy remains a practical limitation even if a model response is interpretable. These plots support transparent model inspection, not clinically actionable recommendations.

### Fairness findings and feasible mitigation plan

- **AfricanAmerican versus Caucasian, test top-20% policy:** TPR 27.71% versus 41.92%; difference -14.21 percentage points (individual bootstrap 95% interval -21.90 to -6.06). Selection rates are 16.66% versus 21.45% (A/reference ratio 0.777); FPRs are 15.63% versus 19.37%.
- **Male versus Female, test top-20% policy:** TPR 35.89% versus 42.08%; difference -6.19 percentage points (individual bootstrap 95% interval -12.37 to +0.24). Selection rates are 18.82% versus 21.07% (A/reference ratio 0.893); FPRs are 17.15% versus 18.99%.

These observed coverage and workload disparities warrant investigation. They do not identify causes or establish discrimination. All-group max/min gaps can be driven by very small groups; use the support flags and intervals rather than ranking fairness by a single summary number. Age-related differences can reflect clinical risk and differences in captured outcomes. Insurance and intersectional findings are exploratory and require contextual interpretation. The two operating policies have different workloads, so their parity differences should not be treated as a controlled model comparison.

**Practical priority:** investigate lower coverage of recorded readmissions, while monitoring false-positive workload, overall capture and calibration. Agree with care-management stakeholders on acceptable coverage gaps and follow-up capacity before setting mitigation objectives. The following actions are proposals; no mitigation is claimed to have succeeded:

| Evidence or concern | Proposed action | How to evaluate it |
|---|---|---|
| Race/gender TPR gaps | Investigate outcome completeness, care access, discharge coding and group calibration; consult affected stakeholders | Compare label capture and calibration with group counts and uncertainty |
| Sparse race, age or intersectional strata | Improve representative data and outcome linkage; use grouped training folds where feasible | Report group support and independent cohort intervals; do not silently remove groups |
| Potential reliance on protected attributes and access proxies | Compare models with/without race, gender and payer; examine correlated proxies | Refit candidates on training data, compare validation AP, capture, TPR/FPR gaps and calibration; attribute removal alone does not guarantee fairness |
| Coverage differences persist after data checks | Evaluate group/outcome reweighting during training | Choose weights with training CV; assess validation utility and disparities under the same capacity constraint |
| Threshold or calibration mismatch | Evaluate calibrated scores and a capacity-constrained policy; consider group-aware post-processing only after stakeholder review | Fit calibration/post-processing within training folds; evaluate validation metrics and tradeoffs, then lock the policy |
| Risk of optimistic mitigation claims | Obtain recent independent data for the final mitigated candidate | Existing test results have already been examined; an untouched external cohort is needed for clean confirmation |

Do not optimize group thresholds from these test outcomes, mechanically enforce equal rates despite clinical context, or interpret the audit as deployment approval. Record the chosen tradeoff and uncertainty explicitly. All new CSV tables and PNG figures are saved under `reports/final_audit/fairness_explainability/`.

## Error analysis and representative predictions