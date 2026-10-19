#!/usr/bin/env python3
"""Regression tests for the claim checker's rules.

Runs sample claims through the real rules in data/editorial.json (claimChecker) using the same scoring
as js/claim-match.js (detect -> types -> rules -> repeat-hit boost -> sort -> how many to show), and
checks which patterns must be near the top and which must not appear at all.

    python3 build/test_claim_checker.py          # table of results, exit 1 on any failure
    python3 build/test_claim_checker.py -v       # also print the shown patterns for every claim

Each case has several wordings of one kind of claim, so a rule that only works for one exact
sentence fails. "include" patterns must be among the patterns shown by default (not hidden behind
"show more"); "exclude" patterns must not appear in the results at all.

If node is available, the same claims are also run through the real JavaScript and the answers are
compared with the Python port, so the two cannot drift apart. Python standard library only.
"""
import json
import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------- port of js/claim-match.js
FIT = {"strong": 3, "likely": 2, "worth": 1}
LIMIT = 8
MIN_SHOWN = 4


def norm(text):
    return re.sub("[‘’]", "'", str(text or ""))


def detect(claim, text):
    t = norm(text)
    return [ty["id"] for ty in claim["types"] if re.search(ty["detect"], t, re.I)]


def compute(claim, text, types):
    t = norm(text)
    m = {}

    def add(rule, pos):
        f = FIT[rule["fit"]]
        cur = m.get(rule["no"])
        if cur is None:
            m[rule["no"]] = {"no": rule["no"], "fit": f, "why": rule["why"], "ask": rule["ask"], "hits": 1, "pos": pos}
            return
        cur["hits"] += 1
        cur["pos"] = min(cur["pos"], pos)
        if f > cur["fit"]:
            cur.update(fit=f, why=rule["why"], ask=rule["ask"])

    for ty in claim["types"]:
        if ty["id"] in types:
            for i, r in enumerate(ty["laws"]):
                add(r, i)
    for mod in claim["modifiers"]:
        if re.search(mod["detect"], t, re.I):
            add(mod, 1)
    out = list(m.values())
    for r in out:
        if r["hits"] >= 2 and r["fit"] < 3:
            r["fit"] += 1
    out.sort(key=lambda r: (-r["fit"], -r["hits"], r["pos"], r["no"]))
    return out


def visible_count(results):
    firm = len([r for r in results if r["fit"] >= 2])
    n = min(firm, LIMIT)
    if n < MIN_SHOWN:
        n = min(len(results), MIN_SHOWN)
    return n


# ---------------------------------------------------------------- the real rules
def load_claim():
    edit = json.loads((ROOT / "data/editorial.json").read_text(encoding="utf-8"))
    laws = json.loads((ROOT / "data/laws.json").read_text(encoding="utf-8"))
    nums = {l["slug"]: l["no"] for l in laws}
    cc = edit["claimChecker"]
    claim = {
        "types": [{"id": t["id"], "label": t["label"], "detect": t["detect"], "laws": [dict(r, no=nums[r["slug"]]) for r in t["laws"]]} for t in cc["types"]],
        "modifiers": [dict(m, no=nums[m["slug"]]) for m in cc["modifiers"]],
    }
    nquestions = {slug: len(edit["laws"][slug]["questions"]) for slug in edit["laws"]}
    return claim, nums, nquestions, cc


