# Product contract

## Users and decisions

**Intended user.** A state pipeline-safety analyst who reviews incoming gas
distribution incident reports across many operators.

**Decisions supported.**

- _Triage:_ when a new incident is reported, estimate which cause category is
  most likely and how costly the incident is likely to be, so the analyst can
  prioritize follow-up and route the report to the right specialist.
- _Pattern review:_ identify recurring incident profiles (combinations of pipe
  material, age, pressure, system part, and setting) that may warrant
  attention across operators.

**Decisions this product must not automate.**

- Determining the cause of record for an incident. Cause is established by the
  operator's report and by investigation, not by this model.
- Enforcement, penalties, or any judgment about an operator's compliance.
- Ranking or scoring operators. Operator identity is deliberately excluded
  from model features.
- Emergency response. Predictions are for after-the-fact review, not for
  decisions made while an incident is in progress.

## Dataset suite

One dataset: PHMSA gas distribution incident reports, January 2010 to present.
Full details are in [`DATASET_CARD.md`](DATASET_CARD.md).

| Property           | Value                                                                                            |
| ------------------ | ------------------------------------------------------------------------------------------------ |
| Source             | PHMSA, U.S. Department of Transportation                                                         |
| License            | U.S. federal government public data                                                              |
| Observation unit   | One incident report                                                                              |
| Rows in scope      | 1,391 final reports involving natural gas (or unspecified commodity), from 1,592 total           |
| Time boundary      | Incidents from January 2010 to July 2026                                                         |
| Representativeness | Only incidents meeting federal reporting thresholds; operator-reported causes and cost estimates |

### Information boundary

Models may use only information that would be available when an incident is
first reported: what an operator would know at initial notification, before
any investigation.

| Allowed                                                                                               | Excluded                                                                                                                        |
| ----------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| Incident time (month, weekday, hour) and location (state, coordinates, location type, class location) | Calendar year as a feature, since the split is by time                                                                          |
| System part involved, pipe material, installation year, diameter, depth of cover, crossing type       | Operator ID and name (operator scoring is out of scope)                                                                         |
| Normal, maximum, and incident pressure                                                                | All cause-specific report sections (corrosion, excavation, vehicle, natural force, and so on); their presence reveals the cause |
| Release type (leak, rupture, mechanical puncture, other)                                              | Investigation findings, root cause, drug testing, investigation status                                                          |
| Ignition, explosion, injuries, fatalities, evacuations                                                | Any cost component, for the cost-regression task                                                                                |
|                                                                                                       | Narrative and free-text detail fields; contact and personal fields                                                              |

Release type is the strongest single signal for cause: 383 of 485 excavation
incidents are mechanical punctures. It is observable on site and so falls
inside the boundary, but the classification notebook reports results with and
without it so that the dependence is visible.

## Task-algorithm matrix

| Course family                       | Project task                          | Applicable?                           | Mathematical justification                                                                                                                                                                  | Evidence         |
| ----------------------------------- | ------------------------------------- | ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------- |
| Linear regression                   | Cost regression                       | Yes                                   | Linear baseline for log cost; ridge penalty because one-hot categorical features are collinear                                                                                              | Notebook 03      |
| Logistic regression                 | Cause classification                  | Yes                                   | Multinomial (softmax) model gives calibrated class probabilities for 8 causes                                                                                                               | Notebook 02      |
| Nearest neighbors                   | Cause classification, cost regression | Yes                                   | Tests whether similar incidents share cause and cost; requires scaled features                                                                                                              | Notebooks 02, 03 |
| Support vector machines and kernels | Cause classification                  | Linear SVM: yes. Kernel SVM: excluded | One-vs-rest hinge-loss classifier as a margin-based alternative to logistic regression. Kernel methods are excluded for time; trees and the neural network already test nonlinear structure | Notebook 02      |
| Decision trees                      | Cause classification, cost regression | Yes                                   | Handles mixed categorical and numeric features and interactions without scaling                                                                                                             | Notebooks 02, 03 |
| Ensembles                           | Cause classification, cost regression | Yes (random forest)                   | Reduces variance of single trees; tests whether that improves on one tree                                                                                                                   | Notebooks 02, 03 |
| Neural networks                     | Cause classification, cost regression | Yes                                   | Softmax output for cause, linear output for log cost; tests nonlinear structure                                                                                                             | Notebooks 02, 03 |
| Clustering                          | Incident profiles                     | Yes (k-means)                         | Groups incidents by pipe, material, pressure, and location features                                                                                                                         | Notebook 04      |
| Dimensionality reduction            | Incident profiles                     | Yes (PCA)                             | Summarizes correlated numeric features before clustering and supports visualization                                                                                                         | Notebook 04      |

