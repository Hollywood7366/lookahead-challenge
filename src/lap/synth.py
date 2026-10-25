"""@file: src/lap/synth.py
@history:
  2026-10-22: challenge scaffold — deterministic synthetic closes for tests.
"""
from __future__ import annotations

import random


def made_up_closes(n: int, seed: int = 42) -> list[int]:
    """Deterministic synthetic closing prices in whole ticks (int).

    Made-up bars for tests and the demo. Never market data.
    """
    rng = random.Random(seed)
    closes: list[int] = []
    px = 5000
    for _ in range(n):
        px += rng.randint(-4, 5)
        closes.append(px)
    return closes
