# Data dictionary

This dictionary expands my original `Data_Dictionary` notes and documents the variables used in my diabetes readmission project. Definitions and cleaning rules are checked against the saved data and notebooks 02, 04, and 05.

## Dataset and modeling files

| File | Contents |
|---|---|
| `data/raw/raw_diabetic_data.csv` | 101,766 hospital encounters and 50 original columns. A patient can have several encounters. |
| `data/raw/IDS_mapping.csv` | Definitions for the three administrative ID columns. |
| `data/processed/diabetic_clean.csv` | Intermediate cleaned data; identifiers and original diagnosis codes are still present. |
| `data/processed/diabetic_cleaned_final.csv` | 69,970 patients, one selected encounter per patient, and 41 columns including the target. |
| `data/processed/train.csv`, `val.csv`, `test.csv` | Approximately 70%, 15%, and 15% of the final data. |
| `data/processed/train_fe.csv`, `val_fe.csv`, `test_fe.csv` | Split files with six added features: 47 columns including the target and original age band. |

The final model uses 45 input columns: it excludes `readmit_30` and the original `age` band from the engineered split files. These are input columns before categorical encoding, not the number of encoded model features.

The cleaning notebook selects the lowest encounter ID for each patient, excludes discharge codes 11, 13, 14, 19, 20, and 21, and removes three rows with invalid gender. The selected encounter is identified by ID order; the data do not supply an admission date to verify chronological order.

Prediction is made using information available at discharge. The outcome is observed later and must never be included as an input.

## Identifiers and target

| Variable | Type and values | Meaning | Use in this project |
|---|---|---|---|
| `encounter_id` | Integer identifier | Identifies a hospital encounter. | Used to order encounters during selection; dropped before modeling. |
| `patient_nbr` | Integer identifier | Identifies a patient across encounters. | Used to retain one encounter per patient; dropped before modeling. |
| `readmitted` | Category: `<30`, `>30`, `NO` | Original recorded readmission outcome: within 30 days, after 30 days, or no recorded readmission. | Converted to `readmit_30`, then removed. Not a predictor. |
| `readmit_30` | Binary integer: 0 or 1 | 1 when `readmitted` is `<30`; 0 for both `>30` and `NO`. | Target created in notebook 02. A value of 0 does not necessarily mean the patient was never readmitted. |

## Demographic and administrative variables

| Variable | Type and values | Meaning | Cleaning and model use |
|---|---|---|---|
| `race` | Category: Caucasian, AfricanAmerican, Asian, Hispanic, Other; `?` in raw data | Recorded race category. | Missing values become `Unknown`; retained. |
| `gender` | Category: Female, Male, Unknown/Invalid | Recorded gender label. | Rows labeled `Unknown/Invalid` are removed; retained. |
| `age` | Ordered category: `[0-10)` through `[90-100)` | Age interval; `[50-60)` means at least 50 and below 60. | Kept in processed files; replaced by `age_numeric` as a model input. |
| `weight` | Category: weight intervals and `>200`; `?` for missing | Recorded weight band in pounds, according to UCI metadata. | Dropped because most values are missing. |
| `payer_code` | Category: BC, CH, CM, CP, DM, FR, HM, MC, MD, MP, OG, OT, PO, SI, SP, UN, WC; `?` for missing | Recorded payer/insurance code. | Missing values become `Unknown`; retained. The local mapping file does not define the individual payer abbreviations. |
| `medical_specialty` | Category: specialty names; `?` for missing | Recorded physician specialty. | Missing values become `Unknown`; retained. |

## Hospital encounter variables

