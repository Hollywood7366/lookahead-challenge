# Trailing-window breakout repair

## The leak

The original `breakout_signals` computes `_mean(closes)` and
`_stdev(closes, mean)` once over the entire supplied series. It then uses
those full-sample statistics for every eligible bar. The configured window
only controls warm-up; it does not limit the normalization baseline.

Consequently, each eligible non-final bar can depend on later closes.
Appending future bars can create or erase an already-released signal. Even
the final bar uses observations older than its configured window when the
series is longer than that window. In a backtest, future price/volatility
information therefore changes historical entry decisions.

A deterministic counterexample, using whole ticks and `Decimal("1.0")`:

```python
cfg = BreakoutConfig(window=3, threshold=Decimal("1.0"))
breakout_signals([10, 10, 10, 12], cfg)
# Original: [False, False, False, True]
breakout_signals([10, 10, 10, 12, 1_000_000], cfg)[:4]
# Original: [False, False, False, False]
```

The future spike retroactively erases the signal at index 3.

## The fix and window boundary

Compute each eligible bar's mean and population standard deviation from:

```python
trailing = closes[i - cfg.window + 1 : i + 1]
```

This preserves the function's explicitly documented **inclusive** window and
existing first eligible index, `window - 1`. The configuration docstring's
conflicting reference to `window` predecessors is corrected. Including the
current released close is causal; excluding it would define a different
strategy and change warm-up, rather than merely repair this leak. A signal
is available only after that bar closes; this is not an assumption that a
trade can execute at the same close.

The repair preserves the frozen configuration, `BreakoutError`, population
variance, strict `z > threshold`, zero-variance behavior, integer tick inputs,
and Decimal-only arithmetic. The straightforward implementation costs
O(number_of_bars * window) time and O(window) temporary space.

For any prefix of length `m`, any appended suffix, and any `i < m`, the
warm-up decision is unchanged and the slice above contains identical values
in the prefix and extended inputs. The mean, deviation, z-score, and boolean
result are therefore unchanged. This establishes the causal property from
the implementation's dependency boundary, alongside the regression tests.

## Verification

No dependencies beyond Python's standard library are required:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -v
```

All 14 tests pass locally on Python 3.12.12 and 3.14.0. Coverage includes:

- The future-spike regression above, observed failing on the original code.
- 3,072 seeded prefix comparisons: four seeds, four window sizes, three
  Decimal thresholds, and every nonempty prefix of each 64-bar series.
- Positive/negative spikes, alternating extreme bars, flat and seeded suffixes.
- A genuinely positive fixture so an all-False implementation cannot pass.
- Expiration of old observations, inclusive warm-up, local zero variance,
  population rather than sample deviation, and strict threshold equality.
- Upward-only signals, large integer ticks, unchanged inputs/output shape,
  default configuration, existing errors, and frozen configuration.

These tests exercise deterministic synthetic data, not market data, and make
no claim about trading profitability.
