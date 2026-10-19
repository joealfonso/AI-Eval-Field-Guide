# AI Evaluation Field Guide

**Live site: [evalfieldguide.com](https://evalfieldguide.com)**

Principles for judging whether an AI system actually holds up. The site collects 26 short, sourced patterns about the reliable ways AI evaluation goes wrong, such as benchmark contamination, prompt sensitivity, judge bias, and the gap between lab results and real use. Each pattern links to the research behind it and comes with questions you can ask.

It is written for people who build, buy, or design with AI, and for anyone who wants to read an AI claim more critically.

## What is on the site

- **26 patterns**, each with a plain-terms summary, the evidence, questions to ask, where the pattern does not apply, and sources.
- **Tools:** a claim checker (a keyword matcher, not an assessment), a "find your patterns" situation finder, a printable checklist builder (questions grouped by before you buy, before you launch, and after launch, scaled by low, medium, or high stakes), a quick brief, a design rubric, and a readiness review.
- **Use it now:** friendly questions to ask when someone shares an AI result at work.
- **Guide pages:** overview, playbook, being pragmatic, glossary, bibliography, and [methodology](https://evalfieldguide.com/methodology).

## Status

This is an independent, self-published reference built from published research. It has not been through formal peer review. See the [methodology](https://evalfieldguide.com/methodology) for how sources were chosen and checked, and what the guide does not claim.

## Corrections

Found a mistake or a better source? Open an [issue](https://github.com/joealfonso/AI-Eval-Field-Guide/issues/new), or use the "Report it" link at the bottom of any pattern page. Corrections are recorded in the [changelog](https://evalfieldguide.com/changelog).

## Building the site

The site is static. Pages are generated from the files in `data/` and `content/`.

```bash
python3 build/build.py
```

Email signup is off by default; the home page shows an RSS box instead. To turn it on, set `newsletter.action` in `data/site.json` to your mail service's hosted-form URL (https), set `newsletter.field` to its email input name, and rebuild. The build adds that one origin to `form-action` in `_headers`.

### Claim checker tests

The claim checker matches keywords in a pasted claim against the rules in the `claimChecker` section of `data/editorial.json`. The scoring lives in `js/claim-match.js`. `build/test_claim_checker.py` runs about 75 sample claims (benchmark scores, comparisons, demos, AI-graded results, satisfaction, productivity, safety, fairness, medical, agents, gibberish and empty input) through the real rules and checks which patterns must be shown and which must not appear. If node is installed it also runs the same claims through the real JavaScript and compares the answers.

```bash
python3 build/test_claim_checker.py      # table of results, exit 1 on failure
python3 build/test_claim_checker.py -v   # also list the patterns shown for each claim
```

The build runs the same test and fails if it fails, so a rule change that breaks an expected result is caught. Checklist phases and stakes are set in the `checklist` section of `data/editorial.json`.

### Share links

Shared and generated links use `?patterns=1,2,3` (quick brief, checklist). Older links with `?laws=` still work. Saved collections in the browser keep working across the rename.

The default social share image and the per-pattern images are generated with `python3 build/make_og.py` (needs Pillow).

## License

Content is licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

Maintained by [Joseph Alfonso](https://josephalfonso.com).