| Variable | Type and values | Meaning | Cleaning and model use |
|---|---|---|---|
| `admission_type_id` | Categorical ID; see mapping below | Type of admission, such as emergency or elective. | Retained and treated as categorical in the modeling workflow. |
| `discharge_disposition_id` | Categorical ID; see mapping below | Discharge destination or patient status. | Death/hospice codes 11, 13, 14, 19, 20, 21 are excluded; remaining codes retained as categories. |
| `admission_source_id` | Categorical ID; see mapping below | Source or referral route for the admission. | Retained as a category. |
| `time_in_hospital` | Integer, 1–14 days in the raw data | Length of the hospital stay. | Retained as numeric. |

Administrative IDs are category labels. A higher code does not mean a more severe condition. Codes described as `NULL`, `Not Available`, or `Not Mapped` in the mapping file remain explicit ID categories in the current workflow.

## Utilization and clinical activity

| Variable | Type | Meaning | Model use |
|---|---|---|---|
| `num_lab_procedures` | Integer count | Laboratory procedures recorded during the encounter. | Retained as numeric. |
| `num_procedures` | Integer count | Procedures other than laboratory tests during the encounter. | Retained as numeric. |
| `num_medications` | Integer count | Distinct generic medications recorded during the encounter, including medicines beyond the diabetes columns. | Retained as numeric. |
| `number_outpatient` | Integer count | Outpatient visits in the year before the encounter. | Retained; also used in `prior_utilization`. |
| `number_emergency` | Integer count | Emergency visits in the year before the encounter. | Retained; also used in `prior_utilization`. |
| `number_inpatient` | Integer count | Inpatient visits in the year before the encounter. | Retained; also used in `prior_utilization` and `prior_inpatient`. |
| `number_diagnoses` | Integer count | Number of diagnoses recorded for the encounter. | Retained. This can exceed three even though only three diagnosis-code fields are provided. |

Zero prior visits means no recorded visits of that type; the notebook does not replace zero with a missing value.

## Diagnosis variables

| Variable | Type | Meaning | Cleaning and model use |
|---|---|---|---|
| `diag_1` | ICD-9-CM code stored as text; `?` for missing | Primary diagnosis code. | Converted to `diag_1_group`, then dropped. |
| `diag_2` | ICD-9-CM code stored as text; `?` for missing | Secondary diagnosis code. | Converted to `diag_2_group`, then dropped. |
| `diag_3` | ICD-9-CM code stored as text; `?` for missing | Additional secondary diagnosis code. | Converted to `diag_3_group`, then dropped. |
| `diag_1_group` | Category | Broad group derived from `diag_1`. | Retained; missing diagnosis becomes `Unknown`. |
| `diag_2_group` | Category | Broad group derived from `diag_2`. | Retained; missing diagnosis becomes `Unknown`. |
| `diag_3_group` | Category | Broad group derived from `diag_3`. | Retained; missing diagnosis becomes `Unknown`. |

The table below documents the exact numeric comparisons in notebook 02. Bounds are inclusive; the first matching group is used. These are the project's mapping rules, rather than a complete clinical coding reference. The Diabetes rule is checked before the broader Endocrine rule. Missing codes become `Unknown`; unparseable or unmatched codes become `Other/Unknown`.

| Code rule | Group |
|---|---|
| 1–139 | Infectious and Parasitic |
| 140–239 | Neoplasms |
| 250–250.99 | Diabetes |
| 240–289 | Endocrine, Nutritional, Metabolic, and Blood |
| 290–319 | Mental Disorders |
| 320–389 | Nervous System and Sense Organs |
| 390–459 | Circulatory |
| 460–519 | Respiratory |
| 520–579 | Digestive |
| 580–629 | Genitourinary |
| 630–679 | Pregnancy, Childbirth, and Puerperium |
| 680–709 | Skin and Subcutaneous Tissue |
| 710–739 | Musculoskeletal |
| 740–759 | Congenital Anomalies |
| 760–779 | Perinatal Conditions |
| 780–799 | Symptoms, Signs, and Ill-Defined Conditions |
| 800–999 | Injury and Poisoning |
| Starts with `V` | Supplementary Factors |
| Starts with `E` | External Causes of Injury |

