"""Contract-wiring smoke tests — prove `halcytone.contracts` v0.3.0 is consumable.

These are not unit tests of `halcytone.core` fusion behavior (there is none
yet — that lands in v0.4.0). They assert that every contract surface the
README promises is reachable from a real downstream caller and that the
drift-detection wiring actually raises when it should. If these break, the
contract has drifted from what `halcytone.core` was built against.

Wave-3 expansion (T2.6–T2.8 folded in): a full typed `SessionManifest`
payload round-trips through JSON; `Baseline` rejects unknown stream keys
through the manifest; `check_contract_version` hard-fails on a pre-1.0
pin and no-ops on the current version.
"""

from __future__ import annotations

import json
import sqlite3
import warnings
from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError

import halcytone
import halcytone.core
from halcytone.core.wiring import (
    PUBLIC_SURFACE,
    expected_streams,
    validate_publisher_roster,
)

# ---------------------------------------------------------------------------
# Fixtures: full typed SessionManifest payload
# ---------------------------------------------------------------------------

_EXAMPLE_ID = "20260417-143022-k7m2"
_STARTED = datetime(2026, 4, 17, 14, 30, 22, tzinfo=UTC)
_ENDED = datetime(2026, 4, 17, 15, 2, 47, tzinfo=UTC)


def _example_baseline() -> dict[str, Any]:
    return {
        "streams": {
            "hrv.rmssd": {"mean": 48.3, "stddev": 4.2, "sample_count": 30},
            "breath.rate": {"mean": 6.2, "stddev": 0.8, "sample_count": 60},
            "eda": {"mean": 2.1, "stddev": 0.3, "sample_count": 60},
        },
        "duration_s": 60,
        "captured_at": _STARTED,
    }


def _example_summary() -> dict[str, Any]:
    return {
        "summary_schema_version": 1,
        "mean_hr": 62.1,
        "mean_hrv_rmssd": 48.3,
        "mean_breath_rate": 6.2,
        "mean_breath_depth": 0.7,
        "mean_eeg_alpha": 0.35,
        "mean_eeg_theta": 0.25,
        "mean_overall_presence": 0.72,
        "peak_heart_breath_coherence": 0.68,
        "total_annotations": 3,
    }


def _example_manifest_payload(*, ended_at: datetime | None = _ENDED) -> dict[str, Any]:
    return {
        "session_id": _EXAMPLE_ID,
        "started_at": _STARTED,
        "ended_at": ended_at,
        "duration_s": 1945,
        "sensors": ["ganglion-01", "emotibit-01", "stemoscope-01"],
        "baselines": _example_baseline(),
        "summary": _example_summary(),
        "artifacts": {
            "video": "video.mp4",
            "audio": "audio.wav",
            "signals": "signals.xdf",
            "state": "state.jsonl",
        },
    }


# ---------------------------------------------------------------------------
# Package identity + version lockstep
# ---------------------------------------------------------------------------


def test_core_version_is_0_3_0() -> None:
    assert isinstance(halcytone.core.__version__, str)
    assert halcytone.core.__version__ == "0.3.0"


def test_versions_in_monorepo_lockstep() -> None:
    # Post-monorepo invariant: top-level package, core subpackage, and the
    # contracts version all advance together. The old per-repo drift guard
    # is gone — this test replaces it.
    assert halcytone.__version__ == halcytone.core.__version__
    assert halcytone.__version__ == halcytone.__contract_version__


# ---------------------------------------------------------------------------
# PUBLIC_SURFACE
# ---------------------------------------------------------------------------


def test_public_surface_is_non_empty() -> None:
    assert len(PUBLIC_SURFACE) > 0


def test_every_public_surface_entry_is_truthy() -> None:
    for entry in PUBLIC_SURFACE:
        assert entry is not None


def test_public_surface_includes_v0_2_0_additions() -> None:
    # T3.4 expanded PUBLIC_SURFACE to include the v0.2.0 typed-manifest
    # additions the canceled core-sprint-2 was supposed to land.
    from halcytone import Baseline, SessionSummary, StreamBaseline

    assert Baseline in PUBLIC_SURFACE
    assert StreamBaseline in PUBLIC_SURFACE
    assert SessionSummary in PUBLIC_SURFACE


# ---------------------------------------------------------------------------
# Contract surfaces the README promises
# ---------------------------------------------------------------------------


def test_signal_packet_constructible() -> None:
    from halcytone import SignalPacket

    pkt = SignalPacket(
        sensor_id="ganglion-01",
        stream="eeg.ch1",
        t_ns=1_700_000_000_000_000_000,
        values=[0.1, 0.2, 0.3],
        quality=0.9,
    )
    assert pkt.stream == "eeg.ch1"
    round_tripped = SignalPacket.model_validate_json(pkt.model_dump_json())
    assert round_tripped == pkt


def test_state_vector_constructible_with_valid_session_id() -> None:
    from halcytone import StateVector, new_session_id

    sid = new_session_id()
    sv = StateVector(
        t_ns=1,
        session_id=sid,
        breath_phase=0.5,
        breath_rate=6.0,
        breath_depth=0.6,
        breath_quality=0.9,
        heart_rate=62.0,
        hrv_rmssd=48.0,
        hrv_quality=0.9,
        eda_level=3.0,
        eda_phasic=0.1,
        eeg_alpha=0.3,
        eeg_theta=0.2,
        eeg_beta=0.3,
        eeg_delta=0.1,
        eeg_gamma=0.1,
        eeg_quality=0.9,
        heart_breath_coherence=0.5,
        overall_presence=0.7,
    )
    assert sv.session_id == sid


