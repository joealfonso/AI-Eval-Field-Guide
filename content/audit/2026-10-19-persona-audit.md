# Persona audit: AI Evaluation Field Guide (v2026.10)

Three fictional reviewers, each reading the site as they would in their own job. They are lenses I constructed, not real people or outside sign-off. They complement the earlier panel audit (`2026-10-19-panel-content-audit.md`) and deliberately avoid repeating it. Pages read: vendor questions and questionnaire, Playbook, Being Pragmatic, Sample size, Case studies, Readiness Review, Methodology, and the pattern data.

---

## Persona 1: Dana Whitfield, Head of AI Procurement and Third-Party Risk (large bank)

**What she needs.** Decide whether to sign a vendor, defend that decision to audit and legal, and attach evidence to a contract file.

**What works.** The 17-question vendor questionnaire has "good answer" and "red flag" columns and links each question to a pattern. The follow-up line "an honest 'we have not tested that' is more useful than a confident reply" is exactly the stance she wants vendors to hear.

**Findings**

1. **It evaluates the evaluation, not the contract.** Nothing covers what happens after signature: notice before model or version changes, deprecation windows, rights to rerun the canary set, incident notification, audit rights, or remedies if reported performance does not hold on her data. The Reproducibility Rule says hosted models change under the same name, but the questionnaire does not turn that into a clause.
2. **No data-handling questions.** Contamination page notes that user-submitted data reached training sets (Balloccu et al.). The questionnaire never asks whether her inputs are retained, used for training, or shared with subprocessors.
3. **No security or abuse questions.** Prompt injection, data exfiltration through tools, and jailbreak resistance are absent. Presence, Not Absence covers red-teaming effort, but not these threat classes.
4. **No way to compare vendors.** The table is pass/fail narrative. She needs a scoring rubric (evidence provided, partial, none) and a roll-up she can put in a committee pack. The Readiness Review has scoring; the questionnaire does not.
5. **Question 5 and 12 are hard to answer in practice.** Vendors rarely disclose prompt-variant counts or omitted benchmarks. Add a fallback: "if they will not say, run it yourself on a pilot" with the sample-size page's numbers.
6. **Tiers and stakes are not tied to procurement.** Being Pragmatic defines low, medium and high tiers. The questionnaire should say which questions are required at which tier.

**Suggested additions**

- A "contract and operations" section: version pinning, change notice, rerun rights, incident SLA, exit and data deletion.
- A data-handling and security block (retention, training use, subprocessors, injection testing).
- A scored version of the questionnaire (0/1/2 per answer, tier-weighted) with a one-page committee summary template.
- A "what to do if they refuse" column for each question.

---

## Persona 2: Priya Raman, Staff ML Engineer, LLM platform and evals (product company)

**What she needs.** Ship evals into CI, set regression gates, and stop arguing about noise.

**What works.** The statistics are right: Wilson intervals, paired differences, McNemar, and a pilot-range calculator. The Playbook's "count each test item once; average runs, then compute intervals across items" is the correct unit-of-analysis advice many teams miss.

**Findings**

1. **No code.** She can read the formulas but there is no copy-paste implementation: paired bootstrap, clustered standard error, the unbiased pass@k estimator (Chen et al., glossary only), Cohen's kappa with an interval, or a regression gate. The page says the formulas are standard; the gap is application.
2. **Nondeterminism is under-explained.** The guide treats run-to-run variance as sampling temperature and seeds. It does not say that many hosted models are not reproducible even at temperature 0, which changes the advice on repeated runs and on what "rerun the eval" can mean.
3. **Rules of thumb stop at "a few dozen".** She needs a decision rule for CI: how many items to detect a regression of X points, what alert threshold for a canary, and how to handle multiple metrics without false alarms. The page admits multiple-comparison correction is out of scope; that is the first thing a CI gate hits.
4. **Agent, RAG and tool-use evals are thin.** Methodology lists agent trajectories as not covered in depth. Retrieval quality versus generation quality, tool-call correctness, and long-horizon tasks are the bulk of current product work.
5. **Judge validation stops at "a few dozen labels".** Forty labels cannot distinguish a good judge from a mediocre one; the guide's own interval for 45/50 shows this. Offer a labels-needed table for a target agreement interval, and show how to estimate a judge's bias on a slice.
6. **No guidance on test-set maintenance cadence** beyond "refresh on a schedule": how to retire items, handle drift in production traffic, and keep a held-out set from leaking through prompt tuning.

