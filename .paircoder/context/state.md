# Current State

> Last updated: 2026-04-18 (post-T3.7)

## Active Plan

**Plan:** `plan-2026-04-sprint-3-monorepo-consolidation` — Sprint 3 — halcytone monorepo consolidation
**Status:** In progress (T3.1 done in halcytone-contracts; T3.2+ run here)
**Current Sprint:** sprint-3
**Total Cx:** 28 across 11 tasks (P0 ×9, P1 ×2)
**Source backlog:** `plans/backlogs/backlog-sprint-3.md`

## Current Focus

Collapse `halcytone-contracts` + `halcytone-core` into this single public monorepo `halcytone` (Apache-2.0) with src-layout subpackages (`halcytone.contracts`, `halcytone.core`, plus placeholders for sensors/audio/hud/breath/publish). Pure structural work — no new functionality, no fusion logic, no breaking schema changes. Ships as **v0.3.0** of the unified package. The only "break" is the import-path rename (`halcytone_contracts` → `halcytone.contracts`); we're the only consumer so this is safe.

## Task Status

### Active Sprint — sprint-3 (monorepo consolidation)

| Task | Title | Cx | Pri | Wave | Status | Depends |
|------|-------|----|-----|------|--------|---------|
| T3.1 | Create `halcytone` repo + scaffold | 3 | P0 | 0 | ✓ done (in halcytone-contracts) | — |
| T3.2 | Migrate contracts source → `halcytone.contracts` | 4 | P0 | 1 | ✓ done | T3.1 |
| T3.3 | Port contracts tests + regen script | 3 | P0 | 2 | ✓ done | T3.2 |
| T3.4 | Migrate core source → `halcytone.core` | 3 | P0 | 2 | ✓ done | T3.2 |
| T3.5 | Port + expand core tests | 4 | P0 | 3 | ✓ done | T3.3, T3.4 |
| T3.6 | Unified CI workflow | 2 | P0 | 4 | ✓ done | T3.3, T3.5 |
| T3.7 | Unified CHANGELOG + ROADMAP | 2 | P0 | 4 | ✓ done | T3.5 |
| T3.8 | README rewrite | 2 | P0 | 2 | pending | T3.1 |
| T3.9 | Commit + push + open PR | 2 | P0 | 5 | pending | T3.6, T3.7, T3.8 |
| T3.10 | Post-merge: tag v0.3.0 + archive old repos | 2 | P1 | 6 | pending | T3.9 (merged) |
| T3.11 | Local cleanup | 1 | P1 | 7 | pending | T3.10 |

### Dependency Graph

```
Wave 0: T3.1 ✓ (scaffold — done in halcytone-contracts)
          ↓
Wave 1: T3.2 (contracts source — blocker)
          ↓
Wave 2: T3.3    T3.4    T3.8         (parallel — tests / core / README)
          ↓      ↓
Wave 3:        T3.5                   (core tests + wiring expansion)
                ↓
Wave 4: T3.6    T3.7                  (parallel — CI / docs)
                ↓
Wave 5: T3.9                          (commit + push + PR)
                ↓  (user merges)
Wave 6: T3.10                         (tag + archive)
                ↓
Wave 7: T3.11                         (local cleanup)
```

### Cut Order if Budget Overflows

T3.11 → T3.10. Both are post-merge housekeeping that can slip to a follow-up session. Never cut T3.2–T3.9 — each is load-bearing.

### Integration Points

- **T3.2 → every downstream task.** `halcytone.contracts` is the foundation. Rename misses cascade into red tests (T3.3) and import failures (T3.4).
- **T3.4 removes `_EXPECTED_CONTRACTS_VERSION` import-time check.** Monorepo = same-package drift is structurally impossible; the guard is dead code.
- **T3.5 folds in deferred T2.6–T2.8 coverage** — this sprint becomes the forcing function that proves the typed manifest is consumable from a real caller.
- **T3.9 → T3.10 cross-repo manual gate.** User merges, then tag + archive. No automation.

## What Was Just Done

### Session: 2026-04-18 — T3.7 Unified CHANGELOG + ROADMAP (Driver)

