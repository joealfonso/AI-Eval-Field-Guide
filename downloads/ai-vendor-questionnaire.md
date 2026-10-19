<!--
AI vendor questionnaire
From the AI Evaluation Field Guide: https://evalfieldguide.com/templates
Licensed CC BY 4.0: https://creativecommons.org/licenses/by/4.0/
You may copy, adapt, and share this with attribution to "AI Evaluation Field Guide, evalfieldguide.com".
-->

# AI vendor questionnaire

Send this to a vendor or internal team before you rely on an AI system. Ask for answers in writing, with the evidence attached. It has four parts: **A** evidence that the system works, **B** contract and operations, **C** data handling, and **D** security and misuse. Each question has a "good answer" and a "red flag", which describe what a specific, checkable reply looks like. Neither column is a pass or fail on its own: a weak answer can be fixed by evidence you have not seen yet.

Parts B, C, and D are this guide's own questions. Part A comes from the patterns at https://evalfieldguide.com/patterns/ (for example, /patterns/data-contamination). Security and contract practice are not covered by the research behind the patterns, so those parts name no pattern and make no claim about what vendors usually do. Have your security, privacy, and legal teams review them; they are not legal or compliance advice.

**System and version under review:**
**Reviewer:**
**Date:**
**Decision this review feeds:**
**Risk tier (low, medium, or high, as defined in Being Pragmatic):**

## How to score

Score each question you are required to ask (see "Which questions at which tier" below) with one of three marks.

- **0**: no answer, a refusal, or a reply with no evidence behind it.
- **1**: a partial answer, or an answer without evidence you can check.
- **2**: a specific answer with evidence you have seen or can check yourself.
- **N/A**: the question does not apply to this system. Write down why.

The score describes how well the vendor evidenced the answer, not how good the system is. It is one reviewer's judgment and this scheme has not been validated, so have a second reviewer score independently and discuss any difference of more than one point (raters disagree, see The Gold Standard Myth).

Add up points for each part separately, and divide by two times the number of questions you scored, which is the most that part could give. Do not combine the parts into one overall number. An average can hide a failure (The Averaging Trap), and a vendor strong on A but silent on C should not look fine. Instead report each part's points, the lowest part, and every required question that scored 0.

## Which questions at which tier

The tiers and the choice of questions are this guide's own model, not a standard. Ask everything for a higher tier too.

| Tier | Ask these |
|---|---|
| Low (internal, easy to undo, a person reviews every output) | A1, A2, A9, A11, A16, B3, B7, C1, C2, C4, D2 |
| Medium (customer-facing, reversible, moderate cost of error), add | A3, A4, A5, A6, A7, A8, A10, A13, A14, B1, B2, B5, C3, C5, D1, D3, D5 |
| High (health, money, safety, rights, or access; hard to reverse), add | A12, A15, A17, B4, B6, D4 |

A required question that scores 0 is a stop until you have a way to cover it yourself, such as your own trial, a contract term, or a technical control. Write that cover next to the score.

## Part A: Does the system work?

