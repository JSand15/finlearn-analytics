"""Portfolio-vs-benchmark comparison analytics."""

import math
from typing import Dict, List

from .utils import validate_returns


def compare_to_benchmark(
    portfolio_returns: List[float],
    benchmark_returns: List[float],
) -> Dict[str, float]:
    """Compare portfolio performance against a benchmark index.

    Computes alpha, beta, correlation, excess return, and tracking error
    using standard financial definitions. Beta is estimated via OLS regression
    of portfolio returns on benchmark returns.

    Args:
        portfolio_returns: List of daily portfolio returns as decimals.
        benchmark_returns: List of daily benchmark returns as decimals.
            Must be the same length as portfolio_returns.

    Returns:
        Dictionary with the following keys:
            - alpha (float): Annualized Jensen's alpha (excess return beyond
              what beta predicts).
            - beta (float): Portfolio sensitivity to benchmark movements.
            - correlation (float): Pearson correlation between portfolio and
              benchmark returns, in [-1, 1].
            - excess_return (float): Annualized mean(portfolio) - mean(benchmark).
            - tracking_error (float): Annualized standard deviation of the
              return difference (portfolio - benchmark).

    Raises:
        TypeError: If either argument is not a list/tuple or contains
            non-numeric values.
        ValueError: If either list is empty, they differ in length, or the
            benchmark has zero variance.

    Example:
        >>> port = [0.001, 0.002, -0.001, 0.003]
        >>> bench = [0.0005, 0.0015, -0.0005, 0.002]
        >>> result = compare_to_benchmark(port, bench)
        >>> result['beta']
        1.5254...
    """
    p = validate_returns(portfolio_returns, "portfolio_returns")
    b = validate_returns(benchmark_returns, "benchmark_returns")

    if len(p) != len(b):
        raise ValueError(
            f"portfolio_returns (len={len(p)}) and benchmark_returns (len={len(b)}) "
            "must have the same length"
        )
    if len(p) < 2:
        raise ValueError("At least 2 observations are required")

    n = len(p)
    mean_p = sum(p) / n
    mean_b = sum(b) / n

    try:
        cov_pb = sum((p[i] - mean_p) * (b[i] - mean_b) for i in range(n)) / (n - 1)
        var_b = sum((x - mean_b) ** 2 for x in b) / (n - 1)
        var_p = sum((x - mean_p) ** 2 for x in p) / (n - 1)
    except OverflowError:
        raise ValueError("returns contain values too large to compute variance") from None

    if var_b == 0.0:
        raise ValueError("Benchmark returns have zero variance; beta is undefined")

    beta = cov_pb / var_b
    alpha_daily = mean_p - beta * mean_b
    alpha = alpha_daily * 252  # annualize

    std_p = math.sqrt(var_p) if var_p > 0 else 0.0
    std_b = math.sqrt(var_b)
    correlation = cov_pb / (std_p * std_b) if std_p > 0 else 0.0
    # Clamp to [-1, 1] for floating-point safety
    correlation = max(-1.0, min(1.0, correlation))

    excess_return = (mean_p - mean_b) * 252  # annualized

    diffs = [p[i] - b[i] for i in range(n)]
    mean_diff = sum(diffs) / n
    try:
        var_diff = sum((d - mean_diff) ** 2 for d in diffs) / (n - 1)
    except OverflowError:
        raise ValueError("returns contain values too large to compute tracking error") from None
    tracking_error = math.sqrt(var_diff) * math.sqrt(252)  # annualized

    return {
        "alpha": alpha,
        "beta": beta,
        "correlation": correlation,
        "excess_return": excess_return,
        "tracking_error": tracking_error,
    }
