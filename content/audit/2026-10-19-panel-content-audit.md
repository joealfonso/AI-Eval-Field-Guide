# Content audit: AI Evaluation Field Guide (v2026.10)

Review panel for white-paper approval. Audit date 19 Oct 2026. Scope: the 26 pattern pages (`data/laws.json`), Overview, Playbook, Being Pragmatic, Glossary, Case studies, Walkthrough, Methodology, About, the sample-size page and calculators, and the claim checker.

**Standing of the document under review.** Self-published practitioner reference, CC BY 4.0, no outside review. It is not a research contribution and does not claim to be.

## Panel decision

**Approve for publication as a practitioner reference, conditional on the five required revisions below. Do not approve it as a peer-reviewed or systematically derived taxonomy.**

| Dimension | Lead | Score (1-5) | One-line basis |
|---|---|---|---|
| Factual accuracy of cited findings | ML scientist | 4.5 | Every number I traced matched its source; two wording issues |
| Statistical correctness | Statistician | 4.5 | Formulas and worked examples recompute exactly; one unsupported rule-of-thumb family |
| Construct validity of the framework | Measurement scholar | 3 | 26 "patterns" are an editorial selection with overlap; evidence labels measure source count, not strength |
| Evidence synthesis and currency | Methods reviewer | 3 | Several bullets are opinion or off-pattern; LLM-era claims rest on 2023-24 models |
| Tool validity (claim checker) | ML scientist | 2.5 | Self-written test set; blind to mitigations; misses ML-native metrics |
| Epistemic honesty and labeling | Chair | 5 | Unusually clear about what is research, what is the author's, and what was not checked |
| Independence of verification | Chair | 2 | Author plus AI-assisted audit; no external reviewer |

## What the panel verified

Method: fetched primary sources for a sample of figures, recomputed every statistic I could, and ran the repository's own tests.

Confirmed against the source (arXiv abstract or full text unless noted):

- **Zhang et al. 2024 (GSM1k):** drops "up to 8%".
- **Singh et al. 2025:** 27 Meta variants, 19.2% / 20.4% / 29.7%, 83 open-weight models, up to 112%.
- **Needham et al. 2025:** 1,000 prompts, 61 datasets, AUC 0.83 for Gemini 2.5 Pro against 0.92 for the human baseline.
- **Sclar et al. 2024:** 76 points for LLaMA-2-13B, about 10 points on average across 50+ tasks.
- **Bean et al. 2025:** 445 benchmarks, 29 reviewers, "less than 10%" complete real-world tasks, 16.0% with uncertainty estimates or tests.
- **Reuel et al. 2024:** 24 benchmarks, 46 practices.
- **Rabanser et al. 2026:** 12 metrics, 15 models; accepted at ICML 2026.
- **Wong et al. 2026 (JAMA Netw Open):** AUROC 0.82-0.92 across four systems (confirmed via search record only).
- **Dell'Acqua et al.:** published in Organization Science, March-April 2026 issue (existence confirmed; findings not re-read).

Recomputed and correct:

- The Wilson intervals (80% on 200 items gives 73.9-85.0%; 45 of 50 gives 78.6-95.7%).
- The sample-size table (±3, ±5, ±10 points give 1,068 / 385 / 97 items).
- The independent-sample figures (906 and 945 items per system).
- The paired figures (312 and 626 items).
- The pilot ranges (155 to 669 items).
- The McNemar parity example (at most 8 disagreements on the normal approximation, at most 6 on the exact test).
- The 5.5-point half-width in No Error Bars, No Result.
- A Monte Carlo of the paired design at n = 312 gave 83% power against a nominal 80%, as expected for a normal approximation.
- `test_sample_size.py` and `test_claim_checker.py` both pass (30 cases, 75 claims, JS and Python agree).

**Limit of this check.** About 15 of roughly 120 citations were touched. Paywalled and book sources were not read. The earlier "full re-audit" is the author's own and I could not reproduce its log. Treat the above as spot-check evidence, not a clean bill of health.

## Required revisions

### R1. The evidence-base label measures source count, not evidence strength

The rule (at least 4 sources, at least 60% "peer-reviewed or classic", at least 3 lead authors) is disclosed, but the words "Well sourced / Developing / Thin" will be read as quality grades. Consequences:

- Once Is Not Reliable is **Thin** (2 sources) although both are strong and one is ICML 2026.
- Adaptive Overfitting is **Well sourced** while its own Evidence section says the large studies found little or no effect.
- The Jagged Frontier is **Developing** but its empirical weight is one 2023 field experiment on GPT-4 at one consultancy. Moravec (1988) is a different idea (human-hard versus machine-hard), and Vaccaro is, in the page's own words, "not about the jagged frontier itself".
- "Peer-reviewed or classic" lumps book chapters, commentary pieces and conference papers together.

**Fix:** replace or supplement the label with a per-bullet evidence-type tag (*replicated empirical / single study / meta-analysis / conceptual or position paper / report*). Show independent-study count across the whole site, because Bengio et al. is cited by 4 patterns, and Ethayarajh & Jurafsky, Liang et al. and Kapoor et al. by 3 each.

### R2. Remove or re-home evidence the page itself says does not fit

- **Distribution Shift** cites Wong et al. (2021) and then states it "is not a clean case of distribution shift". Move it or drop it.
- **The Gold Standard Myth** includes Clark et al. (2021), then concedes it "tests spotting machine authorship, not rating quality".
- **Recht et al. (2019)** appears in both Adaptive Overfitting and Distribution Shift, with opposite attributions of the same drop. The honesty is good, but a reader sees one study counted as support for two patterns.
- **The Metric Mirage** uses HELM's design choice as evidence that one metric hides tradeoffs. That is motivation, not evidence.