| # | Question | Good answer | Red flag | Pattern |
|---|----------|-------------|----------|---------|
| A1 | What evidence shows the system works on data like ours, gathered by someone other than the vendor? | Names the data, who collected it, and when; offers a trial on our own data | Only vendor-run results, or "customers are happy" | The Functionality Fallacy |
| A2 | What does the headline benchmark measure, and how close is it to our task? | Describes the task and format, and says what a high score would not tell us | Treats the benchmark name as the capability ("reasoning", "understanding") | The Construct Gap |
| A3 | Was the test set ever used for tuning, prompt iteration, or choosing between versions? | A locked test set kept apart from the set used for iteration, with a count of how often it was consulted | No separate test set, or "we check it after every change" | Adaptive Overfitting |
| A4 | What overlap or contamination checks were run between the test data and the training data? Were results confirmed on data created after the training cutoff? | Describes the method and the result, or says plainly that no check was run | "The data is proprietary" with no check described | Data Contamination |
| A5 | How many prompt variants, runs, and settings were tried before this result was reported? | A number, the range across variants, and the same variants used for competitors | One prompt, one run, or no answer | Prompt Sensitivity; Once Is Not Reliable |
| A6 | What is the 95% confidence interval on each score, and how many items and runs does it rest on? | Intervals or standard errors on every score, and an interval on the gap between systems (paired, if they were scored on the same items) | Single numbers with no sample size; a "win" of a point or two with no interval on the gap | No Error Bars, No Result |
| A7 | What is the pass rate when every run must succeed, not the best run? | Reports average and all-runs-pass rates, with the number of runs per item | Reports pass@k or best-of-k only | Once Is Not Reliable |
| A8 | Which user groups, languages, or input types matter here, and what are the results for each? What is the worst-performing slice? | A breakdown, the worst slice named, and enough items in each slice to judge it | One overall average | The Averaging Trap |
| A9 | What baselines were included: the simplest thing that could work, and our current process? Did they get the same tuning effort? | Simple and current-process baselines with equal tuning budgets | Compared only with weaker or untuned alternatives | The Baseline Rule |
| A10 | If an AI model graded the answers, was it checked against human judgments on a sample? Is the grader from the same model family? | Reports human-grader agreement on a sample, controls for order and length | "We used GPT-4 to score it" with no validation | Judge Bias |
| A11 | What does each task cost in tokens or dollars, and what is the latency, next to every accuracy number? | Cost and latency beside accuracy, compared with a cheaper baseline at a matched budget | Accuracy only | The Cost Frontier |
| A12 | Which common benchmarks are missing from your results table, and why? | Says why each was left out; the suite was chosen before results were seen | Only the benchmarks the system wins | The Benchmark Lottery |
| A13 | Can we rerun the evaluation? Are the model version, prompts, settings, data version, and scoring code recorded, and are raw outputs saved? | Yes, with a version or date, and a plan for rerunning when the model is updated | "The model changes continuously" with no versioning | The Reproducibility Rule |
| A14 | When was the evaluation data collected, from which users, and how does it compare with our inputs? | Dates and sources, and a plan to validate on our data before rollout | Unknown provenance, or data from a different population | Distribution Shift |
| A15 | What changed for real users in a pilot, measured how? Which lab results did not hold up? | Names pilot sites, measures, and at least one result that did not carry over | No pilot, or only satisfaction quotes | The Lab-to-Field Gap |
| A16 | What does the system do when it is wrong, and how often does that happen? How will we find out? | Describes failure types, rates, and a monitoring and escalation route | "It rarely fails" | The Functionality Fallacy; Presence, Not Absence |
| A17 | How hard did anyone try to make the system fail: which prompts, tools, attempts, and who did the red-teaming? | Describes the effort and the testers' expertise; negative results phrased as "under these conditions we did not observe X" | "We found no problems" with no description of the effort | Presence, Not Absence |

If a vendor will not or cannot answer, you can often run the check yourself. For A3 to A8, run a small pilot on your own locked test set, use the sample-size page to choose the number of items, and score every system on the same items with a paired comparison. For A12, choose the benchmark suite yourself before looking at any results. For A13, record the version and date and rerun your pilot whenever the vendor changes the model.

## Part B: Contract and operations

| # | Question | Good answer | Red flag | Pattern |
|---|----------|-------------|----------|---------|
| B1 | Can we pin a specific model version, and what is the notice before it changes? | Named versions or dated snapshots, written notice of changes before they take effect | The model changes under the same name with no notice | The Reproducibility Rule |
| B2 | How long is a version supported before it is retired, and what happens to our results and prompts when it is? | A stated support window, a migration period, and a way to rerun our evaluation on the replacement | Retirement with short or no notice | The Reproducibility Rule |
| B3 | May we run our own evaluation, including a pilot on our own data, before and after signing, and keep the results? | Yes, with test access that matches production and no restriction on sharing results internally | Terms that bar benchmarking or require approval to share results | Distribution Shift |
| B4 | Can the contract include an acceptance test on our data, with the metrics, threshold, and sample size fixed in advance? | Agrees to a test we design, with a remedy if it is not met | Accepts only the vendor's own reported figures | The Functionality Fallacy |
| B5 | How do you tell us about incidents, such as a serious failure, a data exposure, or a model regression, and how fast? | A written process, a named contact, and a stated notification time | No process, or notice only on request | This guide's own question |
| B6 | Is there independent assurance we can see, such as a third-party assessment or audit, and may we or our assessor test the system? | A recent report with its scope stated, and agreement to a scoped test | Only a marketing summary, or no outside review | This guide's own question |
| B7 | What happens when we leave: can we export our data, and what is deleted and confirmed in writing? | Export format, deletion steps, a deletion deadline, and written confirmation | Deletion is unspecified or by request only | This guide's own question |

