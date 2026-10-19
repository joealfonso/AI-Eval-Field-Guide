#!/usr/bin/env python3
"""Checks for the sample-size page. Python 3 standard library only (node is optional).

    python3 build/test_sample_size.py

What it checks
  1. Wilson interval endpoints satisfy the defining equation (p_hat - p0)^2 = z^2 p0 (1 - p0) / n.
  2. n_for_margin gives the smallest n whose margin is within the target.
  3. n_independent and n_paired reach about the requested power when the power of the
     actual test is computed exactly (sums over the binomial / trinomial distributions).
  4. paired_difference matches a direct calculation from per-item 0/+1/-1 differences.
  5. js/sample-size.js returns the same numbers as build/sample_stats.py (needs node).
  6. If sample-size.html has been built, every figure in its static table appears in the page.

Reference numbers (also printed when the script runs, and used on the page):
  Worst-case 95% margin of error (accuracy near 50%), usual interval:
    n=50 -> 13.9, n=100 -> 9.8, n=200 -> 6.9, n=500 -> 4.4, n=1000 -> 3.1, n=5000 -> 1.4 points.
  Wilson 95% interval, 160 of 200 correct (80%): 73.9% to 85.0%.
  Items for a +/-5 point margin at 95%, accuracy near 50%: 385.
  Detect 80% vs 85%, independent samples, 95% confidence, 80% power: 906 items per system.
  Same detection, same items, systems disagree on 10% of items: 312 items.
"""
import json
import math
import pathlib
import shutil
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import sample_stats as S  # noqa: E402

FAILS = []


def check(cond, msg):
    if not cond:
        FAILS.append(msg)
        print("FAIL:", msg)


def close(a, b, tol, msg):
    check(abs(a - b) <= tol, "%s: %r vs %r (tol %r)" % (msg, a, b, tol))


