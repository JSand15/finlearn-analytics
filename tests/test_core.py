"""Core tests for finlearn-analytics — minimum 3 tests per function."""

import math
import pytest

from finlearn import (
    calculate_sharpe_ratio,
    calculate_max_drawdown,
    compare_to_benchmark,
    analyze_memo_quality,
)


# ── calculate_sharpe_ratio ────────────────────────────────────────────────────

class TestCalculateSharpeRatio:
    def test_happy_path_known_output(self):
        # Uniform returns → mean = 0.01, std → 0, but use slight variation
        returns = [0.01, 0.02, 0.01, 0.02, 0.01, 0.02]
        result = calculate_sharpe_ratio(returns, risk_free_rate=0.0)
        # Should be positive and finite
        assert isinstance(result, float)
        assert result > 0
        # Verify formula manually: mean=0.015, std≈0.005477, annualized *= sqrt(252)
        mean = sum(returns) / len(returns)
        n = len(returns)
        std = math.sqrt(sum((x - mean) ** 2 for x in returns) / (n - 1))
        expected = (mean / std) * math.sqrt(252)
        assert abs(result - expected) < 1e-9

    def test_with_risk_free_rate(self):
        returns = [0.002, 0.003, 0.001, 0.004, 0.002, 0.003]
        rfr = 0.001
        result = calculate_sharpe_ratio(returns, risk_free_rate=rfr)
        result_no_rfr = calculate_sharpe_ratio(returns, risk_free_rate=0.0)
        # Higher risk-free rate → lower Sharpe
        assert result < result_no_rfr

    def test_empty_returns_raises(self):
        with pytest.raises(ValueError, match="empty"):
            calculate_sharpe_ratio([])

    def test_single_element_raises(self):
        with pytest.raises(ValueError):
            calculate_sharpe_ratio([0.01])

    def test_zero_std_raises(self):
        with pytest.raises(ValueError, match="[Ss]tandard deviation"):
            calculate_sharpe_ratio([0.01, 0.01, 0.01, 0.01])

    def test_non_list_raises(self):
        with pytest.raises(TypeError):
            calculate_sharpe_ratio("not a list")

    def test_non_numeric_element_raises(self):
        with pytest.raises(TypeError):
            calculate_sharpe_ratio([0.01, "bad", 0.02])

    def test_bool_raises(self):
        # bool is a subclass of int in Python — must be rejected explicitly
        with pytest.raises(TypeError, match="bool"):
            calculate_sharpe_ratio([True, False, True, False, True, False])

    def test_inf_in_returns_raises(self):
        with pytest.raises(ValueError, match="infinity"):
            calculate_sharpe_ratio([0.01, float("inf"), 0.02])

    def test_nan_in_returns_raises(self):
        with pytest.raises(ValueError, match="NaN"):
            calculate_sharpe_ratio([0.01, float("nan"), 0.02])

    def test_inf_risk_free_rate_raises(self):
        with pytest.raises(ValueError):
            calculate_sharpe_ratio([0.01, 0.02, 0.015], risk_free_rate=float("inf"))

    def test_bool_risk_free_rate_raises(self):
        # bool is a subclass of int — must not pose as a numeric rate
        with pytest.raises(TypeError, match="bool"):
            calculate_sharpe_ratio([0.01, 0.02, 0.015], risk_free_rate=True)

    def test_overflow_returns_raises_valueerror(self):
        # Extreme but finite inputs must surface a clean ValueError, not OverflowError
        with pytest.raises(ValueError):
            calculate_sharpe_ratio([1e308, -1e308, 1e308, -1e308])

    def test_negative_sharpe_with_negative_returns(self):
        returns = [-0.02, -0.01, -0.03, -0.02, -0.015, -0.025]
        result = calculate_sharpe_ratio(returns, risk_free_rate=0.0)
        assert result < 0


# ── calculate_max_drawdown ────────────────────────────────────────────────────

class TestCalculateMaxDrawdown:
    def test_happy_path_known_output(self):
        # Peak at 120, trough at 80 → drawdown = (80-120)/120 = -1/3
        prices = [100, 120, 90, 110, 80, 130]
        result = calculate_max_drawdown(prices)
        expected = (80 - 120) / 120
        assert abs(result - expected) < 1e-9

    def test_monotonically_increasing(self):
        prices = [10, 20, 30, 40, 50]
        assert calculate_max_drawdown(prices) == 0.0

    def test_single_dip(self):
        prices = [100, 50, 100]
        result = calculate_max_drawdown(prices)
        assert abs(result - (-0.5)) < 1e-9

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="empty"):
            calculate_max_drawdown([])

    def test_single_element_raises(self):
        with pytest.raises(ValueError):
            calculate_max_drawdown([100])

    def test_non_positive_price_raises(self):
        with pytest.raises(ValueError):
            calculate_max_drawdown([100, -10, 50])

    def test_zero_price_raises(self):
        with pytest.raises(ValueError):
            calculate_max_drawdown([100, 0, 50])

    def test_non_list_raises(self):
        with pytest.raises(TypeError):
            calculate_max_drawdown(42)

    def test_inf_price_raises(self):
        with pytest.raises(ValueError, match="infinity"):
            calculate_max_drawdown([100, float("inf"), 80])


