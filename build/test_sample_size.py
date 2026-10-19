#!/usr/bin/env python3
"""Checks for the sample-size page. Python 3 standard library only (node is optional).

    python3 build/test_sample_size.py

What it checks
  1. Wilson interval endpoints satisfy the defining equation (p_hat - p0)^2 = z^2 p0 (1 - p0) / n,
     and agree with a separate bisection solver written in this file.
  2. n_for_margin gives the smallest n whose margin is within the target.
  3. n_independent, n_independent_cc and n_paired reach about the requested power when the power of
     the actual test is computed exactly (sums over the binomial / trinomial distributions);
     the exact McNemar sizes (n_paired_exact) are the smallest n that reach 80% power.
  4. paired_difference matches a direct calculation from per-item 0/+1/-1 differences.
  5. The thresholds behind the worked example (3-point gap on 200 items) and the pilot ranges
     match separate exact calculations.
  6. js/sample-size.js returns the same numbers as build/sample_stats.py (needs node).
  7. If sample-size.html has been built: the interval table, the short version and the worked
     examples are checked sentence by sentence, and every number printed in those sections must be
     either a computed result (recomputed here independently) or a declared scenario input.
  8. The statistics printed in downloads/*.md and the matching text on templates.html.
     Rules of thumb with no derivation are not allowed to come back (see test_downloads).

Reference numbers (also printed when the script runs, and used on the page):
  Wilson 95% interval, accuracy 50%: n=50 -> +/-13.4, 100 -> 9.6, 200 -> 6.9, 500 -> 4.4, 1000 -> 3.1, 5000 -> 1.4 points.
  Wilson 95% interval, accuracy 90%: n=50 -> -11.4/+5.7, 100 -> -7.4/+4.5, 200 -> -4.9/+3.4, 500 -> -2.9/+2.3,
    1000 -> -2.0/+1.7, 5000 -> -0.9/+0.8 points.
  Wilson 95% interval, 160 of 200 correct (80%): 73.9% to 85.0%.
  Items for a +/-10, +/-5, +/-3 point margin at 95%, accuracy near 50%: 97, 385, 1,068.
  Detect 80% vs 85%, independent samples, 95% confidence, 80% power: 906 items per system
    (945 with Fleiss's continuity correction).
  Same detection, same items, systems disagree on 10% of items: 312 (normal approximation), 337 (exact McNemar);
    on 20% of items: 626 and 658.
  A 3-point gap on 200 items (net 6 items) is significant at 5% only with at most 8 disagreements
    (McNemar normal approximation) or at most 6 (exact McNemar).
"""
import json
import math
import pathlib
import re
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import sample_stats as S  # noqa: E402

FAILS = []
Z95 = 1.959963984540054
TABLE_N = (50, 100, 200, 500, 1000, 5000)


def check(cond, msg):
    if not cond:
        FAILS.append(msg)
        print("FAIL:", msg)


def close(a, b, tol, msg):
    check(abs(a - b) <= tol, "%s: %r vs %r (tol %r)" % (msg, a, b, tol))


# ------------------------------------------------ independent reference code (does not use sample_stats)
def wilson_bisect(k, n, z=Z95):
    """Wilson interval by bisection on (p_hat - p0)^2 = z^2 p0 (1 - p0) / n, as a check on the closed form."""
    p = k / n

    def f(p0):
        return (p - p0) ** 2 - z * z * p0 * (1 - p0) / n

    def bis(a, b):
        for _ in range(200):
            m = (a + b) / 2
            if (f(m) > 0) == (f(a) > 0):
                a = m
            else:
                b = m
        return (a + b) / 2
    return (0.0 if k == 0 else bis(0.0, p)), (1.0 if k == n else bis(p, 1.0))


def binom_pmf(n, k, p):
    if p <= 0.0:
        return 1.0 if k == 0 else 0.0
    if p >= 1.0:
        return 1.0 if k == n else 0.0
    return math.exp(math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1) + k * math.log(p) + (n - k) * math.log(1 - p))


def mcnemar_exact_p(b, c):
    n = b + c
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(min(b, c) + 1)) / 2 ** n)


_SIG_CACHE = {}


def exact_sig(b, c):
    key = (b, c)
    if key not in _SIG_CACHE:
        _SIG_CACHE[key] = mcnemar_exact_p(b, c) < 0.05
    return _SIG_CACHE[key]


