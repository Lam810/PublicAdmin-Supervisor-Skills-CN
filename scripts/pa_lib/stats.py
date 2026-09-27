"""Small, dependency-free statistics used by the harness.

- Cohen's kappa (Cohen 1960) for two annotators;
- Krippendorff's alpha (nominal / interval) for multi-rater blind scoring;
- paired bootstrap percentile intervals;
- set-based precision / recall / F1 for held-out structure prediction.
"""

from __future__ import annotations

import math
import random
from collections import Counter, defaultdict
from typing import Hashable, Iterable, Sequence


def cohen_kappa(pairs: Sequence[tuple[Hashable, Hashable]]) -> float:
    n = len(pairs)
    if n == 0:
        return float("nan")
    po = sum(1 for a, b in pairs if a == b) / n
    ca = Counter(a for a, _ in pairs)
    cb = Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    if pe >= 1.0:
        return 1.0 if po >= 1.0 else float("nan")
    return (po - pe) / (1 - pe)


def krippendorff_alpha(units: Iterable[Sequence[float | int | str | None]], level: str = "interval") -> float:
    """Krippendorff's alpha from a units x coders table (None = missing).

    Coincidence-matrix formulation; units with fewer than two values are not
    pairable and are skipped.
    """
    if level not in ("nominal", "interval"):
        raise ValueError("level must be 'nominal' or 'interval'")
    coinc: dict[tuple, float] = defaultdict(float)
    for unit in units:
        vals = [v for v in unit if v is not None]
        m = len(vals)
        if m < 2:
            continue
        for i, a in enumerate(vals):
            for j, b in enumerate(vals):
                if i != j:
                    coinc[(a, b)] += 1.0 / (m - 1)
    if not coinc:
        return float("nan")
    marg: dict = defaultdict(float)
    for (a, _), w in coinc.items():
        marg[a] += w
    n = sum(marg.values())

    def d2(a, b) -> float:
        if level == "nominal":
            return 0.0 if a == b else 1.0
        return (float(a) - float(b)) ** 2

    do = sum(w * d2(a, b) for (a, b), w in coinc.items()) / n
    values = list(marg)
    de = sum(marg[a] * marg[b] * d2(a, b) for a in values for b in values) / (n * (n - 1))
    if de == 0:
        return 1.0 if do == 0 else float("nan")
    return 1.0 - do / de


def mean(xs: Sequence[float]) -> float:
    return sum(xs) / len(xs) if xs else float("nan")


def bootstrap_ci(diffs: Sequence[float], n_boot: int = 5000, seed: int = 0, alpha: float = 0.05) -> tuple[float, float, float]:
    """Mean of paired differences with a percentile bootstrap CI (resampling units)."""
    xs = [d for d in diffs if d is not None and not math.isnan(d)]
    if not xs:
        return float("nan"), float("nan"), float("nan")
    rng = random.Random(seed)
    n = len(xs)
    boots = sorted(sum(xs[rng.randrange(n)] for _ in range(n)) / n for _ in range(n_boot))
    lo = boots[int(math.floor(alpha / 2 * n_boot))]
    hi = boots[min(n_boot - 1, int(math.ceil((1 - alpha / 2) * n_boot)) - 1)]
    return mean(xs), lo, hi


def set_f1(pred: set[str], gold: set[str]) -> float | None:
    """F1 between code sets; None when both are empty (the unit is skipped)."""
    if not pred and not gold:
        return None
    if not pred or not gold:
        return 0.0
    tp = len(pred & gold)
    if tp == 0:
        return 0.0
    p = tp / len(pred)
    r = tp / len(gold)
    return 2 * p * r / (p + r)
