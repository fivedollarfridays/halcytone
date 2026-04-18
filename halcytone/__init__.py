"""Halcytone — biofeedback sonification platform (monorepo).

Subpackages under `halcytone.*`:

- `halcytone.contracts`  — shared pydantic schemas, JSON Schema, SQL DDL (shipped v0.3.0).
- `halcytone.core`       — session state + wiring stub (shipped v0.3.0; real fusion
  logic lands v0.4.0).

Additional subpackages (sensors, audio, hud, breath, publish) are planned; see
`ROADMAP.md` for target versions.

The public contract surface is re-exported here so callers can write
``from halcytone import SignalPacket`` and treat submodule layout as an
implementation detail.
"""

from __future__ import annotations

from halcytone.contracts import (
    REQUIRED_SCHEMA_VERSION,
    RESERVED_STREAMS,
    SCHEMA_VERSION,
    SESSION_ID_REGEX,
    Annotation,
    Baseline,
    ContractError,
    MapperConfigUpdate,
    SessionId,
    SessionManifest,
    SessionStart,
    SessionStop,
    SessionSummary,
    SignalPacket,
    StateVector,
    StreamBaseline,
    StreamSpec,
    __contract_version__,
    check_contract_version,
    format_session_id,
    new_session_id,
    parse_session_id,
    read_ddl,
    validate_stream_roster,
)

__version__: str = "0.3.0"

__all__ = [
    "Annotation",
    "Baseline",
    "ContractError",
    "MapperConfigUpdate",
    "REQUIRED_SCHEMA_VERSION",
    "RESERVED_STREAMS",
    "SCHEMA_VERSION",
    "SESSION_ID_REGEX",
    "SessionId",
    "SessionManifest",
    "SessionStart",
    "SessionStop",
    "SessionSummary",
    "SignalPacket",
    "StateVector",
    "StreamBaseline",
    "StreamSpec",
    "__contract_version__",
    "__version__",
    "check_contract_version",
    "format_session_id",
    "new_session_id",
    "parse_session_id",
    "read_ddl",
    "validate_stream_roster",
]
