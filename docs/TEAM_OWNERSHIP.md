# Team ownership and integration

## Participants

- @jkat-codes (solo project)

## Shared core

This is a solo project, so there is no shared core between teammates. All
design decisions, code, tests, documentation, and reviews are owned by the
single participant listed above.

## Individual vertical slices

**@jkat-codes: entire product.**

- **User need:** a state pipeline-safety analyst triaging new gas distribution
  incident reports (see [`PRODUCT_CONTRACT.md`](PRODUCT_CONTRACT.md)).
- **Owned interfaces:**
  - PHMSA data adapter and fixture;
  - student algorithms under `src/dsm_project/algorithms/student/`;
  - experiment configuration;
  - prediction API and client;
  - logging and monitoring.
- **Tests:** unit, property, differential, integration, and API tests under
  `tests/`.
- **Documentation:** README, product contract, dataset card, model card,
  operations, and decision records.
- **Related issues and pull requests:** tracked in the repository's Issues and
  Pull requests tabs. Each pull request links the issue it closes.
- **Dependencies on teammates:** none.

## Integration and conflict history

**Partition strategy: time-based versus stratified random split.**

- _Competing intentions._ A stratified random split keeps enough rare-cause
  examples in every partition and gives more stable metrics. A time-based split
  matches how the product would be used, predicting new incidents from past
  ones, and exposes drift.
- _Evidence._
  - With final natural-gas reports only, splitting at 2019 and 2021 leaves at
    least 5 examples of every cause in each window.
  - Excluding non-final reports removes most of the unsettled "other incident
    cause" labels that had concentrated in 2023–2026.
- _Resulting contract._ Training 2010–2019, validation 2020–2021, final test
  2022–2026, recorded in [`decisions/0001-project-scope.md`](decisions/0001-project-scope.md)
  and `configs/student.toml`. Rare-class metrics are reported with bootstrap
  intervals because the test counts are small.

## Maintenance responsibility

@jkat-codes investigates defects in every component through final
review on 11 December 2026.
