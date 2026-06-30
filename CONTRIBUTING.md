# Contributing to finlearn-analytics

Thanks for your interest! This is a small, dependency-free library and contributions
are welcome — especially new behavioral biases, additional metrics, and test coverage.

## Development setup

```bash
git clone https://github.com/JSand15/finlearn-analytics.git
cd finlearn-analytics
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
```

## Ground rules

- **Zero runtime dependencies.** The library is pure Python (`math`, `re`, stdlib only).
  Do not add a runtime dependency without opening an issue to discuss it first.
- **Validation lives in `finlearn/utils.py`.** Reuse `validate_returns` / `validate_prices`
  / `validate_text` rather than re-checking inputs in each module.
- **Public functions raise only `TypeError` / `ValueError`** on bad input. Keep that contract.
- **Every function needs tests** (3+ covering happy path, edge cases, and error cases).

## Adding a behavioral bias

Each bias is a `BehavioralBias` entry in `finlearn/biases.py`'s `BIASES` tuple with a unique
`key` (snake_case), unique `name`, a `category`, a finance-specific one-line `description`,
and lowercase trigger `phrases`. The catalog self-checks uniqueness and lowercase phrases at
import time, and `tests/test_biases.py` asserts every bias is detectable via its own phrases —
so add a case and run `pytest -q` to confirm.

## Pull requests

1. Branch from `main`.
2. Make the change with tests; ensure `pytest -q` is green.
3. Open a PR — CI runs the suite on Python 3.9–3.13 and validates the build.

## Reporting issues

Open an issue with a minimal reproduction (input + expected vs actual). Good first issues
are labeled `good first issue`.