## Laboratory variables

| Variable | Type and values | Meaning | Cleaning and model use |
|---|---|---|---|
| `max_glu_serum` | Category: Norm, >200, >300, None | Recorded glucose test result category. Threshold labels refer to mg/dL. | Raw `None` is parsed as missing by pandas and becomes `Not_tested`; retained. |
| `A1Cresult` | Category: Norm, >7, >8, None | Recorded HbA1c result category; threshold labels refer to percentages. | Raw `None` is parsed as missing by pandas and becomes `Not_tested`; retained. |

These columns contain result categories, not exact laboratory measurements. `Not_tested` represents no recorded test result in this dataset; it must not be interpreted as a normal result.

## Diabetes medication variables

Each medication column is categorical. `No` means not prescribed; `Steady` means prescribed without a dosage change; `Up` means dosage increased; `Down` means dosage decreased. These labels describe recorded prescribing status during the encounter, not the exact dose or proof that the patient took the medication. Not every medication has all four labels in the observed data.

| Variable | Medication represented | Model use |
|---|---|---|
| `metformin` | metformin | Retained; included in `num_diabetes_meds`. |
| `repaglinide` | repaglinide | Retained; included in `num_diabetes_meds`. |
| `nateglinide` | nateglinide | Retained; included in `num_diabetes_meds`. |
| `chlorpropamide` | chlorpropamide | Retained; included in `num_diabetes_meds`. |
| `glimepiride` | glimepiride | Retained; included in `num_diabetes_meds`. |
| `acetohexamide` | acetohexamide | Dropped: constant or very rare after patient filtering. |
| `glipizide` | glipizide | Retained; included in `num_diabetes_meds`. |
| `glyburide` | glyburide | Retained; included in `num_diabetes_meds`. |
| `tolbutamide` | tolbutamide | Retained; included in `num_diabetes_meds`. |
| `pioglitazone` | pioglitazone | Retained; included in `num_diabetes_meds`. |
| `rosiglitazone` | rosiglitazone | Retained; included in `num_diabetes_meds`. |
| `acarbose` | acarbose | Retained; included in `num_diabetes_meds`. |
| `miglitol` | miglitol | Retained; included in `num_diabetes_meds`. |
| `troglitazone` | troglitazone | Retained: three training patients have non-No status; the exclusion rule is fewer than three. |
| `tolazamide` | tolazamide | Retained; included in `num_diabetes_meds`. |
| `examide` | examide | Dropped: constant or very rare after patient filtering. |
| `citoglipton` | citoglipton | Dropped: constant or very rare after patient filtering. |
| `insulin` | insulin | Retained; included in `num_diabetes_meds`. |
| `glyburide-metformin` | glyburide + metformin | Retained; included in `num_diabetes_meds`. |
| `glipizide-metformin` | glipizide + metformin | Retained; included in `num_diabetes_meds`. |
| `glimepiride-pioglitazone` | glimepiride + pioglitazone | Dropped: constant or very rare after patient filtering. |
| `metformin-rosiglitazone` | metformin + rosiglitazone | Dropped: constant or very rare after patient filtering. |
| `metformin-pioglitazone` | metformin + pioglitazone | Dropped: constant or very rare after patient filtering. |

## Medication change variables

| Variable | Type and values | Meaning | Model use |
|---|---|---|---|
| `change` | Category: Ch, No | Whether a diabetes medication change was recorded, such as a dose or medicine change. | Retained as categorical. |
| `diabetesMed` | Category: Yes, No | Whether any diabetes medication was prescribed. | Retained as categorical. `No` does not establish that the patient does not have diabetes. |

## Engineered features from notebook 04