- Wrote real content for `CHANGELOG.md` (Keep-a-Changelog v1.1.0): `[Unreleased]` header, a `## [0.3.0] — 2026-04-18` section with `### Changed` / `### Added` / `### Migration` subsections, and historical `## [0.2.0]`, `## [0.1.1]`, `## [0.1.0]` sections each annotated `(halcytone-contracts, archived)`. The Migration block lists the codebase-wide import rewrite, the pin replacement (`halcytone-contracts`/`halcytone-core` git deps out → `halcytone @ git+...@v0.3.0` or `halcytone>=0.3,<0.4`), and the `check_contract_version("0.1.x"|"0.2.x")` hard-fail behavior.
- Wrote `ROADMAP.md` with 8 `## ` bands: v0.1.0, v0.1.1, v0.2.0 all `shipped (pre-consolidation)` with archived-repo pointers; v0.3.0 `shipped (this release, monorepo consolidation)` summarizing what T3.2–T3.6 landed; v0.4.0 narrowed to fusion logic (state machine, LSL ingest, 200 Hz StateVector emit, bundle writer, DDL bootstrapper); v0.5.0 to "second consumer" (sensors or audio, decide at v0.4.0 ship); v1.0.0 stability target; `## Out of scope` covering PyPI, git-history preservation, broadcast SaaS, and the now-moot sibling-repo paircoder template.
- Both files link the archived predecessor repos (`halcytone-contracts`, `halcytone-core`). Verified AC by grep: CHANGELOG 6 `## ` headings (≥5), ROADMAP 8 `## ` headings (≥7), "archived" appears 10× across the two files, no stale "7-repo fleet" / "halcytone-contracts as separate repo" language.

### Session: 2026-04-18 — T3.6 Unified CI workflow (Driver)

- Replaced the T3.1 stub `.github/workflows/ci.yml` with a production workflow modeled on `halcytone-contracts/.github/workflows/ci.yml`: three jobs (`lint`, `test`, `schema-drift`), push + PR triggers on `main`, concurrency group `ci-${{ github.ref }}` with `cancel-in-progress: true`.
- `lint`: `actions/checkout@v4` + `actions/setup-python@v5` (3.11, pip-cached on `pyproject.toml`) + `pip install ruff` + `ruff check .`.
- `test`: `fail-fast: false` matrix over Python 3.11/3.12/3.13, `pip install -e '.[dev]'` (single-quoted to survive zsh glob interpretation) + `pytest -q`. `[dev]` extras pull in `pytest`/`ruff`; base install would fail `pytest` on runners without them.
- `schema-drift`: setup-python 3.11, `pip install -e .`, `python scripts/regen_manifest_schema.py`, then `git diff --exit-code halcytone/contracts/bundles/manifest.schema.json` — fails the job if the committed schema is stale vs. the pydantic model.
- Gates: `yaml.safe_load` parses cleanly; jobs set == `{lint, test, schema-drift}`; concurrency group + cancel-in-progress present; test matrix == `[3.11, 3.12, 3.13]`; `fail-fast: false`; no `token:` / `ssh-key:` / `repository:` attributes on any `actions/checkout` step. Dry-run deferred — first real CI signal lands when T3.9 pushes the PR.

### Session: 2026-04-18 — T3.5 Port + expand core tests (Driver)

- Wrote `tests/test_wiring.py` by porting the 14 sprint-1 `halcytone-core/tests/test_wiring.py` tests with imports rewritten: `import halcytone_core` → `import halcytone.core`, `from halcytone_core.wiring` → `from halcytone.core.wiring`, `from halcytone_contracts import X` → `from halcytone import X`. Version assertion retargeted `"0.1.0"` → `"0.3.0"`.
- Reframed the obsolete `test_contract_version_pin_is_consistent` (which referenced the now-deleted `_EXPECTED_CONTRACTS_VERSION`) as `test_versions_in_monorepo_lockstep` — asserts `halcytone.__version__ == halcytone.core.__version__ == halcytone.__contract_version__`, the real post-monorepo invariant.
- Fixed the sprint-1 `test_session_manifest_validates_session_id` for the v0.2.0 typed-manifest shape: added `_example_baseline()`, `_example_summary()`, `_example_manifest_payload()` fixtures (3 reserved streams, all 9 summary numerics) and split into `accepts_valid` / `rejects_invalid`. Also split `test_storage_ddl_applies_to_in_memory_sqlite` into `creates_expected_tables` + `is_idempotent`.
- Folded in the 4 T2.6–T2.8 tests the canceled core-sprint-2 was supposed to land:
  - `test_session_manifest_full_typed_payload_round_trips` — full manifest (3-stream baseline + 9-field summary) dumps JSON and re-parses equal.
  - `test_baseline_rejects_unknown_stream_through_manifest` — `"not.a.real.stream"` in `Baseline.streams` raises `ValidationError` whose message names the offender.
  - `test_check_contract_version_raises_on_0_1_x_pin` — `check_contract_version("0.1.0")` → `ContractError` containing `"pre-1.0"`.
  - `test_check_contract_version_passes_on_current_version` — `check_contract_version("0.3.0")` is a no-op under `warnings.catch_warnings(simplefilter="error")`.
