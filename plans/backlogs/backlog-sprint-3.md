# Sprint 3 Backlog — `halcytone` monorepo consolidation

## Overview

Collapse `halcytone-contracts` and `halcytone-core` into a single public monorepo `halcytone` (Apache-2.0) with src-layout subpackages (`halcytone.contracts`, `halcytone.core`, plus placeholders for sensors/audio/hud/breath/publish). Pure structural work — no new functionality, no fusion logic, no breaking schema changes. Ships as **v0.3.0** of the unified package. The only "break" is the import-path rename (`halcytone_contracts` → `halcytone.contracts`); we're the only consumer so this is safe.

**Why now:**
- Cross-repo tag/merge/pin ceremony costs more than it returns at one dev + one consumer scale.
- 0.x sharpened `check_contract_version` already biting — halcytone-core's test suite currently fails at import because contracts is at v0.2.0 but core still pins `_EXPECTED_CONTRACTS_VERSION = "0.1.1"`. Monorepo makes this drift structurally impossible.
- `halcytone-broadcast` (private SaaS) stays a future separate repo. Only the open/private license split survives long-term.

**Execution note (cross-repo):** T3.1 creates the new `halcytone` repo on GitHub + local scaffold. Everything from T3.2 onward writes into that new repo. If running via `/start-task` (rather than engage), the per-task bookkeeping will need to move into the new repo's `.paircoder/` after T3.1 completes — expect a small handoff between T3.1 and T3.2. Engage can't cross-repo; the first reliable engage point is inside the new repo after T3.1 lands.

**Stack:** Python 3.11+, pydantic v2, pyyaml, pytest, ruff, Apache-2.0. Unchanged from sprints 1 & 2.

## Phase 1: Bootstrap (Wave 0)

### T3.1 — Create `halcytone` repo + scaffold | Cx: 3 | P0

**Description:** Create the new public `halcytone` repo on GitHub under `fivedollarfridays`. Locally scaffold the monorepo at `/home/kmasty/projects/halcytone/`: `pyproject.toml` with single `halcytone` package declaration (Python ≥3.11, pydantic v2 + pyyaml runtime deps, pytest + ruff dev extras), src-layout skeleton (`halcytone/__init__.py` with `__version__ = "0.3.0"`, empty `halcytone/contracts/__init__.py`, empty `halcytone/core/__init__.py`), test harness (`tests/__init__.py`, `tests/conftest.py`), Apache-2.0 `LICENSE` file, `.gitignore` + `.editorconfig`, stub `README.md`/`CHANGELOG.md`/`ROADMAP.md` (T3.7 and T3.8 fill in real content), stub `.github/workflows/ci.yml` (T3.6 fills in jobs), paircoder + Claude scaffolding via `bpsai-pair init --preset library`, and the repo-level governance files (`AGENTS.md`, `CLAUDE.md`). Initial commit on `main`; repo is empty of functionality but installable.

**AC:**
- [ ] Repo created at `github.com/fivedollarfridays/halcytone` — public, Apache-2.0, default branch `main`
- [ ] `/home/kmasty/projects/halcytone/` initialized as a git clone of the new repo
- [ ] `pyproject.toml` declares `halcytone` package, Python ≥3.11, pydantic v2 + pyyaml runtime deps, pytest + ruff dev extras, OSI Apache classifier, version 0.3.0
- [ ] src-layout skeleton exists: `halcytone/__init__.py` (`__version__: str = "0.3.0"`), `halcytone/contracts/__init__.py` (empty stub), `halcytone/core/__init__.py` (empty stub)
- [ ] `tests/__init__.py` and `tests/conftest.py` exist
- [ ] `LICENSE` file (Apache 2.0 full text), `.gitignore` (Python artifacts), `.editorconfig`
- [ ] `README.md`, `CHANGELOG.md`, `ROADMAP.md` stubs exist (single-line placeholder — real content in T3.7 / T3.8)
- [ ] `.github/workflows/ci.yml` stub exists (T3.6 fills in)
- [ ] `bpsai-pair init --preset library` run; `.claude/`, `.paircoder/`, `CLAUDE.md`, `AGENTS.md`, `scripts/` all present; `bpsai-pair validate` passes
- [ ] `pip install -e .[dev]` succeeds in a clean venv
- [ ] `pytest` runs green (0 tests, 0 failures)
- [ ] `ruff check .` clean
- [ ] Initial commit pushed to `origin/main`