# ---------------------------------------------------------------- cases
# texts: several wordings of the same kind of claim. types: claim types that must be detected in every wording.
# include: patterns that must be shown by default. exclude: patterns that must not appear at all.
# none: no claim type and no pattern may come back (the "No claim type detected" state).
CASES = [
    dict(name="Benchmark score, internal benchmark",
         texts=["Our assistant scores 94% on MMLU-Pro and beats leading models on our internal benchmark.",
                "The model reached 94% on our in-house eval set and outperforms competitors."],
         types=["benchmark", "comparison"],
         include=["goodharts-law", "no-error-bars-no-result", "the-baseline-rule", "adaptive-overfitting"],
         exclude=["judge-bias"]),
    dict(name="Public benchmark accuracy",
         texts=["GPT-Next achieves 87.3% accuracy on GSM8K.",
                "Scored 91% on HumanEval, up from 84%.",
                "The new release hits 62 on the leaderboard."],
         types=["benchmark"],
         include=["data-contamination", "no-error-bars-no-result", "the-construct-gap"],
         exclude=["judge-bias", "criteria-drift", "the-lab-to-field-gap"]),
    dict(name="Model A beats model B",
         texts=["Model A outperforms Model B on every benchmark we tested.",
                "Our model is better than GPT-4 across the board.",
                "Ahead of the competition on all tasks."],
         types=["comparison"],
         include=["the-baseline-rule", "the-benchmark-lottery", "no-error-bars-no-result"],
         exclude=["judge-bias", "evaluation-awareness"]),
    dict(name="State of the art and cheaper",
         texts=["Our new model is state-of-the-art and 30% cheaper than competitors.",
                "SOTA results at half the cost."],
         types=["comparison"],
         include=["the-baseline-rule", "the-cost-frontier", "no-error-bars-no-result"]),
    dict(name="Demo as evidence",
         texts=["Watch this demo: the agent books a full trip in under a minute.",
                "In our demo the model answers every question correctly.",
                "Here is a showcase of what the assistant can do."],
         types=["demo"],
         include=["the-lab-to-field-gap", "once-is-not-reliable"],
         exclude=["data-contamination", "benchmark-saturation", "goodharts-law"]),
    dict(name="LLM as judge",
         texts=["Quality was rated with GPT-4 as a judge, and our model won 71% of comparisons.",
                "Responses were graded by another LLM, which found our model more helpful.",
                "We used an LLM-as-a-judge setup to score outputs."],
         types=["aigraded"],
         include=["judge-bias", "the-gold-standard-myth", "no-error-bars-no-result"],
         exclude=["data-contamination", "benchmark-saturation"]),
    dict(name="Model grades itself",
         texts=["The model grades its own outputs and reaches 92% agreement.",
                "We had it self-evaluate its answers."],
         include=["judge-bias"]),
    dict(name="Human preference win rate",
         texts=["Users prefer our assistant: it wins 68% of side-by-side comparisons.",
                "Ranked first on the arena with a 1250 Elo.",
                "Raters picked our answers over the baseline most of the time."],
         types=["preference"],
         include=["campbells-law", "goodharts-law", "the-gold-standard-myth", "no-error-bars-no-result"],
         exclude=["data-contamination", "benchmark-saturation"]),
    dict(name="User satisfaction",
         texts=["98% user satisfaction with the new chatbot.",
                "Our CSAT went up and customers love the assistant.",
                "Positive feedback from users is overwhelming."],
         types=["preference"],
         include=["the-construct-gap", "campbells-law"],
         exclude=["data-contamination", "benchmark-saturation", "judge-bias"]),
    dict(name="Time-savings claim",
         texts=["Customers saved 40% time using our copilot.",
                "Teams reported saving 6 hours a week with the AI assistant.",
                "Our tool cuts handle time by a third."],
         types=["productivity"],
         include=["the-lab-to-field-gap", "the-baseline-rule", "the-construct-gap", "the-functionality-fallacy"],
         exclude=["data-contamination", "benchmark-saturation", "goodharts-law", "judge-bias", "adaptive-overfitting"]),
    dict(name="Productivity and ROI",
         texts=["The tool increased developer productivity by 55% in a study of our own engineers.",
                "Customers see a 3x return on investment within a year.",
                "Employees are twice as productive with the assistant."],
         types=["productivity"],
         include=["the-baseline-rule", "the-lab-to-field-gap"],
         exclude=["data-contamination", "benchmark-saturation", "goodharts-law"]),
    dict(name="Bare safety claim",
         texts=["Our AI is safe.",
                "The assistant is safe to use.",
                "We built a safer model."],
         types=["safety"],
         include=["presence-not-absence", "the-construct-gap", "the-functionality-fallacy"],
         exclude=["data-contamination", "benchmark-saturation", "the-cost-frontier", "judge-bias"]),
    dict(name="Dangerous capability, no evidence found",
         texts=["We tested the model for dangerous bioweapon capabilities and found no evidence of risk.",
                "Red-team testing for CBRN misuse turned up no signs of uplift.",
                "No harmful capabilities were detected in our safety evaluation."],
         types=["safety"],
         include=["presence-not-absence", "evaluation-awareness", "prompt-sensitivity"],
         exclude=["data-contamination", "benchmark-saturation"]),
    dict(name="Jailbreak resistance",
         texts=["The model resisted every jailbreak attempt during red-teaming.",
                "Our guardrails block harmful requests, and the system is safe to deploy."],
         types=["safety"],
         include=["presence-not-absence", "prompt-sensitivity", "the-construct-gap"],
         exclude=["data-contamination"]),
    dict(name="Fairness across groups",
         texts=["The system is fair and unbiased across all demographic groups.",
                "It works equally well for every user, in every language.",
                "We audited the model for gender bias and it performs equitably."],
         types=["fairness"],
         include=["the-averaging-trap", "presence-not-absence"],
         exclude=["data-contamination", "benchmark-saturation", "the-cost-frontier"]),
    dict(name="No bias found in hiring",
         texts=["No bias was found in hiring recommendations for any group.",
                "Our resume screener showed no evidence of discrimination."],
         include=["the-averaging-trap", "presence-not-absence", "distribution-shift"],
         exclude=["benchmark-saturation", "the-cost-frontier"]),
    dict(name="Human-level performance",
         texts=["Our model reaches human-level performance on reasoning.",
                "The system rivals expert humans at understanding legal text.",
                "PhD-level answers across science."],
         types=["humanlevel"],
         include=["the-construct-gap", "the-baseline-rule"],
         exclude=["the-cost-frontier", "judge-bias"]),
    dict(name="Passes a professional exam",
         texts=["The model passed the bar exam in the 90th percentile.",
                "It passes the medical licensing exam, outperforming most doctors."],
         include=["data-contamination", "the-construct-gap", "the-lab-to-field-gap"],
         exclude=["the-cost-frontier", "judge-bias"]),
    dict(name="Superhuman",
         texts=["Superhuman performance on image classification.",
                "The model exceeds humans on the benchmark."],
         include=["benchmark-saturation", "data-contamination", "the-construct-gap"]),
    dict(name="Agent success on a benchmark",
         texts=["Our agent resolves 48% of GitHub issues on SWE-bench Verified.",
                "The coding agent solves 60% of tasks on SWE-bench."],
         types=["agent", "benchmark"],
         include=["once-is-not-reliable", "no-error-bars-no-result", "the-cost-frontier", "data-contamination"],
         exclude=["judge-bias", "criteria-drift"]),
    dict(name="Agent task completion in the field",
         texts=["The autonomous agent completes 90% of customer support tasks end to end.",
                "Our agent has an 85% success rate on multi-step workflows."],
         types=["agent"],
         include=["once-is-not-reliable", "the-lab-to-field-gap", "the-baseline-rule"],
         exclude=["benchmark-saturation", "judge-bias"]),
    dict(name="Medical accuracy",
         texts=["The diagnostic AI detects pneumonia with 95% accuracy, matching radiologists.",
                "Our clinical model identifies sepsis earlier than doctors.",
                "Patients get accurate triage from the symptom checker."],
         types=["domain"],
         include=["distribution-shift", "the-lab-to-field-gap", "the-functionality-fallacy"],
         exclude=["judge-bias", "criteria-drift", "the-cost-frontier"]),
    dict(name="Clinical time savings",
         texts=["Clinical trials show our scribe reduces documentation time by 30% for physicians.",
                "Doctors save two hours a day with the AI note-taker."],
         types=["domain", "productivity"],
         include=["the-lab-to-field-gap", "the-baseline-rule", "the-team-is-the-system"],
         exclude=["benchmark-saturation", "goodharts-law", "judge-bias"]),
    dict(name="Perfect-sounding reliability",
         texts=["It never hallucinates and is 100% accurate on our tests.",
                "The assistant always gives the right answer.",
                "No errors in testing."],
         include=["once-is-not-reliable"],
         exclude=["the-cost-frontier", "judge-bias"]),
    dict(name="Works for everyone",
         texts=["The model performs equally well across all languages and regions.",
                "Accuracy is the same for every user."],
         include=["the-averaging-trap", "distribution-shift"],
         exclude=["judge-bias", "criteria-drift"]),
    dict(name="Explainability builds trust",
         texts=["Our model explains its reasoning, so users can trust it.",
                "Transparent explanations make the system trustworthy."],
         include=["the-team-is-the-system"],
         exclude=["data-contamination", "benchmark-saturation"]),
    dict(name="Accuracy in production",
         texts=["In production the model is 97% accurate on live traffic.",
                "Deployed with real users, it answers correctly 97% of the time."],
         include=["the-functionality-fallacy", "distribution-shift", "the-lab-to-field-gap"],
         exclude=["judge-bias", "criteria-drift"]),
    dict(name="Gibberish",
         texts=["asdf qwerty banana", "lorem ipsum dolor sit amet", "zzzz"],
         none=True),
    dict(name="Unrelated sentence",
         texts=["I like pizza and the weather is nice today.", "Please remind me to call the dentist."],
         none=True),
    dict(name="Empty",
         texts=["", "   "],
         none=True),
]