- Also added `test_public_surface_includes_v0_2_0_additions` to lock in T3.4's tuple expansion (`Baseline`, `StreamBaseline`, `SessionSummary` in `PUBLIC_SURFACE`).
- Gates: `pytest tests/test_wiring.py -v` → **21 passed**, full `pytest` → **357 passed** (336 contracts + 21 wiring; exceeds the ≥356 AC), `ruff check .` clean after auto-fix of import ordering, `bpsai-pair arch check tests/` clean, `grep halcytone_core\|halcytone_contracts tests/test_wiring.py` clean.

### Session: 2026-04-18 — T3.4 Migrate core source → `halcytone.core` (Driver)

- Wrote `halcytone/core/__init__.py` as the monorepo-native `halcytone.core` header: `__version__ = "0.3.0"`, module docstring rephrased to call out monorepo-implicit lockstep with `halcytone.contracts`. **Dropped** `_EXPECTED_CONTRACTS_VERSION` + the import-time `check_contract_version(...)` call — same-package drift is structurally impossible, the guard is dead code. The `check_contract_version` import is gone too.
- Wrote `halcytone/core/wiring.py` by porting `halcytone-core/halcytone_core/wiring.py`: imports from `halcytone.contracts` (not `halcytone_contracts`), docstring + `expected_streams()` doc refs updated to `halcytone.core` v0.3.0 / v0.4.0 timeline.
- Expanded `PUBLIC_SURFACE` tuple to include the v0.2.0 additions (`Baseline`, `StreamBaseline`, `SessionSummary`) alongside the original 16 entries — final size **19**, which the canceled core-sprint-2 was supposed to land.
- Gates: `from halcytone.core.wiring import PUBLIC_SURFACE` → size 19, `halcytone.core.__version__` → "0.3.0", `validate_publisher_roster(expected_streams())` passes, `bpsai-pair arch check halcytone/core/` clean, `ruff check .` clean, `pytest` → 336 passed unchanged (contracts tests unaffected; core tests land in T3.5). `grep -r halcytone_contracts\|_EXPECTED_CONTRACTS_VERSION halcytone/` → 0 matches.

### Session: 2026-04-18 — T3.3 Port contracts tests + regen script (Driver)

- Copied all 10 `test_*.py` files from `halcytone-contracts/tests/` → `tests/` (baseline, drift, exports, manifest, package, session, signals, state, storage, summary).
- Bulk-rewrote imports via scripted replace: `halcytone_contracts.X` → `halcytone.contracts.X`, `"halcytone_contracts"` → `"halcytone.contracts"` (importlib.resources calls), bare `halcytone_contracts` → `halcytone` (top-level package ref + `import halcytone_contracts as hc`).
- Fixed two special cases the bulk rewrite couldn't resolve: `tests/test_manifest.py` `_SCHEMA_PATH` filesystem path rebuilt to `_REPO_ROOT / "halcytone" / "contracts" / "bundles" / "manifest.schema.json"`; `tests/test_storage.py` `from halcytone import storage` corrected to `from halcytone.contracts import storage` (submodule access, not re-export).
- Copied `scripts/regen_manifest_schema.py` with `from halcytone.contracts.bundles.manifest import SessionManifest` and `_OUTPUT_PATH = _REPO_ROOT / "halcytone" / "contracts" / "bundles" / "manifest.schema.json"`.
- Gates: `pytest -q` → **336 passed**, `python scripts/regen_manifest_schema.py && git diff --exit-code` on schema → clean (regen idempotent), `ruff check .` clean, `bpsai-pair arch check tests/ scripts/` clean. `grep -r halcytone_contracts halcytone/ tests/ scripts/` → 0 matches.

### Session: 2026-04-18 — T3.2 Migrate contracts source → `halcytone.contracts` (Driver)

