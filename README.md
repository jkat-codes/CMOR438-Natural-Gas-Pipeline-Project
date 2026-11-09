# Gas Distribution Incident Predictor

**Jasper Katalevsky · CMOR 438 / INDE 577 · Rice University · Fall 2026**

Predicting why natural gas distribution incidents happen, and what they cost,
from the federal incident reports that pipeline operators file with PHMSA.

> This is an independent student project built on public data. It is not
> affiliated with, endorsed by, or produced by PHMSA or the U.S. Department of
> Transportation.

## The question

The Pipeline and Hazardous Materials Safety Administration (PHMSA) regulates
U.S. pipelines and publishes a report for every significant incident. Each
report records the pipe's material and installation year, its operating
pressure, its location, the operator, the system part involved, and the cause
the operator assigned.

This project asks: **using only information known when an incident is first
reported, can we identify why a gas distribution system failed and estimate
how much the incident will cost?**

The intended user is a pipeline-safety analyst (at a state regulator or an
operator's integrity team) who triages new incident reports and looks for
recurring failure patterns. The models support that review; they do not
replace an investigation and must not be used to assign fault or drive
enforcement automatically. See [`docs/PRODUCT_CONTRACT.md`](docs/PRODUCT_CONTRACT.md).

## Tasks

| Task | Target | Question |
| --- | --- | --- |
| Classification | `CAUSE` (8 classes) | Which cause category best explains a new incident? |
| Regression | `log(PRPTY)`, total incident cost | How expensive is an incident likely to be? |
| Unsupervised | none | Do incidents fall into distinct profiles by pipe, material, pressure, and location? |

Each task has its own leakage audit. Fields recorded only after an incident
(fire, explosion, evacuations, investigation results) are excluded from
prediction, and columns that sum to a target (for example the six cost
components of `PRPTY`) are removed for that task.

## Data

- **Source:** PHMSA gas distribution incident data, January 2010 to present,
  from the [PHMSA pipeline incident data page](https://www.phmsa.dot.gov/data-and-statistics/pipeline/distribution-transmission-gathering-lng-and-liquid-accident-and-incident-data).
- **Retrieved:** *fill in retrieval date*
- **License:** U.S. federal government public data.
- **Observation unit:** one incident report (1,592 reports, 468 columns,
  January 2010 to July 2026).

The raw file is **not** committed. Download it and place it in `data/local/`,
which Git ignores. A small fixture in `data/fixtures/`, with all contact and
personal fields removed, lets tests and CI run without the full dataset. Full
provenance, known quirks (a 2020 form revision, non-final reports, placeholder
values), and dropped fields are documented in
[`docs/DATASET_CARD.md`](docs/DATASET_CARD.md).

## Setup

Requires [Git](https://git-scm.com/) and [uv](https://docs.astral.sh/uv/).
Run from the repository root:

```bash
uv sync --locked
uv run python scripts/setup_project.py
uv run dsm-project verify
uv run ruff check src tests scripts
uv run pytest -q
```

Open notebooks in VS Code and select the **DSM Project** kernel.

## Notebooks

Each notebook is a self-contained case study that answers one question using
the project package. Planned sequence:

| Notebook | Question |
| --- | --- |
| `01` Data, question, and baselines | What does the incident data contain, what can it support, and what do simple baselines achieve? Includes the leakage audit. |
| `02` Cause classification | Can pre-incident characteristics identify the cause? Compares logistic regression, linear SVM, k-nearest neighbors, decision tree, random forest, and a neural network. |
| `03` Cost regression | What drives incident cost? Compares linear regression, k-nearest neighbors, decision tree, random forest, and a neural network. |
| `04` Incident profiles | Are there distinct incident profiles? PCA followed by k-means clustering. |
| `05` Model selection and final evaluation | Which models are promoted, and how do they perform on the sealed test set? |

## Package

Algorithms are implemented from scratch in NumPy under
[`src/dsm_project/algorithms/student/`](src/dsm_project/algorithms/student/)
and registered in `src/dsm_project/algorithms/registry.py`. Scikit-learn is
used only as a trusted reference for testing and comparison, and reference
results are labeled as such everywhere they appear.

| Algorithm family | Task | Status |
| --- | --- | --- |
| Linear regression | Regression | Planned |
| Logistic regression | Classification | Planned |
| Linear support vector machine | Classification | Planned |
| k-nearest neighbors | Classification, regression | Planned |
| Decision tree | Classification, regression | Planned |
| Random forest | Classification, regression | Planned |
| Neural network | Classification, regression | Planned |
| k-means clustering | Unsupervised | Planned |
| Principal component analysis | Unsupervised | Planned |

Every estimator follows the `fit` / `predict` (or `transform`) interface,
validates its inputs, rejects use before fitting, controls randomness through a
seed, and is tested against analytic cases and a trusted reference.

```python
from dsm_project.config import load_config
from dsm_project.data import load_project_dataset
from dsm_project.algorithms import registered_student_algorithms

config = load_config("configs/student.toml")
dataset = load_project_dataset(config)
print(registered_student_algorithms())
```

## Repository map

| Location | Contents |
| --- | --- |
| `configs/` | Data and experiment configuration |
| `data/local/` | Raw PHMSA data (ignored by Git) |
| `data/fixtures/` | Small, de-identified fixture for tests and CI |
| `notebooks/` | Case-study notebooks |
| `src/dsm_project/data/` | PHMSA adapter, validation, and task definitions |
| `src/dsm_project/algorithms/student/` | From-scratch algorithm implementations |
| `src/dsm_project/experiments/`, `evaluation/` | Experiments, metrics, and trusted references |
| `src/dsm_project/service/`, `monitoring/` | Prediction API and structured logs |
| `tests/` | Unit, property, differential, integration, and API tests |
| `docs/` | Product contract, dataset card, model card, operations, decisions |

Course assignment and template guidance are kept in
[`ASSIGNMENT.md`](ASSIGNMENT.md), [`START_HERE.md`](START_HERE.md), and
[`PROJECT_CHECKLIST.md`](PROJECT_CHECKLIST.md).