# ---------------------------------------------------------------- run
def run_case(claim, case, text):
    types = detect(claim, text)
    results = compute(claim, text, types)
    shown = results[: visible_count(results)]
    return types, results, shown


def check_data(claim, cc, nquestions):
    """The rules themselves must be well formed."""
    problems = []
    seen = set()
    for t in cc["types"]:
        if t["id"] in seen:
            problems.append("duplicate type id " + t["id"])
        seen.add(t["id"])
        try:
            re.compile(t["detect"])
        except re.error as e:
            problems.append("bad detect regex in %s: %s" % (t["id"], e))
    for where, rules in [(t["id"], t["laws"]) for t in cc["types"]] + [("modifiers", cc["modifiers"])]:
        for r in rules:
            if r["fit"] not in FIT:
                problems.append("%s: bad fit %r for %s" % (where, r["fit"], r["slug"]))
            if r["slug"] not in nquestions:
                problems.append("%s: unknown pattern %s" % (where, r["slug"]))
            elif r["ask"] >= nquestions[r["slug"]]:
                problems.append("%s: ask %d out of range for %s" % (where, r["ask"], r["slug"]))
        if where == "modifiers":
            for r in rules:
                try:
                    re.compile(r["detect"])
                except re.error as e:
                    problems.append("bad modifier regex: %s" % e)
    return problems


