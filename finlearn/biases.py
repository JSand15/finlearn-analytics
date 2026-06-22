"""Behavioral-finance bias catalog and detector.

This module ships a catalog of 60+ specific behavioral and cognitive biases that
commonly distort investment decisions, plus a lightweight heuristic detector that
flags the linguistic fingerprints of those biases in free text (investment memos,
research notes, trade rationales, journal entries).

Detection is intentionally simple and dependency-free: each bias carries a set of
lowercase trigger phrases, and a phrase is "detected" when it appears as a
case-insensitive substring of the input text. It is a heuristic screen, not a
classifier — use it to surface candidate biases for human review.

Public API:
    detect_biases(text)        -> list of biases found, with the phrases that matched
    analyze_biases(text)       -> structured report (counts, categories, density, advice)
    list_biases()              -> metadata for every bias in the catalog
    list_bias_categories()     -> the distinct category labels
    get_bias(key)              -> full metadata (incl. phrases) for one bias
    BIASES                     -> the immutable catalog tuple
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple, Union

from .utils import validate_text

# Category labels grouping the biases by the cognitive mechanism they stem from.
CONFIDENCE = "Confidence & Self-Perception"
RISK = "Loss & Risk"
ANCHORING = "Anchoring & Adjustment"
INFORMATION = "Information Processing"
SOCIAL = "Social & Herding"
PROBABILITY = "Probability & Statistics"
FRAMING = "Framing & Accounting"
TEMPORAL = "Temporal & Planning"
EMOTIONAL = "Emotional & Affective"
ATTENTION = "Memory & Attention"


@dataclass(frozen=True)
class BehavioralBias:
    """A single, specific behavioral-finance bias and its linguistic markers.

    Attributes:
        key: Stable snake_case identifier (unique across the catalog).
        name: Human-readable name.
        category: One of the module-level category labels.
        description: One-sentence, finance-specific explanation of the bias.
        phrases: Lowercase trigger phrases whose presence suggests the bias.
    """

    key: str
    name: str
    category: str
    description: str
    phrases: Tuple[str, ...]

    def find_matches(self, text_lower: str) -> List[str]:
        """Return the trigger phrases present in already-lowercased text."""
        return [phrase for phrase in self.phrases if phrase in text_lower]

    def as_metadata(self, include_phrases: bool = False) -> Dict[str, object]:
        """Return a JSON-friendly metadata dict for this bias."""
        data: Dict[str, object] = {
            "key": self.key,
            "name": self.name,
            "category": self.category,
            "description": self.description,
        }
        if include_phrases:
            data["phrases"] = list(self.phrases)
        return data


# ──────────────────────────────────────────────────────────────────────────────
# The catalog. 60 specific biases. Phrases MUST be lowercase (text is lowercased
# before matching). Keep keys and names unique.
# ──────────────────────────────────────────────────────────────────────────────
BIASES: Tuple[BehavioralBias, ...] = (
    # ── Confidence & Self-Perception ──────────────────────────────────────────
    BehavioralBias(
        "overconfidence", "Overconfidence Bias", CONFIDENCE,
        "Overestimating the accuracy of one's own forecasts and the certainty of a positive outcome.",
        ("guaranteed", "certain to", "will definitely", "cannot fail", "can't fail",
         "sure thing", "no doubt", "without a doubt", "can't go wrong", "slam dunk",
         "easy money", "impossible to lose"),
    ),
    BehavioralBias(
        "overprecision", "Overprecision", CONFIDENCE,
        "Stating point forecasts with unjustified precision, ignoring the wide range of possible outcomes.",
        ("will hit exactly", "exactly", "precisely", "to the dollar", "pinpoint",
         "down to the cent", "will reach exactly"),
    ),
    BehavioralBias(
        "illusion_of_control", "Illusion of Control", CONFIDENCE,
        "Believing one can control or reliably time outcomes that are largely random.",
        ("fully in control", "we control the", "control the outcome", "time the market",
         "timing the market", "manage the risk away", "i can steer"),
    ),
    BehavioralBias(
        "optimism_bias", "Optimism Bias", CONFIDENCE,
        "Systematically expecting favorable outcomes while underweighting the odds of things going wrong.",
        ("best case", "everything will go right", "only upside", "all upside",
         "smooth sailing", "nothing but blue skies", "what could go wrong"),
    ),
    BehavioralBias(
        "self_attribution", "Self-Attribution Bias", CONFIDENCE,
        "Crediting gains to one's own skill while blaming losses on bad luck or others.",
        ("due to my analysis", "because of my pick", "i called it", "thanks to my",
         "proves i was right", "my skill", "i nailed it"),
    ),
    BehavioralBias(
        "dunning_kruger", "Dunning-Kruger Effect", CONFIDENCE,
        "Limited expertise breeding inflated confidence about how easy the analysis is.",
        ("simple to understand", "anyone can see", "it's obvious", "easy to predict",
         "no expertise needed", "not rocket science"),
    ),
    BehavioralBias(
        "restraint_bias", "Restraint Bias", CONFIDENCE,
        "Overestimating one's ability to stay disciplined and resist impulsive selling or buying.",
        ("i can stay disciplined", "won't panic sell", "can resist the urge",
         "i'll be rational", "i won't get emotional", "i can hold through anything"),
    ),

    # ── Loss & Risk ───────────────────────────────────────────────────────────
    BehavioralBias(
        "loss_aversion", "Loss Aversion", RISK,
        "Feeling the pain of losses far more than the pleasure of equivalent gains.",
        ("can't afford to lose", "avoid any loss", "refuse to sell at a loss",
         "hate losing", "protect against any loss", "never take a loss"),
    ),
    BehavioralBias(
        "disposition_effect", "Disposition Effect", RISK,
        "Selling winners too early to lock in gains while holding losers hoping to break even.",
        ("lock in gains now", "sell the winner", "hold until it recovers",
         "wait for it to break even", "ride the loser", "let the winner go but keep"),
    ),
    BehavioralBias(
        "sunk_cost", "Sunk Cost Fallacy", RISK,
        "Continuing a losing position because of resources already committed rather than future merit.",
        ("already invested too much", "can't back out now", "we've come too far",
         "throwing away what we put in", "doubling down to recover", "in too deep"),
    ),
    BehavioralBias(
        "regret_aversion", "Regret Aversion", RISK,
        "Avoiding decisions that could later feel regrettable, even when they are sound.",
        ("would regret missing", "don't want to regret", "avoid the regret",
         "fear of regret", "can't risk the regret", "hate to look back and"),
    ),
    BehavioralBias(
        "zero_risk_bias", "Zero-Risk Bias", RISK,
        "Overvaluing the complete elimination of one small risk over a larger reduction of overall risk.",
        ("completely safe", "zero risk", "risk-free", "no downside",
         "eliminate all risk", "totally secure", "absolutely no risk"),
    ),
    BehavioralBias(
        "ambiguity_aversion", "Ambiguity Aversion", RISK,
        "Preferring known risks over unknown ones, avoiding opportunities that are hard to quantify.",
        ("too uncertain", "avoid the unknown", "can't quantify so avoid",
         "stick to what we know", "too murky", "prefer the familiar bet"),
    ),
    BehavioralBias(
        "endowment_effect", "Endowment Effect", RISK,
        "Valuing an asset more highly simply because one already owns it.",
        ("our position is worth more", "we own it so", "won't sell below cost",
         "it's worth more to us", "wouldn't buy it today but won't sell"),
    ),
    BehavioralBias(
        "status_quo_bias", "Status Quo Bias", RISK,
        "Defaulting to the current allocation and resisting change even when rebalancing is warranted.",
        ("keep things as they are", "no need to change", "leave it as is",
         "stay the course", "why change now", "don't rock the boat"),
    ),
    BehavioralBias(
        "ostrich_effect", "Ostrich Effect", RISK,
        "Avoiding negative information, such as not checking a portfolio during a drawdown.",
        ("ignore the bad news", "don't look at the losses", "avoid checking",
         "head in the sand", "stop watching the account", "rather not know"),
    ),

    # ── Anchoring & Adjustment ────────────────────────────────────────────────
    BehavioralBias(
        "anchoring", "Anchoring Bias", ANCHORING,
        "Over-relying on the first number seen (an initial price or estimate) as a reference point.",
        ("anchored to", "based on the initial price", "relative to the 52-week high",
         "starting from the original", "the reference price of", "first quoted at"),
    ),
    BehavioralBias(
        "purchase_price_anchoring", "Purchase-Price Anchoring", ANCHORING,
        "Fixating on the price originally paid when judging whether to hold or sell.",
        ("we paid", "our cost basis", "below what we bought", "get back to our entry",
         "break even on our purchase", "what i paid for it"),
    ),
    BehavioralBias(
        "round_number_bias", "Round-Number Bias", ANCHORING,
        "Treating psychologically round price levels as meaningful targets or barriers.",
        ("nice round number", "psychological level", "round figure",
         "the 100 level", "the 1000 level", "big round number"),
    ),
    BehavioralBias(
        "conservatism_bias", "Conservatism Bias", ANCHORING,
        "Under-reacting to new evidence and revising prior beliefs too slowly.",
        ("stick with the original estimate", "no need to update", "the old forecast still holds",
         "slow to revise", "wait and see before changing", "let's not overreact to the news"),
    ),
    BehavioralBias(
        "analyst_target_anchoring", "Analyst-Target Anchoring", ANCHORING,
        "Anchoring valuation judgments to published analyst price targets rather than independent analysis.",
        ("the price target is", "analysts peg it at", "street target of",
         "consensus target", "the analyst target says"),
    ),

    # ── Information Processing ─────────────────────────────────────────────────
    BehavioralBias(
        "confirmation_bias", "Confirmation Bias", INFORMATION,
        "Seeking and weighting evidence that supports a pre-existing thesis while discounting the rest.",
        ("confirms my view", "supports our thesis", "as i expected", "consistent with what i believed",
         "ignore the contrary", "proves my point", "just as i thought"),
    ),
    BehavioralBias(
        "selective_perception", "Selective Perception", INFORMATION,
        "Noticing only the data that fits one's expectations and filtering out the rest.",
        ("only the data that fits", "focus on the supportive", "disregard the rest",
         "cherry-pick", "cherry pick", "ignore what doesn't fit"),
    ),
    BehavioralBias(
        "availability_heuristic", "Availability Heuristic", INFORMATION,
        "Judging likelihood by how easily examples come to mind, e.g., recent headlines.",
        ("i just read", "in the news lately", "recent headlines", "top of mind",
         "everyone is talking about", "all over the media"),
    ),
    BehavioralBias(
        "recency_bias", "Recency Bias", INFORMATION,
        "Overweighting the most recent results and assuming the latest trend will persist.",
        ("based on last quarter", "recent trend will continue", "latest results show it will",
         "just kept going up", "momentum will persist", "the last few months prove"),
    ),
    BehavioralBias(
        "base_rate_neglect", "Base-Rate Neglect", INFORMATION,
        "Ignoring the underlying statistical base rate in favor of specific, vivid case details.",
        ("ignore the average", "the odds don't apply here", "forget the historical rate",
         "this is a unique situation", "stats don't apply", "different this time"),
    ),
    BehavioralBias(
        "representativeness", "Representativeness Heuristic", INFORMATION,
        "Judging an opportunity by how much it resembles a stereotype, e.g., 'the next big winner'.",
        ("the next amazon", "the next apple", "looks just like", "reminds me of the last winner",
         "fits the pattern of", "just like the last winner"),
    ),
    BehavioralBias(
        "narrative_fallacy", "Narrative Fallacy", INFORMATION,
        "Buying into a compelling story while neglecting whether the numbers support it.",
        ("the story makes sense", "compelling narrative", "it all fits the story",
         "great story stock", "such a good story", "the narrative is too good"),
    ),
    BehavioralBias(
        "hindsight_bias", "Hindsight Bias", INFORMATION,
        "Believing past events were obvious and predictable after the fact.",
        ("i knew it all along", "obvious in retrospect", "saw it coming",
         "predictable in hindsight", "should have known", "knew this would happen"),
    ),
    BehavioralBias(
        "survivorship_bias", "Survivorship Bias", INFORMATION,
        "Drawing conclusions only from winners while ignoring the failures that dropped out.",
        ("look at the winners", "the ones that succeeded", "ignore the failures",
         "only the survivors", "all the success stories"),
    ),
    BehavioralBias(
        "clustering_illusion", "Clustering Illusion", INFORMATION,
        "Perceiving meaningful patterns or streaks in what is actually random price noise.",
        ("clear pattern in the chart", "the streak proves", "hot streak",
         "obvious pattern", "connected for a reason", "the chart is forming a"),
    ),
    BehavioralBias(
        "curse_of_knowledge", "Curse of Knowledge", INFORMATION,
        "Assuming others share one's information, so it must already be reflected in the price.",
        ("everyone already knows", "common knowledge", "already priced in",
         "the market knows this already", "obviously everyone knows"),
    ),
    BehavioralBias(
        "outcome_bias", "Outcome Bias", INFORMATION,
        "Judging a decision by its result rather than the quality of the reasoning at the time.",
        ("it worked so it was right", "good result proves", "judge by the outcome",
         "the ends justify the pick", "made money so it was a good call"),
    ),
    BehavioralBias(
        "information_bias", "Information Bias", INFORMATION,
        "Seeking more data than is useful, believing extra information always improves the decision.",
        ("need more data before", "just one more report", "keep researching",
         "more analysis needed", "wait for more information", "analysis paralysis"),
    ),

    # ── Social & Herding ──────────────────────────────────────────────────────
    BehavioralBias(
        "herding", "Herding Bias", SOCIAL,
        "Following the crowd's trades instead of independent analysis.",
        ("everyone is buying", "the crowd is", "following the smart money",
         "join the herd", "everybody owns it", "all the funds are in"),
    ),
    BehavioralBias(
        "bandwagon_effect", "Bandwagon Effect", SOCIAL,
        "Adopting a position because it is popular and gaining momentum.",
        ("jumping on the bandwagon", "getting in while it's hot", "don't miss the wave",
         "ride the hype", "everyone's piling in"),
    ),
    BehavioralBias(
        "fomo", "Fear of Missing Out (FOMO)", SOCIAL,
        "Buying out of anxiety about missing further gains rather than a reasoned valuation.",
        ("can't miss this", "fear of missing out", "fomo", "last chance to get in",
         "before it's too late", "missing the boat", "everyone's getting rich but me"),
    ),
    BehavioralBias(
        "authority_bias", "Authority Bias", SOCIAL,
        "Deferring to a perceived expert or celebrity investor instead of evaluating the case.",
        ("the expert said", "the analyst recommends so", "the guru endorsed",
         "because warren buffett", "the ceo promised", "a famous investor bought"),
    ),
    BehavioralBias(
        "halo_effect", "Halo Effect", SOCIAL,
        "Letting a positive impression of a brand or CEO spill over into the stock's expected return.",
        ("great brand so great stock", "good management means", "because it's a beloved company",
         "the brand is loved so", "such a great product so the stock"),
    ),
    BehavioralBias(
        "home_bias", "Home Bias", SOCIAL,
        "Over-allocating to domestic assets and underweighting foreign opportunities.",
        ("prefer domestic", "stick to local companies", "only invest at home",
         "avoid foreign markets", "keep it in our own country"),
    ),
    BehavioralBias(
        "familiarity_bias", "Familiarity Bias", SOCIAL,
        "Favoring well-known names simply because they feel comfortable and recognizable.",
        ("i use their products", "a company i know", "familiar name",
         "brands i recognize", "stick to names i know"),
    ),
    BehavioralBias(
        "in_group_bias", "In-Group Bias", SOCIAL,
        "Favoring companies tied to one's own group, region, employer, or community.",
        ("companies like us", "our kind of business", "founders like me",
         "our community's pick", "people like us back this"),
    ),
    BehavioralBias(
        "commitment_bias", "Commitment & Consistency Bias", SOCIAL,
        "Sticking to a public position to appear consistent, even as evidence turns.",
        ("i committed publicly", "stand by my call", "won't flip-flop",
         "consistent with my prior", "i already told everyone", "can't reverse now"),
    ),

    # ── Probability & Statistics ──────────────────────────────────────────────
    BehavioralBias(
        "gamblers_fallacy", "Gambler's Fallacy", PROBABILITY,
        "Believing a reversal is 'due' after a run, as if independent moves must balance out.",
        ("due for a rebound", "has to go up now", "overdue for a bounce",
         "can't keep falling", "law of averages says", "due for a reversal"),
    ),
    BehavioralBias(
        "hot_hand_fallacy", "Hot-Hand Fallacy", PROBABILITY,
        "Expecting a winning streak to continue because recent picks worked out.",
        ("on a winning streak", "can't lose right now", "riding hot",
         "keeps winning so will continue", "i'm on a roll"),
    ),
    BehavioralBias(
        "probability_neglect", "Probability Neglect", PROBABILITY,
        "Fixating on the size of a potential payoff while ignoring how unlikely it is.",
        ("focus on the payoff not the odds", "ignore the probability", "the prize is huge",
         "doesn't matter how unlikely", "the payoff is what matters"),
    ),
    BehavioralBias(
        "conjunction_fallacy", "Conjunction Fallacy", PROBABILITY,
        "Judging a detailed, specific scenario as more likely than a broader one it is part of.",
        ("both will happen together", "all of these at once", "the perfect combination of events",
         "every one of these has to line up"),
    ),
    BehavioralBias(
        "disaster_myopia", "Disaster Myopia", PROBABILITY,
        "Underestimating the odds of rare crashes because none has happened recently.",
        ("hasn't crashed in years", "tail risk won't happen", "ignore the black swan",
         "crashes are rare so", "it can't happen here", "nothing ever goes to zero"),
    ),
    BehavioralBias(
        "pseudocertainty", "Pseudocertainty Effect", PROBABILITY,
        "Treating a highly probable outcome as if it were a sure thing.",
        ("virtually certain", "as good as guaranteed", "practically sure",
         "almost no chance of loss", "all but certain"),
    ),
    BehavioralBias(
        "ludic_fallacy", "Ludic Fallacy", PROBABILITY,
        "Modeling messy markets with the tidy, known odds of a game and ignoring model risk.",
        ("the model says it's safe", "the backtest proves", "monte carlo guarantees",
         "the simulation says", "the math says it can't"),
    ),

    # ── Framing & Accounting ──────────────────────────────────────────────────
    BehavioralBias(
        "framing_effect", "Framing Effect", FRAMING,
        "Reacting to how a fact is worded rather than its substance, e.g., 90% success vs 10% failure.",
        ("90% success rate", "only a 10% chance of loss", "glass half full",
         "sounds better as", "it's a win rate of", "framed the right way"),
    ),
    BehavioralBias(
        "mental_accounting", "Mental Accounting", FRAMING,
        "Treating money differently based on arbitrary mental buckets like 'house money'.",
        ("house money", "play money", "separate bucket", "this is my fun money",
         "found money", "it's only my gambling pot"),
    ),
    BehavioralBias(
        "money_illusion", "Money Illusion", FRAMING,
        "Focusing on nominal dollar figures while ignoring the effect of inflation on real returns.",
        ("nominal gains", "ignoring inflation", "the number is bigger",
         "doubled in dollars", "more dollars so richer"),
    ),
    BehavioralBias(
        "denomination_effect", "Denomination Effect", FRAMING,
        "Treating a low per-share price as 'cheap' regardless of valuation.",
        ("it's only pennies a share", "cheap at this price", "low share price so cheap",
         "penny stock so room to run", "so cheap per share"),
    ),
    BehavioralBias(
        "default_effect", "Default Effect", FRAMING,
        "Accepting the preset or default option instead of an active, considered choice.",
        ("just go with the default", "the standard allocation", "whatever's preset",
         "the recommended option", "leave it on default"),
    ),
    BehavioralBias(
        "anchoring_to_targets", "Goal-Anchoring Bias", FRAMING,
        "Framing decisions around hitting a self-set dollar goal rather than risk-adjusted merit.",
        ("need to hit my number", "until i reach my goal of", "once i make my target",
         "just need to get to", "my goal is exactly"),
    ),

    # ── Temporal & Planning ───────────────────────────────────────────────────
    BehavioralBias(
        "present_bias", "Present Bias (Hyperbolic Discounting)", TEMPORAL,
        "Overweighting immediate payoffs and undervaluing larger but delayed gains.",
        ("want returns now", "immediate payoff", "can't wait for the long term",
         "quick gains", "instant gratification", "need it to pay off fast"),
    ),
    BehavioralBias(
        "planning_fallacy", "Planning Fallacy", TEMPORAL,
        "Expecting projects and catalysts to land on time despite a track record of delays.",
        ("will be done on time", "no delays expected", "ahead of schedule",
         "everything is on track", "faster than expected", "they always ship on time"),
    ),
    BehavioralBias(
        "projection_bias", "Projection Bias", TEMPORAL,
        "Assuming current conditions, tastes, or moods will persist unchanged into the future.",
        ("current conditions will last", "today's demand will continue forever",
         "extrapolate the present", "this will always be in demand", "the boom will last forever"),
    ),
    BehavioralBias(
        "extrapolation_bias", "Extrapolation Bias", TEMPORAL,
        "Projecting a recent growth rate far into the future without mean reversion.",
        ("grows forever", "keeps compounding at this rate", "straight line up",
         "this growth is permanent", "will keep doubling", "up and to the right forever"),
    ),

    # ── Emotional & Affective ─────────────────────────────────────────────────
    BehavioralBias(
        "affect_heuristic", "Affect Heuristic", EMOTIONAL,
        "Letting an emotional 'feel' about a stock substitute for analysis of its fundamentals.",
        ("i love this company", "feels right", "my gut tells me", "exciting opportunity",
         "just feels good", "in love with the stock"),
    ),
    BehavioralBias(
        "wishful_thinking", "Wishful Thinking", EMOTIONAL,
        "Letting hopes about an outcome drive the forecast instead of evidence.",
        ("hope it goes up", "i wish", "fingers crossed", "praying it works",
         "hopefully it recovers", "i really need this to work"),
    ),
    BehavioralBias(
        "negativity_bias", "Negativity Bias", EMOTIONAL,
        "Giving disproportionate weight to bad news and downside scenarios.",
        ("focus on the bad news", "dwell on the risks", "only see downside",
         "catastrophizing", "everything is going to crash", "it's all falling apart"),
    ),
    BehavioralBias(
        "panic_selling", "Panic-Driven Action", EMOTIONAL,
        "Reacting to fear or euphoria with abrupt trades rather than a plan.",
        ("get me out now", "sell everything", "dump it all", "buy before it runs away",
         "i can't take it anymore", "pull the plug right now"),
    ),
    BehavioralBias(
        "euphoria_bias", "Euphoria Bias", EMOTIONAL,
        "Letting market exuberance inflate risk-taking and return expectations.",
        ("this time is different", "new paradigm", "to the moon", "can only go up",
         "the sky's the limit", "we're all going to be rich"),
    ),

    # ── Memory & Attention ────────────────────────────────────────────────────
    BehavioralBias(
        "salience_bias", "Salience Bias", ATTENTION,
        "Letting the most vivid or dramatic figure dominate attention over more relevant data.",
        ("the headline number", "eye-catching figure", "the dramatic number",
         "stands out so it must matter", "the big flashy stat"),
    ),
    BehavioralBias(
        "attentional_bias", "Attentional Bias", ATTENTION,
        "Fixating on a single metric or ticker to the exclusion of the broader picture.",
        ("can't stop watching", "fixated on", "glued to the ticker",
         "obsessing over", "checking it every minute", "staring at the price all day"),
    ),
    BehavioralBias(
        "recency_of_news", "News-Recency Bias", ATTENTION,
        "Letting the latest single news item drive a decision out of proportion to its importance.",
        ("because of today's news", "after this morning's headline", "this one article says",
         "the latest tweet", "breaking news so i'm acting"),
    ),
    BehavioralBias(
        "anchoring_to_highs", "High-Water-Mark Fixation", ATTENTION,
        "Fixating on a prior peak price as the 'real' value the asset should return to.",
        ("get back to its high", "it was worth more before", "down from its peak so it's cheap",
         "used to trade at", "back to all-time highs"),
    ),
)


# Fast lookup by key. Also enforces uniqueness at import time.
def _build_index() -> Dict[str, BehavioralBias]:
    index: Dict[str, BehavioralBias] = {}
    seen_names = set()
    for bias in BIASES:
        if bias.key in index:
            raise RuntimeError(f"Duplicate bias key in catalog: {bias.key!r}")
        if bias.name in seen_names:
            raise RuntimeError(f"Duplicate bias name in catalog: {bias.name!r}")
        if not bias.phrases:
            raise RuntimeError(f"Bias {bias.key!r} has no trigger phrases")
        for phrase in bias.phrases:
            if phrase != phrase.lower():
                raise RuntimeError(
                    f"Bias {bias.key!r} has non-lowercase phrase {phrase!r}; "
                    "phrases must be lowercase for case-insensitive matching"
                )
        index[bias.key] = bias
        seen_names.add(bias.name)
    return index


_BIAS_BY_KEY: Dict[str, BehavioralBias] = _build_index()


def detect_biases(text: str) -> List[Dict[str, object]]:
    """Detect behavioral biases whose linguistic markers appear in ``text``.

    Args:
        text: Free text to screen (e.g., an investment memo or trade rationale).

    Returns:
        A list of dicts, one per detected bias, each with keys ``key``, ``name``,
        ``category``, ``description``, and ``matched_phrases`` (the trigger phrases
        that fired). The list is ordered by the catalog order. Empty if nothing fired.

    Raises:
        TypeError: If ``text`` is not a string.
        ValueError: If ``text`` is empty or whitespace-only.

    Example:
        >>> hits = detect_biases("This is guaranteed to work, the next amazon!")
        >>> sorted(h["key"] for h in hits)
        ['overconfidence', 'representativeness']
    """
    validated = validate_text(text, "text")
    text_lower = validated.lower()

    detected: List[Dict[str, object]] = []
    for bias in BIASES:
        matched = bias.find_matches(text_lower)
        if matched:
            entry = bias.as_metadata()
            entry["matched_phrases"] = matched
            detected.append(entry)
    return detected


def analyze_biases(text: str) -> Dict[str, Union[int, float, str, List, Dict]]:
    """Produce a structured behavioral-bias report for a block of text.

    Args:
        text: Free text to analyze.

    Returns:
        Dictionary with the following keys:
            - bias_count (int): Number of distinct biases detected.
            - biases_detected (list[str]): Keys of the detected biases.
            - by_category (dict[str, list[str]]): Detected bias keys grouped by category.
            - details (list[dict]): Full per-bias detail (same shape as detect_biases).
            - bias_density_per_100_words (float): Detected biases per 100 words.
            - recommendation (str): Plain-English guidance based on the findings.

    Raises:
        TypeError: If ``text`` is not a string.
        ValueError: If ``text`` is empty or whitespace-only.
    """
    validated = validate_text(text, "text")
    details = detect_biases(validated)

    word_count = len(validated.split())
    by_category: Dict[str, List[str]] = {}
    for entry in details:
        by_category.setdefault(str(entry["category"]), []).append(str(entry["key"]))

    bias_count = len(details)
    density = round(bias_count / word_count * 100, 2) if word_count else 0.0

    if bias_count == 0:
        recommendation = (
            "No behavioral-bias language detected. The text reads neutrally; "
            "continue to support claims with data."
        )
    else:
        top_categories = sorted(by_category, key=lambda c: len(by_category[c]), reverse=True)
        lead = top_categories[0]
        recommendation = (
            f"Detected {bias_count} potential bias signal(s), concentrated in "
            f"'{lead}'. Review flagged language and pressure-test each claim against "
            "base rates and disconfirming evidence."
        )

    return {
        "bias_count": bias_count,
        "biases_detected": [str(e["key"]) for e in details],
        "by_category": by_category,
        "details": details,
        "bias_density_per_100_words": density,
        "recommendation": recommendation,
    }


def list_biases() -> List[Dict[str, str]]:
    """Return metadata (key, name, category, description) for every bias in the catalog."""
    return [bias.as_metadata() for bias in BIASES]  # type: ignore[misc]


def list_bias_categories() -> List[str]:
    """Return the distinct bias category labels, sorted alphabetically."""
    return sorted({bias.category for bias in BIASES})


def get_bias(key: str) -> Dict[str, object]:
    """Return full metadata (including trigger phrases) for a single bias.

    Args:
        key: The snake_case identifier of the bias (see ``list_biases``).

    Returns:
        Dict with keys ``key``, ``name``, ``category``, ``description``, ``phrases``.

    Raises:
        TypeError: If ``key`` is not a string.
        ValueError: If ``key`` does not match any bias in the catalog.
    """
    if not isinstance(key, str):
        raise TypeError(f"key must be a string, got {type(key).__name__}")
    bias = _BIAS_BY_KEY.get(key)
    if bias is None:
        raise ValueError(
            f"Unknown bias key: {key!r}. Use list_biases() to see the {len(BIASES)} available keys."
        )
    return bias.as_metadata(include_phrases=True)