def test_session_id_roundtrip_via_contracts_helpers() -> None:
    from halcytone import format_session_id, new_session_id, parse_session_id

    sid = new_session_id()
    dt, slug = parse_session_id(sid)
    assert isinstance(dt, datetime)
    assert len(slug) == 4
    assert format_session_id(dt, slug) == sid


def test_session_start_payload_roundtrips_as_json() -> None:
    from halcytone import SessionStart, new_session_id

    msg = SessionStart(session_id=new_session_id(), config={"sample_rate": 200})
    payload = msg.model_dump_json()
    parsed = SessionStart.model_validate_json(payload)
    assert parsed == msg
    assert json.loads(payload)["config"]["sample_rate"] == 200


# ---------------------------------------------------------------------------
# Roster + reserved streams
# ---------------------------------------------------------------------------


def test_reserved_streams_covers_core_requirements() -> None:
    from halcytone import RESERVED_STREAMS

    for name in expected_streams():
        assert name in RESERVED_STREAMS, f"{name!r} missing from RESERVED_STREAMS"


def test_validate_publisher_roster_passes_when_roster_complete() -> None:
    published = list(expected_streams()) + ["extra.stream"]
    assert validate_publisher_roster(published) is None


def test_validate_publisher_roster_raises_on_missing_stream() -> None:
    from halcytone import ContractError

    published = [s for s in expected_streams() if s != "ppg"]
    with pytest.raises(ContractError) as exc_info:
        validate_publisher_roster(published)
    assert "ppg" in str(exc_info.value)


# ---------------------------------------------------------------------------
# SessionManifest — validation + full round-trip (T2.6–T2.8 expansion)
# ---------------------------------------------------------------------------


def test_session_manifest_accepts_valid_session_id() -> None:
    from halcytone import SessionManifest

    manifest = SessionManifest(**_example_manifest_payload())
    assert manifest.session_id == _EXAMPLE_ID


def test_session_manifest_rejects_invalid_session_id() -> None:
    from halcytone import SessionManifest

    payload = _example_manifest_payload()
    payload["session_id"] = "not-a-session-id"
    with pytest.raises(ValidationError):
        SessionManifest(**payload)


def test_session_manifest_full_typed_payload_round_trips() -> None:
    # Folded in from T2.6: prove the typed manifest (Baseline + SessionSummary
    # + artifacts) survives a full JSON round-trip, not just construction.
    from halcytone import SessionManifest

    manifest = SessionManifest(**_example_manifest_payload())

    # Baseline carries ≥3 streams with real reserved names.
    assert set(manifest.baselines.streams) >= {"hrv.rmssd", "breath.rate", "eda"}
    # SessionSummary carries every numeric field plus schema version.
    assert manifest.summary.summary_schema_version == 1
    assert manifest.summary.total_annotations == 3

    payload = manifest.model_dump_json()
    round_tripped = SessionManifest.model_validate_json(payload)
    assert round_tripped == manifest


def test_baseline_rejects_unknown_stream_through_manifest() -> None:
    # Folded in from T2.7: a Baseline dict key outside RESERVED_STREAMS
    # must fail at manifest validation, and the error must name the
    # offending key so operators can diff rosters.
    from halcytone import SessionManifest

    payload = _example_manifest_payload()
    payload["baselines"]["streams"]["not.a.real.stream"] = {
        "mean": 1.0,
        "stddev": 0.1,
        "sample_count": 10,
    }
    with pytest.raises(ValidationError) as exc_info:
        SessionManifest(**payload)
    assert "not.a.real.stream" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Storage DDL
# ---------------------------------------------------------------------------


def test_storage_ddl_creates_expected_tables() -> None:
    from halcytone import read_ddl

    ddl = read_ddl()
    assert isinstance(ddl, str) and len(ddl) > 0
    with sqlite3.connect(":memory:") as conn:
        conn.executescript(ddl)
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = {row[0] for row in cursor.fetchall()}
    for expected in ("sessions", "baselines", "annotations", "state_summaries", "meta"):
        assert expected in tables, f"DDL missing expected table {expected!r}"


def test_storage_ddl_is_idempotent() -> None:
    from halcytone import read_ddl

    ddl = read_ddl()
    with sqlite3.connect(":memory:") as conn:
        conn.executescript(ddl)
        conn.executescript(ddl)  # must not raise on re-apply


def test_required_schema_version_matches_contracts() -> None:
    from halcytone import REQUIRED_SCHEMA_VERSION, SCHEMA_VERSION

    assert REQUIRED_SCHEMA_VERSION == SCHEMA_VERSION
    assert isinstance(REQUIRED_SCHEMA_VERSION, int)


# ---------------------------------------------------------------------------
# check_contract_version — drift policy (T2.8 expansion)
# ---------------------------------------------------------------------------


def test_check_contract_version_raises_on_0_1_x_pin() -> None:
    # Folded in from T2.8: a caller pinned to 0.1.x on a 0.x publisher
    # hits the pre-1.0 minor-mismatch branch, which is a hard failure
    # by semver §4.
    from halcytone import ContractError, check_contract_version

    with pytest.raises(ContractError) as exc_info:
        check_contract_version("0.1.0")
    assert "pre-1.0" in str(exc_info.value)


def test_check_contract_version_passes_on_current_version() -> None:
    from halcytone import check_contract_version

    with warnings.catch_warnings():
        warnings.simplefilter("error")  # any warning → raise
        assert check_contract_version("0.3.0") is None
