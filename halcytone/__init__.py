"""Halcytone — biofeedback sonification platform (monorepo).

Subpackages under `halcytone.*`:

- `halcytone.contracts`  — shared pydantic schemas, JSON Schema, SQL DDL (shipped v0.3.0).
- `halcytone.core`       — session state + wiring stub (shipped v0.3.0; real fusion
  logic lands v0.4.0).

Additional subpackages (sensors, audio, hud, breath, publish) are planned; see
`ROADMAP.md` for target versions.
"""

__version__: str = "0.3.0"
