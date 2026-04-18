# Halcytone Roadmap

Scope for each release band. Dates are intentional omissions — milestones ship when the scope is covered, not by calendar.

This roadmap replaces the pre-consolidation roadmaps of the two predecessor repos, [halcytone-contracts](https://github.com/fivedollarfridays/halcytone-contracts) (archived) and [halcytone-core](https://github.com/fivedollarfridays/halcytone-core) (archived). v0.1.x and v0.2.0 shipped from those repos; v0.3.0 onward ships from this monorepo.

## v0.1.0 — shipped (pre-consolidation)

Shipped from the archived [halcytone-contracts](https://github.com/fivedollarfridays/halcytone-contracts) repo.

- `SignalPacket`, `StreamSpec`, `RESERVED_STREAMS` registry.
- `StateVector` flat fused-frame model.
- Control messages + canonical session-id format.
- SQLite DDL + loader (`read_ddl`, `SCHEMA_VERSION`).
- `SessionManifest` + generated `manifest.schema.json`.
- Drift guardrails: `__contract_version__`, `REQUIRED_SCHEMA_VERSION`, `validate_stream_roster`, `check_contract_version`, `ContractError`.
- CI: ruff + pytest matrix (3.11/3.12/3.13) + manifest schema drift check.

## v0.1.1 — shipped (pre-consolidation)

Shipped from the archived [halcytone-contracts](https://github.com/fivedollarfridays/halcytone-contracts) repo.

- Relicensed to Apache-2.0 (LICENSE + OSI classifier). No schema or API changes.
- `halcytone-contracts` and `halcytone-core` repos made public on GitHub.

## v0.2.0 — shipped (pre-consolidation, breaking under 0.x)

Shipped from the archived [halcytone-contracts](https://github.com/fivedollarfridays/halcytone-contracts) repo.

- Typed `Baseline` + `StreamBaseline` models; `Baseline.streams` keys validated against `RESERVED_STREAMS`.
- Versioned `SessionSummary` model (first field `summary_schema_version: int`, default 1).
- `SessionManifest` rewired: `baselines: Baseline`, `summary: SessionSummary` (both were `dict[str, float]`).
- Regenerated `manifest.schema.json` with `$defs` block; AgentGrounds and any TypeScript consumer gets typed shapes at the cross-language boundary.
- Public surface grew from 21 to 24 names: added `Baseline`, `StreamBaseline`, `SessionSummary`.
- `check_contract_version("0.1.x")` became a hard-fail at runtime.

## v0.3.0 — shipped (this release, monorepo consolidation)

**Goal:** collapse `halcytone-contracts` + `halcytone-core` into a single public monorepo so the two-repo coordination overhead disappears.

- `halcytone` package with src-layout subpackages: `halcytone.contracts` (was `halcytone_contracts`) and `halcytone.core` (was `halcytone_core`).
- Top-level re-exports preserve the v0.2.0 24-name public surface unchanged — `from halcytone import X` works for every symbol that used to live at `halcytone_contracts.X`.
- Cross-repo `_EXPECTED_CONTRACTS_VERSION` drift guard in `halcytone.core` **deleted** — same-package drift is structurally impossible in a monorepo.
- `halcytone.core.wiring.PUBLIC_SURFACE` expanded to 19 entries (added `Baseline`, `StreamBaseline`, `SessionSummary`) — the typed-manifest coverage the canceled core-sprint-2 was supposed to land.
- Unified CI (`lint` + `test` matrix over 3.11/3.12/3.13 + `schema-drift`) on `.github/workflows/ci.yml`.
- Test suite: 357 passing (336 contracts + 21 wiring). Every entry in `PUBLIC_SURFACE` proven importable from a real caller.
- **Migration:** see `CHANGELOG.md#migration` — drop the two `git+...` deps, adopt `halcytone>=0.3,<0.4`, run a codebase-wide `halcytone_contracts` / `halcytone_core` → `halcytone` rewrite.

## v0.4.0 — fusion logic (next minor, breaking allowed under 0.x)

**Goal:** make `halcytone.core` a working consumer of the contracts surface, not just a smoke-test wiring stub.

- Session state machine: `Preflight` → `Baseline` → `Active` → `Teardown` transitions driven by `SessionStart` / `SessionStop` control messages.
- LSL ingest layer — `halcytone.core` subscribes to sensor streams advertised by the roster and demarshals to `SignalPacket`.
- Fusion layer emitting `StateVector` at 200 Hz (the per-tick model's target cadence).
- Bundle writer — serialize the typed `SessionManifest` + `state.jsonl` stream into `~/halcytone/sessions/{session_id}/` once `SessionStop` fires.
- DDL bootstrapper — apply `read_ddl()` + seed `SCHEMA_VERSION` into the `meta` table on first launch.
- May trigger a contracts-surface bump if fusion surfaces an unmet need (e.g. a derived-stream registry, unit annotations on `StreamSpec`).

## v0.5.0 — second consumer

**Goal:** prove the contracts surface is consumable from a second real caller. Exact identity decided at v0.4.0 ship.

- Option A: `halcytone.sensors` — LSL adapters for Muse/Ganglion EEG, Emotibit PPG/EDA/IMU, StemoScope breath; plus a deterministic simulator for CI.
- Option B: `halcytone.audio` — parameter mapper + synthesis engine that consumes `StateVector` at 200 Hz and emits audio.
- Whichever lands, its public surface comes back through `halcytone` top-level re-exports so downstream callers never need to know which subpackage owns what.

## v1.0.0 — stability target

**Goal:** freeze the v1 contract. After 1.0, minor bumps are guaranteed additive-only; breaking changes require a major bump.

- All downstream consumers running against the candidate (private `halcytone-broadcast` SaaS + at least one open consumer).
- No reserved-stream churn, no `StateVector` field churn, and no `SessionManifest` shape churn for at least one full release cycle.
- Long-term pin recommendation switches from `halcytone>=0.3,<0.4` to `halcytone>=1.0,<2.0`.
- `check_contract_version` policy relaxes: `≥1.0` minor mismatch becomes `warnings.warn(UserWarning)`, not `ContractError`.

## Out of scope

- **PyPI publishing.** Git-dep stays the distribution model until v1.0.0; no plan to publish earlier. Downstream consumers pin to a tag.
- **Preserving git history from the predecessor repos.** The archived `halcytone-contracts` and `halcytone-core` repos retain their own history; the v0.3.0 initial commit here is the new root.
- **`halcytone-broadcast` (private SaaS).** Separate future repo, separately licensed. Not in this roadmap.
- **Paircoder template for sibling repos.** Moot in a monorepo — the scaffold the old roadmap promised is obsolete.