def js_parity(claim, texts):
    """Run the same claims through the real JavaScript. Returns a list of problems, or None if node is missing."""
    node = shutil.which("node")
    data_js = ROOT / "js/data.js"
    if not node or not data_js.exists():
        return None
    proc = subprocess.run([node, str(ROOT / "build/test_claim_checker.js")], input=json.dumps({"texts": texts}),
                          capture_output=True, text=True, timeout=60)
    if proc.returncode != 0:
        return ["node runner failed: " + proc.stderr.strip()[:300]]
    got = json.loads(proc.stdout)
    problems = []
    for text, g in zip(texts, got):
        types = detect(claim, text)
        results = compute(claim, text, types)
        mine = {"types": types, "results": [[r["no"], r["fit"], r["hits"]] for r in results], "visible": visible_count(results)}
        if mine != g:
            problems.append("JS and Python disagree on %r: python %s, js %s" % (text, json.dumps(mine)[:200], json.dumps(g)[:200]))
    return problems


def main(argv=None, quiet=False):
    argv = sys.argv[1:] if argv is None else argv
    verbose = "-v" in argv
    claim, nums, nquestions, cc = load_claim()
    by_no = {v: k for k, v in nums.items()}
    failures = []

    problems = check_data(claim, cc, nquestions)
    for p in problems:
        failures.append("rules: " + p)

    rows = []
    for case in CASES:
        bad = []
        for text in case["texts"]:
            types, results, shown = run_case(claim, case, text)
            shown_slugs = [by_no[r["no"]] for r in shown]
            all_slugs = [by_no[r["no"]] for r in results]
            label = repr(text[:60])
            if case.get("none"):
                if types or results:
                    bad.append("%s: expected no claim type and no results, got types %s, %d results" % (label, types, len(results)))
                continue
            for ty in case.get("types", []):
                if ty not in types:
                    bad.append("%s: claim type %s not detected (got %s)" % (label, ty, types or "none"))
            for slug in case.get("include", []):
                if slug not in shown_slugs:
                    where = "hidden behind 'show more'" if slug in all_slugs else "missing"
                    bad.append("%s: %s %s" % (label, slug, where))
            for slug in case.get("exclude", []):
                if slug in all_slugs:
                    bad.append("%s: %s should not appear" % (label, slug))
            if verbose and not quiet:
                print("  %s -> types %s" % (label, types or "none"))
                for r in shown:
                    print("      %-6s %s" % ({3: "strong", 2: "likely", 1: "worth"}[r["fit"]], by_no[r["no"]]))
        first_types, first_results, first_shown = run_case(claim, case, case["texts"][0])
        rows.append((case["name"], len(case["texts"]), ",".join(first_types) or "-", "%d/%d" % (len(first_shown), len(first_results)), "FAIL" if bad else "ok"))
        failures.extend("%s: %s" % (case["name"], b) for b in bad)

    parity = js_parity(claim, [t for c in CASES for t in c["texts"]])
    if parity:
        failures.extend("parity: " + p for p in parity)

    if not quiet:
        w = max(len(r[0]) for r in rows)
        print("%-*s  %-4s  %-34s  %-6s  %s" % (w, "Case", "Text", "Types detected (first wording)", "Shown", "Result"))
        for name, n, types, shown, status in rows:
            print("%-*s  %-4d  %-34s  %-6s  %s" % (w, name, n, types[:34], shown, status))
        print()
        if parity is None:
            print("JS parity check skipped (node or js/data.js not found).")
        else:
            print("JS parity check: %s" % ("ok" if not parity else "FAILED"))
        total = sum(len(c["texts"]) for c in CASES)
        print("%d cases, %d claims, %d failures" % (len(CASES), total, len(failures)))
    if failures:
        print("\nFailures:", file=sys.stderr)
        for f in failures:
            print("  - " + f, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
