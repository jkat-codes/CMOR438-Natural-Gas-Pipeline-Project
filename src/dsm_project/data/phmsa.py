"""PHMSA gas distribution incident adapter.

Loads the processed incident table written by ``notebooks/00-acquisition.ipynb``.
One row is one incident report. The adapter keeps final reports whose commodity is
natural gas or unspecified, and declares two tasks: cause classification and
log-cost regression.

Features are limited to information available when an incident is first reported,
before any investigation. Cause-specific report sections, investigation findings,
cost components, operator identity, and calendar year are excluded. The reasoning
for each boundary is in ``docs/PRODUCT_CONTRACT.md``.
"""

from __future__ import annotations

import hashlib
from pathlib import Path


IDENTIFIER = "REPORT_NUMBER"
TIME_COLUMN = "LOCAL_DATETIME"
CAUSE_TARGET = "CAUSE"
COST_SOURCE = "PRPTY"
COST_TARGET = "log_cost"

# Final reports of natural gas incidents; a missing commodity counts as unspecified
KEPT_COMMODITIES: tuple[str, ...] = ("NATURAL GAS",)

# Computed from TIME_COLUMN in the adapter.
DERIVED_FEATURES: tuple[str, ...] = (
    "incident_month",
    "incident_weekday",
    "incident_hour",
)

# Known at initial notification. Grouped as in the product contract.
SOURCE_FEATURES: tuple[str, ...] = (
    # Location
    "LOCATION_STATE_ABBREVIATION",
    "LOCATION_LATITUDE",
    "LOCATION_LONGITUDE",
    "LOCATION_TYPE",
    "CLASS_LOCATION_TYPE",
    # Pipe and system
    "SYSTEM_PART_INVOLVED",
    "MATERIAL_INVOLVED",
    "INSTALLATION_YEAR",
    "installation_year_unknown",
    "PIPE_DIAMETER",
    "DEPTH_OF_COVER",
    "CROSSING",
    "BRIDGE_CROSSING_IND",
    "RAILROAD_CROSSING_IND",
    "ROAD_CROSSING_IND",
    "WATER_CROSSING_IND",
    # Pressure
    "NORMAL_PSIG",
    "MOP_PSIG",
    "ACCIDENT_PSIG",
    # Observed at the scene
    "RELEASE_TYPE",
    "IGNITE_IND",
    "EXPLODE_IND",
    "FATAL",
    "INJURE",
    "NUM_PUB_EVACUATED",
)

FEATURES: tuple[str, ...] = DERIVED_FEATURES + SOURCE_FEATURES

# Cause-specific report sections. An operator fills in only the section for the
# cause they reported, so any of these columns would reveal the label.
EXCLUDED_PREFIXES: tuple[str, ...] = (
    "NF_", "EX_", "OSF_", "PWJF_", "EQ_", "IO_", "RELATED_", "ROOT_CAUSE_",
)

REQUIRED_COLUMNS: tuple[str, ...] = (
    IDENTIFIER,
    TIME_COLUMN,
    CAUSE_TARGET,
    COST_SOURCE,
    "is_final",
    "COMMODITY_RELEASED_TYPE",
    *SOURCE_FEATURES,
)


def sha256_file(path: Path, chunk_size: int = 1 << 20) -> str:
    """Return the hex SHA-256 digest of a file, read in fixed-size chunks."""

    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()