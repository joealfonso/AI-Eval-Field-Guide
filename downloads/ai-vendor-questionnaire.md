<!--
AI vendor questionnaire
From the AI Evaluation Field Guide: https://evalfieldguide.com/templates
Licensed CC BY 4.0: https://creativecommons.org/licenses/by/4.0/
You may copy, adapt, and share this with attribution to "AI Evaluation Field Guide, evalfieldguide.com".
-->

# AI vendor questionnaire

Send this to a vendor or internal team before you rely on an AI system. Ask for answers in writing, with the evidence attached. "Good answer" describes what a specific, checkable reply looks like. "Red flag" describes replies that should lead to a follow-up. Neither column is a pass or fail on its own: a weak answer can be fixed by evidence you have not seen yet.

Pattern names refer to pages on https://evalfieldguide.com/patterns/ (for example, /patterns/data-contamination).

**System and version under review:**
**Reviewer:**
**Date:**
**Decision this review feeds:**

| # | Question | Good answer | Red flag | Pattern |
|---|----------|-------------|----------|---------|
| 1 | What evidence shows the system works on data like ours, gathered by someone other than the vendor? | Names the data, who collected it, and when; offers a trial on our own data | Only vendor-run results, or "customers are happy" | The Functionality Fallacy |
| 2 | What does the headline benchmark measure, and how close is it to our task? | Describes the task and format, and says what a high score would not tell us | Treats the benchmark name as the capability ("reasoning", "understanding") | The Construct Gap |
| 3 | Was the test set ever used for tuning, prompt iteration, or choosing between versions? | A locked test set kept apart from the set used for iteration, with a count of how often it was consulted | No separate test set, or "we check it after every change" | Adaptive Overfitting |
| 4 | What overlap or contamination checks were run between the test data and the training data? Were results confirmed on data created after the training cutoff? | Describes the method and the result, or says plainly that no check was run | "The data is proprietary" with no check described | Data Contamination |
| 5 | How many prompt variants, runs, and settings were tried before this result was reported? | A number, the range across variants, and the same variants used for competitors | One prompt, one run, or no answer | Prompt Sensitivity; Once Is Not Reliable |
| 6 | What is the 95% confidence interval on each score, and how many items and runs does it rest on? | Intervals or standard errors on every score; gaps compared on the same items | Single numbers with no sample size; a "win" of a point or two | No Error Bars, No Result |
| 7 | What is the pass rate when every run must succeed, not the best run? | Reports average and all-runs-pass rates, with the number of runs per item | Reports pass@k or best-of-k only | Once Is Not Reliable |
| 8 | Which user groups, languages, or input types matter here, and what are the results for each? What is the worst-performing slice? | A breakdown, the worst slice named, and enough items in each slice to judge it | One overall average | The Averaging Trap |
| 9 | What baselines were included: the simplest thing that could work, and our current process? Did they get the same tuning effort? | Simple and current-process baselines with equal tuning budgets | Compared only with weaker or untuned alternatives | The Baseline Rule |
| 10 | If an AI model graded the answers, was it checked against human judgments on a sample? Is the grader from the same model family? | Reports human-grader agreement on a sample, controls for order and length | "We used GPT-4 to score it" with no validation | Judge Bias |
| 11 | What does each task cost in tokens or dollars, and what is the latency, next to every accuracy number? | Cost and latency beside accuracy, compared with a cheaper baseline at a matched budget | Accuracy only | The Cost Frontier |
| 12 | Which common benchmarks are missing from your results table, and why? | Says why each was left out; the suite was chosen before results were seen | Only the benchmarks the system wins | The Benchmark Lottery |
| 13 | Can we rerun the evaluation? Are the model version, prompts, settings, data version, and scoring code recorded, and are raw outputs saved? | Yes, with a version or date, and a plan for rerunning when the model is updated | "The model changes continuously" with no versioning | The Reproducibility Rule |
| 14 | When was the evaluation data collected, from which users, and how does it compare with our inputs? | Dates and sources, and a plan to validate on our data before rollout | Unknown provenance, or data from a different population | Distribution Shift |
| 15 | What changed for real users in a pilot, measured how? Which lab results did not hold up? | Names pilot sites, measures, and at least one result that did not carry over | No pilot, or only satisfaction quotes | The Lab-to-Field Gap |
| 16 | What does the system do when it is wrong, and how often does that happen? How will we find out? | Describes failure types, rates, and a monitoring and escalation route | "It rarely fails" | The Functionality Fallacy; Presence, Not Absence |
| 17 | How hard did anyone try to make the system fail: which prompts, tools, attempts, and who did the red-teaming? | Describes the effort and the testers' expertise; negative results phrased as "under these conditions we did not observe X" | "We found no problems" with no description of the effort | Presence, Not Absence |

## Follow-up

- Which answers came with evidence attached?
- Which answers were "we do not know"? An honest "we have not tested that" is more useful than a confident reply with nothing behind it.
- What can we check ourselves in a small trial before signing?

Template from the AI Evaluation Field Guide, https://evalfieldguide.com, CC BY 4.0.
