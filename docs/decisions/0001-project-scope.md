# ADR 0001: Project scope

- Status: accepted
- Date: 2026-10-17

## Context

A state pipeline-safety analyst reviews incoming gas distribution incident
reports from many operators and must decide which ones need follow-up and by
whom. PHMSA publishes every report since 2010: 1,592 reports with 468 fields
each, covering facility, pressure, location, consequences, the
operator-assigned cause, and the estimated cost.

Constraints:

- the project is solo, due 11 December 2026;
- the course requires a regression task, a classification task, and an
  unsupervised task where the data supports them, with every applicable course
  algorithm implemented from scratch;
- the data mixes final and still-revisable reports, changed its report form
  around 2020, and includes a small number of non-natural-gas incidents.

## Decision

**Scope.**

- _Dataset:_ PHMSA gas distribution incident reports from 2010 onward.
- _Reports:_ final reports only.
- _Commodity:_ natural gas, or commodity left blank. 1,391 reports remain.
- _Information boundary:_ only what is known at initial report. Operator
  identity, calendar year, cause-specific sections, investigation findings,
  free text, and personal fields are excluded from features.

**Tasks.**

- _Classification:_ `CAUSE`, 8 classes. Primary metric: balanced accuracy.
- _Regression:_ `log(1 + PRPTY)`, total estimated cost. Primary metric: RMSE
  on the log scale.
- _Unsupervised:_ incident profiles, using PCA followed by k-means. Evaluated
  by silhouette score and stability across seeds and resamples.

**Partitions by incident year.** Training 2010–2019, validation 2020–2021,
final test 2022–2026. Preprocessing is fitted on training rows only, and the
test window is opened once after selection is frozen.

**Algorithms implemented from scratch.**

- linear (ridge) regression;
- logistic (softmax) regression;
- linear SVM, one-vs-rest;
- k-nearest neighbors;
- decision tree;
- random forest;
- neural network;
- k-means;
- PCA.

Scikit-learn is used only as a trusted reference for testing and comparison.

## Alternatives considered

- **Stratified random split.** It gives more rare-class examples and more stable
  metrics, but it mixes future incidents into training, so it overstates how
  well the model would predict new incidents. Rejected in favor of a time
  split; small-sample uncertainty is reported instead.
- **Time split at 2020 and 2022.** It leaves only 3 to 4 test examples of
  several causes. Rejected for boundaries one year earlier.
- **Keeping non-final reports, with a flag.** It adds 180 reports, but their
  causes and costs may still change, and they concentrate in the test window.
  Rejected.
- **All gas types.** Too few propane and synthetic reports (25) to learn from,
  and they fall outside the stated question. Rejected.
- **Operator identity as a feature.** It would likely improve accuracy, but it
  turns the model into an operator rating, which is outside the responsible-use
  boundary. Rejected.
- **Kernel SVM.** Excluded for time. Nonlinear structure is already tested by
  trees, the random forest, and the neural network.
- **Adding transmission and gathering pipeline data.** These are different
  systems with different report forms. Out of scope.

## Consequences

**Benefits.**

- Evaluation reflects real use: models predict later incidents from earlier
  ones.
- Labels in every window are final.
- The feature set is defensible under the initial-report boundary.

**Costs and risks.**

- The test window is small (225 reports). Corrosion and equipment failure have
  5 test examples each, so their per-class metrics are uncertain and are
  reported with bootstrap intervals.
- Training data predates the 2020 form revision, so newer form fields cannot
  be used.
- Release type strongly signals excavation damage, so classification results
  are also reported without it.

**Follow-up.**

- Implement the PHMSA adapter with checksum verification and a de-identified
  fixture.
- Record partitions in `configs/student.toml`.
- Add validation tests before fitting any model.

**Revisit if:**

- validation shows no model beats the baselines for a task, in which case
  narrow the task (for example, a binary excavation versus non-excavation
  target);
- PHMSA revises historical reports, which changes the checksum;
- the course clarifies that kernel SVM is required.
