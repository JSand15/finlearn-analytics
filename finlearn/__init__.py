"""finlearn-analytics: Financial analytics and behavioral finance research tools."""

__version__ = "0.1.0"
__author__ = "Jeevun Sandhu"

from .metrics import calculate_sharpe_ratio, calculate_max_drawdown
from .benchmarks import compare_to_benchmark
from .memo import analyze_memo_quality
from .biases import (
    BehavioralBias,
    BIASES,
    detect_biases,
    analyze_biases,
    list_biases,
    list_bias_categories,
    get_bias,
)

__all__ = [
    "calculate_sharpe_ratio",
    "calculate_max_drawdown",
    "compare_to_benchmark",
    "analyze_memo_quality",
    # Behavioral bias detection
    "BehavioralBias",
    "BIASES",
    "detect_biases",
    "analyze_biases",
    "list_biases",
    "list_bias_categories",
    "get_bias",
]
