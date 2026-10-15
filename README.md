# Predicting 30-day hospital readmission among patients with diabetes

This retrospective capstone predicts recorded readmission within 30 days using information available at discharge. The final dataset contains 69,970 patients. Results support risk prioritization, with no demonstrated effect of follow-up on prevention.

## Notebook order

Run notebooks from the project folder in this order:

1. `01_problem_statement.ipynb`: objective, target, and success criteria.
2. `02_data_cleaning_split.ipynb`: cleaning, target creation, diagnosis groups, and stratified splits.
3. `03_eda.ipynb`: training-data exploration.
4. `04_feature_engineering.ipynb`: fixed row-level features for all splits.
5. `05_model_evaluation.ipynb`: model comparison, tuning, final results, and executed audits.
6. `06_final_results_&_conclusions.ipynb`: refreshed final results and conclusions, incorporating the completed notebook 5 audits and saved audit reports.

The notebooks are numbered 01 through 06. EDA and feature engineering remain separate: notebook 03 explores training data, while notebook 04 applies the same feature formulas to all splits. Re-running earlier notebooks can overwrite processed files, reports, and the fitted model. Use the intended kernel and run cells in order.

## Environment

This project was verified using Python 3.13.12 and the package versions listed in requirements.txt. Install these dependencies and select the corresponding Python environment as your Jupyter kernel. The saved model requires scikit-learn 1.8.0, matching the version used during training. Notebook 3’s PNG exports use Kaleido and require an installed Chrome/Chromium browser. requirements.txt lists the project’s Python dependencies; it is not a complete environment lockfile.

## Files and results

- `data/raw/`: original encounter data and administrative ID descriptions.
- `data/processed/`: cleaned data, split files, and engineered split files.
- `models/final_gradient_boosting.joblib`: pipeline, threshold, input columns, and tuning settings.
- `reports/final_gradient_boosting_test_metrics.csv`: existing final test report.
- `reports/final_audit/`: nine completed audit tables covering calibration, permutation importance, subgroup results, uncertainty intervals, identity checks, split performance, policy comparisons, and learning curves.
- `reports/figures/`: saved EDA charts.
- `Data_Dictionary.md`: complete variable definitions, cleaning rules, engineered features, and administrative ID mappings.
- `capstone_presentation/Diabetes_Readmission_Capstone.pptx`: editable five-slide presentation.
- `.presentation-build/`: presentation intermediate artifacts, outside the main notebook workflow.
- `reports/significance_analysis/`: all 30 paired candidate-model comparisons and the standalone analysis script.
- `reports/final_audit/fairness_explainability/`: parity metrics, uncertainty contrasts, PDP/ICE tables and figures.
- `reports/reproducibility/`: ordered execution runner, logs and verification results.

The final audit section loads the existing saved model. It does not replace it or change threshold 0.10. Learning curves fit fresh copies on training folds only. Test subgroup and bootstrap results describe the fixed model and must not guide new model selection.

The recorded top-20% result selects 2,100 patients and captures 369 of 942 readmissions (39.17%), with 17.57% precision and 1.96× lift. The source dataset covers 1999–2008. External validation and intervention benefit remain untested.

## Key results and audit findings

| Measure | Result |
|---|---:|
| Test average precision | 0.1866 |
| Test ROC-AUC | 0.6523 |
| Recall at threshold 0.10 | 47.77% |
| Precision at threshold 0.10 | 15.35% |
| Patients flagged at threshold 0.10 | 2,932 (27.93%) |
| Capture among the highest-risk 20% | 39.17% |
| Approximate 95% bootstrap interval for top-20% capture | 35.93%–41.60% |
| Top-20% precision | 17.57% |
| Top-20% lift over random selection | 1.96× |

The top-20% result exceeds the predefined 30% capture target. The bootstrap interval describes uncertainty for the existing fitted model on this test population, not performance in future hospitals.

Validation permutation importance ranks discharge disposition, previous inpatient visits, and payer code highest. This describes predictive associations, not causes. Validation Brier score is 0.07918 versus 0.08169 for the constant training-prevalence baseline. Calibration diagnostics do not establish clinical readiness.

Under the test top-20% policy, recall is 27.71% for AfricanAmerican patients and 41.92% for Caucasian patients. These observed gaps require investigation with group sizes and uncertainty. The learning curves show improved cross-validation AP with more training data, but a training–validation gap remains.

## Submission details

Author, course and dataset references are completed in notebook 01. Preserve the distinction between threshold 0.10 and selecting the top 20% by rank. Notebook 6 includes significance findings, expanded fairness/explainability evidence, uncertainty and subgroup limitations. The paired tests do not establish tuned boosting as superior to full logistic regression or the leading tree alternatives. Its advantage over SVD survives Holm correction on both metrics.

## Ordered execution verification

Run `python reports/reproducibility/run_notebooks.py` from the project root in the AIM environment. The runner starts a fresh IPython process for each notebook, executes every code cell in file order, captures outputs, and stops on the first error. It writes `execution_summary.json` and per-notebook progress logs under `reports/reproducibility/`. A full run regenerates processed splits, reports and the fitted model using the recorded settings. Notebook 03 exports PNGs through Kaleido and requires a compatible Chrome/Chromium installation.

The ordered run verified on **15 October 2026** completed all six notebooks without code-cell errors. The workflow includes training-only medication exclusions and an exact patient split manifest. Candidate comparisons were regenerated; the final test performance is checked in the current verification report. See `reports/reproducibility/execution_summary.json` and `verification_checks.json` for evidence.

## Training-only medication selection and exact split identity

Notebook 02 fixes stratified split membership before calculating medication frequencies. Medication columns with fewer than three training patients having a status other than `No` are excluded; the same list is applied to all splits. The count table is saved in `reports/final_audit/training_medication_selection.csv`.

`data/processed/split_patient_manifest.csv` records Split, Row (zero-based saved split row order), patient_nbr and encounter_id. It is an audit artifact, never a model input. Notebook 05 checks unique patients/encounters, source-row alignment, complete coverage and zero patient overlap directly.

The presentation decks predate the training-only medication update; use the regenerated notebook model-comparison tables for current candidate metrics and feature counts.
