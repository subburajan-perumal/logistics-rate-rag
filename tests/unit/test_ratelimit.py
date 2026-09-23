"""RateLimiter tests (docs/SPEC.md §5.6). No network; `time.sleep` is
monkeypatched so this stays fast rather than actually sleeping 30s+."""

from __future__ import annotations

from logistics_rate_rag.chain import ratelimit


def test_wait_does_not_sleep_on_first_call(monkeypatch):
    calls = []
    monkeypatch.setattr(ratelimit.time, "sleep", lambda s: calls.append(s))
    limiter = ratelimit.RateLimiter(min_interval_s=7.0)
    limiter.wait()
    assert calls == []


def test_wait_sleeps_remaining_interval(monkeypatch):
    times = iter([100.0, 100.0, 102.0, 102.0])
    monkeypatch.setattr(ratelimit.time, "monotonic", lambda: next(times))
    calls = []
    monkeypatch.setattr(ratelimit.time, "sleep", lambda s: calls.append(s))

    limiter = ratelimit.RateLimiter(min_interval_s=7.0)
    limiter.wait()  # now=100, last_return=None -> no sleep, last_return=100
    limiter.wait()  # now=102, elapsed=2, remaining=5 -> sleeps 5
    assert calls == [5.0]


def test_backoff_sleeps_exponentially(monkeypatch):
    calls = []
    monkeypatch.setattr(ratelimit.time, "sleep", lambda s: calls.append(s))
    limiter = ratelimit.RateLimiter(min_interval_s=7.0)
    limiter.backoff(0)
    limiter.backoff(1)
    limiter.backoff(2)
    assert calls == [30, 60, 120]
