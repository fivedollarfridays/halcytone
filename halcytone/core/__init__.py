"""`halcytone.core` — fusion, session lifecycle, storage orchestration.

This package is the consumer of `halcytone.contracts`. It ships in lockstep
with the contracts subpackage — drift within the monorepo is structurally
impossible, so no import-time version check is needed.

v0.3.0 is a wiring stub — it proves every public surface of
`halcytone.contracts` v0.3.0 is importable and constructible. Real fusion
logic lands in v0.4.0.
"""

from __future__ import annotations

__version__: str = "0.3.0"

__all__ = ["__version__"]
