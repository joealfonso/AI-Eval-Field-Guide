"""Reference implementations for the sample-size page (sample-size.html).

Python standard library only. js/sample-size.js implements the same formulas;
build/test_sample_size.py checks the two agree and checks the formulas
against exact calculations. build/build.py uses these functions to fill in the
static table and worked examples on the page, so the page text cannot drift
from the code.

Which formula is used where (the page says the same):
  - Intervals for an observed score: Wilson (not the usual symmetric "Wald" interval).
  - Items for a target margin: the usual normal approximation z^2 p (1 - p) / e^2. A planning figure.
  - Two systems on separate items: Fleiss et al. normal approximation, no continuity correction
    (n_independent), and the same with Fleiss's continuity correction (n_independent_cc).
  - Two systems on the same items: Connor (1987) normal approximation (n_paired). An exact
    McNemar test needs somewhat more items; mcnemar_exact_p gives its p-value.

Sources for the methods are listed on the page:
  Wilson (1927), JASA 22(158), 209-212.
  Brown, Cai & DasGupta (2001), Statistical Science 16(2), 101-133.
  Miller (2024), arXiv:2411.00640 (standard errors, paired differences, power).
  Fleiss, Levin & Paik (2003), Statistical Methods for Rates and Proportions.
  Connor (1987), Biometrics 43(1) (sample size, paired proportions).
"""
import math
from statistics import NormalDist

_N = NormalDist()


def z_two_sided(confidence):
    """z for a two-sided interval, e.g. 0.95 -> 1.95996."""
    return _N.inv_cdf(1 - (1 - confidence) / 2)


def z_power(power):
    """z_beta for a one-sided power target, e.g. 0.80 -> 0.84162."""
    return _N.inv_cdf(power)


def wilson(p, n, z=1.959963984540054):
    """Wilson score interval for a proportion p observed on n items. Returns (low, high)."""
    if n <= 0:
        raise ValueError("n must be positive")
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z / denom * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return max(0.0, centre - half), min(1.0, centre + half)


def wilson_offsets(k, n, z=1.959963984540054):
    """How far the Wilson interval reaches below and above the observed share k/n, in
    proportions: (below, above). Symmetric at k/n = 0.5, asymmetric elsewhere."""
    p = k / n
    lo, hi = wilson(p, n, z)
    return p - lo, hi - p


def worst_case_margin(n, z=1.959963984540054):
    """Half-width of the usual (Wald) interval at p = 0.5. Used for planning only;
    the page's table uses Wilson intervals (wilson_offsets)."""
    return z * math.sqrt(0.25 / n)


def margin(p, n, z=1.959963984540054):
    """Half-width of the usual (Wald) interval, z * sqrt(p(1-p)/n)."""
    return z * math.sqrt(p * (1 - p) / n)


def n_for_margin(p, e, z=1.959963984540054):
    """Items needed so the usual interval has half-width e: ceil(z^2 p (1-p) / e^2)."""
    return math.ceil(z * z * p * (1 - p) / (e * e) - 1e-9)


