# The Lookahead Challenge

**Time: ~90 minutes. Python 3.11+, standard library only.**

This is a real module pattern from a live quantitative research lab's codebase
(ES futures, whole-tick prices, `Decimal` arithmetic — never float). One rule
governs everything here: **a signal for bar `i` may never use information from
any bar after `i`.** In trading, that's the difference between a backtest and
a fantasy.

## The files

- `breakout.py` — volatility breakout signal. Read the docstring. Then read the code.
- `synth.py` — deterministic synthetic closes for your tests. Not market data.

## Your three tasks

1. **Find the leak.** Something in `breakout_signals` violates the module's own
   documented invariant. Name exactly what it is and why it matters — in
   trading terms, not just code terms.
2. **Fix it.** Rewrite the computation so every bar's signal uses only data
   available at that bar. Keep the codebase conventions: whole-tick ints in,
   `Decimal` arithmetic, no floats, the existing `BreakoutError` type, and the
   frozen `BreakoutConfig`.
3. **Prove it.** Write a test that fails on the broken version and passes on
   your fix. The core property: *appending future bars must not change the
   signals of already-released bars.* A synthetic series with a large future
   spike is the obvious weapon — use it.

## How you're graded

- Did you name the actual leak (full-sample normalization), not a symptom? (35%)
- Does the fix use trailing data only, with conventions intact? (35%)
- Does your property test fail before and pass after? (30%)

70/100 advances to a conversation. The docstring is part of the test — read it
like a skeptic.