| Variable | Type and values | Calculation | Interpretation |
|---|---|---|---|
| `age_numeric` | Numeric: 5, 15, …, 95 | Midpoint of each age band. | Approximate age in years, not the patient's exact age. |
| `prior_utilization` | Integer count, at least 0 | `number_outpatient + number_emergency + number_inpatient` | Total recorded visits across the three types in the preceding year. |
| `prior_inpatient` | Binary: 0 or 1 | 1 if `number_inpatient > 0`; otherwise 0. | Any previous inpatient visit. |
| `num_diabetes_meds` | Integer count, possible 0–16 | Count retained medication columns with Steady, Up, or Down. | Number of active medication columns, not unique ingredients; combination medicines count as one column. |
| `insulin_used` | Binary: 0 or 1 | 1 if `insulin` is Steady, Up, or Down; otherwise 0. | Recorded insulin prescribing indicator. |
| `diabetes_diag_count` | Integer: 0, 1, 2, 3 | Count Diabetes labels across `diag_1_group`, `diag_2_group`, and `diag_3_group`. | Diabetes entries among the three available diagnosis fields. |

All six features are retained as numeric model inputs. Their formulas are applied separately and identically to each split without learning values from other patients.

**A `diabetes_diag_count` of 0 does not mean the patient has no diabetes.** Dataset inclusion can reflect diabetes recorded elsewhere, while only three diagnosis fields are supplied here. A mean count of 0.40 is an average number of entries, not evidence that 40% of patients have diabetes.

## Missing-value handling

The following percentages use all 101,766 raw encounters. They can differ from the percentages after selecting one encounter per patient and applying exclusions.

| Raw variable | Raw marker | Count | Percentage | Handling |
|---|---|---:|---:|---|
| `race` | `?` | 2,273 | 2.23% | Replaced with `Unknown`. |
| `weight` | `?` | 98,569 | 96.86% | Dropped. |
| `payer_code` | `?` | 40,256 | 39.56% | Replaced with `Unknown`. |
| `medical_specialty` | `?` | 49,949 | 49.08% | Replaced with `Unknown`. |
| `diag_1` | `?` | 21 | 0.02% | Missing diagnosis maps to `Unknown` in the derived group. |
| `diag_2` | `?` | 358 | 0.35% | Missing diagnosis maps to `Unknown` in the derived group. |
| `diag_3` | `?` | 1,423 | 1.40% | Missing diagnosis maps to `Unknown` in the derived group. |
| `max_glu_serum` | `None` (no recorded test) | 96,420 | 94.75% | Replaced with `Not_tested`. |
| `A1Cresult` | `None` (no recorded test) | 84,748 | 83.28% | Replaced with `Not_tested`. |

The final cleaned file has no empty cells. `Unknown` and `Not_tested` are still informative categories; no empty cells does not mean every measurement was available.

## Administrative ID mappings

The following labels reproduce `data/raw/IDS_mapping.csv`, including codes that do not occur in the raw sample. SNF means skilled nursing facility; ICF means intermediate care facility; AMA means against medical advice. The source file's labels are preserved.

### `admission_type_id`

| Code | Source description |
|---|---|
| 1 | Emergency |
| 2 | Urgent |
| 3 | Elective |
| 4 | Newborn |
| 5 | Not Available |
| 6 | NULL |
| 7 | Trauma Center |
| 8 | Not Mapped |

### `discharge_disposition_id`