## Evaluation contract

These boundaries and metrics are fixed before any model is fitted and before the
test set is opened.

**Partitions** (by incident year, in `configs/student.toml`):

| Role       | Years     | Reports |
| ---------- | --------- | ------- |
| Training   | 2010–2019 | 977     |
| Validation | 2020–2021 | 189     |
| Final test | 2022–2026 | 225     |

- All learned preprocessing (scaling, imputation, encoding vocabularies) is
  fitted on training rows only.
- Model and hyperparameter choices use the validation window only.
- After selection is frozen, the chosen models are refitted on 2010–2021 and
  the test window is evaluated once. The date it is opened is recorded in the
  model card.

**Cause classification**

- Primary metric: balanced accuracy, because the classes are imbalanced
  (excavation 35%, corrosion 2%).
- Also reported: macro-F1, per-class recall, confusion matrix, log loss.
- Baselines: majority class, and random guessing at training-set class
  frequencies.

**Cost regression**

- Target: `log(1 + PRPTY)`. Ten reports have zero cost.
- Primary metric: RMSE on the log scale. Also reported: MAE on the log scale,
  and the error expressed as a multiplicative factor on cost.
- Baselines: the mean and the median of training log cost.

**Incident profiles**

- PCA: explained variance and reconstruction error.
- k-means: choose the number of clusters from silhouette score and stability
  across seeds and bootstrap resamples (adjusted Rand index).
- Cause labels are used only to describe clusters after fitting, never to fit
  them.

**Uncertainty.** Bootstrap confidence intervals over test rows for every
reported metric, and variation across random seeds for stochastic models.

**Slices.** System part involved, pipe material, U.S. region, and incident year
within the test window.

**Promotion rule.** A model is promoted to the API only if its validation
primary metric beats the best baseline and the 95% bootstrap interval of the
difference excludes zero. Otherwise the baseline is served and the result is
reported as negative.

## System interfaces

| Component        | Interface                                                                                                                                       |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| Data boundary    | PHMSA adapter in `src/dsm_project/data/` reads the raw file from `data/local/`; a de-identified fixture in `data/fixtures/` serves tests and CI |
| Training         | `scripts/train.py` with `configs/student.toml`                                                                                                  |
| Artifact         | Versioned bundle in `artifacts/` with model, configuration, feature order, data checksum, and metrics                                           |
| Prediction API   | FastAPI service: `POST /predict` returns cause probabilities and an estimated cost range; `GET /health` and `GET /model` report model identity  |
| User interface   | Minimal browser client in `src/dsm_project/service/static/` for entering an incident's initial details                                          |
| Deployment       | Docker image via `compose.yaml`                                                                                                                 |
| Logs and metrics | Structured JSON logs with request ID, model version, validation failures, latency, and prediction                                               |
| Rollback         | Redeploy the previous artifact version; documented in [`OPERATIONS.md`](OPERATIONS.md)                                                          |

## Responsible-use boundary

- **Privacy.** The source data names the people who prepared each report. All
  contact and personal fields are dropped at ingestion and never committed,
  logged, or served.
- **Uncertainty.** Every prediction is returned as probabilities or a range,
  never as a bare label or point estimate.
- **Label quality.** Causes are assigned by the reporting operator and include
  broad "other" categories. The model learns what operators report, which is
  not necessarily the true cause.
- **Coverage.** Only incidents above federal reporting thresholds are included,
  so the model says nothing about minor leaks. Performance may differ by
  region, operator size, and reporting period.
- **What a good result does not prove.** Accurate predictions do not establish
  that any feature causes incidents, and do not make the model fit to replace
  an investigation.