- Copied all 10 source files (`signals.py`, `state.py`, `session.py`, `storage.py`, `drift.py`, `baseline.py`, `summary.py`, `__init__.py`, `bundles/__init__.py`, `bundles/manifest.py`) and 2 data artifacts (`storage.sql`, `bundles/manifest.schema.json`) from `halcytone-contracts/halcytone_contracts/` into `halcytone/contracts/`.
- Rewrote every internal import `halcytone_contracts.X` → `halcytone.contracts.X` across the migrated source (baseline, bundles/__init__, bundles/manifest, state, storage, summary, drift, contracts/__init__) plus the embedded `halcytone_contracts.signals.RESERVED_STREAMS` doc reference in `baseline.py` docstring and `bundles/manifest.schema.json` description mirror. `grep -r halcytone_contracts halcytone/` → 0 matches.
- Updated `storage.py`: `resources.files("halcytone_contracts")` → `resources.files("halcytone.contracts")` so DDL loads from the renamed package; verified `read_ddl()` returns 1440 bytes.
- Bumped `halcytone/contracts/__init__.py` → `__contract_version__ = "0.3.0"` (preserves 25-name `__all__` parity with sprint-2 source, verified via set-diff vs. `halcytone_contracts.__all__`).
- Rewrote `halcytone/__init__.py` to re-export the full surface from `halcytone.contracts` with explicit imports + `__all__` list (not star-import). `from halcytone import SignalPacket, Baseline, SessionManifest, __contract_version__` → "0.3.0".
- `pyproject.toml` `[tool.setuptools.package-data]` added: `"halcytone.contracts" = ["*.sql"]`, `"halcytone.contracts.bundles" = ["*.json"]`.
- Gates: `bpsai-pair arch check halcytone/` clean, `ruff check .` clean, smoke-import `SignalPacket(sensor_id="x", stream="eeg.ch1", t_ns=1, values=[0.1], quality=0.9)` succeeds, `pip install -e .` reinstalls cleanly.

### Session: 2026-04-18 — T3.1 Create halcytone repo + scaffold (Driver, in halcytone-contracts)

- Created public repo `fivedollarfridays/halcytone` via `gh repo create --public`; cloned to `/home/kmasty/projects/halcytone/` (this directory).
- Scaffolded `pyproject.toml` (`halcytone@0.3.0`, Python ≥3.11, pydantic v2 + pyyaml, pytest + ruff dev extras, ruff line-length 100 + target py311, `include=["halcytone*"]`), src-layout skeleton (`halcytone/__init__.py` with `__version__ = "0.3.0"` + module docstring naming shipped vs. planned subpackages; empty `halcytone/contracts/__init__.py` + `halcytone/core/__init__.py` stubs), test harness (`tests/__init__.py`, `tests/conftest.py`).
- Top-level: `LICENSE` (Apache 2.0), `.editorconfig`, `.gitignore`, stub `README.md` / `CHANGELOG.md` / `ROADMAP.md`, stub `.github/workflows/ci.yml`.
- `bpsai-pair init --preset library` installed `.claude/`, `.paircoder/`, `CLAUDE.md`, `scripts/`. `AGENTS.md` written manually as a `.paircoder/` pointer.
- Verified: `pip install -e '.[dev]'` clean, `pytest` 0-tests-0-failures green, `ruff check .` clean, `bpsai-pair validate` passes.
- Initial commit `f2beda1` pushed to `origin/main`.
- Planning artifacts (plan yaml, task files T3.2–T3.11, backlog) copied from halcytone-contracts into this repo's `.paircoder/plans/`, `.paircoder/tasks/`, and `plans/backlogs/` so `/start-task T3.2` can run here.

## What's Next

1. **Wave 2 remaining:** T3.8 (README rewrite). T3.3 + T3.4 ✓ done.
2. **Wave 3:** T3.5 ✓ done (357-test suite green).
3. **Wave 4:** ✓ done (T3.6 + T3.7).
4. **Wave 5:** T3.9 (commit + push + open PR against `main`).
5. **Post-merge (manual):** T3.10 tags v0.3.0 + archives `halcytone-contracts` and `halcytone-core`; T3.11 `rm -rf`s the old local working copies.

## Blockers

None.

## Out of Scope (documented in backlog)

- Fusion logic in `halcytone.core` (v0.4.0).
- `halcytone-broadcast` (private SaaS — separate future repo).
- PyPI publishing (git dep stays the distribution model).
- New sensor adapters / audio / hud / publish logic (placeholders only).
- Paircoder template for sibling repos (moot in a monorepo).
- Preserving git history from the two predecessor repos (archived repos retain their own).

## Quick Commands

```bash
# Plan inspection
bpsai-pair plan show plan-2026-04-sprint-3-monorepo-consolidation
bpsai-pair task list --plan plan-2026-04-sprint-3-monorepo-consolidation

# Start next task
bpsai-pair task update T3.2 --status in_progress

# Complete (non-Trello)
bpsai-pair task update T3.X --status done

# Verify gates locally
pytest && ruff check .
python scripts/regen_manifest_schema.py && git diff --exit-code halcytone/contracts/bundles/manifest.schema.json

# Status
bpsai-pair status
```