def power_paired(n, pd, delta, test):
    """Power of a paired test on n items by summing over (D, b): D disagreements ~ Bin(n, pd), b | D ~ Bin(D, q)."""
    q = (pd + delta) / (2 * pd)
    total = 0.0
    for D in range(1, n + 1):
        w = binom_pmf(n, D, pd)
        if w < 1e-18:
            continue
        total += w * sum(binom_pmf(D, b, q) for b in range(D + 1) if test(b, D - b))
    return total


def power_mcnemar_exact(n, pd, delta):
    return power_paired(n, pd, delta, exact_sig)


def power_mcnemar_chi(n, pd, delta):
    return power_paired(n, pd, delta, lambda b, c: (b + c) > 0 and (b - c) ** 2 / (b + c) > Z95 ** 2)


def power_independent(n, p1, p2, corrected=False, alpha=0.05):
    """Power of the pooled two-proportion z test, n items per group, optionally continuity corrected (Yates)."""
    za = S.z_two_sided(1 - alpha)
    l1 = [binom_pmf(n, k, p1) for k in range(n + 1)]
    l2 = [binom_pmf(n, k, p2) for k in range(n + 1)]
    power = 0.0
    for x1 in range(n + 1):
        if l1[x1] < 1e-14:
            continue
        for x2 in range(n + 1):
            w = l1[x1] * l2[x2]
            if w < 1e-16:
                continue
            pb = (x1 + x2) / (2 * n)
            if pb in (0.0, 1.0):
                continue
            diff = abs(x1 - x2) / n
            if corrected:
                diff = max(0.0, diff - 1.0 / n)
            if diff / math.sqrt(2 * pb * (1 - pb) / n) > za:
                power += w
    return power


