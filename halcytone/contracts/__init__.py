"""Top-level public surface for the `halcytone.contracts` subpackage.

Everything a consumer is allowed to depend on is re-exported here so that
callers can write ``from halcytone.contracts import SignalPacket`` (or the
monorepo shortcut ``from halcytone import SignalPacket``) and treat the
submodule layout as an implementation detail.

`__contract_version__` is the authoritative semver string for the contracts
surface and must stay in lockstep with the version declared in
``pyproject.toml`` (`tests/test_exports.py` enforces the invariant at test
time).
"""

from __future__ import annotations

from halcytone.contracts.baseline import Baseline, StreamBaseline
from halcytone.contracts.bundles.manifest import SessionManifest
from halcytone.contracts.drift import (
    ContractError,
    check_contract_version,
    validate_stream_roster,
)
from halcytone.contracts.session import (
    SESSION_ID_REGEX,
    Annotation,
    MapperConfigUpdate,
    SessionId,
    SessionStart,
    SessionStop,
    format_session_id,
    new_session_id,
    parse_session_id,
)
from halcytone.contracts.signals import RESERVED_STREAMS, SignalPacket, StreamSpec
from halcytone.contracts.state import StateVector
from halcytone.contracts.storage import (
    REQUIRED_SCHEMA_VERSION,
    SCHEMA_VERSION,
    read_ddl,
)
from halcytone.contracts.summary import SessionSummary

__contract_version__: str = "0.3.0"
__version__: str = __contract_version__

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
