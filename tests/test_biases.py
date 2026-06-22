"""Tests for the behavioral-bias catalog and detector (finlearn.biases)."""

import re

import pytest

from finlearn import (
    BIASES,
    BehavioralBias,
    detect_biases,
    analyze_biases,
    list_biases,
    list_bias_categories,
    get_bias,
    analyze_memo_quality,
)


# ── Catalog integrity ─────────────────────────────────────────────────────────

class TestCatalogIntegrity:
    def test_at_least_50_biases(self):
        assert len(BIASES) >= 50, f"catalog has only {len(BIASES)} biases; need 50+"

    def test_list_biases_matches_catalog(self):
        assert len(list_biases()) == len(BIASES)

    def test_keys_are_unique(self):
        keys = [b.key for b in BIASES]
        assert len(keys) == len(set(keys)), "duplicate bias keys present"

    def test_names_are_unique(self):
        names = [b.name for b in BIASES]
        assert len(names) == len(set(names)), "duplicate bias names present"

    def test_every_bias_is_specific(self):
        # Each bias must be fully specified: key, name, category, description, phrases.
        for b in BIASES:
            assert isinstance(b, BehavioralBias)
            assert b.key and re.fullmatch(r"[a-z0-9_]+", b.key), f"bad key: {b.key!r}"
            assert b.name.strip(), f"empty name for {b.key}"
            assert b.category.strip(), f"empty category for {b.key}"
            assert len(b.description.split()) >= 5, f"description too thin for {b.key}"
            assert len(b.phrases) >= 1, f"no phrases for {b.key}"

    def test_all_phrases_lowercase(self):
        for b in BIASES:
            for phrase in b.phrases:
                assert phrase == phrase.lower(), f"{b.key}: phrase not lowercase: {phrase!r}"

    def test_categories_nonempty_and_sorted(self):
        cats = list_bias_categories()
        assert len(cats) >= 5
        assert cats == sorted(cats)
        assert all(c.strip() for c in cats)


# ── Detection wiring ──────────────────────────────────────────────────────────

class TestDetection:
    def test_every_bias_is_detectable(self):
        # Feeding any one of a bias's own phrases must detect that bias.
        for b in BIASES:
            for phrase in b.phrases:
                hits = {d["key"] for d in detect_biases(f"prefix {phrase} suffix")}
                assert b.key in hits, f"{b.key} not detected by its phrase {phrase!r}"

    def test_detect_returns_matched_phrases(self):
        result = detect_biases("This is guaranteed to be a slam dunk.")
        oc = [d for d in result if d["key"] == "overconfidence"]
        assert oc, "overconfidence not detected"
        assert "guaranteed" in oc[0]["matched_phrases"]
        assert "slam dunk" in oc[0]["matched_phrases"]

    def test_detect_multiple_distinct_biases(self):
        memo = (
            "Everyone is buying this, it's the next amazon and guaranteed to work. "
            "We've already invested too much to back out now, and it's due for a rebound."
        )
        keys = {d["key"] for d in detect_biases(memo)}
        for expected in ("herding", "representativeness", "overconfidence",
                         "sunk_cost", "gamblers_fallacy"):
            assert expected in keys, f"expected {expected} in {keys}"

    def test_detect_is_case_insensitive(self):
        keys = {d["key"] for d in detect_biases("This is GUARANTEED to work.")}
        assert "overconfidence" in keys

    def test_clean_text_detects_nothing(self):
        memo = (
            "The company reported revenue of 4.2 billion dollars, up from 3.9 billion. "
            "Operating margin held at 18 percent. We model a base scenario and a downside scenario."
        )
        assert detect_biases(memo) == []

    def test_detect_empty_raises(self):
        with pytest.raises(ValueError, match="empty"):
            detect_biases("")

    def test_detect_whitespace_raises(self):
        with pytest.raises(ValueError):
            detect_biases("   \n\t ")

    def test_detect_non_string_raises(self):
        with pytest.raises(TypeError):
            detect_biases(12345)


# ── analyze_biases report ─────────────────────────────────────────────────────

class TestAnalyzeBiases:
    def test_report_has_all_keys(self):
        result = analyze_biases("This is guaranteed to work, the next amazon.")
        for key in ("bias_count", "biases_detected", "by_category", "details",
                    "bias_density_per_100_words", "recommendation"):
            assert key in result

    def test_count_matches_detected(self):
        memo = "Everyone is buying and it's guaranteed, a sure thing."
        result = analyze_biases(memo)
        assert result["bias_count"] == len(result["biases_detected"])
        assert result["bias_count"] == len(result["details"])
        assert result["bias_count"] > 0

    def test_by_category_groups_keys(self):
        result = analyze_biases("guaranteed to be the next amazon, everyone is buying")
        flat = [k for keys in result["by_category"].values() for k in keys]
        assert sorted(flat) == sorted(result["biases_detected"])

    def test_density_is_computed(self):
        result = analyze_biases("guaranteed sure thing")  # 3 words, overconfidence fires
        assert result["bias_density_per_100_words"] > 0

    def test_clean_text_zero_and_neutral_recommendation(self):
        result = analyze_biases("Revenue rose four percent on steady demand and stable margins.")
        assert result["bias_count"] == 0
        assert "No behavioral-bias language" in result["recommendation"]

    def test_non_string_raises(self):
        with pytest.raises(TypeError):
            analyze_biases(None)


# ── get_bias / list helpers ───────────────────────────────────────────────────

class TestLookupHelpers:
    def test_get_bias_returns_full_metadata(self):
        bias = get_bias("loss_aversion")
        assert bias["key"] == "loss_aversion"
        assert bias["name"] == "Loss Aversion"
        assert isinstance(bias["phrases"], list) and bias["phrases"]
        assert "category" in bias and "description" in bias

    def test_get_bias_unknown_key_raises_valueerror(self):
        with pytest.raises(ValueError, match="Unknown bias key"):
            get_bias("not_a_real_bias")

    def test_get_bias_non_string_raises_typeerror(self):
        with pytest.raises(TypeError):
            get_bias(42)

    def test_list_biases_entries_have_no_phrases(self):
        # The lightweight listing should not leak the phrase lists.
        for entry in list_biases():
            assert set(entry.keys()) == {"key", "name", "category", "description"}

    def test_every_listed_key_is_gettable(self):
        for entry in list_biases():
            assert get_bias(entry["key"])["key"] == entry["key"]


# ── memo integration ──────────────────────────────────────────────────────────

class TestMemoIntegration:
    def test_memo_exposes_behavioral_biases(self):
        result = analyze_memo_quality("This is guaranteed to be the next amazon.")
        assert "behavioral_biases" in result
        assert "overconfidence" in result["behavioral_biases"]
        assert "representativeness" in result["behavioral_biases"]

    def test_clean_memo_has_no_biases(self):
        memo = (
            "The company faces headwinds from rising costs. Management outlined a "
            "credible plan to improve margins. We recommend a cautious position pending data."
        )
        result = analyze_memo_quality(memo)
        assert result["behavioral_biases"] == []
