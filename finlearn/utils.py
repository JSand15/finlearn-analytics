"""Shared validation and helper utilities for finlearn."""

import math
from typing import List


def validate_returns(returns: List[float], name: str = "returns") -> List[float]:
    """Validate that a returns list is non-empty and contains finite numbers."""
    if not isinstance(returns, (list, tuple)):
        raise TypeError(f"{name} must be a list or tuple, got {type(returns).__name__}")
    if len(returns) == 0:
        raise ValueError(f"{name} must not be empty")
    for i, v in enumerate(returns):
        if isinstance(v, bool):
            raise TypeError(f"{name}[{i}] must be numeric, got bool")
        if not isinstance(v, (int, float)):
            raise TypeError(f"{name}[{i}] must be numeric, got {type(v).__name__}")
        if v != v:  # NaN check
            raise ValueError(f"{name}[{i}] contains NaN")
        if math.isinf(v):
            raise ValueError(f"{name}[{i}] contains infinity")
    return [float(v) for v in returns]


def validate_prices(prices: List[float], name: str = "prices") -> List[float]:
    """Validate a price series: non-empty, numeric, all positive."""
    validated = validate_returns(prices, name)
    for i, v in enumerate(validated):
        if v <= 0:
            raise ValueError(f"{name}[{i}] must be positive, got {v}")
    return validated


def validate_text(text: str, name: str = "text") -> str:
    """Validate that input is a non-empty string."""
    if not isinstance(text, str):
        raise TypeError(f"{name} must be a string, got {type(text).__name__}")
    if not text.strip():
        raise ValueError(f"{name} must not be empty or whitespace-only")
    return text