def n_independent(p1, p2, za=1.959963984540054, zb=0.8416212335729143):
    """Items per system to detect p1 vs p2 on two separate item samples (Fleiss et al.)."""
    d = p1 - p2
    if d == 0:
        raise ValueError("difference must be non-zero")
    pbar = (p1 + p2) / 2
    num = (za * math.sqrt(2 * pbar * (1 - pbar)) + zb * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    return math.ceil(num / (d * d) - 1e-9)


def n_independent_cc(p1, p2, za=1.959963984540054, zb=0.8416212335729143):
    """As n_independent, with Fleiss's continuity correction
    n' = n/4 * (1 + sqrt(1 + 4 / (n |d|)))^2. More conservative; closer to what a
    continuity-corrected or exact test needs."""
    d = abs(p1 - p2)
    pbar = (p1 + p2) / 2
    if d == 0:
        raise ValueError("difference must be non-zero")
    num = (za * math.sqrt(2 * pbar * (1 - pbar)) + zb * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    n = num / (d * d)
    return math.ceil(n / 4 * (1 + math.sqrt(1 + 4 / (n * d))) ** 2 - 1e-9)


def n_paired(pd, delta, za=1.959963984540054, zb=0.8416212335729143):
    """Items needed to detect an accuracy difference delta when both systems run on
    the same items and pd is the share of items on which exactly one is right (Connor 1987).
    """
    if delta == 0:
        raise ValueError("difference must be non-zero")
    if pd < abs(delta) or pd <= delta * delta:
        raise ValueError("disagreement rate must be at least the difference")
    num = (za * math.sqrt(pd) + zb * math.sqrt(pd - delta * delta)) ** 2
    return math.ceil(num / (delta * delta) - 1e-9)


def paired_difference(n, b, c, z=1.959963984540054):
    """A minus B on the same n items. b = items only A got right, c = items only B got right.
    Standard error from the per-item differences (Miller 2024, eq. 7).
    Returns (difference, standard_error, low, high); standard_error is None if undefined.
    """
    if n < 2 or b < 0 or c < 0 or b + c > n:
        raise ValueError("bad counts")
    d = (b - c) / n
    ss = (b + c) - (b - c) ** 2 / n
    se = math.sqrt(max(ss, 0.0) / (n - 1) / n)
    return d, se, d - z * se, d + z * se


def mcnemar_exact_p(b, c):
    """Two-sided exact McNemar p-value: a binomial test of b against b + c at 1/2.
    b = items only A got right, c = items only B got right."""
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2.0 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def max_disagreements_for_gap(n, gap_items, method="normal", z=1.959963984540054):
    """Largest number of disagreements D = b + c for which a net gap of gap_items
    (b - c) on n items is significant at the level implied by z, for two systems scored on
    the same items. D must have the same parity as gap_items.
    method "normal": McNemar chi-square, gap^2 / D > z^2.
    method "exact": exact binomial McNemar test, p < 1 - confidence for z (z = 1.96 -> 0.05).
    Returns None if no D qualifies."""
    alpha = 2 * (1 - NormalDist().cdf(z))
    best = None
    for D in range(gap_items, n + 1):
        if (D - gap_items) % 2:
            continue
        b, c = (D + gap_items) // 2, (D - gap_items) // 2
        ok = (gap_items ** 2 / D > z * z) if method == "normal" else (mcnemar_exact_p(b, c) < alpha)
        if ok:
            best = D
    return best


def pilot_range(k, m, delta, za=1.959963984540054, zb=0.8416212335729143, z_pilot=1.959963984540054):
    """The disagreement rate from a pilot is itself uncertain. k of m pilot items had exactly
    one system right. Returns (rate_low, rate_high, n_low, n_high): the Wilson interval for
    the rate, and the items n_paired asks for at each end. The rate cannot be below the gap
    itself, so the low end is raised to |delta| when the interval reaches below it."""
    lo, hi = wilson(k / m, m, z_pilot)
    d = abs(delta)
    lo_used = max(lo, d)
    hi_used = max(hi, d)
    return lo, hi, n_paired(lo_used, d, za, zb), n_paired(hi_used, d, za, zb)


def _log_choose(n, k):
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


def _pmf(n, k, p):
    if p <= 0.0:
        return 1.0 if k == 0 else 0.0
    if p >= 1.0:
        return 1.0 if k == n else 0.0
    return math.exp(_log_choose(n, k) + k * math.log(p) + (n - k) * math.log(1 - p))


def exact_power_paired(n, pd, delta, alpha=0.05):
    """Exact power of the two-sided exact McNemar test on n items when a share pd of items
    has exactly one system right and system A is better by delta (both as proportions).
    Sums over the number of disagreements D ~ Binomial(n, pd), then over how they split."""
    q = (pd + delta) / (2 * pd)
    total = 0.0
    for D in range(1, n + 1):
        w = _pmf(n, D, pd)
        if w < 1e-18:
            continue
        # largest k with exact two-sided p = 2 * P(Binomial(D, 1/2) <= k) < alpha; -1 if none
        crit, cum = -1, 0.0
        for k in range(D // 2 + 1):
            cum += _pmf(D, k, 0.5)
            if min(1.0, 2 * cum) < alpha:
                crit = k
            else:
                break
        if crit < 0:
            continue
        sig = sum(_pmf(D, b, q) for b in range(0, crit + 1))
        sig += sum(_pmf(D, b, q) for b in range(D - crit, D + 1) if b > crit)
        total += w * sig
    return total


def n_paired_exact(pd, delta, power=0.80, alpha=0.05):
    """Smallest n at which the exact McNemar test reaches the target power (searching up from
    the normal-approximation answer; power rises with n in a slightly saw-toothed way)."""
    n = max(2, n_paired(pd, delta) - 20)
    while exact_power_paired(n, pd, delta, alpha) < power:
        n += 1
    return n