**Suggested additions**

- A short "recipes" page with runnable Python for the five calculations above, tested like `sample_stats.py`.
- A page on LLM nondeterminism and what it implies for repeat runs and reproducibility claims.
- A CI-gating worked example: detect a 3-point regression with stated power, include false-alarm control.
- A labels-needed table for judge validation, linked from Judge Bias and Playbook step 8.
- A pattern or chapter for agent, RAG and tool-use evaluation (the largest content gap).

---

## Persona 3: Marcus Oyelaran, AI Policy and Standards Analyst (advises public-sector clients)

**What he needs.** Map practices to frameworks and regulations, cite stable sources, and avoid overclaiming compliance.

**What works.** Clear "this guide's own" markers, a methodology that states its limits, and a Readiness Review whose criteria cite NIST AI 100-1, the EU AI Act and Microsoft HAX. The "not legal advice" boundary is stated where it matters.

**Findings**

1. **Regulatory references can date quickly.** The Readiness Review cites AI Act articles (for example Art. 13 and Art. 50). The application dates and some obligations for general-purpose and high-risk systems have been in flux; each citation should carry an "as of" date and a pointer to the primary text. I could not verify current dates in this review, so treat this as a prompt to check rather than a finding that they are wrong.
2. **No crosswalk.** Patterns are not mapped to NIST AI RMF functions (Govern, Map, Measure, Manage), ISO/IEC 42001, or AI Act obligations. The Overview mentions NIST "Measure" only. A crosswalk table would make the guide usable in a policy memo.
3. **US and EU only.** UK, Canada, and sector regulators (health devices, financial model risk such as SR 11-7) are absent, though the sepsis and credit examples invite them.
4. **Citing the guide is awkward.** It asks readers to cite sources, not the guide, but policy writers do cite it. There is no versioned, permanent identifier (DOI or archived snapshot) and pattern versions change daily.
5. **Evidence-level language.** "Well sourced" will be quoted in policy documents as if it were a quality rating (the earlier panel flagged this). A short sentence in the label's tooltip stating "counts sources, not effect size" should travel with the label wherever it appears.
6. **Equity coverage is light.** The Averaging Trap rests on Gender Shades (2017 systems) and hidden stratification. Fairness is explicitly out of scope, but a policy reader will look for it; link to authoritative guidance rather than leave a gap.

**Suggested additions**

- A crosswalk page: patterns and Readiness Review criteria against NIST AI RMF, ISO/IEC 42001, and AI Act articles, each row with an "as of" date and primary-source link.
- A "how to cite" box with a version, date and archived snapshot or DOI for each release.
- Sector add-ons: model risk management (finance), clinical decision support (health), public-sector procurement.
- A fairness and equity pointer page, honest that it is out of scope.

---

## Where the three personas agree

| Theme | Dana | Priya | Marcus |
|---|---|---|---|
| Move from "what to ask" to "what to do next" (contracts, code, crosswalks) | Yes | Yes | Yes |
| Cover agents, RAG and security explicitly | Yes (security) | Yes (agents, RAG) | Partly |
| Make rules of thumb decision-ready | Scored questionnaire | Power and labels tables | "As of" dates |
| Reduce misreading of the evidence labels | Yes | | Yes |

## Prioritised suggestions (impact against effort)

1. **Recipes page with tested code** (high impact, medium effort). Fits the existing `sample_stats.py` and test pattern.
2. **Scored questionnaire plus contract and data-handling section** (high impact, low-medium effort). Mostly editorial.
3. **Framework crosswalk with "as of" dates** (high impact, medium effort; needs primary-source checking).
4. **Agent, RAG and tool-use evaluation chapter** (high impact, high effort; needs new sources and the same verification the rest got).
5. **LLM nondeterminism note and labels-needed table** (medium impact, low effort).
6. **How-to-cite box with a versioned snapshot** (medium impact, low effort).

None of these have been implemented. New factual claims in any of them should go through the same source-by-source verification as the existing pages before publishing.