**Depends on:** none

---

## Phase 2: Migrate source (Wave 1)

### T3.2 — Migrate contracts source → `halcytone.contracts` | Cx: 4 | P0

**Description:** Copy all 10 `halcytone_contracts` source files (`signals.py`, `state.py`, `session.py`, `storage.py`, `drift.py`, `baseline.py`, `summary.py`, `__init__.py`, and `bundles/{__init__.py, manifest.py}`) plus the two data artifacts (`storage.sql`, `bundles/manifest.schema.json`) into `halcytone/contracts/`. Rewrite every internal import from `halcytone_contracts.X` to `halcytone.contracts.X`. Preserve the 24-name documented public surface (`Baseline`, `StreamBaseline`, `SessionSummary`, `SignalPacket`, etc.). Update `halcytone/__init__.py` to re-export the full public surface at the top level so `from halcytone import SignalPacket, SessionManifest` works. Update `pyproject.toml` `package-data` entries so `storage.sql` and `manifest.schema.json` ship inside the installed package.

**AC:**
- [ ] 10 source files present in `halcytone/contracts/` (+ `halcytone/contracts/bundles/`)
- [ ] Every `from halcytone_contracts.X import Y` rewritten to `from halcytone.contracts.X import Y` (source-wide grep = 0 matches for old path)
- [ ] `halcytone/contracts/__init__.py` exports the same 24 names as sprint-2's `halcytone_contracts/__init__.py`
- [ ] `halcytone/__init__.py` re-exports the 24-name surface via `from halcytone.contracts import *` + explicit `__all__`
- [ ] `storage.sql` copied to `halcytone/contracts/storage.sql`; `read_ddl()` works via `importlib.resources` for the new path
- [ ] `manifest.schema.json` copied to `halcytone/contracts/bundles/manifest.schema.json`
- [ ] `pyproject.toml` `[tool.setuptools.package-data]` updated: `halcytone.contracts = ["*.sql"]`, `"halcytone.contracts.bundles" = ["*.json"]`
- [ ] `__contract_version__: str = "0.3.0"` in `halcytone/contracts/__init__.py` (bumped from 0.2.0 to reflect the unified release)
- [ ] `bpsai-pair arch check halcytone/contracts/` reports no violations
- [ ] `from halcytone import SignalPacket; SignalPacket(sensor_id="x", stream="eeg.ch1", t_ns=1, values=[0.1], quality=0.9)` smoke-imports without error

**Depends on:** T3.1

---

## Phase 3: Migrate consumers + tests (Wave 2, parallel)

### T3.3 — Port contracts tests + regen script | Cx: 3 | P0

**Description:** Copy all 10 test files from `halcytone-contracts/tests/` into the new repo's `tests/` directory: `test_signals.py`, `test_state.py`, `test_session.py`, `test_storage.py`, `test_drift.py`, `test_manifest.py`, `test_baseline.py`, `test_summary.py`, `test_exports.py`, `test_package.py`. Rewrite all imports: `halcytone_contracts.*` → `halcytone.contracts.*`, and the handful of `import halcytone_contracts as hc` → `import halcytone as hc` (since `halcytone` is the new top-level). Copy `scripts/regen_manifest_schema.py` and update its import from `halcytone_contracts.bundles.manifest` to `halcytone.contracts.bundles.manifest`. Full suite must pass unchanged test-count — this is a pure port, no coverage change.

