# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) with the 0.x sharpening documented in the [Versioning](README.md#versioning) section of the README (minor bumps on 0.x are treated as breaking).

## [Unreleased]

## [0.3.0] — 2026-04-18

### Changed

- **Structural: monorepo consolidation.** The two predecessor repos `halcytone-contracts` and `halcytone-core` are folded into this single `halcytone` package with subpackages `halcytone.contracts` (was `halcytone_contracts`) and `halcytone.core` (was `halcytone_core`). Both predecessors are now [archived](#pre-consolidation-halcytone-contracts). No functional change vs. the `halcytone-contracts` v0.2.0 surface and the `halcytone-core` v0.1.0 surface combined — every public symbol still resolves at the same name, only the import path changes.
- **Breaking:** Import path rename. `from halcytone_contracts import X` → `from halcytone import X` (or `from halcytone.contracts import X` for submodule access). `from halcytone_core.wiring import PUBLIC_SURFACE` → `from halcytone.core.wiring import PUBLIC_SURFACE`. The 25-entry `__all__` surface (24 documented names + the `__version__` legacy alias) is unchanged.
- **Removed:** the cross-repo `_EXPECTED_CONTRACTS_VERSION` + import-time `check_contract_version(...)` dance in `halcytone.core`. Same-package drift is structurally impossible inside a monorepo, so the guard is dead code. The `check_contract_version` helper itself is preserved on the contracts surface for future cross-package consumers.
- `__contract_version__` bumped `0.2.0` → `0.3.0`. Under the 0.x sharpened policy, `check_contract_version("0.1.x")` and `check_contract_version("0.2.x")` now both **hard-fail** against v0.3.0 — re-pin before upgrading.
- `halcytone.core.wiring.PUBLIC_SURFACE` expanded to 19 entries: the original 16 plus `Baseline`, `StreamBaseline`, `SessionSummary` (the v0.2.0 typed-manifest additions the canceled core-sprint-2 was supposed to land). Tests prove every entry is importable.

### Added

- Nothing new functionally. The documented 24-name public surface is unchanged from `halcytone-contracts` v0.2.0.
- Folded-in test coverage from the canceled core-sprint-2: full-payload `SessionManifest` JSON round-trip, unknown-stream rejection through the manifest, and assertions on the `check_contract_version` 0.x policy. Total suite is now 357 tests (336 contracts + 21 wiring).

### Migration

Consumers pinned to `halcytone-contracts>=0.2,<0.3` (or `halcytone-core`) must migrate to the new package:

1. **Drop** any `halcytone-contracts @ git+...` and `halcytone-core @ git+...` dep lines from `pyproject.toml` / `requirements.txt`.
2. **Add** `halcytone @ git+https://github.com/fivedollarfridays/halcytone@v0.3.0` (or `halcytone>=0.3,<0.4` once published).
3. **Rewrite imports** with a codebase-wide replace:
   - `from halcytone_contracts import X` → `from halcytone import X`
   - `from halcytone_contracts.Y import X` → `from halcytone.contracts.Y import X`
   - `from halcytone_core import X` → `from halcytone.core import X`
   - `from halcytone_core.wiring import X` → `from halcytone.core.wiring import X`
4. **Delete** any remaining `_EXPECTED_CONTRACTS_VERSION` constants and their import-time `check_contract_version(...)` calls — the monorepo makes them dead code.

Under the 0.x sharpened semver policy, `check_contract_version("0.1.x")` and `check_contract_version("0.2.x")` both raise `ContractError` against v0.3.0, so a stale pin fails loudly at import time rather than drifting silently.

## Pre-consolidation (halcytone-contracts)

The sections below document versions shipped from the original [halcytone-contracts](https://github.com/fivedollarfridays/halcytone-contracts) repo (now archived). `halcytone-core` v0.1.0 shipped in parallel from the [halcytone-core](https://github.com/fivedollarfridays/halcytone-core) repo (also archived) and carried a single stub release with no independent changelog — its history is subsumed by the v0.3.0 consolidation notes above.

## [0.2.0] — 2026-04-18 (halcytone-contracts, archived)

### Changed

- **Breaking:** `SessionManifest.baselines` changes type from `dict[str, float]` to `Baseline` (a pydantic model with per-stream mean/stddev/sample_count, capture window, and stream-name validation against `RESERVED_STREAMS`). The previous free-form dict shape no longer validates.
- **Breaking:** `SessionManifest.summary` changes type from `dict[str, float]` to `SessionSummary` (a pydantic model with `summary_schema_version: int` plus nine typed aggregate fields, five of them range-bounded to `[0, 1]`). The previous free-form dict shape no longer validates.
- `manifest.schema.json` regenerated — the mirror now carries `$defs` for `Baseline`, `StreamBaseline`, and `SessionSummary` with the manifest `baselines` / `summary` properties as `$ref`s.
- Bumped `__contract_version__` to `0.2.0`. Under the 0.x sharpened semver policy, `check_contract_version("0.1.x")` hard-fails on any consumer still pinned to 0.1.

### Added

- `halcytone_contracts.baseline` — `Baseline` + `StreamBaseline` pydantic v2 models with reserved-stream key validation and `duration_s ≥ 1`, `stddev ≥ 0`, `sample_count ≥ 1` bounds.
- `halcytone_contracts.summary` — `SessionSummary` pydantic v2 model with `summary_schema_version: int = Field(default=1, ge=1)` for shape evolution.
- Top-level exports grew from 21 to 24 names: added `Baseline`, `StreamBaseline`, `SessionSummary`.

## [0.1.1] — 2026-04-17 (halcytone-contracts, archived)

### Changed

- Relicensed from `Proprietary` to `Apache-2.0`. Added `LICENSE` file + OSI classifier. The contract surface, wire format, and SQL DDL are open under Apache 2.0.
- Bumped `__contract_version__` to `0.1.1`. No schema or API changes — licensing-only patch.

## [0.1.0] — 2026-04-17 (halcytone-contracts, archived)

### Added

- `halcytone_contracts.signals` — `SignalPacket` pydantic v2 model, `StreamSpec` frozen dataclass, `RESERVED_STREAMS` registry covering EEG raw + band powers, PPG, HRV, EDA, skin temp, IMU, breath.
- `halcytone_contracts.state` — `StateVector` flat per-tick fused-frame model with `[0, 1]` validation on every `*_quality` and normalized field.
- `halcytone_contracts.session` — `SessionStart`, `SessionStop`, `Annotation`, `MapperConfigUpdate` control-message models; `SessionId` validated alias; `SESSION_ID_REGEX`; `format_session_id` / `parse_session_id` / `new_session_id` helpers.
- `halcytone_contracts.storage` + `storage.sql` — raw DDL for `sessions`, `baselines`, `annotations`, `state_summaries`, `meta` tables (idempotent via `CREATE TABLE IF NOT EXISTS`), `read_ddl()` loader, `SCHEMA_VERSION` constant.
- `halcytone_contracts.bundles.manifest` — `SessionManifest` pydantic v2 model + generated `manifest.schema.json` mirror.
- `halcytone_contracts.drift` — `ContractError`, `validate_stream_roster`, `check_contract_version` with the 0.x-sharpened semver policy.
- `scripts/regen_manifest_schema.py`, GitHub Actions CI (ruff + pytest matrix + manifest-schema-drift check), `README.md`, `ROADMAP.md`, and this CHANGELOG.

[Unreleased]: https://github.com/fivedollarfridays/halcytone/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/fivedollarfridays/halcytone/releases/tag/v0.3.0
[0.2.0]: https://github.com/fivedollarfridays/halcytone-contracts/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/fivedollarfridays/halcytone-contracts/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/fivedollarfridays/halcytone-contracts/releases/tag/v0.1.0
