"""Standard-library regression tests for causal, trailing-window signals."""
from __future__ import annotations

from dataclasses import FrozenInstanceError
from decimal import Decimal
import unittest

from lap.breakout import BreakoutConfig, BreakoutError, breakout_signals
from lap.synth import made_up_closes


class BreakoutSignalsTests(unittest.TestCase):
    def test_appending_future_spike_preserves_released_signals(self) -> None:
        closes = [10, 10, 10, 12]
        config = BreakoutConfig(window=3, threshold=Decimal("1.0"))
        before = breakout_signals(closes, config)
        self.assertEqual(before, [False, False, False, True])

        after = breakout_signals(closes + [1_000_000], config)
        self.assertEqual(after[: len(closes)], before)

    def test_seeded_prefix_invariance_for_every_release_boundary(self) -> None:
        for seed in (0, 7, 42, 1337):
            closes = made_up_closes(64, seed=seed)
            for window in (2, 3, 5, 20):
                for threshold in (Decimal("0.5"), Decimal("1.0"), Decimal("2.0")):
                    config = BreakoutConfig(window=window, threshold=threshold)
                    full = breakout_signals(closes, config)
                    for released in range(1, len(closes) + 1):
                        with self.subTest(
                            seed=seed,
                            window=window,
                            threshold=threshold,
                            released=released,
                        ):
                            self.assertEqual(
                                breakout_signals(closes[:released], config),
                                full[:released],
                            )

    def test_arbitrary_future_suffix_does_not_change_prefix(self) -> None:
        for seed in (3, 11, 42):
            closes = made_up_closes(40, seed=seed)
            config = BreakoutConfig(window=5, threshold=Decimal("0.5"))
            before = breakout_signals(closes, config)
            self.assertTrue(any(before), "fixture must exercise positive signals")
            for future in (
                [1_000_000],
                [-1_000_000],
                [1_000_000, -1_000_000] * 8,
                [closes[-1]] * 30,
                made_up_closes(30, seed=seed + 100),
            ):
                with self.subTest(seed=seed, future=future):
                    self.assertEqual(
                        breakout_signals(closes + future, config)[: len(closes)],
                        before,
                    )

    def test_only_configured_window_affects_current_signal(self) -> None:
        config = BreakoutConfig(window=3, threshold=Decimal("1.0"))
        window = [0, 2, 10]
        for old_close in (-1_000_000, 0, 1_000_000):
            with self.subTest(old_close=old_close):
                self.assertTrue(breakout_signals([old_close] + window, config)[-1])

    def test_warmup_and_first_complete_window(self) -> None:
        config = BreakoutConfig(window=3, threshold=Decimal("1.0"))
        self.assertEqual(breakout_signals([0], config), [False])
        self.assertEqual(breakout_signals([0, 2], config), [False, False])
        self.assertEqual(breakout_signals([0, 2, 10], config), [False, False, True])

    def test_zero_variance_is_not_a_breakout(self) -> None:
        config = BreakoutConfig(window=3, threshold=Decimal("-1"))
        self.assertEqual(breakout_signals([7] * 8, config), [False] * 8)
        self.assertFalse(breakout_signals([1_000_000, 7, 7, 7], config)[-1])

    def test_population_standard_deviation_is_preserved(self) -> None:
        # Population z=sqrt(2)>1.3; sample z=2/sqrt(3)<1.3.
        self.assertEqual(
            breakout_signals([0, 0, 3], BreakoutConfig(3, Decimal("1.3"))),
            [False, False, True],
        )

    def test_zero_variance_is_local_to_current_window(self) -> None:
        self.assertEqual(
            breakout_signals([0, 2, 2], BreakoutConfig(2, Decimal("0.5"))),
            [False, True, False],
        )

    def test_threshold_is_strict(self) -> None:
        # Mean=1, population stdev=1, so the last bar's z-score is exactly 1.
        self.assertEqual(
            breakout_signals([0, 2], BreakoutConfig(2, Decimal("1"))),
            [False, False],
        )
        self.assertEqual(
            breakout_signals([0, 2], BreakoutConfig(2, Decimal("0.999"))),
            [False, True],
        )

    def test_only_upward_breakouts_are_flagged(self) -> None:
        self.assertEqual(
            breakout_signals([2, 0], BreakoutConfig(2, Decimal("0.5"))),
            [False, False],
        )

    def test_large_integer_ticks_preserve_decimal_precision(self) -> None:
        offset = 10**20
        self.assertEqual(
            breakout_signals(
                [offset, offset + 2, offset + 10],
                BreakoutConfig(3, Decimal("1")),
            ),
            [False, False, True],
        )

    def test_defaults_output_shape_and_input_are_preserved(self) -> None:
        closes = made_up_closes(40, seed=42)
        original = closes.copy()
        result = breakout_signals(closes)
        self.assertEqual(result, breakout_signals(closes, BreakoutConfig()))
        self.assertEqual(len(result), len(closes))
        self.assertTrue(all(type(signal) is bool for signal in result))
        self.assertEqual(closes, original)

    def test_invalid_inputs_raise_existing_error(self) -> None:
        with self.assertRaises(BreakoutError):
            breakout_signals([])
        for window in (-1, 0, 1):
            with self.subTest(window=window), self.assertRaises(BreakoutError):
                breakout_signals([1, 2, 3], BreakoutConfig(window=window))

    def test_config_remains_frozen(self) -> None:
        config = BreakoutConfig()
        with self.assertRaises(FrozenInstanceError):
            config.window = 3  # type: ignore[misc]


if __name__ == "__main__":
    unittest.main()