| Code | Source description |
|---|---|
| 1 | Discharged to home |
| 2 | Discharged/transferred to another short term hospital |
| 3 | Discharged/transferred to SNF |
| 4 | Discharged/transferred to ICF |
| 5 | Discharged/transferred to another type of inpatient care institution |
| 6 | Discharged/transferred to home with home health service |
| 7 | Left AMA |
| 8 | Discharged/transferred to home under care of Home IV provider |
| 9 | Admitted as an inpatient to this hospital |
| 10 | Neonate discharged to another hospital for neonatal aftercare |
| 11 | Expired |
| 12 | Still patient or expected to return for outpatient services |
| 13 | Hospice / home |
| 14 | Hospice / medical facility |
| 15 | Discharged/transferred within this institution to Medicare approved swing bed |
| 16 | Discharged/transferred/referred another institution for outpatient services |
| 17 | Discharged/transferred/referred to this institution for outpatient services |
| 18 | NULL |
| 19 | Expired at home. Medicaid only, hospice. |
| 20 | Expired in a medical facility. Medicaid only, hospice. |
| 21 | Expired, place unknown. Medicaid only, hospice. |
| 22 | Discharged/transferred to another rehab fac including rehab units of a hospital . |
| 23 | Discharged/transferred to a long term care hospital. |
| 24 | Discharged/transferred to a nursing facility certified under Medicaid but not certified under Medicare. |
| 25 | Not Mapped |
| 26 | Unknown/Invalid |
| 30 | Discharged/transferred to another Type of Health Care Institution not Defined Elsewhere |
| 27 | Discharged/transferred to a federal health care facility. |
| 28 | Discharged/transferred/referred to a psychiatric hospital of psychiatric distinct part unit of a hospital |
| 29 | Discharged/transferred to a Critical Access Hospital (CAH). |

### `admission_source_id`

| Code | Source description |
|---|---|
| 1 | Physician Referral |
| 2 | Clinic Referral |
| 3 | HMO Referral |
| 4 | Transfer from a hospital |
| 5 | Transfer from a Skilled Nursing Facility (SNF) |
| 6 | Transfer from another health care facility |
| 7 | Emergency Room |
| 8 | Court/Law Enforcement |
| 9 | Not Available |
| 10 | Transfer from critial access hospital |
| 11 | Normal Delivery |
| 12 | Premature Delivery |
| 13 | Sick Baby |
| 14 | Extramural Birth |
| 15 | Not Available |
| 17 | NULL |
| 18 | Transfer From Another Home Health Agency |
| 19 | Readmission to Same Home Health Agency |
| 20 | Not Mapped |
| 21 | Unknown/Invalid |
| 22 | Transfer from hospital inpt/same fac reslt in a sep claim |
| 23 | Born inside this hospital |
| 24 | Born outside this hospital |
| 25 | Transfer from Ambulatory Surgery Center |
| 26 | Transfer from Hospice |

## Sources and maintenance

- Original project notes: `Data_Dictionary` (preserved).
- Project implementation: [cleaning and splitting notebook](02_data_cleaning_split.ipynb), [feature engineering notebook](04_feature_engineering.ipynb), and [model evaluation notebook](05_model_evaluation.ipynb).
- Local values and mappings: `data/raw/raw_diabetic_data.csv`, `data/raw/IDS_mapping.csv`, and saved processed files.
- Dataset reference: [UCI Diabetes 130-US Hospitals for Years 1999–2008](https://archive.ics.uci.edu/dataset/296/diabetes%2B130%2Bus%2Bhospitals%2Bfor%2Byears%2B1999%2B2008), DOI 10.24432/C5230J.
- Original study referenced by the notebooks: [Strack et al. (2014), Impact of HbA1c Measurement on Hospital Readmission Rates](https://doi.org/10.1155/2014/781670). The linked full text was not accessible during this dictionary refresh; project-specific rules were verified from the local notebooks.

Update this dictionary if the selected variables, diagnosis rules, cleaning decisions, or feature formulas change.

## Training-only medication selection and exact split identity

Notebook 02 fixes stratified split membership before calculating medication frequencies. Medication columns with fewer than three training patients having a status other than `No` are excluded; the same list is applied to all splits. The count table is saved in `reports/final_audit/training_medication_selection.csv`.

`data/processed/split_patient_manifest.csv` records Split, Row (zero-based saved split row order), patient_nbr and encounter_id. It is an audit artifact, never a model input. Notebook 05 checks unique patients/encounters, source-row alignment, complete coverage and zero patient overlap directly.
