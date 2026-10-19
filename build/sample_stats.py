"""Reference implementations for the sample-size page (sample-size.html).

Python standard library only. js/sample-size.js implements the same formulas;
build/test_sample_size.py checks the two agree and checks the formulas
against exact calculations. build/build.py uses these functions to fill in the
static table and worked examples on the page, so the page text cannot drift
from the code.

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


def worst_case_margin(n, z=1.959963984540054):
    """Half-width of the usual (Wald) interval at p = 0.5, the widest it gets."""
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
