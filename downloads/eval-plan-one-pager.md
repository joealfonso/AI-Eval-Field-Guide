<!--
Eval plan one-pager
From the AI Evaluation Field Guide: https://evalfieldguide.com/templates
Licensed CC BY 4.0: https://creativecommons.org/licenses/by/4.0/
You may copy, adapt, and share this with attribution to "AI Evaluation Field Guide, evalfieldguide.com".
-->

# Eval plan (one page)

Fill this in before running the evaluation and keep it with the results. Writing the choices down first is what makes them credible later: metrics, test set, and stopping rules chosen after seeing results can be bent to fit them.

**System and version:**
**Owner (a named person):**
**Date written:**
**Plan version:**

## 1. The decision

What will be decided with this evaluation, by whom, and by when? What result would change the decision?

> Example: "Whether to roll the support assistant out to all agents by 30 June. We roll out if it resolves at least as many tickets as the current process without more escalations."

## 2. What we are measuring

Finish this sentence: "This score is evidence that the system can ______ under ______ conditions."

Out of scope (what a high score would not tell us):

## 3. Data

| Set | Source | Size | How collected | Date range | Notes |
|-----|--------|------|---------------|------------|-------|
| Dev (for iteration) | | | | | |
| Locked test (for deciding) | | | | | |

- Does the locked test set resemble the users, languages, sites, and time period where the system will run?
- Has any of it been posted online or used in training or prompt tuning? How do we know?
- Who may look at the locked test results, and how is each look logged?

## 4. Metrics

| Metric | Why this one | Written down before results? |
|--------|--------------|------------------------------|
| Primary | | |
| Second, continuous metric | | |
| Cost per task and latency | | |

## 5. Baselines

- The simplest thing that could work:
- Today's process (the non-AI workflow, if there is one):
- Tuning effort given to each baseline (same as the new system?):

## 6. Prompt variants and repeats

- Prompt variants (as many as you can afford; there is no fixed minimum, and the number needed depends on how much results differ between variants), listed or linked:
- Runs per item (for stochastic outputs, more than one; there is no fixed minimum, so use enough that run-to-run variation is small next to the differences that matter). Repeats reduce run-to-run noise only, not the uncertainty from which items you chose:
- Settings held fixed (model version or date, temperature, system prompt):
- Reported as: average, range across variants, and all-runs-pass rate.

## 7. Grader validation

- Who or what scores outputs (people, rules, an AI model)?
- If an AI model: which one, and is it from the same family as the system under test?
- Human check: sample size (a rate measured on 50 items is imprecise: 45 of 50 in agreement is 90%, but its 95% Wilson interval runs from about 79% to 96%, so use more items if the decision depends on it), who labels, how agreement is measured and the threshold for trusting the grader:
- Order and length controls:

## 8. Slices and sample size

- Groups or input types that matter (defined before looking at the overall score):
- Items per slice, and the interval width we can afford. These intervals cover which items were drawn, not run-to-run variation (see https://evalfieldguide.com/sample-size):
- Smallest difference between systems that would matter to the decision:
- Expected disagreement rate between systems (from a pilot; a pilot of 50 to 100 items gives only a rough rate, so also note the items needed at the high end of its range), and the number of items that implies:

## 9. Stopping rules

- Stop when: (for example, the planned number of items and runs are complete, or a hard failure class appears)
- We will not: add items, change metrics, or change prompts after seeing locked-test results without recording it as a new plan version.
- What happens if the interval for the difference includes zero? (No difference has been shown. That is not proof the systems are equal.)

## 10. Reproducibility

- Where the prompts, data version, scoring code, and raw outputs are stored:
- Canary set to rerun when the vendor updates the model:

## 11. After launch

- What will we monitor, how often, and who looks?
- What triggers a re-evaluation?

## Sign-off

Owner: ____________________   Date: ____________

Template from the AI Evaluation Field Guide, https://evalfieldguide.com, CC BY 4.0.
