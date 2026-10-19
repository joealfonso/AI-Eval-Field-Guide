<!--
Results reporting template
From the AI Evaluation Field Guide: https://evalfieldguide.com/templates
Licensed CC BY 4.0: https://creativecommons.org/licenses/by/4.0/
You may copy, adapt, and share this with attribution to "AI Evaluation Field Guide, evalfieldguide.com".
-->

# Evaluation results

Put the answer and its uncertainty on the first screen. A reader should be able to tell what was tested, how much to trust the number, and what the evaluation cannot show.

**System and version:**
**Evaluation date:**
**Eval plan (link, version):**
**Author:**

## Summary

One or two sentences: what was decided or recommended, and how confident we are.

> Example (invented numbers, for layout only): "On 400 recent tickets, the assistant resolved 78% (95% interval 74% to 82%) against 71% (66% to 75%) for the current process; the paired difference is +7 points (+2 to +12). We recommend a limited rollout, not a full one."

## What was tested

- Task and conditions:
- Test set: source, size (n), date range, how it was kept separate from tuning data:
- Number of prompt variants and runs per item:
- Model versions and settings:

## Results

Report every score with its sample size and interval.

| System | n (items) | Runs per item | Score | 95% interval | Cost per task | Latency |
|--------|-----------|---------------|-------|--------------|---------------|---------|
| New system | | | | | | |
| Current process | | | | | | |
| Simplest baseline | | | | | | |

How the intervals were computed (for example, Wilson interval for accuracy; standard errors clustered by document where items come in groups). These intervals cover which items were drawn; say separately how run-to-run variation from the model was handled:

### Comparison

| Comparison | Difference (points) | 95% interval | Method | Reading |
|------------|---------------------|--------------|--------|---------|
| New vs current | | | Paired, same items | Interval excludes zero / includes zero (no difference shown) |

If the interval for a difference includes zero, report that no difference was shown. Do not report it as equal.

### Reliability

- Average success rate across runs:
- All-runs-pass rate:
- Spread across prompt variants (lowest to highest):

## Breakdowns

Slices defined in the plan before the overall number was seen.

| Slice | n | Score | 95% interval |
|-------|---|-------|--------------|
| | | | |

Worst-performing slice, and whether it has enough items to support its own interval:

Examples of failures a person read (read as many as you can; five is a suggested minimum, not a statistical threshold), and what they have in common:

## Grader

- Who or what scored the outputs:
- Agreement between the grader and people on a sample (n, measure, value):

## Cost

Cost per task and latency, next to the accuracy. Is the gain worth the cost for this use?

## What this evaluation cannot show

Be specific. Examples to adapt:

- Populations, languages, sites, or time periods not represented in the test set:
- Behaviors that were not tested (and why):
- Effort spent trying to make the system fail, and by whom. A negative result means "not found with this effort", not "absent":
- Whether results will hold after the vendor updates the model:
- Effects on the people who use the output (human plus AI) that were not measured:

## Changes from the plan

List anything that differs from the eval plan, with the reason. If there are none, say so.

## Reproducing this

Where the prompts, data version, scoring code, and raw outputs are stored:

Template from the AI Evaluation Field Guide, https://evalfieldguide.com, CC BY 4.0.
