"""QueryPlanner tests (docs/SPEC.md §5.1). No network.

Closes a gap flagged when Phase 2 shipped: the planner was only verified
by a live manual check, not a committed test.
"""

from __future__ import annotations

from datetime import date

from logistics_rate_rag.chain.planner import QueryPlanner
from logistics_rate_rag.config import Carrier

CARRIERS = {
    "MERIDIAN": Carrier(
        display_name="Meridian Ocean Lines",
        aliases=["meridian", "meridian ocean", "meridian ocean lines", "mer"],
        currency="USD",
        baf_included=True,
        thc_included=False,
        tariff_refs=["MER-2026-H2-FCL", "MER-2026-Q2-FCL"],
    ),
    "HALCYON": Carrier(
        display_name="Halcyon Container Line",
        aliases=["halcyon", "halcyon container", "halcyon container line", "hal"],
        currency="EUR",
        baf_included=False,
        thc_included=False,
        tariff_refs=["HAL-2026-H2-FCL"],
    ),
}
SURCHARGE_KEYWORDS = [
    "baf",
    "bunker",
    "surcharge",
    "all-in",
    "all in",
    "including",
    "included",
    "thc",
    "terminal handling",
]

DEFAULT_AS_OF = date(2026, 9, 1)


def _planner() -> QueryPlanner:
    return QueryPlanner(CARRIERS, SURCHARGE_KEYWORDS)


def test_single_carrier_sets_filter():
    plan = _planner().plan("What is Halcyon's 40HC rate to Rotterdam?", DEFAULT_AS_OF)
    assert plan.filter == {"carrier": "HALCYON"}
    assert plan.carriers_mentioned == ("HALCYON",)


def test_no_carrier_mentioned_no_filter():
    plan = _planner().plan("What is the 40HC rate to Rotterdam?", DEFAULT_AS_OF)
    assert plan.filter is None
    assert plan.carriers_mentioned == ()


def test_both_carriers_mentioned_no_filter():
    plan = _planner().plan("Compare Meridian and Halcyon 40HC rates.", DEFAULT_AS_OF)
    assert plan.filter is None
    assert set(plan.carriers_mentioned) == {"MERIDIAN", "HALCYON"}


def test_alias_is_whole_word_not_substring():
    # "mer" is a MERIDIAN alias; "Bermuda" must not match it mid-word.
    plan = _planner().plan("What is the Bermuda triangle rate?", DEFAULT_AS_OF)
    assert plan.carriers_mentioned == ()


def test_as_of_override_in_question():
    plan = _planner().plan("What was the rate as of 2026-05-15?", DEFAULT_AS_OF)
    assert plan.as_of == date(2026, 5, 15)


def test_invalid_as_of_override_falls_back():
    plan = _planner().plan("What was the rate as of 2026-13-45?", DEFAULT_AS_OF)
    assert plan.as_of == DEFAULT_AS_OF


def test_no_as_of_override_uses_given_default():
    plan = _planner().plan("What is the current rate?", DEFAULT_AS_OF)
    assert plan.as_of == DEFAULT_AS_OF


def test_surcharge_keyword_detected():
    plan = _planner().plan("Is BAF included in the base rate?", DEFAULT_AS_OF)
    assert plan.mentions_surcharge is True


def test_no_surcharge_keyword():
    plan = _planner().plan("What is the 40HC rate to Rotterdam?", DEFAULT_AS_OF)
    assert plan.mentions_surcharge is False


def test_surcharge_keyword_whole_word_only():
    # "including" as a real word should match; a word that merely contains
    # the substring should not.
    plan = _planner().plan("Excluding terminal fees, what is the rate?", DEFAULT_AS_OF)
    assert plan.mentions_surcharge is False
