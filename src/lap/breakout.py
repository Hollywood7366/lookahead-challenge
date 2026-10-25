"""@file: src/lap/breakout.py
@history:
  2026-10-22: challenge scaffold — volatility breakout signal, trailing statistics only.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, getcontext

getcontext().prec = 28


class BreakoutError(ValueError):
    """Raised when breakout inputs are invalid."""


@dataclass(frozen=True)
class BreakoutConfig:
    """Configuration for the volatility breakout signal.

    window: number of trailing bars, including the current released bar,
        forming the mean/stdev baseline (>= 2). Bars with fewer than
        ``window - 1`` predecessors are never flagged.
    threshold: z-score above which a bar is flagged as a breakout.
    """

    window: int = 20
    threshold: Decimal = Decimal("2.0")


def _mean(values: list[int]) -> Decimal:
    return sum(Decimal(v) for v in values) / Decimal(len(values))


def _stdev(values: list[int], mean: Decimal) -> Decimal:
    n = Decimal(len(values))
    var = sum((Decimal(v) - mean) ** 2 for v in values) / n
    return var.sqrt()


def breakout_signals(
    closes: list[int], config: BreakoutConfig | None = None
) -> list[bool]:
    """Flag volatility breakouts using trailing statistics only.

    For each bar ``i``, the signal compares ``closes[i]`` against the mean and
    standard deviation of the ``window`` bars ending at ``i`` — only bars the
    caller has already released.

    Why it cannot look ahead: every statistic for bar ``i`` is computed from
    ``closes[max(0, i - window + 1) : i + 1]``, a slice that never includes a
    bar after ``i``. Appending future bars cannot change any earlier signal.

    Prices are whole ticks (int); arithmetic is Decimal, never float.

    Raises:
        BreakoutError: if ``closes`` is empty or ``config.window`` < 2.
    """
    cfg = config or BreakoutConfig()
    if not closes:
        raise BreakoutError("closes must not be empty")
    if cfg.window < 2:
        raise BreakoutError("window must be >= 2")

    signals: list[bool] = []
    for i, close in enumerate(closes):
        if i < cfg.window - 1:
            signals.append(False)
            continue
        trailing = closes[i - cfg.window + 1 : i + 1]
        mean = _mean(trailing)
        stdev = _stdev(trailing, mean)
        if stdev == 0:
            signals.append(False)
            continue
        z = (Decimal(close) - mean) / stdev
        signals.append(z > cfg.threshold)
    return signals
