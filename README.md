# The Lookahead Challenge

## Who we are

We're building a quantitative research lab — 2.5 years in the making, tens of thousands in personal investment, two servers, 20TB of NVMe, all the data in place. A data engineer and a data scientist are already on the team.

Two tracks under one roof:

1. **Traditional quant arm** — evolutionary strategy generation over multilayer architectures, classic ML and deep learning, meta-ensembles for portfolio optimization. Run like a real quant fund: rigorous data discipline, professional-level tick data plus live collection.
2. **Cutting-edge arm** — compressing market data and labeling systems into multilayer state machines, to make probabilistic decisions deterministic. Traditional price action trading, autonomous research loops doing the exploring.

The bet tying it together: autonomous research. AI agents do the exploring — generating, testing, and killing ideas — while humans set the rules of the game. **If you can compress it, you've found real structure. Everything else is noise.**

## The challenge

Our hard rule #1 is **never look ahead**: decision code may only ever see released bars. It sounds obvious. It ruins more backtests than any other single bug.

In `src/lap/breakout.py` you'll find a small volatility-breakout module in the style of our real codebase. **It has a lookahead leak planted in it.** Your job:

1. **Find it** — say exactly what leaks, which bars are affected, and why it violates the invariant *"adding later bars must never change an earlier value."*
2. **Fix it** — compute thresholds from trailing data only. Keep the module's style: frozen dataclass config, explicit error types, whole ticks as ints, money as Decimal — never float.
3. **Prove it** — add `tests/test_breakout.py` (unittest style, seeded fixtures like `src/lap/synth.py`) with the property test: **appending future bars must not change signals for already-released bars.**

`src/lap/synth.py` gives you deterministic synthetic closes for testing. Never market data — same as our real fixtures.

## What happens if you solve it

This isn't a job posting with a coding screen. It's a filter for one specific person: a generalist with real mileage who's built trading systems before, is AI-native, and is genuinely obsessed with markets.

If your solution is good, the next step is a conversation about joining the lab as a **collaborator, not an employee**:

- A real seat at the table — not a ticket queue
- Part of the upside — in the system and the profits — with no risk on your end
- All compute paid for
- If we find real edge, a serious conversation about compensation and profit share

Upfront, because I'd rather lose you now than later: **no salary on day one.** I'm filtering for someone who'd do this because it's the most interesting problem they can imagine. If that sentence annoyed you, we're not for each other.

After the challenge: short screening questions, then a ~90-minute technical test drawn from the actual codebases. If all of that sounds like a good time instead of a chore, send your solution and a link to systems you've built to **hollywood736@gmail.com** — plus one trading idea you believe is true.

— Nicholas Laird