# ---------------------------------------------------------------- 1 Wilson
def test_wilson():
    for n in (10, 30, 50, 100, 200, 1000):
        for k in range(0, n + 1, max(1, n // 10)):
            p = k / n
            lo, hi = S.wilson(p, n)
            check(0 <= lo <= p + 1e-12 and p - 1e-12 <= hi <= 1, "Wilson bounds order n=%d k=%d" % (n, k))
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


# ---------------------------------------------------------------- 2 margin and n
TABLE_N = (50, 100, 200, 500, 1000, 5000)


def test_margin():
    close(S.z_two_sided(0.95), 1.959963984540054, 1e-12, "z95")
    close(S.z_two_sided(0.90), 1.6448536269514722, 1e-12, "z90")
    close(S.z_two_sided(0.99), 2.5758293035489004, 1e-12, "z99")
    close(S.z_power(0.80), 0.8416212335729143, 1e-12, "z80")
    close(S.z_power(0.90), 1.2815515655446004, 1e-12, "z90 power")
    close(S.z_power(0.95), 1.6448536269514722, 1e-12, "z95 power")
    expect = {50: 13.9, 100: 9.8, 200: 6.9, 500: 4.4, 1000: 3.1, 5000: 1.4}
    for n, e in expect.items():
        got = round(S.worst_case_margin(n) * 100, 1)
        check(got == e, "worst-case margin n=%d: %s vs %s" % (n, got, e))
    for p in (0.5, 0.7, 0.9):
        for e in (0.02, 0.05, 0.1):
            n = S.n_for_margin(p, e)
            check(S.margin(p, n) <= e + 1e-12, "n_for_margin large enough p=%s e=%s" % (p, e))
            check(S.margin(p, n - 1) > e, "n_for_margin smallest p=%s e=%s" % (p, e))
    check(S.n_for_margin(0.5, 0.05) == 385, "385 items for +/-5 at 50%")
    check(S.n_for_margin(0.5, 0.03) == 1068, "1068 items for +/-3 at 50%")


# ---------------------------------------------------------------- 3 exact power
def log_binom_pmf(n, p):
    out = []
    for k in range(n + 1):
        if p in (0.0, 1.0):
            out.append(0.0 if (k == 0 and p == 0.0) or (k == n and p == 1.0) else -math.inf)
        else:
            out.append(math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1) + k * math.log(p) + (n - k) * math.log(1 - p))
    return out


def exact_power_independent(n, p1, p2, alpha=0.05):
    """Power of the pooled two-proportion z test with n items per group."""
    za = S.z_two_sided(1 - alpha)
    l1, l2 = log_binom_pmf(n, p1), log_binom_pmf(n, p2)
    power = 0.0
    for x1 in range(n + 1):
        for x2 in range(n + 1):
            pb = (x1 + x2) / (2 * n)
            if pb in (0.0, 1.0):
                continue
            z = abs(x1 - x2) / n / math.sqrt(2 * pb * (1 - pb) / n)
            if z > za:
                power += math.exp(l1[x1] + l2[x2])
    return power


def exact_power_paired(n, p10, p01, alpha=0.05):
    """Power of the McNemar chi-square test (no continuity correction) on n paired items."""
    za = S.z_two_sided(1 - alpha)
    p00 = 1 - p10 - p01
    power = 0.0
    lf = [math.lgamma(k + 1) for k in range(n + 2)]
    for b in range(n + 1):
        for c in range(n - b + 1):
            if b + c == 0:
                continue
            if (b - c) ** 2 / (b + c) > za * za:
                rest = n - b - c
                lp = lf[n] - lf[b] - lf[c] - lf[rest] + b * math.log(p10) + c * math.log(p01)
                lp += rest * math.log(p00) if rest else 0.0
                power += math.exp(lp)
    return power


def test_power():
    za, zb = S.z_two_sided(0.95), S.z_power(0.80)
    for p1, p2 in ((0.80, 0.85), (0.70, 0.80), (0.50, 0.60)):
        n = S.n_independent(p1, p2, za, zb)
        pw = exact_power_independent(n, p1, p2)
        print("independent %.2f vs %.2f: n=%d per system, exact power %.3f" % (p1, p2, n, pw))
        check(0.77 <= pw <= 0.84, "independent power near 0.80 for %s vs %s (got %.3f)" % (p1, p2, pw))
    for pd, delta in ((0.10, 0.05), (0.20, 0.05), (0.30, 0.10), (0.10, 0.03)):
        n = S.n_paired(pd, delta, za, zb)
        p10, p01 = (pd + delta) / 2, (pd - delta) / 2
        pw = exact_power_paired(n, p10, p01)
        print("paired pd=%.2f delta=%.2f: n=%d, exact power %.3f" % (pd, delta, n, pw))
        check(0.77 <= pw <= 0.84, "paired power near 0.80 for pd=%s delta=%s (got %.3f)" % (pd, delta, pw))
    check(S.n_independent(0.80, 0.85) == 906, "906 per system for 80 vs 85")
    check(S.n_paired(0.10, 0.05) == 312, "312 paired items for pd=10%, delta=5")
    # paired needs fewer items than independent when systems disagree on little
    check(S.n_paired(0.10, 0.05) < S.n_independent(0.80, 0.85), "paired smaller than independent at low disagreement")
    # page claim: a 3-point gap on 200 items on the same items is distinguishable only if disagreement < about 5%
    import math as _m
    z = S.z_two_sided(0.95)
    check(z * _m.sqrt((0.04 - 0.03 ** 2) / 200) < 0.03, "3-point gap detectable at 4% disagreement")
    check(z * _m.sqrt((0.06 - 0.03 ** 2) / 200) > 0.03, "3-point gap not detectable at 6% disagreement")
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


# ---------------------------------------------------------------- 5 JS parity
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
        "out.i2=[[0.8,0.85]].map(([a,b])=>s.nIndependent(a,b,s.Z_CONF['99'],s.Z_POWER['90']));"
        "out.p=[[0.1,0.05],[0.3,0.1],[0.2,-0.05]].map(([a,b])=>s.nPaired(a,b,s.Z_CONF['95'],s.Z_POWER['80']));"
        "out.d=[[200,20,10],[500,40,15]].map(([n,b,c])=>s.pairedDifference(n,b,c,s.Z_CONF['95']));"
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
    check(js["i2"][0] == S.n_independent(0.8, 0.85, S.z_two_sided(0.99), S.z_power(0.90)), "js nIndependent 99/90")
    for (a, b), got in zip([(0.1, 0.05), (0.3, 0.1), (0.2, -0.05)], js["p"]):
        check(got == S.n_paired(a, b), "js nPaired %s %s" % (a, b))
    for (n, b, c), got in zip([(200, 20, 10), (500, 40, 15)], js["d"]):
        d, se, lo, hi = S.paired_difference(n, b, c)
        close(got["diff"], d, 1e-12, "js paired diff")
        close(got["se"], se, 1e-12, "js paired se")
        close(got["low"], lo, 1e-12, "js paired low")
    print("js parity checked")


# ---------------------------------------------------------------- 6 page
def test_page():
    page = ROOT / "sample-size.html"
    if not page.exists():
        print("sample-size.html not built: skipping page check")
        return
    text = page.read_text(encoding="utf-8")
    for n in TABLE_N:
        check(format(n, ",") in text, "table row n=%d present" % n)
        m = "%.1f" % (S.worst_case_margin(n) * 100)
        check(m in text, "table margin %s for n=%d present" % (m, n))
    for needle in ("385", "906", "312"):
        check(needle in text, "worked-example figure %s present" % needle)


def main():
    test_wilson()
    test_margin()
    test_power()
    test_paired_difference()
    test_js()
    test_page()
    print()
    print("Worst-case 95%% margins: %s" % ", ".join("n=%d: %.1f" % (n, S.worst_case_margin(n) * 100) for n in TABLE_N))
    print("Wilson 160/200: %.1f%% to %.1f%%" % tuple(100 * x for x in S.wilson(0.8, 200)))
    if FAILS:
        print("\n%d check(s) failed" % len(FAILS))
        sys.exit(1)
    print("all checks passed")


if __name__ == "__main__":
    main()
