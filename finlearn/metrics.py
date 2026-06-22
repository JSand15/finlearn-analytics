"""Portfolio risk and return metrics."""

import math
from typing import List

from .utils import validate_returns, validate_prices


def calculate_sharpe_ratio(
    returns: List[float],
    risk_free_rate: float = 0.0,
) -> float:
    """Calculate the annualized Sharpe ratio for a series of daily returns.

    The Sharpe ratio measures risk-adjusted return: how much excess return is
    earned per unit of volatility relative to a risk-free baseline.

    Args:
        returns: List of daily returns as decimals (e.g., 0.01 for 1%).
        risk_free_rate: Daily risk-free rate as a decimal. Defaults to 0.0.

    Returns:
        Annualized Sharpe ratio as a float.

    Raises:
        TypeError: If returns is not a list/tuple or contains non-numeric values.
        ValueError: If returns is empty or has zero standard deviation.

    Example:
        >>> daily_returns = [0.001, 0.002, -0.001, 0.003, 0.0015]
        >>> calculate_sharpe_ratio(daily_returns, risk_free_rate=0.0001)
        12.8431...
    """
    # bool is a subclass of int — reject it explicitly so True/False can't pose
    # as a numeric risk-free rate (consistent with how returns are validated).
    if isinstance(risk_free_rate, bool) or not isinstance(risk_free_rate, (int, float)):
        raise TypeError(f"risk_free_rate must be numeric, got {type(risk_free_rate).__name__}")
    if risk_free_rate != risk_free_rate or math.isinf(risk_free_rate):
        raise ValueError(f"risk_free_rate must be a finite number, got {risk_free_rate}")

    r = validate_returns(returns, "returns")

    if len(r) < 2:
        raise ValueError("returns must contain at least 2 values to compute standard deviation")

    n = len(r)
    mean = sum(r) / n
    try:
        variance = sum((x - mean) ** 2 for x in r) / (n - 1)
    except OverflowError:
        raise ValueError("returns contain values too large to compute variance") from None
    std = math.sqrt(variance)

    if std == 0.0:
        raise ValueError("Standard deviation of returns is zero; Sharpe ratio is undefined")

    excess_return = mean - risk_free_rate
    return (excess_return / std) * math.sqrt(252)


def calculate_max_drawdown(prices: List[float]) -> float:
    """Calculate the maximum drawdown from a price series.

    Maximum drawdown measures the largest peak-to-trough decline, expressed
    as a negative decimal (e.g., -0.25 means a 25% loss from peak to trough).

    Args:
        prices: List of asset prices in chronological order. All values must
            be positive.

    Returns:
        Maximum drawdown as a negative decimal between -1.0 and 0.0.
        Returns 0.0 if the price series never declines.

    Raises:
        TypeError: If prices is not a list/tuple or contains non-numeric values.
        ValueError: If prices is empty, contains non-positive values, or has
            fewer than 2 elements.

    Example:
        >>> prices = [100, 120, 90, 110, 80, 130]
        >>> calculate_max_drawdown(prices)
        -0.3333...
    """
    p = validate_prices(prices, "prices")

    if len(p) < 2:
        raise ValueError("prices must contain at least 2 values")

    max_drawdown = 0.0
    peak = p[0]

    for price in p[1:]:
        if price > peak:
            peak = price
        drawdown = (price - peak) / peak
        if drawdown < max_drawdown:
            max_drawdown = drawdown

    return max_drawdown