## Part C: Data handling

| # | Question | Good answer | Red flag | Pattern |
|---|----------|-------------|----------|---------|
| C1 | Are our inputs and outputs stored, for how long, and where? | A stated retention period and location, with a way to turn retention off | Retention is unknown or open-ended | This guide's own question |
| C2 | Are our inputs or outputs used to train or tune any model, yours or anyone else's? | No by default and in writing, or an explicit opt-in we control | Used for training unless we find and change a setting | Data Contamination |
| C3 | Who else processes our data, such as subprocessors or other model providers, and in which countries? | A current list, with notice of changes | No list, or "partners" with no names | This guide's own question |
| C4 | Can we have specific data deleted on request, and how do you confirm it? | A described process, a deadline, and written confirmation | No process, or deletion that excludes backups and logs with no explanation | This guide's own question |
| C5 | Who at the vendor can see our data, and is access logged and reviewable? | Role-based access, access logs, and a way to review them | Broad access with no logging | This guide's own question |

## Part D: Security and misuse

Use these when the system reads untrusted text (web pages, email, documents, user messages) or can call tools, query your data, or take actions. If it does neither, mark the question N/A and say so.

| # | Question | Good answer | Red flag | Pattern |
|---|----------|-------------|----------|---------|
| D1 | How has the system been tested against instructions hidden in the content it reads, and what were the results? | Describes the test method and attempts, reports what got through, and says what was done about it | "The model is trained to refuse" with no test described | This guide's own question |
| D2 | What can the system do on its own, with which permissions, and which actions need a person to confirm first? | Least-privilege permissions, a list of actions, human confirmation for anything hard to undo | Broad access by default, or actions taken with no confirmation | This guide's own question |
| D3 | How could data from our systems leave through the AI, for example through tool calls, links, or generated output, and what stops that? | Names the routes and the controls, and offers to test them | No analysis, or "that cannot happen" | This guide's own question |
| D4 | How hard did anyone try to misuse or break the system, who did it, and what did they find? | Describes the effort, the testers' expertise, and findings; negative results phrased as "under these conditions we did not observe X" | "We found no problems" with no description of the effort | Presence, Not Absence |
| D5 | How do you receive and fix vulnerability reports, and can you show recent fixes? | A public reporting route, a stated response time, and a record of past fixes | No route, or no record | This guide's own question |

## Scoring sheet and summary

Copy this into your review file.

| Part | Questions scored | Points earned | Most possible (2 per question) | Required questions that scored 0 |
|---|---|---|---|---|
| A: Does the system work? | | | | |
| B: Contract and operations | | | | |
| C: Data handling | | | | |
| D: Security and misuse | | | | |

**Lowest part and why:**
**Questions marked N/A, with reasons:**
**Cover for each zero** (own trial, contract term, technical control):
**What we could check ourselves in a small trial before signing:**
**Second reviewer's scores and the differences discussed:**
**Recommendation** (proceed, proceed with conditions, or do not proceed):
**Conditions and owners:**

## Follow-up

- Which answers came with evidence attached?
- Which answers were "we do not know"? An honest "we have not tested that" is more useful than a confident reply with nothing behind it.
- What can we check ourselves in a small trial before signing?

Template from the AI Evaluation Field Guide, https://evalfieldguide.com, CC BY 4.0.
