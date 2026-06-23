# Changelog

All notable changes to **finlearn-analytics** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-06-22

### Added
- `calculate_sharpe_ratio` — annualized, risk-free-adjusted Sharpe ratio.
- `calculate_max_drawdown` — maximum peak-to-trough decline of a price series.
- `compare_to_benchmark` — alpha, beta, correlation, excess return, tracking error.
- `analyze_memo_quality` — word count, sentiment, clarity, overconfidence flags,
  and a full behavioral-bias screen.
- `finlearn.biases` — a catalog of **69 specific behavioral-finance biases** across
  10 categories, with detection helpers: `detect_biases`, `analyze_biases`,
  `list_biases`, `list_bias_categories`, and `get_bias`.
- PEP 561 typing marker (`py.typed`) — the package ships its type hints.
- Input validation helpers in `finlearn.utils` (NaN/inf/bool rejection, positivity
  checks) shared across all modules.

### Notes
- Zero runtime dependencies; pure-Python and importable on Python 3.9+.

[0.1.0]: https://github.com/JSand15/finlearn-analytics/releases/tag/v0.1.0
