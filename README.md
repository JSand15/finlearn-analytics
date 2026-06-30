# finlearn-analytics

**Detect 69 behavioral-finance biases in investment memos — plus Sharpe ratio, max drawdown, and benchmark analytics. Pure Python, zero dependencies.**

[![PyPI version](https://badge.fury.io/py/finlearn-analytics.svg)](https://pypi.org/project/finlearn-analytics/)
[![CI](https://github.com/JSand15/finlearn-analytics/actions/workflows/ci.yml/badge.svg)](https://github.com/JSand15/finlearn-analytics/actions/workflows/ci.yml)
[![Downloads](https://static.pepy.tech/badge/finlearn-analytics)](https://pepy.tech/project/finlearn-analytics)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)

---

## Installation

```bash
pip install finlearn-analytics
```

---

## Quick Start

```python
from finlearn import (
    calculate_sharpe_ratio,
    calculate_max_drawdown,
    compare_to_benchmark,
    analyze_memo_quality,
)

# Daily returns for a hypothetical portfolio
daily_returns = [0.012, -0.005, 0.008, 0.003, -0.002, 0.015, 0.001, -0.007, 0.009, 0.004]

# 1. Sharpe Ratio
sharpe = calculate_sharpe_ratio(daily_returns, risk_free_rate=0.0001)
print(f"Sharpe Ratio: {sharpe:.2f}")

# 2. Max Drawdown
prices = [100, 112, 107, 115, 109, 124, 125, 118, 127, 129]
drawdown = calculate_max_drawdown(prices)
print(f"Max Drawdown: {drawdown:.2%}")

# 3. Benchmark Comparison
benchmark_returns = [0.008, -0.003, 0.005, 0.002, -0.001, 0.010, 0.000, -0.004, 0.006, 0.003]
metrics = compare_to_benchmark(daily_returns, benchmark_returns)
print(f"Alpha: {metrics['alpha']:.4f}  Beta: {metrics['beta']:.2f}  Correlation: {metrics['correlation']:.2f}")
print(f"Excess Return: {metrics['excess_return']:.4f}  Tracking Error: {metrics['tracking_error']:.4f}")

# 4. Memo Quality Analysis
memo = """
This stock shows strong momentum and profit potential. The company's
revenue growth is robust, with favorable market conditions driving
an expected increase in earnings next quarter.
"""
analysis = analyze_memo_quality(memo)
print(f"Word Count: {analysis['word_count']}")
print(f"Sentiment: {analysis['sentiment_score']:.2f}")
print(f"Clarity Score: {analysis['clarity_score']}/100")
print(f"Overconfidence Flags: {analysis['overconfidence_flags']}")
print(f"Behavioral Biases: {analysis['behavioral_biases']}")
print(f"Recommendation: {analysis['recommendation']}")

# 5. Behavioral Bias Detection (60+ specific biases)
from finlearn import analyze_biases, get_bias

note = "It's guaranteed to be the next Amazon. Everyone is buying — can't miss this."
report = analyze_biases(note)
print(f"Biases detected: {report['biases_detected']}")
print(f"By category: {report['by_category']}")
print(get_bias("fomo")["description"])
```

---

## Functions

### `calculate_sharpe_ratio(returns, risk_free_rate=0.0)`

Computes the annualized Sharpe ratio for a series of daily returns. The Sharpe ratio measures risk-adjusted performance: how much excess return is earned per unit of volatility. A ratio above 1.0 is generally considered acceptable; above 2.0 is considered excellent. Raises `ValueError` if returns have zero standard deviation or fewer than 2 observations.

**Parameters:** `returns` — list of daily returns as decimals; `risk_free_rate` — daily risk-free rate (default 0.0).  
**Returns:** `float` — annualized Sharpe ratio.

---

### `calculate_max_drawdown(prices)`

Calculates the maximum peak-to-trough decline in a price series, returned as a negative decimal (e.g., `-0.25` means a 25% loss from peak to trough). This metric is a standard measure of downside risk. Requires at least 2 positive price values.

**Parameters:** `prices` — list of asset prices in chronological order (all positive).  
**Returns:** `float` — maximum drawdown, between -1.0 and 0.0.

---

### `compare_to_benchmark(portfolio_returns, benchmark_returns)`

Benchmarks a portfolio against an index by computing Jensen's alpha, beta, Pearson correlation, annualized excess return, and annualized tracking error. Alpha represents return beyond what market exposure (beta) predicts. Tracking error measures consistency of outperformance. Both lists must be equal in length with at least 2 observations.

**Parameters:** `portfolio_returns`, `benchmark_returns` — lists of daily returns as decimals of equal length.  
**Returns:** `dict` with keys `alpha`, `beta`, `correlation`, `excess_return`, `tracking_error`.

---

### `analyze_memo_quality(memo_text)`

Applies behavioral finance heuristics to score the quality of an investment memo. Detects overconfidence bias (guaranteed returns, zero-risk claims), measures sentiment polarity using financial vocabulary, estimates structural clarity from sentence length and vocabulary diversity, and produces a plain-English improvement recommendation.

**Parameters:** `memo_text` — full text of the investment memo as a string.  
**Returns:** `dict` with keys `word_count`, `sentiment_score`, `overconfidence_flags`, `behavioral_biases`, `clarity_score`, `recommendation`.

---

### Behavioral Bias Detection

`finlearn.biases` ships a catalog of **69 specific behavioral-finance biases** across 10 categories (Confidence, Loss & Risk, Anchoring, Information Processing, Social & Herding, Probability, Framing, Temporal, Emotional, and Memory & Attention). Each bias carries a finance-specific description and a set of lowercase trigger phrases. A lightweight, dependency-free detector flags the linguistic fingerprints of these biases in any text — investment memos, research notes, or trade rationales. It is a heuristic screen to surface candidates for human review, not a classifier.

| Function | Returns |
|----------|---------|
| `detect_biases(text)` | `list[dict]` — each detected bias with `key`, `name`, `category`, `description`, `matched_phrases` |
| `analyze_biases(text)` | `dict` — `bias_count`, `biases_detected`, `by_category`, `details`, `bias_density_per_100_words`, `recommendation` |
| `list_biases()` | `list[dict]` — metadata (`key`, `name`, `category`, `description`) for every bias |
| `list_bias_categories()` | `list[str]` — the distinct category labels |
| `get_bias(key)` | `dict` — full metadata for one bias, including its trigger `phrases` |

Detected biases include: overconfidence, overprecision, loss aversion, the disposition effect, sunk-cost fallacy, anchoring, confirmation bias, recency bias, herding, FOMO, the gambler's fallacy, the hot-hand fallacy, mental accounting, the framing effect, present bias, the affect heuristic, survivorship bias, and ~50 more — each individually addressable by key.

```python
from finlearn import detect_biases

hits = detect_biases("We're in too deep to sell now, but it's a sure thing.")
print([h["key"] for h in hits])   # ['overconfidence', 'sunk_cost']
```

---

## About

Built by **Jeevun Sandhu**, a high school student and founder of **FinanceOS**, a financial literacy platform deployed in LAUSD Title I schools. `finlearn-analytics` powers the quantitative backend of FinanceOS research, giving students and educators access to professional-grade financial analytics tools.

---

## License

MIT — see [LICENSE](LICENSE) for details.