# ── compare_to_benchmark ──────────────────────────────────────────────────────

class TestCompareToBenchmark:
    def test_happy_path_returns_all_keys(self):
        port = [0.01, 0.02, -0.01, 0.03, 0.005]
        bench = [0.005, 0.015, -0.005, 0.02, 0.003]
        result = compare_to_benchmark(port, bench)
        for key in ("alpha", "beta", "correlation", "excess_return", "tracking_error"):
            assert key in result

    def test_perfect_correlation_beta_one(self):
        # Same returns → beta=1, alpha=0, correlation=1
        returns = [0.01, -0.01, 0.02, -0.005, 0.015]
        result = compare_to_benchmark(returns, returns)
        assert abs(result["beta"] - 1.0) < 1e-9
        assert abs(result["alpha"]) < 1e-9
        assert abs(result["correlation"] - 1.0) < 1e-9
        assert abs(result["excess_return"]) < 1e-9
        assert result["tracking_error"] == 0.0

    def test_mismatched_lengths_raises(self):
        with pytest.raises(ValueError, match="same length"):
            compare_to_benchmark([0.01, 0.02], [0.01])

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="empty"):
            compare_to_benchmark([], [])

    def test_zero_variance_benchmark_raises(self):
        with pytest.raises(ValueError, match="zero variance"):
            compare_to_benchmark([0.01, 0.02, 0.03], [0.0, 0.0, 0.0])

    def test_non_list_raises(self):
        with pytest.raises(TypeError):
            compare_to_benchmark("bad", [0.01])

    def test_inf_in_portfolio_raises(self):
        with pytest.raises(ValueError, match="infinity"):
            compare_to_benchmark([0.01, float("inf"), 0.02], [0.01, 0.01, 0.01])

    def test_beta_value_correct(self):
        # benchmark doubles the portfolio movement: beta should be ~0.5
        bench = [0.02, -0.02, 0.04, -0.04, 0.01]
        port  = [0.01, -0.01, 0.02, -0.02, 0.005]
        result = compare_to_benchmark(port, bench)
        assert abs(result["beta"] - 0.5) < 1e-9

    def test_overflow_raises_valueerror(self):
        # Extreme but finite inputs must surface a clean ValueError, not OverflowError
        with pytest.raises(ValueError):
            compare_to_benchmark([1e308, -1e308, 1e308], [1e308, -1e308, -1e308])


# ── analyze_memo_quality ──────────────────────────────────────────────────────

class TestAnalyzeMemoQuality:
    def test_happy_path_returns_all_keys(self):
        memo = (
            "This company has strong revenue growth and profit momentum. "
            "We expect a positive increase in earnings next quarter driven by "
            "favorable market conditions and robust demand."
        )
        result = analyze_memo_quality(memo)
        for key in ("word_count", "sentiment_score", "overconfidence_flags", "clarity_score", "recommendation"):
            assert key in result

    def test_overconfidence_detected(self):
        memo = "This investment is guaranteed to succeed with no risk whatsoever."
        result = analyze_memo_quality(memo)
        assert len(result["overconfidence_flags"]) > 0
        assert any(f in ("guaranteed", "no risk") for f in result["overconfidence_flags"])

    def test_clean_memo_no_flags(self):
        memo = (
            "The company faces headwinds from rising costs. "
            "However, management has outlined a credible plan to improve margins. "
            "We recommend a cautious position pending further data."
        )
        result = analyze_memo_quality(memo)
        assert result["overconfidence_flags"] == []

    def test_word_count_correct(self):
        memo = "The quick brown fox jumps over the lazy dog"
        result = analyze_memo_quality(memo)
        assert result["word_count"] == 9

    def test_word_count_includes_numeric_tokens(self):
        # Financial memos contain numbers — must not be silently dropped
        memo = "Q3 2024 earnings up 15% driven by strong growth"
        result = analyze_memo_quality(memo)
        assert result["word_count"] == 9

    def test_sentiment_bounds(self):
        memo = "Strong profit growth with positive upside momentum and favorable gains."
        result = analyze_memo_quality(memo)
        assert -1.0 <= result["sentiment_score"] <= 1.0

    def test_clarity_score_bounds(self):
        memo = "Short memo."
        result = analyze_memo_quality(memo)
        assert 0 <= result["clarity_score"] <= 100

    def test_empty_string_raises(self):
        with pytest.raises(ValueError, match="empty"):
            analyze_memo_quality("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError):
            analyze_memo_quality("   \n\t  ")

    def test_non_string_raises(self):
        with pytest.raises(TypeError):
            analyze_memo_quality(12345)