**AC:**
- [ ] 10 test files copied to `tests/` under the new repo
- [ ] Every `from halcytone_contracts.X` rewritten to `from halcytone.contracts.X` (grep = 0 matches)
- [ ] Every `import halcytone_contracts as hc` rewritten to `import halcytone as hc`
- [ ] `scripts/regen_manifest_schema.py` imports `from halcytone.contracts.bundles.manifest import SessionManifest`
- [ ] `pytest` passes with **336 tests** (identical count to halcytone-contracts v0.2.0)
- [ ] `python scripts/regen_manifest_schema.py && git diff --exit-code halcytone/contracts/bundles/manifest.schema.json` exits 0 (regen idempotent)
- [ ] `ruff check .` clean

**Depends on:** T3.2

---

### T3.4 — Migrate core source → `halcytone.core` | Cx: 3 | P0

**Description:** Copy the 2 `halcytone_core` source files (`__init__.py`, `wiring.py`) into `halcytone/core/`. Rewrite internal imports: `from halcytone_contracts import X` → `from halcytone.contracts import X` (or `from halcytone import X` since the top-level re-exports everything). **Remove** `_EXPECTED_CONTRACTS_VERSION` and the import-time `check_contract_version(...)` call — same-package drift is structurally impossible, so the guard is dead code. Set `halcytone.core.__version__ = "0.3.0"` in lockstep with the package. Expand `halcytone.core.wiring.PUBLIC_SURFACE` to include `Baseline`, `StreamBaseline`, and `SessionSummary` (this is the T2.7 expansion the canceled core-sprint-2 would have done — fold it in here since we're already touching `wiring.py`).

**AC:**
- [ ] `halcytone/core/__init__.py` exists with `__version__: str = "0.3.0"` and no `_EXPECTED_CONTRACTS_VERSION` / `check_contract_version(...)` call at module level
- [ ] `halcytone/core/wiring.py` exists; imports `Baseline`, `StreamBaseline`, `SessionSummary` alongside the pre-sprint-2 surface
- [ ] `halcytone.core.wiring.PUBLIC_SURFACE` is a tuple including all three new names plus the pre-existing entries
- [ ] Every `from halcytone_contracts` in core source rewritten to `from halcytone.contracts` or `from halcytone`
- [ ] `from halcytone.core.wiring import PUBLIC_SURFACE` succeeds at import time (no `ContractError`, no warnings)
- [ ] `bpsai-pair arch check halcytone/core/` clean

**Depends on:** T3.2

---

### T3.5 — Port + expand core tests | Cx: 4 | P0

**Description:** Copy the existing `tests/test_wiring.py` (14 tests) into the new repo's `tests/` dir and rewrite imports. Then fold in the T2.6–T2.8 coverage that the canceled core-sprint-2 was supposed to deliver — this sprint becomes the forcing function that proves the typed manifest is consumable from a real caller. Add three new tests: (a) construct a `SessionManifest` with a multi-stream `Baseline` (≥3 streams, real `RESERVED_STREAMS` names) and a fully-populated `SessionSummary` (every numeric field + `summary_schema_version=1`), JSON round-trip, assert equality; (b) `Baseline` rejects an unknown stream name with a `ValidationError` whose message names the offender (exercises the roster-coupling through a core-side import); (c) `check_contract_version("0.2.9")` stays silent (matches current major+minor 0.3.x … wait, actually need to verify — does 0.2.9 → 0.3.0 warn or raise? 0.x sharpened minor mismatch = hard fail) and `check_contract_version("0.1.0")` hard-fails.

**AC:**
- [ ] `tests/test_wiring.py` exists in the new repo's `tests/`
- [ ] Existing 14 wiring tests ported cleanly with imports rewritten (no `halcytone_core.*` or `halcytone_contracts.*` imports remain)
- [ ] New test: full-payload `SessionManifest` with multi-stream `Baseline` + complete `SessionSummary`, JSON round-trip, equality
- [ ] New test: `Baseline` with unknown stream key raises `ValidationError`; message contains the offending stream name
- [ ] New test: `check_contract_version("0.1.0")` raises `ContractError`; message mentions "pre-1.0"
- [ ] New test: `check_contract_version("0.3.0")` is a no-op
- [ ] `pytest tests/test_wiring.py -q` passes, at least 20 tests total
- [ ] Full `pytest` still green (≥ 356 tests: 336 contracts + ≥20 wiring)
- [ ] `ruff check .` clean

**Depends on:** T3.3, T3.4

---

## Phase 4: Unification (Wave 3, parallel)

### T3.6 — Unified CI workflow | Cx: 2 | P0

**Description:** Write `.github/workflows/ci.yml` in the new monorepo using the same three-job shape as halcytone-contracts v0.2.0: `lint` (ruff), `test` (matrix Python 3.11/3.12/3.13, `pip install -e '.[dev]'` then `pytest -q`), and `schema-drift` (run `scripts/regen_manifest_schema.py` and fail if `git diff --exit-code halcytone/contracts/bundles/manifest.schema.json` reports changes). Trigger on push + pull_request to `main`. Use the same `concurrency` group pattern to cancel stale PR runs. No cross-repo auth needed — the monorepo replaces the deploy-key / visibility dance halcytone-core previously required.

**AC:**
- [ ] `.github/workflows/ci.yml` has three jobs: `lint`, `test` (matrix 3.11/3.12/3.13), `schema-drift`
- [ ] Triggers: `on: push: branches: [main]`, `on: pull_request: branches: [main]`
- [ ] `concurrency` group `ci-${{ github.ref }}` with `cancel-in-progress: true`
- [ ] `test` job: `pip install -e '.[dev]'` (single-quoted `[dev]` for shell-safety), then `pytest -q`
- [ ] `schema-drift` job: `python scripts/regen_manifest_schema.py && git diff --exit-code halcytone/contracts/bundles/manifest.schema.json`
- [ ] No `actions/checkout` with `token:`, `ssh-key:`, or cross-repo params — single-repo clone only
- [ ] Workflow file parses cleanly (YAML-lint equivalent; GitHub Actions accepts it on push)

**Depends on:** T3.3, T3.5

---

### T3.7 — Unified CHANGELOG + ROADMAP | Cx: 2 | P0

**Description:** Fill in the real content of `CHANGELOG.md` and `ROADMAP.md` (scaffolded as stubs by T3.1). `CHANGELOG.md` seeded at `[0.3.0] — 2026-04-18` in Keep-a-Changelog format: `### Changed` section documenting the structural consolidation (import-path rename, removal of `_EXPECTED_CONTRACTS_VERSION` dance in `halcytone.core`), `### Migration` section with concrete rewrite rules (`from halcytone_contracts import X` → `from halcytone import X`; drop any `halcytone-contracts @ git+...` pins; adopt `halcytone>=0.3,<0.4`), and historical `[0.2.0]`, `[0.1.1]`, `[0.1.0]` sections preserved under a "Pre-consolidation (halcytone-contracts)" header so the lineage is readable. `ROADMAP.md` restructured: v0.3.0 marked "shipped (consolidation)", v0.4.0 scope is real fusion logic in `halcytone.core` (session state machine, LSL ingest, 200 Hz StateVector emission), v0.5.0 scope is a second consumer (sensors or audio), v1.0.0 stability target unchanged. Both files link to the archived `halcytone-contracts` and `halcytone-core` GitHub repos for history.

**AC:**
- [ ] `CHANGELOG.md` has a `## [0.3.0] — 2026-04-18` section with `### Changed` and `### Migration` subsections
- [ ] Migration section lists the import rewrite, pin replacement, and pin recommendation explicitly
- [ ] Historical `[0.2.0]`, `[0.1.1]`, `[0.1.0]` sections preserved verbatim under a "Pre-consolidation (halcytone-contracts)" heading
- [ ] CHANGELOG comparison links updated for the new repo (`[Unreleased]`, `[0.3.0]`, `[0.2.0]`, `[0.1.1]`, `[0.1.0]`)
- [ ] `ROADMAP.md` has sections for v0.1.x shipped (pre-consolidation), v0.2.0 shipped (pre-consolidation), v0.3.0 shipped (this release), v0.4.0 (fusion logic), v0.5.0 (second consumer), v1.0.0 (stability target)
- [ ] Both files include a link to `https://github.com/fivedollarfridays/halcytone-contracts` (archived) and `...halcytone-core` (archived)
- [ ] No remaining references to "7-repo fleet" language — ROADMAP reflects the monorepo reality

**Depends on:** T3.5

---

### T3.8 — README rewrite | Cx: 2 | P0

**Description:** Rewrite `README.md` for the new monorepo positioning. Lead with: "Halcytone — biofeedback sonification platform. Monorepo with subpackages under `halcytone.*`." Replace the old 7-repo fleet architecture diagram with a subpackage table showing role + status for each: `contracts` (shipped), `core` (stub), `sensors` (planned), `audio` (planned), `hud` (planned), `breath` (planned), `publish` (planned). Keep the Versioning section (Apache-2.0 + 0.x sharpened semver policy) and update the pin recommendation to `halcytone>=0.3,<0.4`. Include a quick-start code example: `pip install halcytone @ git+https://github.com/fivedollarfridays/halcytone.git@v0.3.0` + `from halcytone import SignalPacket, StateVector, SessionManifest`. Verify links to `ROADMAP.md` and `CHANGELOG.md` resolve.

**AC:**
- [ ] README top-level positioning sentence mentions "monorepo with subpackages under `halcytone.*`"
- [ ] Subpackage table present with 7 rows: contracts, core, sensors, audio, hud, breath, publish; each row has a role description + status (shipped / stub / planned)
- [ ] No remaining "7-repo fleet" / "halcytone-contracts" / "halcytone-core" as separate-repo references in the README body (except in archived-repo pointer notes)
- [ ] Versioning section present: semver policy including 0.x sharpening, pin recommendation `halcytone>=0.3,<0.4`, `check_contract_version` runtime pattern
- [ ] Quick-start code block with the git-dep install line and `from halcytone import ...` example
- [ ] Links to `ROADMAP.md` and `CHANGELOG.md` resolve to the new repo's files

**Depends on:** T3.1

---

## Phase 5: Ship (Wave 4)

### T3.9 — Commit + push + open PR | Cx: 2 | P0

**Description:** Stage every file produced by T3.2–T3.8 on a feature branch `engage/backlog-sprint-3` in the new `halcytone` repo. Single comprehensive commit (or a small number of logically grouped commits — contracts migration / core migration / docs — driver's choice) with descriptive messages. Push to `origin/engage/backlog-sprint-3`. Open a PR against `main` titled something like "v0.3.0 — halcytone monorepo consolidation" with a body summarizing the intent (collapse + import rename + version sharpened policy still active) and a test plan. Pre-push locally: `pytest` green, `ruff check .` clean, `bpsai-pair security scan-secrets` clean, `git diff main...HEAD | grep -iE "(api[_-]?key|password|secret=|token=|bearer)"` clean. Wait for CI green on all 5 jobs (lint + test × 3 + schema-drift).

**AC:**
- [ ] All T3.2–T3.8 work committed on `engage/backlog-sprint-3`
- [ ] Pre-push gates locally: `pytest` all-green, `ruff check .` clean, secret scan clean (`bpsai-pair security scan-secrets`)
- [ ] Branch pushed to `origin/engage/backlog-sprint-3`
- [ ] PR opened against `main` with a descriptive title, summary, and test plan
- [ ] CI run: `lint` pass, `test (3.11)` pass, `test (3.12)` pass, `test (3.13)` pass, `schema-drift` pass
- [ ] No new CI warnings vs. halcytone-contracts baseline

**Depends on:** T3.6, T3.7, T3.8

---

### T3.10 — Post-merge: tag v0.3.0 + archive old repos | Cx: 2 | P1

**Description:** After the user merges the PR from T3.9, tag `v0.3.0` on `main` of the new `halcytone` repo and push the tag. Then archive the two predecessor repos on GitHub: `halcytone-contracts` and `halcytone-core`. For each, first add a single commit updating their `README.md` with a prominent "This repo is archived. Continuing work lives in https://github.com/fivedollarfridays/halcytone." pointer at the top, then run `gh repo edit --archived` to flip the repo state. Existing tags (`v0.1.0`, `v0.1.1`, `v0.2.0` on contracts) are retained — they're still historically valid install targets for anyone who needs the pre-consolidation shape.

**AC:**
- [ ] `v0.3.0` tag created on `main` via `git tag -a v0.3.0 -m "halcytone v0.3.0 — monorepo consolidation"` and pushed to origin
- [ ] `halcytone-contracts` README gains a pointer to the new monorepo at the top (single commit on its default branch)
- [ ] `halcytone-core` README gains the same pointer
- [ ] Both `halcytone-contracts` and `halcytone-core` set to archived via `gh repo edit <repo> --archived`
- [ ] Existing `v0.1.0`, `v0.1.1`, `v0.2.0` tags on halcytone-contracts still present (not deleted)
- [ ] GitHub releases page shows v0.3.0 as the latest release on the new `halcytone` repo

**Depends on:** T3.9 (plus user action: merge the PR)

---

### T3.11 — Local cleanup | Cx: 1 | P1

**Description:** Delete the two old local working copies (`/home/kmasty/projects/halcytone-contracts` and `/home/kmasty/projects/halcytone-core`) — the remote archives are preserved, so local deletion is safe. Remove `/home/kmasty/projects/.paircoder-workspace.yaml` since we no longer have a cross-repo workspace to coordinate. Confirm the new `/home/kmasty/projects/halcytone/` clone is the single source of truth for all future work. Run `bpsai-pair validate` in the new repo to confirm paircoder health.

**AC:**
- [ ] `/home/kmasty/projects/halcytone-contracts/` removed (rm -rf)
- [ ] `/home/kmasty/projects/halcytone-core/` removed (rm -rf)
- [ ] `/home/kmasty/projects/.paircoder-workspace.yaml` removed
- [ ] `/home/kmasty/projects/halcytone/` exists and is the new working copy
- [ ] `bpsai-pair validate` passes in the new clone
- [ ] `git status` in the new clone is clean (or only `.paircoder/` bookkeeping)

**Depends on:** T3.10

---

## Delivery Summary

| Task | Title | Cx | Pri | Depends |
|------|-------|----|-----|---------|
| T3.1 | Create `halcytone` repo + scaffold | 3 | P0 | — |
| T3.2 | Migrate contracts source → `halcytone.contracts` | 4 | P0 | T3.1 |
| T3.3 | Port contracts tests + regen script | 3 | P0 | T3.2 |
| T3.4 | Migrate core source → `halcytone.core` | 3 | P0 | T3.2 |
| T3.5 | Port + expand core tests | 4 | P0 | T3.3, T3.4 |
| T3.6 | Unified CI workflow | 2 | P0 | T3.3, T3.5 |
| T3.7 | Unified CHANGELOG + ROADMAP | 2 | P0 | T3.5 |
| T3.8 | README rewrite | 2 | P0 | T3.1 |
| T3.9 | Commit + push + open PR | 2 | P0 | T3.6, T3.7, T3.8 |
| T3.10 | Post-merge: tag v0.3.0 + archive old repos | 2 | P1 | T3.9 |
| T3.11 | Local cleanup | 1 | P1 | T3.10 |

**Sprint Budget:** 28 Cx across 11 tasks — P0 ×9, P1 ×2, P2 ×0.

**Cut order if budget overflows:** T3.11 → T3.10. Both are post-merge housekeeping that can slip to a follow-up session without blocking the v0.3.0 ship. Never cut T3.1–T3.9 — each is load-bearing.

## Priority Order

1. **T3.1** — Bootstrap (P0, blocks everything)
2. **T3.2** — Contracts migration (P0, foundation for T3.3–T3.5)
3. **T3.3** — Contracts tests port (P0, wave 2, parallel with T3.4 / T3.8)
4. **T3.4** — Core migration (P0, wave 2)
5. **T3.8** — README rewrite (P0, wave 2, independent)
6. **T3.5** — Core tests + wiring expansion (P0, wave 3)
7. **T3.6** — Unified CI (P0, wave 4, parallel with T3.7)
8. **T3.7** — CHANGELOG + ROADMAP (P0, wave 4)
9. **T3.9** — Ship: commit + push + PR (P0, wave 5)
10. **T3.10** — Tag + archive (P1, post-merge)
11. **T3.11** — Local cleanup (P1, post-merge tail)

## Dependency Graph

```
Wave 0:  T3.1                                                (scaffold the new repo)
           ↓
Wave 1:  T3.2 (← T3.1)                                       (contracts source — blocker)
           ↓
Wave 2:  T3.3 (← T3.2)    T3.4 (← T3.2)    T3.8 (← T3.1)    (parallel: tests / core / README)
           ↓                 ↓
Wave 3:                   T3.5 (← T3.3, T3.4)                (core tests + wiring expansion)
                             ↓
Wave 4:  T3.6 (← T3.3, T3.5)    T3.7 (← T3.5)                (parallel: CI / docs)
                                     ↓                    ↓
Wave 5:                          T3.9 (← T3.6, T3.7, T3.8)   (commit + push + PR)
                                     ↓
─── user merges the PR ───
                                     ↓
Wave 6:                          T3.10 (← T3.9 merged)       (tag + archive)
                                     ↓
Wave 7:                          T3.11 (← T3.10)             (local cleanup)
```

## File Collision Matrix

| Wave | Parallel tasks | Shared files | Status |
|------|----------------|--------------|--------|
| 2 | T3.3, T3.4, T3.8 | T3.3 → `tests/test_*.py` + `scripts/regen_manifest_schema.py`; T3.4 → `halcytone/core/*.py`; T3.8 → `README.md` — all disjoint | Clean |
| 4 | T3.6, T3.7 | T3.6 → `.github/workflows/ci.yml`; T3.7 → `CHANGELOG.md`, `ROADMAP.md` — disjoint | Clean |

## Integration Points

- **T3.2 → every downstream task.** `halcytone.contracts` is the foundation; T3.3, T3.4, T3.5 all import from it. Any rename T3.2 misses cascades into red tests in T3.3 and import failures in T3.4.
- **T3.4 removes `_EXPECTED_CONTRACTS_VERSION` import-time check.** If forgotten, monorepo fails at import because `check_contract_version("0.1.1")` would hard-fail against the current `__contract_version__ = "0.3.0"`. This is a **deletion**, not a bump — don't carry it forward.
- **T3.5 folds in deferred T2.6–T2.8 coverage.** This sprint becomes the forcing function that the canceled core-sprint-2 would have been: "can a real consumer construct the typed manifest?" test moves inside the monorepo.
- **T3.9 → T3.10 cross-repo manual gate.** Same pattern as sprints 1 and 2: user merges, then tag + archive. No automation.
- **T3.1 scaffolded stubs unblock parallel work.** T3.1 creates empty-but-present `CHANGELOG.md` / `ROADMAP.md` so T3.7 has files to fill; same for `README.md` so T3.8 can work in parallel with T3.7.

## Out of Scope

- **Any fusion logic in `halcytone.core`.** Still consumer-stub scope; real fusion engine is v0.4.0.
- **`halcytone-broadcast` (private SaaS).** Does not exist yet; defer until the open monorepo has enough surface to host against.
- **PyPI publishing.** v0.3.0 ships as a git dep (`halcytone @ git+https://github.com/fivedollarfridays/halcytone.git@v0.3.0`). PyPI is post-consolidation work.
- **New sensor adapters / audio mapper / HUD / publish logic.** Subpackage placeholders only.
- **Paircoder template for sibling repos.** Moot in a monorepo; drop from future roadmap entirely.
- **Preserving git history from `halcytone-contracts` / `halcytone-core`.** Archived repos retain their own history; new monorepo starts fresh. `git subtree` merge was considered and rejected — not worth the ceremony for 3-day-old repos.
- **`bpsai-pair #190` hook fix.** Still upstream; `/start-task` per-task remains the workaround for execution.
