"""RateCandidate validation tests (docs/SPEC.md §6.1). No network."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from logistics_rate_rag.schema.candidate import RateCandidate


def test_minimal_refusal():
    c = RateCandidate(answerable=False)
    assert c.answerable is False
    assert c.rate_value is None


def test_upper_strips_carrier_and_ports():
    c = RateCandidate(answerable=False, carrier=" meridian ", origin="inmaa", destination="nlrtm")
    assert c.carrier == "MERIDIAN"
    assert c.origin == "INMAA"
    assert c.destination == "NLRTM"


def test_rate_value_whole_float_accepted():
    c = RateCandidate(answerable=True, rate_value=2224.0)
    assert c.rate_value == 2224
    assert isinstance(c.rate_value, int)


def test_rate_value_fractional_float_rejected():
    with pytest.raises(ValidationError):
        RateCandidate(answerable=True, rate_value=2224.5)


def test_rate_value_must_be_positive():
    with pytest.raises(ValidationError):
        RateCandidate(answerable=True, rate_value=0)
    with pytest.raises(ValidationError):
        RateCandidate(answerable=True, rate_value=-5)


def test_confidence_out_of_range_rejected():
    with pytest.raises(ValidationError):
        RateCandidate(answerable=False, confidence=1.5)
    with pytest.raises(ValidationError):
        RateCandidate(answerable=False, confidence=-0.1)


def test_confidence_default_zero():
    c = RateCandidate(answerable=False)
    assert c.confidence == 0.0


def test_unknown_container_type_rejected():
    with pytest.raises(ValidationError):
        RateCandidate(answerable=True, container_type="20RF")


def test_extra_field_rejected():
    with pytest.raises(ValidationError):
        RateCandidate.model_validate({"answerable": False, "unexpected_field": 1})