### R3. Fix the two wording issues in cited statistics

- **GSM1k correlation.** The pattern page, case study and walkthrough say "Spearman rank correlation of 0.36". The arXiv abstract as I fetched it writes "Spearman's r² = 0.36". If r² is meant, the rank correlation is about 0.6; if r is meant, the symbol is wrong in the source. Say which, or quote the source's notation and note the ambiguity.
- **Meta's 27 variants.** Goodhart's Law gives "January to March 2025" next to the 27 figure, while the case study and walkthrough say "a single month". The paper says 27 in March alone, with a January-March data window. Harmonize.

### R4. Make the currency of LLM-era claims visible

The guide is dated October 2026, yet its LLM-specific effect sizes rest on 2023-24 systems:

- Zheng et al. (GPT-4 judge agreement)
- Wang et al. (GPT-4 and ChatGPT order bias)
- Panickssery et al. (GPT-4, GPT-3.5, Llama 2)
- Sclar et al. (LLaMA-2-13B)
- τ-bench (GPT-4o)
- Dell'Acqua (GPT-4)

Some pages note "(2024 models)"; most do not. Add a "model generation tested" note wherever an effect size is quoted. Also add the Epic Sepsis Model v2 follow-up (Wong 2026) to the Functionality Fallacy and Distribution Shift pages, since it appears only on the case-study and walkthrough pages.

### R5. Disclose the claim checker's real validity, or rename it

The 75-claim test set was written by the same author as the rules, so it demonstrates consistency, not accuracy. Probes I ran:

- A claim reporting "12 random seeds, paired bootstrap CIs, held-out test set released after the training cutoff, 71.2 ± 1.1" returns the same top results as a bare score, with No Error Bars and Data Contamination both rated *strong*. The tool cannot see mitigations.
- "recall@10 from 0.61 to 0.64 on BEIR" and "Perplexity dropped from 8.1 to 7.9 on WikiText-103" return nothing.
- "Our chatbot always responds politely" fires Once Is Not Reliable; "risks are minimal" fires the safety set.

The page already says it is a keyword matcher. That is adequate for a hobby tool. For a document going to a board, either rename it (for example "claim prompts") or publish a held-out evaluation with precision and recall on claims the author did not write.

## Recommended, not blocking

1. **External review.** The About page itself names the ideal reviewers: an evaluation researcher and a statistician. Obtain two named sign-offs on at least the statistical pages (No Error Bars, Sample Size, Playbook step 8). Publish the audit log (claim, source, locator, verdict) as CSV so the "full re-audit" is checkable.
2. **Rules of thumb are unsupported.** The thresholds are 3-5 prompt variants, 3 runs, a few dozen human labels and a few dozen outputs to read. They are clearly labeled, but they sit in tension with the guide's own evidence:
   - Sclar shows the spread keeps widening as formats are added.
   - 45/50 agreement already has a 17-point interval.
   Offer a power-based alternative (labels needed for a target κ or agreement interval) next to each rule.
3. **Framework scope and overlap.** Add a one-page inclusion/exclusion statement and a coverage matrix. Missing or thin: pass@k estimator and best-of-n selection bias (glossary only), multiple-comparison correction (acknowledged), contamination detection methods, multi-turn and long-context evaluation, reasoning-model variance, calibration (acknowledged).
4. **Opinion versus evidence.** Tag Lin (2019), Liao & Xiao, Raji et al. (2021), Hand (2006) and Ethayarajh & Jurafsky consistently as position papers wherever they sit under "Evidence".
5. **Paired-gap heuristic.** The pattern page says a 3-point gap on 200 items stands out only if models disagree on "roughly 3% to 5%" of items. The sample-size page gives 4% (normal approximation) and 3% (exact). Use the latter's numbers.
6. **Buolamwini & Gebru (2018).** Add the follow-up audit that measured vendor improvement, since the page quotes only the 2017 snapshot (a caveat is present).
7. **Naming debt.** The repository, `data/laws.json` and the `?laws=` parameter still use the old "laws" vocabulary. This is internal and legacy links are supported, so it affects maintainers only.

## Strengths the panel wants preserved

- **Labeled provenance.** Research versus the author's own model, rule of thumb, and mapping are distinguished throughout.
- **Reported nulls and disputes.** Adaptive Overfitting reports the null results, and the LMArena dispute is given alongside Singh et al.
- **Case studies.** Each ends in "what this case does not show".
- **A reproducible statistics page.** Code, tests, formulas and sources are published, and the page states its assumptions.
- **Transparent limits.** The Methodology section lists what is not covered.

## Residual risk if approved as is

A reader who takes "Well sourced" or "Thin" as an effect-strength grade, or who treats the claim checker output as an assessment, will be misled. Neither is a factual error; both are framing risks, which is why R1 and R5 are required.

## Status of revisions (updated after the audit)

Applied on 19 Oct 2026: R3 (GSM1k statistic and Meta window), the Wong and Clark placement fixes under R2, and recommended item 5 (paired-gap heuristic). Pattern versions and the changelog were updated, and the site was rebuilt with all tests passing. Still open: R1, R4, R5, the rest of R2 (Recht double-count, HELM as evidence), and recommended items 1-4, 6 and 7.
