# Dataset card

## Identity and provenance

- **Dataset name:** PHMSA Gas Distribution Incident Data, January 2010 to present
- **Source owner:** Pipeline and Hazardous Materials Safety Administration
  (PHMSA), U.S. Department of Transportation
- **Retrieval method and date:** Manual download from the
  [PHMSA pipeline incident data page](https://www.phmsa.dot.gov/data-and-statistics/pipeline/distribution-transmission-gathering-lng-and-liquid-accident-and-incident-data),
  file `incident_gas_distribution_jan2010_present.txt`, retrieved _fill in date_.
- **License or access agreement:** U.S. federal government public data; no
  credentials required.
- **Immutable version:** SHA-256
  `fb98390d443eff00a6de9f5046c15ca9de19f6dc18488f8fb053b8da43eac533`.
  PHMSA updates the file over time, so this checksum identifies the exact
  version used. The adapter verifies it at load time.

**File format:** tab-separated text, UTF-8, Windows line endings, one header
row, 1,592 rows × 468 columns, about 4.2 MB.

## Observation and sampling

- **One row** is one incident report filed by a gas distribution operator
  under 49 CFR Part 191. `REPORT_NUMBER` is unique and serves as the row
  identifier.
- **Population.** Incidents on gas distribution systems (local utility mains,
  service lines, meters and regulators) that meet the federal reporting
  criteria, such as a death, an in-patient injury, or property damage above a
  threshold. Minor leaks are not reported.
- **Dependence.**
  - 225 operators file the reports. The ten largest file 33% of them, so rows
    from the same operator are not independent.
  - Reports cluster in space and time; for example, two West Virginia
    incidents share a timestamp on 23 June 2016, consistent with that month's
    floods.
- **Boundaries that matter.**
  - _Time._ Incidents run from January 2010 to July 2026, and 2026 is a partial
    year. A revised report form adds about 25 fields for reports filed from
    roughly 2020 onward; they are blank on older reports.
  - _Report status._ Operators file an original report and may supplement it.
    180 reports are not yet final and may still be revised.
  - _Commodity._ 1,504 reports involve natural gas, 25 involve propane,
    synthetic, or other gas, and 63 leave the commodity blank.

## Scope used in this project

| Filter                                                           | Reports removed | Remaining |
| ---------------------------------------------------------------- | --------------- | --------- |
| All reports                                                      | —               | 1,592     |
| Keep final reports only (`ORIGINAL FINAL`, `SUPPLEMENTAL FINAL`) | 180             | 1,412     |
| Keep natural gas or unspecified commodity                        | 21              | 1,391     |

Partitions by incident year: training 2010–2019 (977), validation 2020–2021
(189), final test 2022–2026 (225).

## Schema and measurement

**Identifier:** `REPORT_NUMBER`.

**Targets.**

- `CAUSE`, 8 categories, operator-assigned. Counts in scope: excavation damage
  485, other outside force 443, incorrect operation 100, natural force 96,
  pipe/weld/joint failure 91, other incident cause 85, equipment failure 58,
  corrosion 33.
- `PRPTY`, total estimated cost in U.S. dollars. It equals exactly the sum of
  the six `EST_COST_*` columns in every row. Median about $109,000, maximum
  $1.59 billion, 10 zero values. Modeled as `log(1 + PRPTY)`.

**Feature groups**, all known at initial report:

| Group                   | Columns                                                                                                   |
| ----------------------- | --------------------------------------------------------------------------------------------------------- |
| Time                    | `LOCAL_DATETIME` (month, weekday, and hour derived)                                                       |
| Location                | state, latitude/longitude, location type, incident area type, class location, crossing flags              |
| Facility                | system part involved, pipe material, installation year, pipe diameter, depth of cover, pipe facility type |
| Pressure                | normal, maximum operating, and incident pressure (psig); whether incident pressure exceeded the limit     |
| Release and consequence | release type, ignition, explosion, injuries, fatalities, evacuations                                      |

**Missing-value conventions.**

- Blank cells mean missing or not applicable.
- `UNKNOWN`, `N/A`, `NA` and `NONE` appear in otherwise numeric columns. For
  example, `INSTALLATION_YEAR` is `UNKNOWN` in 280 reports. These become
  missing values, with an "unknown" indicator where the unknown status may
  itself be informative.
- 154 checkbox columns (`*_IND`) contain only `YES` or blank, where blank
  means no.
- Most cause-specific sections are filled only for incidents of that cause; 60
  columns are completely empty and 316 are more than 90% empty.

**Units and coding.**

- Costs are in nominal U.S. dollars, not adjusted for inflation.
- Pressures are in psig, diameter in inches, depth of cover in inches.
- Dates are text in `M/D/YYYY H:MM` format, local time.
- ZIP codes are text; 186 are ZIP+4 and are truncated to 5 digits.
- `ONE_CALL_TICKET_NUM` was corrupted into scientific notation upstream and is
  not used.

**Leakage risks.**

- _Cause-specific sections._ Whether a section is filled reveals `CAUSE`.
  Excluded from all tasks.
- _Cost components._ The six `EST_COST_*` columns and `GAS_COST_IN_MCF` sum to,
  or contribute to, `PRPTY`. Excluded from cost regression.
- _Investigation fields._ Root cause, investigation status and drug testing
  are not known at initial report. Excluded.
- _Year._ Excluded as a feature because partitions are defined by year.

**Values needing review before modeling.**

- Pipe diameter or pressure recorded as 0.
- Installation year 1900, likely a placeholder.
- Depth of cover up to 840 inches.
- 39 reports where incident pressure exceeds maximum operating pressure,
  which are checked against the `ACCIDENT_PRESSURE` field before being
  treated as errors.

## Data access and privacy

- **Committed:** the adapter code, configuration, this card, and a fixture of
  about 50 rows in `data/fixtures/`. The fixture has every contact and personal
  field removed and covers edge cases: unknown values, zero cost, rare causes,
  and the shared-timestamp pair.
- **Local only:** the raw file, in `data/local/`, which Git ignores.
- **Personal fields dropped at ingestion:** names, titles, emails, telephone
  and fax numbers of report preparers, authorizers, and local contacts (12
  columns), plus operator street addresses. They are never committed, logged,
  or served.
- **Credentials:** none. CI runs entirely on the fixture.

## Representativeness and limitations

- **Thresholds.** Only incidents above federal reporting thresholds are
  included, so the data is not evidence about minor leaks or near-misses.
- **Self-reported labels.** Causes are assigned by the reporting operator, and
  the broad "other" categories absorb uncertain cases. Cost figures are
  operator estimates in nominal dollars.
- **Measurement change.** The 2020 form revision means newer reports describe
  incidents in more detail. Fields that exist only on the new form are not
  used.
- **Recent years.** The 2022–2026 test window is smaller than earlier windows
  and has fewer final reports, because recent incidents are still being
  finalized.
- **Operator concentration.** A few large operators dominate, so results may
  not transfer to small operators or to regions with few incidents.
- **Scope.** Distribution systems only. Gas transmission and gathering
  pipelines are reported separately and are out of scope.