# ---------------------------------------------------------------- 1 Wilson
def test_wilson():
    for n in (10, 30, 50, 100, 200, 1000):
        for k in range(0, n + 1, max(1, n // 10)):
            p = k / n
            lo, hi = S.wilson(p, n)
            check(0 <= lo <= p + 1e-12 and p - 1e-12 <= hi <= 1, "Wilson bounds order n=%d k=%d" % (n, k))
            blo, bhi = wilson_bisect(k, n)
            close(lo, blo, 1e-9, "Wilson low vs bisection n=%d k=%d" % (n, k))
            close(hi, bhi, 1e-9, "Wilson high vs bisection n=%d k=%d" % (n, k))
            for edge in (lo, hi):
                if 0 < edge < 1:
                    lhs = (p - edge) ** 2
                    rhs = S.z_two_sided(0.95) ** 2 * edge * (1 - edge) / n
                    close(lhs, rhs, 1e-12, "Wilson defining equation n=%d k=%d" % (n, k))
    lo, hi = S.wilson(0.8, 200)
    close(lo, 0.7391, 5e-4, "Wilson 160/200 low")
    close(hi, 0.8495, 5e-4, "Wilson 160/200 high")
    lo, hi = S.wilson(0.0, 20)
    close(lo, 0.0, 1e-12, "Wilson 0/20 low")
    close(hi, 0.1611, 5e-4, "Wilson 0/20 high")
    # The interval is asymmetric near the edge, and the symmetric (Wald) figure is too narrow below
    # and too wide above at 90% on small n. These are why the page table uses Wilson.
    below, above = S.wilson_offsets(45, 50)
    check(below > above, "Wilson interval at 90% is longer below than above")
    check(below > S.margin(0.9, 50) > above, "Wald 90%% margin sits between the Wilson offsets (%.3f)" % S.margin(0.9, 50))
    for n in TABLE_N:
        half = S.wilson_offsets(n // 2, n)
        close(half[0], half[1], 1e-12, "Wilson symmetric at 50%% n=%d" % n)
        widest = max(sum(S.wilson_offsets(round(q * n), n)) / 2 for q in (0.6, 0.7, 0.8, 0.9))
        check(half[0] >= widest - 1e-12, "Wilson half-width widest at 50%% n=%d" % n)


# ---------------------------------------------------------------- 2 margin and n
def test_margin():
    close(S.z_two_sided(0.95), 1.959963984540054, 1e-12, "z95")
    close(S.z_two_sided(0.90), 1.6448536269514722, 1e-12, "z90")
    close(S.z_two_sided(0.99), 2.5758293035489004, 1e-12, "z99")
    close(S.z_power(0.80), 0.8416212335729143, 1e-12, "z80")
    close(S.z_power(0.90), 1.2815515655446004, 1e-12, "z90 power")
    close(S.z_power(0.95), 1.6448536269514722, 1e-12, "z95 power")
    for p in (0.5, 0.7, 0.9):
        for e in (0.02, 0.05, 0.1):
            n = S.n_for_margin(p, e)
            check(S.margin(p, n) <= e + 1e-12, "n_for_margin large enough p=%s e=%s" % (p, e))
            check(S.margin(p, n - 1) > e, "n_for_margin smallest p=%s e=%s" % (p, e))
    check(S.n_for_margin(0.5, 0.10) == 97, "97 items for +/-10 at 50%")
    check(S.n_for_margin(0.5, 0.05) == 385, "385 items for +/-5 at 50%")
    check(S.n_for_margin(0.5, 0.03) == 1068, "1068 items for +/-3 at 50%")


# ---------------------------------------------------------------- 3 exact power
def test_power():
    za, zb = S.z_two_sided(0.95), S.z_power(0.80)
    for p1, p2 in ((0.80, 0.85), (0.70, 0.80), (0.50, 0.60)):
        n = S.n_independent(p1, p2, za, zb)
        pw = power_independent(n, p1, p2)
        print("independent %.2f vs %.2f: n=%d per system, exact power %.3f (uncorrected z test)" % (p1, p2, n, pw))
        check(0.77 <= pw <= 0.84, "independent power near 0.80 for %s vs %s (got %.3f)" % (p1, p2, pw))
    check(S.n_independent(0.80, 0.85) == 906, "906 per system for 80 vs 85")
    check(S.n_independent_cc(0.80, 0.85) == 945, "945 per system for 80 vs 85 with continuity correction")
    # the continuity-corrected test reaches about 80% power at 945, and the uncorrected 906 is too few for it
    pw944, pw945 = power_independent(944, 0.80, 0.85, corrected=True), power_independent(945, 0.80, 0.85, corrected=True)
    print("independent 80 vs 85, continuity-corrected test: power %.4f at 944, %.4f at 945" % (pw944, pw945))
    check(abs(pw945 - 0.80) < 0.003, "continuity-corrected power is about 0.80 at 945 (got %.4f)" % pw945)
    check(power_independent(906, 0.80, 0.85, corrected=True) < 0.79, "uncorrected 906 is too few for the corrected test")
    check(S.n_independent(0.80, 0.85) < S.n_independent_cc(0.80, 0.85), "correction raises n")
    for pd, delta in ((0.10, 0.05), (0.20, 0.05), (0.30, 0.10), (0.10, 0.03)):
        n = S.n_paired(pd, delta, za, zb)
        pw = power_mcnemar_chi(n, pd, delta)
        print("paired pd=%.2f delta=%.2f: n=%d, power of the McNemar chi-square test %.3f" % (pd, delta, n, pw))
        check(0.77 <= pw <= 0.84, "paired power near 0.80 for pd=%s delta=%s (got %.3f)" % (pd, delta, pw))
    check(S.n_paired(0.10, 0.05) == 312, "312 paired items for pd=10%, delta=5")
    check(S.n_paired(0.20, 0.05) == 626, "626 paired items for pd=20%, delta=5")
    # exact McNemar test: the planning formula is a little short, and n_paired_exact is the smallest n that reaches 80%
    for pd, n_norm, n_exact in ((0.10, 312, 337), (0.20, 626, 658)):
        check(S.n_paired_exact(pd, 0.05) == n_exact, "n_paired_exact pd=%s" % pd)
        p_norm, p_below, p_at = power_mcnemar_exact(n_norm, pd, 0.05), power_mcnemar_exact(n_exact - 1, pd, 0.05), power_mcnemar_exact(n_exact, pd, 0.05)
        print("paired pd=%.2f delta=0.05, exact McNemar test: power %.4f at %d, %.4f at %d, %.4f at %d" % (pd, p_norm, n_norm, p_below, n_exact - 1, p_at, n_exact))
        check(p_norm < 0.80, "exact test is under-powered at the normal-approximation n (pd=%s)" % pd)
        check(p_below < 0.80 <= p_at, "exact McNemar needs %d for pd=%s" % (n_exact, pd))
        close(S.exact_power_paired(n_exact, pd, 0.05), p_at, 1e-9, "exact_power_paired agrees with the separate enumeration pd=%s" % pd)
    # paired needs fewer items than independent when systems disagree on little
    check(S.n_paired(0.10, 0.05) < S.n_independent(0.80, 0.85), "paired smaller than independent at low disagreement")
    # symmetry
    check(S.n_independent(0.85, 0.80) == S.n_independent(0.80, 0.85), "independent symmetric")


# ---------------------------------------------------------------- 4 paired difference
def test_paired_difference():
    from statistics import stdev
    for n, b, c in ((200, 20, 10), (100, 5, 5), (500, 40, 15), (50, 0, 7)):
        diffs = [1] * b + [-1] * c + [0] * (n - b - c)
        d = sum(diffs) / n
        se = stdev(diffs) / math.sqrt(n)
        got = S.paired_difference(n, b, c)
        close(got[0], d, 1e-12, "paired diff mean")
        close(got[1], se, 1e-12, "paired diff se")
        close(got[2], d - S.z_two_sided(0.95) * se, 1e-12, "paired diff low")


# ---------------------------------------------------------------- 5 worked-example thresholds and pilot ranges
def f_pair(pd, delta=0.05, za=Z95, zb=None):
    zb = S.z_power(0.80) if zb is None else zb
    return math.ceil((za * math.sqrt(pd) + zb * math.sqrt(pd - delta * delta)) ** 2 / (delta * delta) - 1e-9)


def test_thresholds_and_pilot():
    n, gap = 200, 6  # a 3-point gap on 200 items is a net of 6 items
    # separate enumeration over every split (b, c) with b - c = 6
    sig_norm, sig_exact, sig_interval = [], [], []
    for D in range(gap, 60, 2):
        b, c = (D + gap) // 2, (D - gap) // 2
        if gap ** 2 / D > Z95 ** 2:
            sig_norm.append(D)
        if mcnemar_exact_p(b, c) < 0.05:
            sig_exact.append(D)
        d, se, lo, hi = S.paired_difference(n, b, c)
        if lo > 0:
            sig_interval.append(D)
    check(sig_norm == [6, 8], "McNemar normal approximation: significant only for D = 6, 8 (got %s)" % sig_norm)
    check(sig_exact == [6], "exact McNemar: significant only for D = 6 (got %s)" % sig_exact)
    check(sig_interval == [6, 8], "paired-difference interval (calculator 4) agrees with the normal test (got %s)" % sig_interval)
    check(S.max_disagreements_for_gap(200, 6, "normal") == 8, "max_disagreements normal")
    check(S.max_disagreements_for_gap(200, 6, "exact") == 6, "max_disagreements exact")
    # the earlier 'about 5%' came from the continuous formula d^2 (1 + n / z^2); integer counts give 4% and 3%
    close(0.03 ** 2 * (1 + n / Z95 ** 2), 0.04776, 1e-4, "continuous (no integer rounding) threshold is about 4.8%")
    # unpaired interval for 82% vs 79% on 200 items each
    half = Z95 * math.sqrt(0.82 * 0.18 / 200 + 0.79 * 0.21 / 200) * 100
    close(half, 7.76, 0.01, "unpaired 95% half-width for a 3-point gap on 200 items")
    # pilot uncertainty
    for k, m, nlo, nhi, rlo, rhi in ((5, 50, 155, 669, 0.0435, 0.2136), (10, 100, 172, 546, 0.0552, 0.1744)):
        lo, hi = wilson_bisect(k, m)
        close(lo, rlo, 5e-5, "pilot %d/%d rate low" % (k, m))
        close(hi, rhi, 5e-5, "pilot %d/%d rate high" % (k, m))
        got = S.pilot_range(k, m, 0.05)
        check(got[2] == nlo and got[3] == nhi, "pilot %d/%d implies %d to %d items (got %s)" % (k, m, nlo, nhi, got[2:]))
        check(f_pair(max(lo, 0.05)) == nlo and f_pair(hi) == nhi, "pilot %d/%d items from first principles" % (k, m))
    # an unclamped low end (rate 4.35%, below the 5-point gap itself) would give an impossible, smaller figure
    check(f_pair(0.0435) < 155, "unclamped low end would be smaller (and impossible)")


# ---------------------------------------------------------------- 6 JS parity
def test_js():
    node = shutil.which("node")
    if not node:
        print("node not found: skipping JS parity check")
        return
    script = (
        "const s=require(%s);const out={};"
        "out.w=[[0.8,200],[0.5,50],[0.0,20],[0.97,1000],[0.3,10]].map(([p,n])=>s.wilson(p,n,s.Z_CONF['95']));"
        "out.m=[[0.5,0.05],[0.7,0.03],[0.9,0.02]].map(([p,e])=>s.nForMargin(p,e,s.Z_CONF['95']));"
        "out.i=[[0.8,0.85],[0.7,0.8],[0.5,0.55]].map(([a,b])=>s.nIndependent(a,b,s.Z_CONF['95'],s.Z_POWER['80']));"
        "out.ic=[[0.8,0.85],[0.7,0.8],[0.5,0.55],[0.85,0.8]].map(([a,b])=>s.nIndependentCC(a,b,s.Z_CONF['95'],s.Z_POWER['80']));"
        "out.i2=[[0.8,0.85]].map(([a,b])=>s.nIndependent(a,b,s.Z_CONF['99'],s.Z_POWER['90']));"
        "out.p=[[0.1,0.05],[0.3,0.1],[0.2,-0.05]].map(([a,b])=>s.nPaired(a,b,s.Z_CONF['95'],s.Z_POWER['80']));"
        "out.d=[[200,20,10],[500,40,15]].map(([n,b,c])=>s.pairedDifference(n,b,c,s.Z_CONF['95']));"
        "out.mc=[[7,1],[6,0],[3,3],[12,2],[30,18],[0,0]].map(([b,c])=>s.mcnemarExactP(b,c));"
        "out.pr=[[5,50],[10,100],[2,40],[0,30]].map(([k,m])=>s.pilotRange(k,m,0.05,s.Z_CONF['95'],s.Z_POWER['80'],s.Z_CONF['95']));"
        "console.log(JSON.stringify(out));" % json.dumps(str(ROOT / "js/sample-size.js"))
    )
    r = subprocess.run([node, "-e", script], capture_output=True, text=True)
    if r.returncode != 0:
        check(False, "node failed: " + r.stderr)
        return
    js = json.loads(r.stdout)
    for (p, n), got in zip([(0.8, 200), (0.5, 50), (0.0, 20), (0.97, 1000), (0.3, 10)], js["w"]):
        lo, hi = S.wilson(p, n)
        close(got["low"], lo, 1e-12, "js wilson low %s %s" % (p, n))
        close(got["high"], hi, 1e-12, "js wilson high %s %s" % (p, n))
    for (p, e), got in zip([(0.5, 0.05), (0.7, 0.03), (0.9, 0.02)], js["m"]):
        check(got == S.n_for_margin(p, e), "js nForMargin %s %s" % (p, e))
    for (a, b), got in zip([(0.8, 0.85), (0.7, 0.8), (0.5, 0.55)], js["i"]):
        check(got == S.n_independent(a, b), "js nIndependent %s %s" % (a, b))
    for (a, b), got in zip([(0.8, 0.85), (0.7, 0.8), (0.5, 0.55), (0.85, 0.8)], js["ic"]):
        check(got == S.n_independent_cc(a, b), "js nIndependentCC %s %s" % (a, b))
    check(js["i2"][0] == S.n_independent(0.8, 0.85, S.z_two_sided(0.99), S.z_power(0.90)), "js nIndependent 99/90")
    for (a, b), got in zip([(0.1, 0.05), (0.3, 0.1), (0.2, -0.05)], js["p"]):
        check(got == S.n_paired(a, b), "js nPaired %s %s" % (a, b))
    for (n, b, c), got in zip([(200, 20, 10), (500, 40, 15)], js["d"]):
        d, se, lo, hi = S.paired_difference(n, b, c)
        close(got["diff"], d, 1e-12, "js paired diff")
        close(got["se"], se, 1e-12, "js paired se")
        close(got["low"], lo, 1e-12, "js paired low")
    for (b, c), got in zip([(7, 1), (6, 0), (3, 3), (12, 2), (30, 18), (0, 0)], js["mc"]):
        close(got, S.mcnemar_exact_p(b, c), 1e-12, "js mcnemarExactP %s %s" % (b, c))
        close(got, mcnemar_exact_p(b, c), 1e-12, "js mcnemarExactP vs separate %s %s" % (b, c))
    for (k, m), got in zip([(5, 50), (10, 100), (2, 40), (0, 30)], js["pr"]):
        py = S.pilot_range(k, m, 0.05)
        close(got["rateLow"], py[0], 1e-12, "js pilot rate low %s/%s" % (k, m))
        close(got["rateHigh"], py[1], 1e-12, "js pilot rate high %s/%s" % (k, m))
        check(got["nLow"] == py[2] and got["nHigh"] == py[3], "js pilot n range %s/%s" % (k, m))
    print("js parity checked")


# ---------------------------------------------------------------- 7 page
def strip_tags(h):
    h = re.sub(r"<[^>]+>", " ", h)
    h = h.replace("&amp;", "&").replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", h).strip()


def section(html, sec_id):
    m = re.search(r'<section[^>]*><h2 id="%s">.*?</section>' % re.escape(sec_id), html, re.S)
    return m.group(0) if m else ""


def number_tokens(text):
    return [t.rstrip(",.") for t in re.findall(r"\d[\d,]*(?:\.\d+)?", text)]


def fmt(x):
    return "%.1f" % x


def test_page():
    page = ROOT / "sample-size.html"
    if not page.exists():
        print("sample-size.html not built: skipping page check")
        return
    html = page.read_text(encoding="utf-8")
    results = set()  # numbers the page may print because they are computed here
    # scenario inputs and labels that are not results: the 200-item / 80% / 85% example, the 5-point gap,
    # 10% and 20% disagreement, the 82% vs 79% example (3-point gap = net 6 items), the 5 of 50 and 10 of 100 pilots,
    # the 95% level, the 1.96 in the formula, the 4% / 3% / 8 / 6 thresholds checked in test_thresholds_and_pilot,
    # 0% / 100% in "near 0% or 100%", and the 5% test level.
    inputs = {"200", "80", "85", "5", "10", "20", "82", "79", "50", "100", "95", "1.96", "1", "0", "3", "6", "4", "8", "45", "90"}

    # --- table: every cell, from a separate Wilson solver
    tbl = section(html, "table")
    check(bool(tbl), "interval table section present")
    rows = re.findall(r"<tr><td>([^<]+)</td><td>([^<]+)</td><td>([^<]+)</td></tr>", tbl)
    check([int(r[0].replace(",", "")) for r in rows] == list(TABLE_N), "table has one row per n in %s" % (TABLE_N,))
    for (n_txt, c50, c90) in rows:
        n = int(n_txt.replace(",", ""))
        lo, hi = wilson_bisect(n // 2, n)
        want50 = "±" + fmt((hi - lo) / 2 * 100)
        lo9, hi9 = wilson_bisect(round(0.9 * n), n)
        want90 = "−%s / +%s" % (fmt((0.9 - lo9) * 100), fmt((hi9 - 0.9) * 100))
        check(c50 == want50, "table n=%d 50%% cell %r vs %r" % (n, c50, want50))
        check(c90 == want90, "table n=%d 90%% cell %r vs %r" % (n, c90, want90))
        results.update(number_tokens(want50) + number_tokens(want90) + [n_txt])
    check("±8.3" not in tbl and "±5.9" not in tbl, "old symmetric 90% column is gone")
    lo45, hi45 = wilson_bisect(45, 50)
    sent = "45 correct out of 50 gives %s%% to %s%%" % (fmt(lo45 * 100), fmt(hi45 * 100))
    check(sent in strip_tags(tbl), "table note gives the asymmetric example: %s" % sent)
    results.update([fmt(lo45 * 100), fmt(hi45 * 100)])

    # --- short version and worked examples: sentence checks with independently computed numbers
    lo160, hi160 = wilson_bisect(160, 200)
    r160 = (fmt(lo160 * 100), fmt(hi160 * 100))
    n97, n385, n1068 = (math.ceil(Z95 ** 2 * 0.25 / e ** 2 - 1e-9) for e in (0.10, 0.05, 0.03))
    za, zb = Z95, S.z_power(0.80)
    p1, p2 = 0.8, 0.85
    d = p2 - p1
    pbar = (p1 + p2) / 2
    n0 = (za * math.sqrt(2 * pbar * (1 - pbar)) + zb * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2 / d ** 2
    n906 = math.ceil(n0)
    n945 = math.ceil(n0 / 4 * (1 + math.sqrt(1 + 4 / (n0 * d))) ** 2)
    n312, n626 = f_pair(0.10), f_pair(0.20)
    n337, n658 = 337, 658  # smallest n with exact power >= 0.80, re-verified just below
    check((n906, n945, n312, n626) == (906, 945, 312, 626), "independent recomputation of 906/945/312/626")
    check(power_mcnemar_exact(n337, 0.10, 0.05) >= 0.80 > power_mcnemar_exact(n337 - 1, 0.10, 0.05), "337 is the exact-test size for 10% disagreement")
    check(power_mcnemar_exact(n658, 0.20, 0.05) >= 0.80 > power_mcnemar_exact(n658 - 1, 0.20, 0.05), "658 is the exact-test size for 20% disagreement")
    half_unpaired = fmt(Z95 * math.sqrt(0.82 * 0.18 / 200 + 0.79 * 0.21 / 200) * 100)
    pilots = []
    for k, m in ((5, 50), (10, 100)):
        lo, hi = wilson_bisect(k, m)
        pilots.append((fmt(lo * 100), fmt(hi * 100), f_pair(max(lo, 0.05)), f_pair(hi)))
    results.update(r160 + (str(n97), str(n385), "{:,}".format(n1068), str(n906), str(n945), str(n312), str(n626), str(n337), str(n658), half_unpaired))
    for p in pilots:
        results.update([p[0], p[1], str(p[2]), str(p[3])])

    short = strip_tags(section(html, "short-version"))
    worked = strip_tags(section(html, "worked"))
    check(bool(short) and bool(worked), "short version and worked examples present")
    expect_short = [
        "the Wilson 95%% interval runs from %s%% to %s%%." % r160,
        "±10 points takes about %d items, ±5 about %d, and ±3 about %s" % (n97, n385, "{:,}".format(n1068)),
        "takes about %d items per system by the standard formula, or about %d with a continuity correction" % (n906, n945),
        "about %d by the normal approximation; an exact test needs about %d" % (n312, n337),
    ]
    for e in expect_short:
        check(e in short, "short version contains: %s" % e)
    expect_worked = [
        "a score of 80%% has a 95%% interval of %s%% to %s%%" % r160,
        "the 95%% interval for a 3-point gap is about ±%s points" % half_unpaired,
        "at most 8 (4%) by the McNemar normal-approximation test, or at most 6 (3%) by the exact McNemar test",
        "you need about %d items by the normal approximation, or about %d by an exact test" % (n312, n337),
        "about %d (exact: about %d)" % (n626, n658),
        "needs about %d items per system by the standard formula without a continuity correction, or about %d with it" % (n906, n945),
        "If 5 of 50 items disagree (10%%), the 95%% Wilson range for the true rate is %s%% to %s%%, and the items needed for a 5-point gap run from about %d to about %d" % pilots[0],
        "With 10 of 100, the range is %s%% to %s%% and the items needed run from about %d to about %d" % pilots[1],
    ]
    for e in expect_worked:
        check(e in worked, "worked examples contain: %s" % e)
    check("fewer than about 5% of items" not in worked + short, "the old 'fewer than about 5%' wording is gone")

    # --- every number printed in the table, the short version and the worked examples is accounted for
    scope = strip_tags(tbl) + " " + short + " " + worked
    unknown = sorted({t for t in number_tokens(scope) if t not in results and t not in inputs})
    check(not unknown, "numbers on the page with no computed value or declared input: %s" % unknown)
    toks = set(number_tokens(scope))
    missing = sorted(t for t in results if t not in toks)
    check(not missing, "computed values missing from the page: %s" % missing)
    # the page may only claim what the test covers
    check("Every figure above and in the table is checked" not in html, "page no longer claims 'every figure' is checked")
    check("checks every number in the interval table, the short version, and these worked examples" in html, "page describes what the test covers")
    print("page checked: %d table rows, %d computed values, %d declared inputs" % (len(rows), len(results), len(inputs)))


# ---------------------------------------------------------------- 8 downloads and templates page
DOWNLOAD_PCT_ALLOWED = {
    # results-reporting-template.md: worked example, labelled "invented numbers, for layout only"
    "78%", "74%", "82%", "71%", "66%", "75%", "95%",
    # eval-plan-one-pager.md: grader-agreement example, 45 of 50
    "90%", "79%", "96%",
}


def test_downloads():
    dl = ROOT / "downloads"
    texts = {f.name: f.read_text(encoding="utf-8") for f in sorted(dl.glob("*.md"))}
    check(len(texts) == 3, "three downloads present")
    for name, t in texts.items():
        body = re.sub(r"<!--.*?-->", "", t, flags=re.S)
        for tok in set(re.findall(r"\d+(?:\.\d+)?%", body)):
            check(tok in DOWNLOAD_PCT_ALLOWED, "%s: percentage %s is not an accounted-for figure" % (name, tok))
    plan, rep, ven = texts["eval-plan-one-pager.md"], texts["results-reporting-template.md"], texts["ai-vendor-questionnaire.md"]
    # unsourced rules of thumb must not come back as bare minimums
    for name, t in texts.items():
        for bad in ("at least 3 to 5", "50 to 100 is a reasonable start", "as a tie", "Treat a difference whose interval includes zero"):
            check(bad not in t, "%s no longer says %r" % (name, bad))
    check("there is no fixed minimum" in plan, "eval plan says repeats and variants have no fixed minimum")
    check("a pilot of 50 to 100 items gives only a rough rate" in plan, "eval plan hedges the pilot")
    check("Repeats reduce run-to-run noise only" in plan, "eval plan separates repeats from items")
    check("cover which items were drawn" in rep, "results template says intervals are over items")
    check("Interval excludes zero / includes zero (no difference shown)" in rep, "results template reading column")
    check("an interval on the gap between systems" in ven, "vendor questionnaire asks for an interval on the gap")
    # 45 of 50 in agreement: Wilson 95% = 78.6% to 95.7%, written as 'about 79% to 96%'
    lo, hi = wilson_bisect(45, 50)
    check(round(lo * 100) == 79 and round(hi * 100) == 96, "45/50 Wilson rounds to 79% and 96%")
    check("45 of 50 in agreement is 90%, but its 95% Wilson interval runs from about 79% to 96%" in plan, "eval plan example text")
    # results template example (invented numbers): 78% of 400, 71% of 400, paired +7 (+2 to +12)
    m = re.search(r"On 400 recent tickets, the assistant resolved 78% \(95% interval 74% to 82%\) against 71% \(66% to 75%\) for the current process; the paired difference is \+7 points \(\+2 to \+12\)", rep)
    check(bool(m), "results template example sentence present")
    for k, (a, b) in ((312, (74, 82)), (284, (66, 75))):
        lo, hi = wilson_bisect(k, 400)
        check((round(lo * 100), round(hi * 100)) == (a, b), "%d/400 Wilson rounds to %d%% to %d%%" % (k, a, b))
    check(round(312 / 400 * 100) == 78 and round(284 / 400 * 100) == 71, "78% and 71% of 400")
    # +7 (+2 to +12): a 5-point half-width on 400 items implies this disagreement rate; it must be a possible one
    se = 0.05 / Z95
    pd_implied = 400 * se ** 2 + 0.07 ** 2
    check(0.07 <= pd_implied <= 0.6, "example's paired interval implies a possible disagreement rate (%.3f)" % pd_implied)
    # the same text must be on the built templates page
    tpl = ROOT / "templates.html"
    if tpl.exists():
        th = strip_tags(tpl.read_text(encoding="utf-8"))
        for needle in ("there is no fixed minimum", "a pilot of 50 to 100 items gives only a rough rate", "Interval excludes zero / includes zero (no difference shown)", "an interval on the gap between systems"):
            check(needle in th, "templates.html contains: %s" % needle)
        for bad in ("at least 3 to 5", "50 to 100 is a reasonable start"):
            check(bad not in th, "templates.html no longer says %r" % bad)
    else:
        print("templates.html not built: skipping templates page check")
    print("downloads checked")


def main():
    test_wilson()
    test_margin()
    test_power()
    test_paired_difference()
    test_thresholds_and_pilot()
    test_js()
    test_page()
    test_downloads()
    print()
    print("Wilson 95%% at 50%%: %s" % ", ".join("n=%d: +/-%.1f" % (n, S.wilson_offsets(n // 2, n)[0] * 100) for n in TABLE_N))
    print("Wilson 95%% at 90%%: %s" % ", ".join("n=%d: -%.1f/+%.1f" % ((n,) + tuple(x * 100 for x in S.wilson_offsets(round(0.9 * n), n))) for n in TABLE_N))
    print("Wilson 160/200: %.1f%% to %.1f%%" % tuple(100 * x for x in S.wilson(0.8, 200)))
    if FAILS:
        print("\n%d check(s) failed" % len(FAILS))
        sys.exit(1)
    print("all checks passed")


if __name__ == "__main__":
    main()
