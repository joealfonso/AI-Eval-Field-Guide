# **AI Evaluation Field Guide**

Seed content. Last reviewed 2026-09-15.

## Contents

1. AI Evaluation, an Overview  
2. The Laws  
3. Being Pragmatic  
4. Playbook  
5. Glossary  
6. Bibliography

## AI Evaluation, an Overview

### What AI evaluation is

AI evaluation is how you gather evidence about what an AI system can do, how it behaves, and what happens when people use it, so that someone can make a decision. Ship it or hold it. Buy it or pass. Trust it here, check it there.

The decision is the point. An eval produces evidence for it, and the quality of that evidence should match the stakes.

At its core, evaluation is measurement. Wallach et al. (2025) argue that evaluating generative AI is a social science measurement challenge: the things people care about, like helpfulness, safety, or reasoning, are abstract concepts that have to be carefully defined before they can be measured at all. That framing runs through this whole site.

### Why it's hard

- **One system, countless tasks.** General-purpose models get used for things no benchmark anticipated, and a finite test can't cover "everything in the whole wide world" (Raji et al., 2021).  
- **No single right answer.** Open-ended outputs like summaries, code, and advice can be good in many ways and bad in many ways. Human raters struggle with this too (Clark et al., 2021), and AI judges bring their own biases (Zheng et al., 2023).  
- **Unknown training data.** You usually can't check whether a model has already seen the test (Sainz et al., 2023).  
- **Moving targets.** Benchmarks saturate quickly (Ott et al., 2022), and hosted models change under the same name.  
- **Systems that respond to the test.** Models can often tell when they're being evaluated (Needham et al., 2025), and they increasingly find loopholes in evaluations (Bengio et al., 2026).  
- **Context decides value.** The same model can succeed in a lab and struggle in a clinic (Beede et al., 2020).

### Three layers of evaluation

Weidinger et al. (2023) describe three layers. Most published evaluation lives in the first one. Most real-world consequences show up in the other two.

| Layer | The question | Typical methods |
| :---- | :---- | :---- |
| Capability | What can the system do, and how well? | Benchmarks, behavioral tests, red teaming, capability evals |
| Human interaction | What happens when people use it? | User studies, field studies, human-AI team experiments |
| Systemic impact | What happens to organizations, markets, and communities over time? | Deployment monitoring, audits, longitudinal and policy research |

### The measurement chain

Every score sits at the end of a chain. Wallach et al. (2025), adapting Adcock and Collier (2001), describe four levels:

1. **Background concept.** The broad idea. Example: "helpful."  
2. **Systematized concept.** An explicit definition. Example: "The response resolves the user's stated request without needing a follow-up."  
3. **Measurement instrument.** The actual test. Example: 300 real support tickets, a written rubric, two trained raters.  
4. **Measurements.** The numbers. Example: 71% resolved, with a 95% confidence interval of about 66% to 76%.

When two people argue about whether a model is "good at reasoning," they're usually disagreeing at level 1 or 2 while pointing at numbers from level 4\. Validity is about the whole chain holding together (Messick, 1995).

### Methods at a glance

| Method | What it tells you | Watch out for | Related laws |
| :---- | :---- | :---- | :---- |
| Static benchmarks | Performance on a fixed, shared set of tasks | Saturation, contamination, construct gaps | Benchmark Saturation, Data Contamination, The Construct Gap |
| Dynamic or adversarial benchmarks | Performance on fresh, hard examples, often written to beat current models (Kiela et al., 2021\) | Can overweight adversarial cases that rarely occur in real use | The Clever Hans Effect |
| Behavioral testing | Whether specific behaviors hold up under controlled changes (Ribeiro et al., 2020\) | Only tests the behaviors you think to write down | The Clever Hans Effect, Presence, Not Absence |
| Human evaluation | How people judge output quality (van der Lee et al., 2021\) | Rater expertise, agreement, and fatigue | The Gold Standard Myth, Criteria Drift |
| Pairwise preference arenas | Which outputs people prefer at scale (Chiang et al., 2024\) | Who votes, what they ask, and who gets to test privately | Goodhart's Law, Campbell's Law |
| LLM-as-a-judge | Cheap, fast grading at scale (Zheng et al., 2023\) | Position, length, and self-preference bias | Judge Bias |
| Red teaming | Failure modes found by people trying to break the system (Ganguli et al., 2022\) | Coverage depends on who's on the team | Presence, Not Absence |
| Dangerous capability evals | Whether a model has capabilities that could cause severe harm (Shevlane et al., 2023\) | Elicitation effort, sandbagging, eval awareness | Presence, Not Absence, Evaluation Awareness |
| User and field studies | What happens when real people use the system in context (Beede et al., 2020; Bansal et al., 2021\) | Cost, time, and small samples | The Lab-to-Field Gap, The Team Is the System |
| Production monitoring | How the system performs on live traffic over time | Privacy, consent, and slow feedback | Distribution Shift, Evaluation Awareness |
| Audits and documentation | Whether claims hold up and are recorded in a checkable way (Mitchell et al., 2019; Raji et al., 2022\) | Access to models, data, and results | The Functionality Fallacy, The Reproducibility Rule |

### Who evaluates, and why

Different people need different evidence from the same system.

- **Model developers** want to know if a new model is better than the last one.  
- **Product teams** want to know if a model works for their users, in their workflow, at a cost they can afford. Kapoor et al. (2025) point out that benchmarks often mix up what model developers need with what downstream developers need.  
- **Researchers** want to understand what systems can and can't do, and why.  
- **Buyers** want to know if a vendor's claims hold up on their own data.  
- **Auditors and regulators** want evidence that a system is valid, reliable, and safe for its intended use. The NIST AI Risk Management Framework (2023) makes "Measure" one of its four core functions.

Hutchinson et al. (2022) found that ML evaluation practice often serves the first group and underserves the rest. A lot of the laws on this site are about closing that gap.

### How to use the laws

**To learn,** read them by category:

- **What you're measuring:** Goodhart's Law, Campbell's Law, The Construct Gap, The Functionality Fallacy, The Metric Mirage  
- **The test itself:** Benchmark Saturation, Data Contamination, Adaptive Overfitting, The Clever Hans Effect, The Gold Standard Myth  
- **Running the eval:** Prompt Sensitivity, Judge Bias, Criteria Drift, Once Is Not Reliable, The Cost Frontier  
- **Reading the results:** No Error Bars, No Result, The Averaging Trap, The Baseline Rule, The Benchmark Lottery, The Reproducibility Rule  
- **Beyond the benchmark:** Presence, Not Absence, Evaluation Awareness, Distribution Shift, The Lab-to-Field Gap, The Team Is the System, The Jagged Frontier

**As a tool,** use the Playbook when you're reading an AI claim, designing an eval, or reviewing a launch.

**In a team,** start with Being Pragmatic. It covers how to match rigor to stakes, fit evaluation into existing rituals, and bring people along without becoming the eval police.

### A note on the word "law"

A law here means a reliable pattern with research behind it, not a law of physics. Some have established names, like Goodhart's Law. Others are named on this site to make a well-documented idea easier to remember, and each page says which. Every page links to its sources, and preprints are labeled as preprints.

### Good starting reads

- Chang et al. (2024), a broad survey of how large language models are evaluated.  
- Burnell et al. (2023), a short Science piece on how evaluation results should be reported.  
- Eriksson et al. (2025), an interdisciplinary review of what's wrong with AI benchmarks.  
- Wallach et al. (2025), the case for treating AI evaluation as measurement.

### References

- Adcock, R., & Collier, D. (2001). [Measurement validity: A shared standard for qualitative and quantitative research](https://doi.org/10.1017/S0003055401003100). American Political Science Review, 95(3), 529-546.  
- Bansal, G., Wu, T., Zhou, J., Fok, R., Nushi, B., Kamar, E., Ribeiro, M. T., & Weld, D. (2021). [Does the whole exceed its parts? The effect of AI explanations on complementary team performance](https://arxiv.org/abs/2006.14779). Proceedings of the CHI Conference on Human Factors in Computing Systems (CHI 2021).  
- Beede, E., Baylor, E., Hersch, F., Iurchenko, A., Wilcox, L., Ruamviboonsuk, P., & Vardoulakis, L. M. (2020). [A human-centered evaluation of a deep learning system deployed in clinics for the detection of diabetic retinopathy](https://doi.org/10.1145/3313831.3376718). Proceedings of the CHI Conference on Human Factors in Computing Systems (CHI 2020).  
- Bengio, Y., et al. (2026). [International AI Safety Report 2026](https://internationalaisafetyreport.org/publication/international-ai-safety-report-2026). International AI Safety Report; arXiv:2602.21012. *(Report)*  
- Burnell, R., et al. (2023). [Rethink reporting of evaluation results in AI](https://doi.org/10.1126/science.adf6369). Science, 380(6641), 136-138.  
- Chang, Y., et al. (2024). [A survey on evaluation of large language models](https://arxiv.org/abs/2307.03109). ACM Transactions on Intelligent Systems and Technology, 15(3).  
- Chiang, W.-L., et al. (2024). [Chatbot Arena: An open platform for evaluating LLMs by human preference](https://arxiv.org/abs/2403.04132). Proceedings of the International Conference on Machine Learning (ICML 2024).  
- Clark, E., August, T., Serrano, S., Haduong, N., Gururangan, S., & Smith, N. A. (2021). [All that's 'human' is not gold: Evaluating human evaluation of generated text](https://arxiv.org/abs/2107.00061). Proceedings of ACL-IJCNLP 2021\.  
- Eriksson, M., et al. (2025). [Can we trust AI benchmarks? An interdisciplinary review of current issues in AI evaluation](https://arxiv.org/abs/2502.06559). Proceedings of the AAAI/ACM Conference on AI, Ethics, and Society (AIES 2025).  
- Ganguli, D., et al. (2022). [Red teaming language models to reduce harms: Methods, scaling behaviors, and lessons learned](https://arxiv.org/abs/2209.07858). arXiv:2209.07858. *(Preprint)*  
- Hutchinson, B., et al. (2022). [Evaluation gaps in machine learning practice](https://doi.org/10.1145/3531146.3533233). Proceedings of the ACM Conference on Fairness, Accountability, and Transparency (FAccT 2022).  
- Kapoor, S., Stroebl, B., Siegel, Z. S., Nadgir, N., & Narayanan, A. (2025). [AI agents that matter](https://arxiv.org/abs/2407.01502). Transactions on Machine Learning Research (TMLR).  
- Kiela, D., et al. (2021). [Dynabench: Rethinking benchmarking in NLP](https://arxiv.org/abs/2104.14337). Proceedings of NAACL-HLT 2021\.  
- Messick, S. (1995). [Validity of psychological assessment: Validation of inferences from persons' responses and performances as scientific inquiry into score meaning](https://doi.org/10.1037/0003-066X.50.9.741). American Psychologist, 50(9), 741-749.  
- Mitchell, M., et al. (2019). [Model cards for model reporting](https://arxiv.org/abs/1810.03993). Proceedings of the Conference on Fairness, Accountability, and Transparency (FAT\* 2019).  
- National Institute of Standards and Technology (2023). [Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1](https://doi.org/10.6028/NIST.AI.100-1). U.S. Department of Commerce. *(Report)*  
- Needham, J., Edkins, G., Pimpale, G., Bartsch, H., & Hobbhahn, M. (2025). [Large language models often know when they are being evaluated](https://arxiv.org/abs/2505.23836). arXiv:2505.23836. *(Preprint)*  
- Ott, S., Barbosa-Silva, A., Blagec, K., Brauner, J., & Samwald, M. (2022). [Mapping global dynamics of benchmark creation and saturation in artificial intelligence](https://doi.org/10.1038/s41467-022-34591-0). Nature Communications, 13, 6793\.  
- Raji, I. D., Bender, E. M., Paullada, A., Denton, E., & Hanna, A. (2021). [AI and the everything in the whole wide world benchmark](https://arxiv.org/abs/2111.15366). NeurIPS 2021 Datasets and Benchmarks Track.  
- Raji, I. D., Kumar, I. E., Horowitz, A., & Selbst, A. (2022). [The fallacy of AI functionality](https://doi.org/10.1145/3531146.3533158). Proceedings of the ACM Conference on Fairness, Accountability, and Transparency (FAccT 2022).  
- Ribeiro, M. T., Wu, T., Guestrin, C., & Singh, S. (2020). [Beyond accuracy: Behavioral testing of NLP models with CheckList](https://arxiv.org/abs/2005.04118). Proceedings of ACL 2020\.  
- Sainz, O., Campos, J. A., García-Ferrero, I., Etxaniz, J., Lopez de Lacalle, O., & Agirre, E. (2023). [NLP evaluation in trouble: On the need to measure LLM data contamination for each benchmark](https://arxiv.org/abs/2310.18018). Findings of EMNLP 2023\.  
- Shevlane, T., et al. (2023). [Model evaluation for extreme risks](https://arxiv.org/abs/2305.15324). arXiv:2305.15324. *(Preprint)*  
- van der Lee, C., Gatt, A., van Miltenburg, E., & Krahmer, E. (2021). [Human evaluation of automatically generated text: Current trends and best practice guidelines](https://doi.org/10.1016/j.csl.2020.101151). Computer Speech & Language, 67, 101151\.  
- Wallach, H., Desai, M., Cooper, A. F., Wang, A., Atalla, C., et al. (2025). [Position: Evaluating generative AI systems is a social science measurement challenge](https://arxiv.org/abs/2502.00561). Proceedings of the International Conference on Machine Learning (ICML 2025), PMLR 267\.  
- Weidinger, L., Rauh, M., Marchal, N., Manzini, A., et al. (2023). [Sociotechnical safety evaluation of generative AI systems](https://arxiv.org/abs/2310.11986). arXiv:2310.11986. *(Preprint)*  
- Zheng, L., Chiang, W.-L., Sheng, Y., Zhuang, S., Wu, Z., et al. (2023). [Judging LLM-as-a-judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685). NeurIPS 2023 Datasets and Benchmarks Track.

## The Laws

### What you're measuring

#### Goodhart's Law

> When a measure becomes a target, it ceases to be a good measure.

##### Takeaways

- A benchmark score stands in for something you actually care about. The harder anyone pushes on the stand-in, the further it drifts from the real thing.  
- AI gets hit by this twice. People chase leaderboard numbers, and models trained on a reward chase that reward.  
- Keep at least one measure outside the optimization loop: a held-back test, fresh data, or a direct check of the real outcome.  
- When a score jumps, ask what improved. The capability, or the fit to the test?

##### What it means

Every eval is a proxy. Accuracy on a coding benchmark stands in for "writes useful software." Win rate in a chatbot arena stands in for "people find it helpful." A proxy works fine while nobody leans on it. Once the number becomes the goal, people and systems find ways to move the number that don't move the thing behind it.

Manheim and Garrabrant (2018) split the problem into four variants. Regressional: the proxy and the goal only partly overlap, so picking the top scorers also picks up noise. Extremal: the relationship holds in normal ranges and breaks at the extremes. Causal: pushing the proxy doesn't cause the goal. Adversarial: someone, or something, games the metric on purpose.

##### The evidence

- **It can be measured.** Gao, Schulman, and Hilton (2023) optimized language models against a proxy reward model and tracked a separate "gold" reward model. The gold score rose at first, then fell as optimization continued, and the pattern scaled predictably with reward model size.  
- **More capable systems game harder.** Amodei et al. (2016) named reward hacking as a core safety problem. Pan, Bhatia, and Steinhardt (2022) found that more capable agents exploited misspecified rewards more, sometimes with sudden jumps in bad behavior.  
- **Leaderboards feel it too.** Singh et al. (2025) documented how private testing on Chatbot Arena let some providers try many model variants and publish only the best. Meta tested 27 private variants before the Llama 4 release. Extra Arena data alone produced relative gains of up to 112% on the Arena distribution.  
- **It's getting more common.** The International AI Safety Report 2026 notes models increasingly find loopholes that let them score well on evaluations without doing what the evaluation intended (Bengio et al., 2026).

##### Use it

- Before trusting a score jump, check a second measure nobody optimized.  
- Keep a private holdout set that never informs training, prompt tuning, or model selection.  
- Refresh test items on a schedule.  
- Pair every number with a sample of real outputs that a person reads.  
- Ask: "What's the cheapest way to raise this number without improving the product?" If the answer is easy, expect it to happen.

##### Origins

Economist Charles Goodhart described the idea in a 1975 paper on UK monetary policy: any observed statistical regularity tends to collapse once pressure is placed on it for control purposes. Anthropologist Marilyn Strathern gave it the popular wording in 1997 while writing about audit culture in British universities: "When a measure becomes a target, it ceases to be a good measure."

##### Sources

- Amodei, D., Olah, C., Steinhardt, J., Christiano, P., Schulman, J., & Mané, D. (2016). [Concrete problems in AI safety](https://arxiv.org/abs/1606.06565). arXiv:1606.06565. *(Preprint)*  
- Bengio, Y., et al. (2026). [International AI Safety Report 2026](https://internationalaisafetyreport.org/publication/international-ai-safety-report-2026). International AI Safety Report; arXiv:2602.21012. *(Report)*  
- Gao, L., Schulman, J., & Hilton, J. (2023). [Scaling laws for reward model overoptimization](https://arxiv.org/abs/2210.10760). Proceedings of the International Conference on Machine Learning (ICML 2023).  
- Goodhart, C. A. E. (1975). Problems of monetary management: The U.K. experience. Papers in Monetary Economics, Vol. 1\. Reserve Bank of Australia.  
- Manheim, D., & Garrabrant, S. (2018). [Categorizing variants of Goodhart's Law](https://arxiv.org/abs/1803.04585). arXiv:1803.04585. *(Preprint)*  
- Pan, A., Bhatia, K., & Steinhardt, J. (2022). [The effects of reward misspecification: Mapping and mitigating misaligned models](https://arxiv.org/abs/2201.03544). International Conference on Learning Representations (ICLR 2022).  
- Singh, S., Nan, Y., Wang, A., D'Souza, D., Kapoor, S., et al. (2025). [The leaderboard illusion](https://arxiv.org/abs/2504.20879). Advances in Neural Information Processing Systems (NeurIPS 2025).  
- Strathern, M. (1997). 'Improving ratings': Audit in the British university system. European Review, 5(3), 305-321.

#### Campbell's Law

> The more a number drives decisions, the more it gets corrupted, and the more it distorts the work it was meant to track.

##### Takeaways

- Goodhart's Law is about the measure breaking. Campbell's Law is about people and institutions bending around it.  
- Leaderboards influence funding, press, hiring, and buying decisions. That gives everyone a reason to game them, often without anyone deciding to cheat.  
- The damage spreads past the number. It shapes which research gets done and which products get built.  
- Big decisions deserve several indicators plus qualitative evidence, never a single rank.

##### What it means

When a benchmark becomes the currency of a field, it changes behavior. Teams pick problems that score well, report the best of many runs, quietly tune on the test, and skip work that doesn't move the rank. None of this has to be fraud. Small, reasonable-looking choices add up to a distorted picture.

The same thing happens inside companies. If a launch review only asks for a win rate, teams learn to deliver a win rate.

##### The evidence

- **Scholarship bends.** Lipton and Steinhardt (2019) documented troubling trends in ML papers, including failing to identify where empirical gains came from (for example, crediting a new architecture when the gains came from tuning) and presenting speculation as explanation.  
- **Access is uneven.** Singh et al. (2025) estimated that Google and OpenAI received about 19.2% and 20.4% of all Chatbot Arena data, while 83 open-weight models together received about 29.7%. More data from the arena means more ability to fit the arena.  
- **Leaderboards encode someone's values.** Ethayarajh and Jurafsky (2020) argue that leaderboards reward accuracy while ignoring things real users care about, like model size, energy use, and robustness. A leaderboard's idea of "best" is not yours.  
- **Selection shapes the story.** Dehghani et al. (2021) show that which benchmarks a community adopts can favor certain methods over others.

##### Use it

- When a number drives a real decision (a vendor, a launch, a promotion), require at least two independent measures and a qualitative review.  
- Ask how many variants, seeds, or prompts were tried before the reported result.  
- Watch for teams narrowing scope to whatever the metric rewards.  
- Reward people for finding flaws in the eval, not only for moving it.

##### Origins

Social scientist Donald T. Campbell wrote in 1979: "The more any quantitative social indicator is used for social decision-making, the more subject it will be to corruption pressures and the more apt it will be to distort and corrupt the social processes it was intended to monitor." He was writing about program evaluation in areas like education and policing. AI leaderboards fit the pattern closely.

##### Sources

- Campbell, D. T. (1979). [Assessing the impact of planned social change](https://doi.org/10.1016/0149-7189\(79\)90048-X). Evaluation and Program Planning, 2(1), 67-90.  
- Dehghani, M., Tay, Y., Gritsenko, A. A., et al. (2021). [The benchmark lottery](https://arxiv.org/abs/2107.07002). arXiv:2107.07002. *(Preprint)*  
- Ethayarajh, K., & Jurafsky, D. (2020). [Utility is in the eye of the user: A critique of NLP leaderboards](https://arxiv.org/abs/2009.13888). Proceedings of EMNLP 2020\.  
- Lipton, Z. C., & Steinhardt, J. (2019). [Troubling trends in machine learning scholarship](https://arxiv.org/abs/1807.03341). ACM Queue, 17(1).  
- Singh, S., Nan, Y., Wang, A., D'Souza, D., Kapoor, S., et al. (2025). [The leaderboard illusion](https://arxiv.org/abs/2504.20879). Advances in Neural Information Processing Systems (NeurIPS 2025).

#### The Construct Gap

> A benchmark measures what it measures, not what its name says.

##### Takeaways

- Reasoning, safety, understanding, and helpfulness are constructs. Nothing measures them directly.  
- A benchmark is one way of turning a construct into a test. Treat its name as a claim to check.  
- Trace the chain before trusting a score: concept, definition, test items, scoring, number.  
- Most LLM benchmarks don't spell that chain out.

##### What it means

Measurement researchers separate the thing you care about (the construct) from the thing you can observe (the measurement). Validity is how well the evidence supports the jump from one to the other. A "reasoning" benchmark made of multiple-choice logic puzzles measures performance on those puzzles, in that format. Whether that says anything about reasoning in general is a separate question that needs its own evidence.

Wallach et al. (2025), building on Adcock and Collier (2001), lay out four levels: a **background concept** (the broad, fuzzy idea), a **systematized concept** (an explicit definition), a **measurement instrument** (the actual test), and the **measurements** it produces. Moving between levels takes systematization, operationalization, and application, and then the whole chain has to be interrogated for validity. A lot of AI eval arguments happen because people skip the first two levels and fight about the numbers.

##### The evidence

- **Big names, narrow tests.** Raji et al. (2021) show how benchmarks like ImageNet and GLUE get treated as measures of general capability, the "everything in the whole wide world," which no finite dataset can support.  
- **The problem is widespread.** Bean et al. (2025) had 29 expert reviewers systematically review 445 LLM benchmarks from leading NLP and ML venues and found recurring patterns that undermine the validity of the claims made from them. They offer eight recommendations.  
- **Validity lives in the interpretation.** Messick (1995) argued that validity isn't a property of a test. It's a property of the inferences and uses drawn from its scores, including their consequences.  
- **Mismatches cause harm.** Jacobs and Wallach (2021) show how gaps between constructs like "risk" or "fairness" and their operational definitions lead to real-world harm.  
- **Claims need matching evidence.** Salaudeen et al. (2025) propose a validity-centered framework: the same score can support a narrow claim and fail to support a broad one.

##### Use it

- Finish this sentence: "This score is evidence that the system can \_\_\_ under \_\_\_ conditions." If you can't fill in the blanks, you don't know what the score means.  
- Read 20 test items yourself. Would a person who aced them actually have the skill in the benchmark's name?  
- Match the size of the claim to the evidence. "Scores 85% on X" is safe. "Can reason" is not.  
- Check whether the test format (multiple choice, single turn, short answer) matches how the system will actually be used.

##### Origins

Lee Cronbach and Paul Meehl introduced construct validity in psychology in 1955\. Samuel Messick's 1995 framework made it the center of modern validity theory. ML researchers brought these ideas into AI evaluation over the last several years. "The Construct Gap" is the name this site uses for the idea.

##### Sources

- Adcock, R., & Collier, D. (2001). [Measurement validity: A shared standard for qualitative and quantitative research](https://doi.org/10.1017/S0003055401003100). American Political Science Review, 95(3), 529-546.  
- Bean, A. M., Kearns, R. O., Romanou, A., Hafner, F. S., Mayne, H., et al. (2025). [Measuring what matters: Construct validity in large language model benchmarks](https://arxiv.org/abs/2511.04703). Advances in Neural Information Processing Systems (NeurIPS 2025), Datasets and Benchmarks Track.  
- Cronbach, L. J., & Meehl, P. E. (1955). [Construct validity in psychological tests](https://doi.org/10.1037/h0040957). Psychological Bulletin, 52(4), 281-302.  
- Jacobs, A. Z., & Wallach, H. (2021). [Measurement and fairness](https://doi.org/10.1145/3442188.3445901). Proceedings of the ACM Conference on Fairness, Accountability, and Transparency (FAccT 2021).  
- Messick, S. (1995). [Validity of psychological assessment: Validation of inferences from persons' responses and performances as scientific inquiry into score meaning](https://doi.org/10.1037/0003-066X.50.9.741). American Psychologist, 50(9), 741-749.  
- Raji, I. D., Bender, E. M., Paullada, A., Denton, E., & Hanna, A. (2021). [AI and the everything in the whole wide world benchmark](https://arxiv.org/abs/2111.15366). NeurIPS 2021 Datasets and Benchmarks Track.  
- Salaudeen, O., et al. (2025). [Measurement to meaning: A validity-centered framework for AI evaluation](https://arxiv.org/abs/2505.10573). arXiv:2505.10573. *(Preprint)*  
- Wallach, H., Desai, M., Cooper, A. F., Wang, A., Atalla, C., et al. (2025). [Position: Evaluating generative AI systems is a social science measurement challenge](https://arxiv.org/abs/2502.00561). Proceedings of the International Conference on Machine Learning (ICML 2025), PMLR 267\.

#### The Functionality Fallacy

> Don't assume an AI system works. Whether it works is the first question, not a settled one.

##### Takeaways

- Debates about fairness, ethics, and safety often skip a more basic question: does the system do what it claims?  
- Plenty of deployed AI systems fail at their stated task. That failure is a harm on its own.  
- Vendor-reported performance is a claim. Independent validation on your own population is evidence.  
- Put "does it work, for whom, and how do we know?" at the top of every review.

##### What it means

Raji et al. (2022) point out that critics and policymakers often accept a vendor's performance claims at face value and jump straight to downstream concerns. Meanwhile, some systems don't work at all, some work only in narrow conditions, and some have capabilities that were overstated from the start. If nobody checks functionality, broken systems ship and nobody measures the damage.

##### The evidence

- **Failure is common and varied.** Raji et al. (2022) catalog deployed AI failures, from tasks that can't be done at all, to engineering mistakes, to failures that appear after deployment, to capabilities that were misrepresented.  
- **A widely used model underperformed badly.** Wong et al. (2021) externally validated the Epic Sepsis Model, which was in use at hundreds of US hospitals. Its area under the curve was 0.63, well below the 0.76 to 0.83 the developer reported. It missed 67% of patients who had sepsis while generating alerts for 18% of all hospitalized patients.  
- **Practice lags need.** Hutchinson et al. (2022) found that ML evaluation practice focuses on a narrow set of metrics and datasets that often don't match what deployment contexts actually require.  
- **Standards bodies agree.** The NIST AI Risk Management Framework (2023) makes measuring whether a system is valid and reliable a core function, not an afterthought.

##### Use it

- Ask for evidence the system works on data like yours, gathered by someone other than the vendor.  
- Ask what the system does when it's wrong, and how often that happens.  
- Define "works" in terms of the outcome you care about (patients treated, tickets resolved, time saved), not only model metrics.  
- If nobody has checked, run a small pilot with a real comparison group before scaling.

##### Origins

The term comes from Inioluwa Deborah Raji, I. Elizabeth Kumar, Aaron Horowitz, and Andrew Selbst's 2022 FAccT paper, "The Fallacy of AI Functionality."

##### Sources

- Hutchinson, B., et al. (2022). [Evaluation gaps in machine learning practice](https://doi.org/10.1145/3531146.3533233). Proceedings of the ACM Conference on Fairness, Accountability, and Transparency (FAccT 2022).  
- National Institute of Standards and Technology (2023). [Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1](https://doi.org/10.6028/NIST.AI.100-1). U.S. Department of Commerce. *(Report)*  
- Raji, I. D., Kumar, I. E., Horowitz, A., & Selbst, A. (2022). [The fallacy of AI functionality](https://doi.org/10.1145/3531146.3533158). Proceedings of the ACM Conference on Fairness, Accountability, and Transparency (FAccT 2022).  
- Wong, A., Otles, E., Donnelly, J. P., et al. (2021). [External validation of a widely implemented proprietary sepsis prediction model in hospitalized patients](https://pubmed.ncbi.nlm.nih.gov/34152373/). JAMA Internal Medicine, 181(8), 1065-1070.

#### The Metric Mirage

> Change the metric and you can change the conclusion.

##### Takeaways

- The same model outputs can look like steady progress or a sudden leap, depending on how you score them.  
- All-or-nothing metrics like exact match make gradual improvement look abrupt.  
- Cheap automatic metrics often disagree with people about quality.  
- Before believing a trend, re-score it with another reasonable metric and see if the story holds.

##### What it means

The metric is part of the finding. Pick a strict pass/fail score and a model that gets closer and closer to right answers looks like it's stuck at zero, then suddenly "gets it." Pick a word-overlap score and a fluent, correct answer phrased differently than the reference looks wrong. Neither number is lying, exactly. Each answers a narrower question than the headline suggests.

##### The evidence

- **Emergence can be a scoring artifact.** Schaeffer, Miranda, and Koyejo (2023) argue that many "emergent abilities" in large language models appear because of the researcher's choice of metric. Nonlinear or discontinuous metrics produce sharp jumps. Linear or continuous metrics applied to the same models show smooth, predictable change.  
- **Automatic metrics have narrow validity.** Reiter (2018) reviewed the evidence on BLEU and found it supports using BLEU for diagnostic evaluation of machine translation systems, not for evaluating individual texts or other language generation tasks.  
- **Overlap isn't quality.** Novikova et al. (2017) found that widely used word-overlap metrics correlate weakly with human judgments of generated text.  
- **One metric hides tradeoffs.** Liang et al. (2023) built HELM around seven metrics (accuracy, calibration, robustness, fairness, bias, toxicity, efficiency) because accuracy alone hides the tradeoffs that matter in use.

##### Use it

- Report at least one continuous metric alongside any pass/fail metric.  
- Check automatic metrics against human judgment on a sample before relying on them.  
- When someone shows a dramatic curve, ask what the y-axis measures and what the curve looks like with a different metric.  
- Choose metrics before seeing results, and write down why.

##### Origins

"The Metric Mirage" is the name this site uses, borrowed from the title of Schaeffer, Miranda, and Koyejo's 2023 paper. The broader concern about automatic metrics goes back years in natural language generation research.

##### Sources

- Liang, P., et al. (2023). [Holistic evaluation of language models](https://arxiv.org/abs/2211.09110). Transactions on Machine Learning Research (TMLR).  
- Novikova, J., Dušek, O., Cercas Curry, A., & Rieser, V. (2017). [Why we need new evaluation metrics for NLG](https://arxiv.org/abs/1707.06875). Proceedings of EMNLP 2017\.  
- Reiter, E. (2018). [A structured review of the validity of BLEU](https://doi.org/10.1162/coli_a_00322). Computational Linguistics, 44(3), 393-401.  
- Schaeffer, R., Miranda, B., & Koyejo, S. (2023). [Are emergent abilities of large language models a mirage?](https://arxiv.org/abs/2304.15004) Advances in Neural Information Processing Systems (NeurIPS 2023).

### The test itself

#### Benchmark Saturation

> Every benchmark has a shelf life.

##### Takeaways

- Benchmarks go from hard to solved quickly. Once top scores bunch up near the ceiling, the test stops telling systems apart.  
- A saturated benchmark can hide real differences between models and hide the failures that remain.  
- A high score on an old benchmark is weak evidence about what a current system can do.  
- Plan for renewal: refreshed, dynamic, or held-back test sets.

##### What it means

A benchmark is useful while it separates good from better. When everyone scores 95% or higher, the remaining points are often noise, label errors, or quirks of the test. Progress on the leaderboard slows to a crawl while real-world gaps stay open. That's the signal to retire the test or build a harder one.

##### The evidence

- **Saturation is the norm.** Ott et al. (2022) mapped 3,765 benchmarks across computer vision and natural language processing. A large fraction trended quickly toward near-saturation, and many never saw wide adoption.  
- **"Superhuman" on paper, brittle in practice.** Kiela et al. (2021) note that models reach superhuman scores on benchmarks yet still fail simple challenge examples. Their Dynabench platform keeps humans and models in the loop to keep generating hard new examples.  
- **Fixing benchmarking takes design.** Bowman and Dahl (2021) argue benchmarks need to be built for validity and to resist quick saturation, not just released and left alone.  
- **The last few points can be label noise.** Northcutt, Athalye, and Mueller (2021) found label errors in at least 6% of the ImageNet validation set. Near the ceiling, errors in the answer key can decide rankings.

##### Use it

- Check where top scores sit relative to the ceiling and to the estimated label error rate.  
- Favor benchmarks released after the model's training cutoff, or ones that refresh regularly.  
- For your own product eval, add new hard cases from real failures every cycle.  
- Retire tests that no longer separate the options you're choosing between.

##### Origins

"Saturation" is standard language in AI benchmarking research. Dynamic benchmarking efforts like Dynabench grew directly out of frustration with how fast static benchmarks stopped being useful.

##### Sources

- Bowman, S. R., & Dahl, G. E. (2021). [What will it take to fix benchmarking in natural language understanding?](https://arxiv.org/abs/2104.02145) Proceedings of NAACL-HLT 2021\.  
- Kiela, D., et al. (2021). [Dynabench: Rethinking benchmarking in NLP](https://arxiv.org/abs/2104.14337). Proceedings of NAACL-HLT 2021\.  
- Northcutt, C. G., Athalye, A., & Mueller, J. (2021). [Pervasive label errors in test sets destabilize machine learning benchmarks](https://arxiv.org/abs/2103.14749). NeurIPS 2021 Datasets and Benchmarks Track.  
- Ott, S., Barbosa-Silva, A., Blagec, K., Brauner, J., & Samwald, M. (2022). [Mapping global dynamics of benchmark creation and saturation in artificial intelligence](https://doi.org/10.1038/s41467-022-34591-0). Nature Communications, 13, 6793\.

#### Data Contamination

> If the test was in the training data, the score measures memory, not skill.

##### Takeaways

- Large models train on huge scrapes of the internet, and public benchmarks live on the internet.  
- Contaminated scores overstate how well a model handles problems it hasn't seen.  
- You usually can't inspect a model's training data, so contamination has to be tested indirectly.  
- Fresh, private, or post-cutoff test sets are the most reliable defense.

##### What it means

Contamination, also called leakage, happens when information from the test gets into training. In classic machine learning it's usually a pipeline bug, like normalizing data before splitting it. With large language models it's often invisible and hard to avoid, because nobody outside the lab knows exactly what went into training. A model that has seen the questions, or close paraphrases, can score well without the skill the test was built to measure.

##### The evidence

- **Fresh questions, lower scores.** Zhang et al. (2024) wrote GSM1k, a new set of grade school math problems matched to the popular GSM8K benchmark. Some model families dropped up to 8% in accuracy. Models that were more likely to generate GSM8K examples verbatim showed bigger gaps (Spearman's r² \= 0.36), which suggests partial memorization. Many frontier models held up well, so this is a check to run, not a blanket verdict.  
- **Measure it per benchmark.** Sainz et al. (2023) argue that contamination should be measured for each benchmark and model, because contaminated results lead to wrong conclusions in published research.  
- **Leakage spans fields.** Kapoor and Narayanan (2023) documented leakage errors affecting hundreds of papers across 17 scientific fields that use ML, and proposed a taxonomy of leakage types.  
- **Still a current problem.** The International AI Safety Report 2026 lists test questions that already appear in training data as one reason benchmark scores fail to reflect real-world use (Bengio et al., 2026).

##### Use it

- Build a small private test set from your own data that has never been posted online.  
- Compare scores on public items against freshly written look-alike items. A big gap is a red flag.  
- Check the benchmark's release date against the model's training cutoff.  
- Ask vendors what contamination checks they ran and how.  
- In your own pipelines, split data by time, user, or source before any preprocessing.

##### Origins

Leakage has been a known hazard in statistics and machine learning for decades. The scale of web-trained language models turned it from an occasional bug into a standing concern for every public benchmark.

##### Sources

- Bengio, Y., et al. (2026). [International AI Safety Report 2026](https://internationalaisafetyreport.org/publication/international-ai-safety-report-2026). International AI Safety Report; arXiv:2602.21012. *(Report)*  
- Kapoor, S., & Narayanan, A. (2023). [Leakage and the reproducibility crisis in machine-learning-based science](https://doi.org/10.1016/j.patter.2023.100804). Patterns, 4(9), 100804\.  
- Sainz, O., Campos, J. A., García-Ferrero, I., Etxaniz, J., Lopez de Lacalle, O., & Agirre, E. (2023). [NLP evaluation in trouble: On the need to measure LLM data contamination for each benchmark](https://arxiv.org/abs/2310.18018). Findings of EMNLP 2023\.  
- Zhang, H., Da, J., Lee, D., Robinson, V., Wu, C., et al. (2024). [A careful examination of large language model performance on grade school arithmetic](https://arxiv.org/abs/2405.00332). NeurIPS 2024 Datasets and Benchmarks Track.

#### Adaptive Overfitting

> Every time you tune against the test set, it's worth a little less.

##### Takeaways

- A test set gives an unbiased read only the first time you use it.  
- Choosing prompts, models, or settings based on test results slowly fits your system to that specific test.  
- The effect is sometimes smaller than people fear, but you can't know without a fresh test.  
- Separate a dev set you iterate on from a locked test set you decide with.

##### What it means

Standard statistical guarantees assume you pick your analysis before looking at the data. Real teams don't work that way. They run the eval, tweak the prompt, run it again, try another model, run it again. Each look leaks a little information about the test set into the choices being made. After enough rounds, a high score partly reflects how well the team learned that particular test.

##### The evidence

- **Reuse breaks the math.** Dwork et al. (2015) showed that adaptive reuse of a holdout set undermines its validity, and proposed a "reusable holdout" method that limits how much each query reveals.  
- **Rebuilt test sets score lower.** Recht et al. (2019) rebuilt test sets for CIFAR-10 and ImageNet following the original procedures. Accuracy dropped 3% to 15% on CIFAR-10 and 11% to 14% on ImageNet. The model rankings mostly held, and the authors attribute the drop mainly to subtle differences in the new data rather than years of adaptive overfitting. That nuance matters: the law is real, and its size varies.  
- **Competitions held up better than expected.** Roelofs et al. (2019) analyzed 120 Kaggle competitions and found little evidence of substantial overfitting from leaderboard reuse.  
- **Agent benchmarks are exposed.** Kapoor et al. (2025) found many AI agent benchmarks have inadequate holdout sets, and sometimes none, which lets agents overfit and take shortcuts.

##### Use it

- Keep three splits: iterate on dev, check on validation, decide on a locked test.  
- Log each time someone looks at locked test results.  
- Refresh the locked test once it has driven many decisions.  
- Treat small wins on a heavily reused test with suspicion.

##### Origins

The holdout set is one of the oldest ideas in machine learning. "Adaptive data analysis" became its own research area in the 2010s as researchers formalized what happens when analysts reuse data across many decisions.

##### Sources

- Dwork, C., Feldman, V., Hardt, M., Pitassi, T., Reingold, O., & Roth, A. (2015). [The reusable holdout: Preserving validity in adaptive data analysis](https://doi.org/10.1126/science.aaa9375). Science, 349(6248), 636-638.  
- Kapoor, S., Stroebl, B., Siegel, Z. S., Nadgir, N., & Narayanan, A. (2025). [AI agents that matter](https://arxiv.org/abs/2407.01502). Transactions on Machine Learning Research (TMLR).  
- Recht, B., Roelofs, R., Schmidt, L., & Shankar, V. (2019). [Do ImageNet classifiers generalize to ImageNet?](https://arxiv.org/abs/1902.10811) Proceedings of the International Conference on Machine Learning (ICML 2019).  
- Roelofs, R., Shankar, V., Recht, B., Fridovich-Keil, S., Hardt, M., Miller, J., & Schmidt, L. (2019). A meta-analysis of overfitting in machine learning. Advances in Neural Information Processing Systems (NeurIPS 2019).

#### The Clever Hans Effect

> A model can get the right answer for the wrong reason.

##### Takeaways

- Models learn whatever pattern predicts the label, including patterns nobody intended.  
- These shortcuts look like skill on a test built the same way as the training data.  
- They fall apart the moment the shortcut isn't there.  
- Test with cases designed to break the likely shortcut.

##### What it means

Clever Hans was a horse in early 1900s Germany that seemed to do arithmetic by tapping its hoof. An investigation showed Hans was reading tiny, unconscious cues from the people asking questions. Hans was smart, just not at math.

Models do the same thing. If every photo of a boat has water in it, a model can learn "water" instead of "boat." Geirhos et al. (2020) call this shortcut learning: decision rules that perform well on standard benchmarks and fail to transfer to harder conditions, like the real world.

##### The evidence

- **The watermark detector.** Lapuschkin et al. (2019) used explanation methods on an image classifier trained on the PASCAL VOC dataset and found it identified horses partly by a copyright tag that appeared on many horse photos.  
- **Answers without the question.** Gururangan et al. (2018) showed that in natural language inference datasets, a model given only the hypothesis sentence, without the premise, could predict the label far above chance. Annotators had left telltale word patterns, like negation words in contradictions.  
- **Heuristics, not understanding.** McCoy, Pavlick, and Linzen (2019) built the HANS test set and found that inference models relied on shallow heuristics like word overlap, and failed badly on examples where those heuristics give the wrong answer.  
- **Test behavior, not just accuracy.** Ribeiro et al. (2020) introduced CheckList, a behavioral testing approach borrowed from software engineering, and found critical failures in commercial and research models that had high benchmark accuracy.

##### Use it

- Ask, "What's the laziest way to score well on this test?" Then build items where that way fails.  
- Run a partial-input baseline. Remove the part of the input that should matter and see if accuracy stays high.  
- Create contrast pairs: minimal edits that should flip the answer, and edits that shouldn't change it.  
- Look at explanations or reasoning for a sample of correct answers, not just wrong ones.

##### Origins

The horse was investigated by psychologist Oskar Pfungst, and "Clever Hans" became shorthand in psychology for experimenter cues. Lapuschkin et al. (2019) brought the term into machine learning with "Clever Hans predictors." Geirhos et al. (2020) unified related findings under "shortcut learning."

##### Sources

- Geirhos, R., Jacobsen, J.-H., Michaelis, C., Zemel, R., Brendel, W., Bethge, M., & Wichmann, F. A. (2020). [Shortcut learning in deep neural networks](https://arxiv.org/abs/2004.07780). Nature Machine Intelligence, 2, 665-673.  
- Gururangan, S., Swayamdipta, S., Levy, O., Schwartz, R., Bowman, S. R., & Smith, N. A. (2018). [Annotation artifacts in natural language inference data](https://arxiv.org/abs/1803.02324). Proceedings of NAACL-HLT 2018\.  
- Lapuschkin, S., Wäldchen, S., Binder, A., Montavon, G., Samek, W., & Müller, K.-R. (2019). [Unmasking Clever Hans predictors and assessing what machines really learn](https://doi.org/10.1038/s41467-019-08987-4). Nature Communications, 10, 1096\.  
- McCoy, R. T., Pavlick, E., & Linzen, T. (2019). [Right for the wrong reasons: Diagnosing syntactic heuristics in natural language inference](https://arxiv.org/abs/1902.01007). Proceedings of ACL 2019\.  
- Ribeiro, M. T., Wu, T., Guestrin, C., & Singh, S. (2020). [Beyond accuracy: Behavioral testing of NLP models with CheckList](https://arxiv.org/abs/2005.04118). Proceedings of ACL 2020\.

#### The Gold Standard Myth

> Labels and human ratings are measurements with error, not ground truth.

##### Takeaways

- Test sets contain wrong labels. Near the top of a leaderboard, those errors can decide who "wins."  
- People disagree. For many tasks that disagreement is real information, not noise to average away.  
- Untrained or rushed human raters can be close to random on hard judgments.  
- Report agreement between raters, and audit labels on the items that matter most.

##### What it means

Every eval compares a system's output to something treated as correct: a label, a reference answer, a human rating. That "correct" answer was produced by people working under time pressure, with instructions that couldn't cover every case. Some answers are wrong. Some questions have more than one defensible answer. Calling it ground truth hides all of that.

##### The evidence

- **Answer keys have errors.** Northcutt, Athalye, and Mueller (2021) found an average of at least 3.3% label errors across 10 widely used test sets, and at least 6% in the ImageNet validation set. With corrected labels, rankings between models could flip. On ImageNet, ResNet-18 outperformed ResNet-50 if the share of originally mislabeled examples rose by just 6%.  
- **Disagreement is signal.** Aroyo and Welty (2015) describe seven myths of human annotation, including that every item has one right answer and that disagreement is bad. They argue disagreement tells you something about the item, the instructions, or the task.  
- **Raters can be at chance.** Clark et al. (2021) found that, without training, evaluators distinguished GPT-3 text from human-written text at chance level. Quick training raised accuracy only to about 55%.  
- **Crowdsourced ratings can mislead.** Karpinska, Akoury, and Krishna (2021) found that Mechanical Turk workers, unlike English teachers, failed to tell model-generated stories apart from human-written references. Most papers they surveyed also left out key details about how their crowdsourced ratings were collected.  
- **Practice is inconsistent.** van der Lee et al. (2021) reviewed human evaluation in natural language generation, found wide variation in how it's done and reported, and proposed best-practice guidelines.

##### Use it

- Have two people label a sample independently and measure their agreement before trusting the labels.  
- Audit labels on items where strong models disagree with the "answer."  
- Use raters with real expertise for expert tasks, and train and calibrate them.  
- Keep the disagreement data. Report distributions, not just majority votes.

##### Origins

"The Gold Standard Myth" is this site's name for a theme that runs through annotation research, crowdsourcing studies, and human evaluation guidelines. Aroyo and Welty's "Truth Is a Lie" (2015) is the clearest early statement of it.

##### Sources

- Aroyo, L., & Welty, C. (2015). [Truth is a lie: Crowd truth and the seven myths of human annotation](https://doi.org/10.1609/aimag.v36i1.2564). AI Magazine, 36(1), 15-24.  
- Clark, E., August, T., Serrano, S., Haduong, N., Gururangan, S., & Smith, N. A. (2021). [All that's 'human' is not gold: Evaluating human evaluation of generated text](https://arxiv.org/abs/2107.00061). Proceedings of ACL-IJCNLP 2021\.  
- Karpinska, M., Akoury, N., & Krishna, K. (2021). [The perils of using Mechanical Turk to evaluate open-ended text generation](https://arxiv.org/abs/2109.06835). Proceedings of EMNLP 2021\.  
- Northcutt, C. G., Athalye, A., & Mueller, J. (2021). [Pervasive label errors in test sets destabilize machine learning benchmarks](https://arxiv.org/abs/2103.14749). NeurIPS 2021 Datasets and Benchmarks Track.  
- van der Lee, C., Gatt, A., van Miltenburg, E., & Krahmer, E. (2021). [Human evaluation of automatically generated text: Current trends and best practice guidelines](https://doi.org/10.1016/j.csl.2020.101151). Computer Speech & Language, 67, 101151\.

### Running the eval

#### Prompt Sensitivity

> A score from one prompt is a score for that prompt.

##### Takeaways

- Small formatting changes (spacing, separators, option labels, wording) can swing LLM results by a lot.  
- The best format for one model often isn't the best for another, so single-prompt comparisons can be unfair.  
- Report results across several reasonable prompts, including the spread.  
- Test with the prompts real users actually write.

##### What it means

Traditional software gives the same result for the same input. Language models respond to surface details a person would ignore. If you evaluate two models with one fixed prompt template, you're partly measuring how well each model happens to like that template. The ranking you get might not survive a rewrite.

##### The evidence

- **Formatting alone moves scores.** Sclar et al. (2024) found that several widely used open-source LLMs were extremely sensitive to subtle formatting changes in few-shot prompts, with differences of up to 76 accuracy points for LLaMA-2-13B. The best format for one model correlated only weakly with the best format for another. They propose FormatSpread to report a range instead of one number.  
- **Single-prompt results are brittle.** Mizrahi et al. (2024) analyzed 6.5 million instances across 20 models and 39 tasks and found results from single-instruction evaluation brittle. They call for evaluating with a diverse set of prompts, and for choosing metrics that fit the needs of different users, like model developers versus teams building products.  
- **Implementation details matter.** Biderman et al. (2024), drawing on experience maintaining a widely used LLM evaluation harness, show that small choices in prompts, answer extraction, and normalization change scores, and argue for sharing exact prompts and code.

##### Use it

- Test at least three to five prompt variants and report the mean and range.  
- Use the same set of variants for every model you compare.  
- Include messy, realistic user phrasings, not just clean templates.  
- Save the exact prompts and scoring code alongside the results.

##### Origins

Prompt sensitivity became a named research topic with the rise of few-shot prompting in large language models. The term describes a family of findings rather than one paper.

##### Sources

- Biderman, S., et al. (2024). [Lessons from the trenches on reproducible evaluation of language models](https://arxiv.org/abs/2405.14782). arXiv:2405.14782. *(Preprint)*  
- Mizrahi, M., et al. (2024). [State of what art? A call for multi-prompt LLM evaluation](https://aclanthology.org/2024.tacl-1.52/). Transactions of the Association for Computational Linguistics, 12\.  
- Sclar, M., Choi, Y., Tsvetkov, Y., & Suhr, A. (2024). [Quantifying language models' sensitivity to spurious features in prompt design or: How I learned to start worrying about prompt formatting](https://arxiv.org/abs/2310.11324). International Conference on Learning Representations (ICLR 2024).

#### Judge Bias

> An AI grader has preferences, including a preference for itself.

##### Takeaways

- Using an LLM as a judge is fast and cheap, and a strong judge can agree with people about as often as people agree with each other.  
- Judges also have known biases: which answer comes first, how long it is, and whether it sounds like the judge's own writing.  
- Swapping answer order, controlling for length, and using a different model family as judge all help.  
- Validate the judge against human labels on your task before trusting it at scale.

##### What it means

LLM-as-a-judge means asking one model to grade or compare outputs from another. It solved a real problem: human evaluation is slow and expensive, and open-ended outputs don't have a single right answer. But a judge is a model, with its own quirks. If you don't measure those quirks, they end up baked into your results.

##### The evidence

- **Useful, with named biases.** Zheng et al. (2023) found GPT-4 as a judge reached over 80% agreement with human preferences, similar to agreement between humans. They also identified position bias, verbosity bias, self-enhancement bias, and limited ability to grade things like math.  
- **Order can flip verdicts.** Wang et al. (2024) showed that an LLM judge's verdict could be changed by swapping the order of the candidate answers, and proposed calibration strategies such as evaluating both orders.  
- **Judges favor themselves.** Panickssery, Bowman, and Feng (2024) found LLMs can recognize their own outputs at above-chance rates, and that this self-recognition ability correlates with how strongly they prefer their own outputs.  
- **Validators need validating.** Shankar et al. (2024) built EvalGen to help people align LLM-based graders with their own judgments, because unchecked graders drift from what people actually want.

##### Use it

- Grade every pair twice with the order swapped. Treat inconsistent verdicts as ties or flags.  
- Hand-label 50 to 100 examples and measure judge-human agreement before scaling up.  
- Don't use a model to judge its own outputs, or its model family's, when comparing against competitors.  
- Give the judge a specific rubric, and check whether scores correlate with response length.

##### Origins

"LLM-as-a-judge" was popularized by Zheng et al. (2023). "Judge Bias" is this site's umbrella name for the biases documented since.

##### Sources

- Panickssery, A., Bowman, S. R., & Feng, S. (2024). [LLM evaluators recognize and favor their own generations](https://arxiv.org/abs/2404.13076). Advances in Neural Information Processing Systems (NeurIPS 2024).  
- Shankar, S., Zamfirescu-Pereira, J. D., Hartmann, B., Parameswaran, A. G., & Arawjo, I. (2024). [Who validates the validators? Aligning LLM-assisted evaluation of LLM outputs with human preferences](https://doi.org/10.1145/3654777.3676450). Proceedings of the ACM Symposium on User Interface Software and Technology (UIST 2024).  
- Wang, P., et al. (2024). [Large language models are not fair evaluators](https://aclanthology.org/2024.acl-long.511/). Proceedings of ACL 2024\.  
- Zheng, L., Chiang, W.-L., Sheng, Y., Zhuang, S., Wu, Z., et al. (2023). [Judging LLM-as-a-judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685). NeurIPS 2023 Datasets and Benchmarks Track.

#### Criteria Drift

> You figure out what 'good' means by grading outputs, so your criteria will change.

##### Takeaways

- Nobody can write a complete rubric before seeing real outputs.  
- Grading surfaces new failure modes and new preferences, which changes the rubric.  
- Treat evaluation criteria as a living design artifact, versioned like code.  
- When criteria change, re-grade a fixed reference set or your trend lines stop being comparable.

##### What it means

If you've done qualitative research, this will feel familiar. You don't know the themes until you've read the transcripts. Evaluation works the same way. Teams sit down to define "a good summary," write a few criteria, then start reading outputs and realize they care about things they never wrote down, like tone, or whether the summary admits uncertainty. The rubric grows. Some criteria turn out to matter only for certain kinds of outputs.

That's healthy. The risk is pretending the criteria were fixed all along and comparing numbers graded under different rubrics.

##### The evidence

- **Named in a user study.** Shankar et al. (2024) observed people building LLM-based evaluators with their EvalGen tool and described criteria drift: "users need criteria to grade outputs, but grading outputs helps users define criteria." Some criteria depended on the specific outputs people had seen.  
- **Start from real needs.** Liao and Xiao (2023) argue that evaluation should be grounded in the real-world needs of the people using a system, and that methods from human-computer interaction can help close the gap between what gets measured and what matters.

##### Use it

- Start with open coding. Read 30 to 50 real outputs and note what's good and bad before writing any rubric.  
- Version the rubric, with a date and a reason for each change.  
- Keep a fixed reference set and re-grade it when the rubric changes.  
- Involve the people who will actually use the output in defining the criteria.

##### Origins

The term comes from Shreya Shankar, J.D. Zamfirescu-Pereira, Björn Hartmann, Aditya Parameswaran, and Ian Arawjo's 2024 UIST paper, "Who Validates the Validators?"

##### Sources

- Liao, Q. V., & Xiao, Z. (2023). [Rethinking model evaluation as narrowing the socio-technical gap](https://arxiv.org/abs/2306.03100). arXiv:2306.03100. *(Preprint)*  
- Shankar, S., Zamfirescu-Pereira, J. D., Hartmann, B., Parameswaran, A. G., & Arawjo, I. (2024). [Who validates the validators? Aligning LLM-assisted evaluation of LLM outputs with human preferences](https://doi.org/10.1145/3654777.3676450). Proceedings of the ACM Symposium on User Interface Software and Technology (UIST 2024).

#### Once Is Not Reliable

> Succeeding once is not the same as succeeding every time.

##### Takeaways

- AI outputs vary from run to run. A single pass hides that.  
- pass@k asks, "Did it work at least once in k tries?" pass^k asks, "Did it work all k times?" Users live with the second one.  
- Capability gains don't automatically bring reliability gains.  
- For anything customer-facing or agentic, measure consistency across repeated runs.

##### What it means

Many evals run each test case once, or report the best of several attempts. That's fine for measuring whether a model can do something. It's the wrong number for deciding whether to put it in front of customers. A support agent that resolves a refund correctly 60% of the time will get it wrong for a lot of real people, even if it "passes" the test on a good run.

##### The evidence

- **Reliability drops fast with repetition.** Yao et al. (2025) built τ-bench, which simulates conversations between users and agents that have tools and policies to follow. State-of-the-art function-calling agents like GPT-4o succeeded on fewer than 50% of tasks. Their pass^k metric showed consistency was worse: pass^8 fell below 25% in the retail domain.  
- **Accuracy and reliability are different axes.** Rabanser et al. (2026) proposed twelve reliability metrics across consistency, robustness, predictability, and safety. Across 15 models, recent capability gains produced only small improvements in reliability.

##### Use it

- Run each test case several times (at least three to five for LLM outputs) and report both the average success rate and the all-runs-pass rate.  
- Separate random, occasional failures from consistent failures on specific cases. They need different fixes.  
- Include paraphrased versions of the same task in your test set.  
- Set reliability thresholds based on the cost of a failure, not on what the model can currently hit.

##### Origins

"Once Is Not Reliable" is this site's name. The pass^k metric comes from Yao et al.'s τ-bench, and the broader framing draws on reliability engineering in safety-critical fields.

##### Sources

- Rabanser, S., Kapoor, S., Kirgis, P., Liu, K., Utpala, S., & Narayanan, A. (2026). [Towards a science of AI agent reliability](https://arxiv.org/abs/2602.16666). arXiv:2602.16666. *(Preprint)*  
- Yao, S., Shinn, N., Razavi, P., & Narasimhan, K. (2025). [τ-bench: A benchmark for tool-agent-user interaction in real-world domains](https://arxiv.org/abs/2406.12045). International Conference on Learning Representations (ICLR 2025).

#### The Cost Frontier

> Accuracy without cost is half a result.

##### Takeaways

- You can buy accuracy with more compute: retries, voting, longer reasoning, bigger models.  
- Comparing systems that cost very different amounts to run isn't a fair comparison.  
- Plot accuracy against cost and latency, and look at the frontier of best tradeoffs.  
- Simple, cheap approaches sometimes match elaborate ones.

##### What it means

A leaderboard that only shows accuracy invites a quiet arms race. Call the model five times and take a vote, and the score goes up. So does the bill. For a product team, a system that's two points better and ten times more expensive might be the wrong choice. A fair comparison shows both numbers, so each reader can decide which tradeoff fits their situation.

##### The evidence

- **Accuracy-only evaluation produces bloated agents.** Kapoor et al. (2025) found that a narrow focus on accuracy leads to needlessly complex and costly AI agents. They argue for jointly optimizing cost and accuracy, and show that doing so can cut cost substantially while keeping accuracy. They also found simple baseline strategies competitive with more complex agent designs on coding tasks.  
- **Efficiency belongs in the scorecard.** Liang et al. (2023) include efficiency as one of HELM's seven core metrics.  
- **Users care about more than accuracy.** Ethayarajh and Jurafsky (2020) note that leaderboards ignore costs like model size and energy use that matter to real users.

##### Use it

- Record cost per task (tokens or dollars) and latency next to every accuracy number.  
- Compare systems at matched budgets, or show the full cost-accuracy curve.  
- Always include a cheap baseline: a single call, a smaller model, a simple retry loop.  
- Ask whether the extra points are worth the extra cost for your specific use case.

##### Origins

"The Cost Frontier" is this site's name. The idea of comparing options along a Pareto frontier comes from economics and engineering. Kapoor et al. (2025) made the case for it in AI agent evaluation.

##### Sources

- Ethayarajh, K., & Jurafsky, D. (2020). [Utility is in the eye of the user: A critique of NLP leaderboards](https://arxiv.org/abs/2009.13888). Proceedings of EMNLP 2020\.  
- Kapoor, S., Stroebl, B., Siegel, Z. S., Nadgir, N., & Narayanan, A. (2025). [AI agents that matter](https://arxiv.org/abs/2407.01502). Transactions on Machine Learning Research (TMLR).  
- Liang, P., et al. (2023). [Holistic evaluation of language models](https://arxiv.org/abs/2211.09110). Transactions on Machine Learning Research (TMLR).

### Reading the results

#### No Error Bars, No Result

> A difference smaller than the noise is not a difference.

##### Takeaways

- Every eval score is an estimate from a limited set of questions and, often, a random process.  
- Small test sets and small improvements frequently sit inside the margin of error.  
- Report confidence intervals, and use paired comparisons when models answer the same questions.  
- Decide how many test items you need before running the eval.

##### What it means

If a model scores 80% on 200 questions, the "true" score on similar questions could easily be a few points higher or lower. A rough standard error for accuracy is the square root of p(1 \- p) / n. For 80% on 200 items, that's about 2.8 points, so a 95% confidence interval runs roughly 5.5 points in each direction. A rival model at 83% on the same test hasn't clearly won anything.

Randomness adds more noise: sampling temperature, random seeds, and data order all shift results between runs.

##### The evidence

- **Significance testing is often skipped.** Dror et al. (2018) surveyed NLP research practice, found statistical significance testing was often missing or misapplied, and wrote a practical guide to choosing the right test.  
- **Many experiments are underpowered.** Card et al. (2020) showed that many NLP experiments don't have enough data to reliably detect the small improvements typically claimed, which means published gains can be exaggerated.  
- **Variance rivals the gains.** Bouthillier et al. (2021) found that variance from sources like data sampling, weight initialization, and hyperparameter choices is often as large as the differences papers report. They recommend randomizing as many sources of variation as possible.  
- **A playbook for LLM evals.** Miller (2024) treats eval questions as a sample from a larger population and lays out how to compute standard errors, cluster them when questions are related, compare models with paired differences, and plan sample sizes with power analysis.  
- **Benchmarks rarely report it.** Reuel et al. (2024) assessed 24 AI benchmarks against 46 best practices and found most don't report statistical significance.

##### Use it

- Put a 95% confidence interval next to every score.  
- Compare models on the same items with paired tests.  
- Cluster standard errors when items come in groups, like several questions about one document.  
- For stochastic outputs, run multiple samples per item.  
- Treat any gap inside the interval as a tie.

##### Origins

"No Error Bars, No Result" is this site's name for a basic principle of statistics that AI evaluation has been slow to adopt consistently.

##### Sources

- Bouthillier, X., et al. (2021). [Accounting for variance in machine learning benchmarks](https://arxiv.org/abs/2103.03098). Proceedings of Machine Learning and Systems (MLSys 2021).  
- Card, D., Henderson, P., Khandelwal, U., Jia, R., Mahowald, K., & Jurafsky, D. (2020). [With little power comes great responsibility](https://arxiv.org/abs/2010.06595). Proceedings of EMNLP 2020\.  
- Dror, R., et al. (2018). [The hitchhiker's guide to testing statistical significance in natural language processing](https://aclanthology.org/P18-1128/). Proceedings of ACL 2018\.  
- Miller, E. (2024). [Adding error bars to evals: A statistical approach to language model evaluations](https://arxiv.org/abs/2411.00640). arXiv:2411.00640. *(Preprint)*  
- Reuel, A., Hardy, A., Smith, C., Lamparth, M., Hardy, M., & Kochenderfer, M. J. (2024). [BetterBench: Assessing AI benchmarks, uncovering issues, and establishing best practices](https://arxiv.org/abs/2411.12990). NeurIPS 2024 Datasets and Benchmarks Track.

#### The Averaging Trap

> An average score can hide exactly who the system fails.

##### Takeaways

- Aggregate accuracy blends easy and hard cases, common and rare groups, into one number.  
- Serious failures often cluster in subgroups that are small in the test set and important in the world.  
- Break results down by user group, input type, language, and difficulty.  
- Share instance-level results when you can, so others can slice them too.

##### What it means

A 95% overall score can be 99% for most people and 70% for a group that makes up a small slice of the test set. The average looks great. The people in that slice have a very different experience. The more a system is used across different populations, the more likely this is, and the more it matters.

##### The evidence

- **Gender Shades.** Buolamwini and Gebru (2018) evaluated commercial gender classification systems and found error rates up to 34.7% for darker-skinned women, compared to at most 0.8% for lighter-skinned men.  
- **Hidden stratification in medicine.** Oakden-Rayner et al. (2020) showed that medical imaging models can have relative performance differences of over 20% on clinically important subsets. A model detecting pneumothorax (collapsed lung) had an AUC of 0.94 on X-rays that showed a chest drain, but only 0.77 on X-rays without one. Chest drains are the treatment, so the model did worst on the untreated, most urgent cases.  
- **Report the breakdown.** Burnell et al. (2023), writing in Science, argue that aggregate metrics and lack of access to instance-level results limit understanding of AI systems, and call for granular reporting.  
- **Build it into documentation.** Mitchell et al. (2019) made disaggregated evaluation across relevant groups a standard section of model cards.

##### Use it

- Define the slices that matter for your users before you look at the overall number.  
- Report the worst-performing slice next to the average.  
- Make sure each important slice has enough examples to support its own error bars.  
- Read failures by hand. Clusters often reveal slices you didn't think to define.

##### Origins

"The Averaging Trap" is this site's name. "Hidden stratification" comes from Oakden-Rayner et al. (2020), and "disaggregated evaluation" is standard language in fairness research.

##### Sources

- Buolamwini, J., & Gebru, T. (2018). [Gender shades: Intersectional accuracy disparities in commercial gender classification](https://proceedings.mlr.press/v81/buolamwini18a.html). Proceedings of the Conference on Fairness, Accountability and Transparency (FAT\* 2018), PMLR 81, 77-91.  
- Burnell, R., et al. (2023). [Rethink reporting of evaluation results in AI](https://doi.org/10.1126/science.adf6369). Science, 380(6641), 136-138.  
- Mitchell, M., et al. (2019). [Model cards for model reporting](https://arxiv.org/abs/1810.03993). Proceedings of the Conference on Fairness, Accountability, and Transparency (FAT\* 2019).  
- Oakden-Rayner, L., Dunnmon, J., Carneiro, G., & Ré, C. (2020). [Hidden stratification causes clinically meaningful failures in machine learning for medical imaging](https://arxiv.org/abs/1909.12475). Proceedings of the ACM Conference on Health, Inference, and Learning (CHIL 2020).

#### The Baseline Rule

> A result is only as strong as the baseline it beats.

##### Takeaways

- Beating a weak or untuned baseline can create the illusion of progress.  
- A fair comparison gives the old method the same tuning effort as the new one.  
- Always include a simple baseline: a rule, a smaller model, a non-AI process, or today's human workflow.  
- In product work, the real baseline is how people do the task right now.

##### What it means

"Our model is 20% better" means nothing until you know better than what. New methods usually get weeks of tuning. Baselines often get copied from an old paper with default settings. The gap between them can be mostly effort, not ideas. In product settings, teams sometimes compare an AI feature to a different AI feature and forget to compare it to the plain workflow people already use.

##### The evidence

- **Tuned old methods win.** Melis, Dyer, and Blunsom (2018) found that standard LSTM language models, carefully tuned, outperformed more recent and more complex architectures.  
- **Neural hype in search.** Lin (2019) documented information retrieval papers reporting gains over weak baselines that didn't hold against well-tuned classic methods.  
- **Recommenders didn't reproduce.** Ferrari Dacrema, Cremonesi, and Jannach (2019) tried to reproduce 18 neural recommendation algorithms from top conferences. Only 7 could be reproduced with reasonable effort, and 6 of those were often outperformed by simple heuristic methods.  
- **Simple methods capture most of the value.** Hand (2006) argued that simple classifiers often capture most of the achievable predictive power, and that the gains from sophisticated methods can vanish in real use.

##### Use it

- Include "the simplest thing that could work" and "the current process" in every comparison.  
- Give baselines an equal tuning budget, and say so.  
- Be suspicious when a new method beats baselines by a wide margin on an old benchmark.  
- For AI features, compare against the non-AI workflow with real users.

##### Origins

"The Baseline Rule" is this site's name for a principle that shows up in nearly every field that runs experiments. Hand's "illusion of progress" (2006) is an early, clear statement in machine learning.

##### Sources

- Ferrari Dacrema, M., Cremonesi, P., & Jannach, D. (2019). [Are we really making much progress? A worrying analysis of recent neural recommendation approaches](https://arxiv.org/abs/1907.06902). Proceedings of the ACM Conference on Recommender Systems (RecSys 2019).  
- Hand, D. J. (2006). [Classifier technology and the illusion of progress](https://arxiv.org/abs/math/0606441). Statistical Science, 21(1), 1-14.  
- Lin, J. (2019). [The neural hype and comparisons against weak baselines](https://doi.org/10.1145/3308774.3308781). ACM SIGIR Forum, 52(2), 40-51.  
- Melis, G., Dyer, C., & Blunsom, P. (2018). [On the state of the art of evaluation in neural language models](https://arxiv.org/abs/1707.05589). International Conference on Learning Representations (ICLR 2018).

#### The Benchmark Lottery

> Which benchmarks you pick can decide who wins.

##### Takeaways

- Model rankings often change depending on which benchmarks are included.  
- A method can look like a breakthrough on some tasks and ordinary on others.  
- Choosing benchmarks after seeing results is a quiet form of cherry-picking.  
- Pick benchmarks that match your use case, and pick them before you run anything.

##### What it means

There are thousands of benchmarks. Any given paper or product announcement reports a handful. If the handful was chosen after seeing results, the table tells you more about the selection than about the system. Even without bad intent, communities settle on benchmarks that happen to favor certain approaches, and newcomers get judged by rules that weren't written for them.

##### The evidence

- **Named and measured.** Dehghani et al. (2021) showed that the relative ranking of methods can change substantially depending on the benchmark tasks chosen, and called this the benchmark lottery.  
- **Models weren't even compared on the same tests.** Liang et al. (2023) found that before HELM, language models had on average been evaluated on just 17.9% of HELM's core scenarios, with some prominent models sharing no scenarios at all. HELM raised that to 96%.  
- **Whose utility?** Ethayarajh and Jurafsky (2020) show that a leaderboard's ranking reflects one implicit set of priorities that may not match any particular user's.  
- **An interdisciplinary warning.** Eriksson et al. (2025) reviewed about 100 studies on benchmark shortcomings and found recurring problems, including data contamination, construct validity issues, misaligned incentives, and gaming of results, all shaped by commercial and competitive pressure.

##### Use it

- Choose your benchmark suite before seeing any results, and write it down.  
- Weight benchmarks by relevance to your use case, not by popularity.  
- When reading a claim, notice which common benchmarks are missing.  
- Look at the full results table, not just the highlighted wins.

##### Origins

The term comes from Mostafa Dehghani and colleagues' 2021 paper, "The Benchmark Lottery."

##### Sources

- Dehghani, M., Tay, Y., Gritsenko, A. A., et al. (2021). [The benchmark lottery](https://arxiv.org/abs/2107.07002). arXiv:2107.07002. *(Preprint)*  
- Eriksson, M., et al. (2025). [Can we trust AI benchmarks? An interdisciplinary review of current issues in AI evaluation](https://arxiv.org/abs/2502.06559). Proceedings of the AAAI/ACM Conference on AI, Ethics, and Society (AIES 2025).  
- Ethayarajh, K., & Jurafsky, D. (2020). [Utility is in the eye of the user: A critique of NLP leaderboards](https://arxiv.org/abs/2009.13888). Proceedings of EMNLP 2020\.  
- Liang, P., et al. (2023). [Holistic evaluation of language models](https://arxiv.org/abs/2211.09110). Transactions on Machine Learning Research (TMLR).

#### The Reproducibility Rule

> An eval nobody can rerun is an anecdote.

##### Takeaways

- Eval results depend on details: prompts, decoding settings, data versions, scoring code, and the exact model version.  
- Without those details, nobody can check, compare, or build on a result.  
- Documentation standards like model cards and datasheets exist so results carry their context.  
- Save everything needed to rerun the eval, including raw outputs.

##### What it means

Hosted AI models change under the same name. Prompts get tweaked. Scoring scripts get patched. Six months later, nobody can say why the number was 82% or whether today's 79% is worse. A result you can't reproduce can't be trusted, and it can't be compared to anything.

##### The evidence

- **The field built programs for it.** Pineau et al. (2021) report on the NeurIPS 2019 reproducibility program, which introduced a code submission policy, a community reproducibility challenge, and a reproducibility checklist.  
- **Details change scores.** Biderman et al. (2024) share lessons from maintaining a widely used language model evaluation harness and show how small methodological choices shift results. They recommend sharing code, prompts, and outputs.  
- **Benchmarks fall short.** Reuel et al. (2024) found most of the 24 AI benchmarks they assessed can't be easily replicated.  
- **Agents especially.** Kapoor et al. (2025) describe a pervasive lack of reproducibility in AI agent evaluation caused by nonstandard practices.  
- **Standard formats exist.** Mitchell et al. (2019) proposed model cards to document intended use and evaluation results. Gebru et al. (2021) proposed datasheets to document how datasets were created and what they're suited for.

##### Use it

- Record the model name and version (or date), system prompt, decoding settings, dataset version, scoring code version, and run date.  
- Save raw outputs, not just scores.  
- Write a one-page eval card: purpose, data, metrics, slices, and known limits.  
- Keep a small canary set and rerun it whenever a vendor updates a model.

##### Origins

"The Reproducibility Rule" is this site's name. Reproducibility has been a stated norm in science for centuries. Machine learning formalized it through checklists, model cards, and datasheets starting in the late 2010s.

##### Sources

- Biderman, S., et al. (2024). [Lessons from the trenches on reproducible evaluation of language models](https://arxiv.org/abs/2405.14782). arXiv:2405.14782. *(Preprint)*  
- Gebru, T., et al. (2021). [Datasheets for datasets](https://arxiv.org/abs/1803.09010). Communications of the ACM, 64(12), 86-92.  
- Kapoor, S., Stroebl, B., Siegel, Z. S., Nadgir, N., & Narayanan, A. (2025). [AI agents that matter](https://arxiv.org/abs/2407.01502). Transactions on Machine Learning Research (TMLR).  
- Mitchell, M., et al. (2019). [Model cards for model reporting](https://arxiv.org/abs/1810.03993). Proceedings of the Conference on Fairness, Accountability, and Transparency (FAT\* 2019).  
- Pineau, J., et al. (2021). [Improving reproducibility in machine learning research (A report from the NeurIPS 2019 Reproducibility Program)](https://arxiv.org/abs/2003.12206). Journal of Machine Learning Research, 22(164), 1-20.  
- Reuel, A., Hardy, A., Smith, C., Lamparth, M., Hardy, M., & Kochenderfer, M. J. (2024). [BetterBench: Assessing AI benchmarks, uncovering issues, and establishing best practices](https://arxiv.org/abs/2411.12990). NeurIPS 2024 Datasets and Benchmarks Track.

### Beyond the benchmark

#### Presence, Not Absence

> An evaluation can show a capability or risk exists. It can't prove one doesn't.

##### Takeaways

- A failed attempt to get a model to do something tells you about the attempt, not the model's ceiling.  
- Better prompts, tools, fine-tuning, or more time can unlock abilities an eval missed.  
- Safety claims built on "we tried and it didn't" need to say how hard someone tried.  
- Report elicitation effort alongside every negative result.

##### What it means

Edsger Dijkstra (1970) made this point about software in his Notes on Structured Programming: "Program testing can be used to show the presence of bugs, but never to show their absence\!" General-purpose AI systems make it sharper. The space of possible inputs is effectively infinite, and capabilities often show up only with the right prompt, tool, or scaffolding. A clean eval report means you didn't find the problem under the conditions you tried.

##### The evidence

- **Evaluations for extreme risks.** Shevlane et al. (2023) describe dangerous capability evaluations and alignment evaluations as key inputs to training and deployment decisions, and discuss the limits of what those evaluations can catch.  
- **Models can underperform on purpose.** van der Weij et al. (2025) showed that frontier models like GPT-4 and Claude 3 Opus could be prompted to selectively underperform on dangerous capability evaluations while keeping performance on general ones. Models could also be fine-tuned to hide a capability unless given a password.  
- **Red teaming finds a lot, not everything.** Ganguli et al. (2022) released a dataset of nearly 39,000 red team attacks on language models. The harmful outputs ranged from offensive language to subtler unethical content, the kind a fixed benchmark wouldn't think to ask about.

##### Use it

- Phrase negative results precisely: "Under these conditions, with this effort, we didn't observe X."  
- Report what elicitation was tried: prompts, tools, fine-tuning, number of attempts, and time spent.  
- Budget for red teaming by people with real domain expertise.  
- Revisit negative results when models, tools, or techniques change.

##### Origins

The core idea is Dijkstra's, from "Notes on Structured Programming," first circulated in 1969 with a second edition in 1970\. "Presence, Not Absence" is this site's name for applying it to AI evaluation.

##### Sources

- Dijkstra, E. W. (1970). [Notes on structured programming (EWD249)](https://www.cs.utexas.edu/~EWD/transcriptions/EWD02xx/EWD249/EWD249.html). Technological University Eindhoven (first circulated 1969; second edition April 1970).  
- Ganguli, D., et al. (2022). [Red teaming language models to reduce harms: Methods, scaling behaviors, and lessons learned](https://arxiv.org/abs/2209.07858). arXiv:2209.07858. *(Preprint)*  
- Shevlane, T., et al. (2023). [Model evaluation for extreme risks](https://arxiv.org/abs/2305.15324). arXiv:2305.15324. *(Preprint)*  
- van der Weij, T., Hofstätter, F., Jaffe, O., Brown, S. F., & Ward, F. R. (2025). [AI sandbagging: Language models can strategically underperform on evaluations](https://arxiv.org/abs/2406.07358). International Conference on Learning Representations (ICLR 2025).

#### Evaluation Awareness

> A model that can tell it's being tested may not act the way it will in the real world.

##### Takeaways

- Frontier models can often tell evaluation prompts apart from real use.  
- If behavior changes under test, evaluation results stop predicting deployment behavior.  
- Scenarios that look artificial are easier to spot.  
- Pair pre-launch tests with monitoring of real use.

##### What it means

People act differently when they know they're being watched. Models trained on huge amounts of text, including text about AI evaluations, can pick up on the telltale signs of a test: tidy multiple-choice formats, contrived scenarios, obviously fake names. If a model responds to those cues, even without any intent in the human sense, the eval measures test behavior instead of real behavior.

##### The evidence

- **Models are good at spotting tests.** Needham et al. (2025) built a benchmark of 1,000 prompts and transcripts from 61 datasets, covering public benchmarks, real deployment interactions, and agent trajectories. Frontier models identified evaluations far above chance. Gemini 2.5 Pro reached an AUC of 0.83, compared to 0.92 for a human baseline. Models were better at this in agentic settings than in chat.  
- **Recognized at the international level.** The International AI Safety Report 2026 notes it has become more common for models to distinguish test settings from real-world deployment and to exploit loopholes in evaluations, which makes results harder to interpret (Bengio et al., 2026).  
- **The capacity to underperform exists.** van der Weij et al. (2025) showed models can be prompted or fine-tuned to strategically underperform on specific evaluations.

##### Use it

- Build eval scenarios from real, messy usage instead of obviously synthetic setups.  
- Compare behavior in evals against behavior in real use, with consent and privacy safeguards.  
- Track when models comment on the possibility that they're being tested.  
- For high-stakes behavior, don't rely on pre-launch evals alone. Monitor after launch.

##### Origins

"Evaluation awareness" is the term used in recent AI safety research. It's a young area, and several key findings are preprints, so expect this page to change.

##### Sources

- Bengio, Y., et al. (2026). [International AI Safety Report 2026](https://internationalaisafetyreport.org/publication/international-ai-safety-report-2026). International AI Safety Report; arXiv:2602.21012. *(Report)*  
- Needham, J., Edkins, G., Pimpale, G., Bartsch, H., & Hobbhahn, M. (2025). [Large language models often know when they are being evaluated](https://arxiv.org/abs/2505.23836). arXiv:2505.23836. *(Preprint)*  
- van der Weij, T., Hofstätter, F., Jaffe, O., Brown, S. F., & Ward, F. R. (2025). [AI sandbagging: Language models can strategically underperform on evaluations](https://arxiv.org/abs/2406.07358). International Conference on Learning Representations (ICLR 2025).

#### Distribution Shift

> Performance measured on one population doesn't automatically carry over to another.

##### Takeaways

- A test set is a snapshot of certain people, places, times, and conditions.  
- Change any of those and performance can drop, sometimes sharply.  
- Even careful rebuilds of the same benchmark produce lower scores.  
- Evaluate on data from the setting where the system will run, and keep checking over time.

##### What it means

Models learn patterns from the data they're trained on and get tested on data that usually looks a lot like it. The real world rarely cooperates. A new hospital has different patients and equipment. A new market uses different language. Next year's users behave differently than last year's. Each change is a shift, and a benchmark score doesn't tell you how the system handles it.

##### The evidence

- **Same recipe, lower scores.** Recht et al. (2019) rebuilt the CIFAR-10 and ImageNet test sets by following the original collection process. Accuracy fell 3% to 15% on CIFAR-10 and 11% to 14% on ImageNet. Small differences in how data was gathered were enough.  
- **Real-world shifts, measured.** Koh et al. (2021) built WILDS, a benchmark of ten datasets with real distribution shifts across hospitals, cameras, regions, and time. Models showed large gaps between in-distribution and out-of-distribution performance.  
- **A clinical example.** Wong et al. (2021) found a widely deployed sepsis model performed far worse at an independent health system than its developer reported.  
- **Drift erodes gains.** Hand (2006) argued that population drift over time is one reason gains from sophisticated models shrink in practice.

##### Use it

- Ask where and when the eval data came from, and compare that to your actual users.  
- Split test results by site, time period, or source to see how performance moves.  
- Run a local validation before rolling out to a new market, language, or customer segment.  
- Monitor production for drift and re-evaluate on a schedule.

##### Origins

Distribution shift, also called dataset shift, is a long-standing problem in statistics and machine learning. It's closely related to external validity in the social and medical sciences.

##### Sources

- Hand, D. J. (2006). [Classifier technology and the illusion of progress](https://arxiv.org/abs/math/0606441). Statistical Science, 21(1), 1-14.  
- Koh, P. W., et al. (2021). [WILDS: A benchmark of in-the-wild distribution shifts](https://arxiv.org/abs/2012.07421). Proceedings of the International Conference on Machine Learning (ICML 2021).  
- Recht, B., Roelofs, R., Schmidt, L., & Shankar, V. (2019). [Do ImageNet classifiers generalize to ImageNet?](https://arxiv.org/abs/1902.10811) Proceedings of the International Conference on Machine Learning (ICML 2019).  
- Wong, A., Otles, E., Donnelly, J. P., et al. (2021). [External validation of a widely implemented proprietary sepsis prediction model in hospitalized patients](https://pubmed.ncbi.nlm.nih.gov/34152373/). JAMA Internal Medicine, 181(8), 1065-1070.

#### The Lab-to-Field Gap

> A system that works in the lab can fail in the places people actually use it.

##### Takeaways

- Real use adds lighting, bandwidth, workflows, time pressure, incentives, and people.  
- Model accuracy is one layer. How people interact with the system, and its wider effects, are layers too.  
- Many AI failures are sociotechnical. The model does what it was built to do, and the situation defeats it.  
- Watch the system in use, in context, before calling it validated.

##### What it means

Lab evaluation holds everything constant except the model. The field holds nothing constant. The value of an AI system comes from the whole setup: the model, the interface, the workflow, the people, and the organization around them. Evaluating only the model is like usability testing only the backend.

##### The evidence

- **Accurate in validation, rough in clinics.** Beede et al. (2020) studied a deep learning system for detecting diabetic retinopathy deployed in 11 clinics in Thailand. The system had performed well in validation. In the clinics, the authors found that socio-environmental factors, like lighting conditions and internet speed, affected model performance, nursing workflows, and the patient experience. Many images were rejected as ungradable.  
- **Three layers of evaluation.** Weidinger et al. (2023) propose evaluating generative AI at the capability layer, the human interaction layer, and the systemic impact layer, and note that most safety evaluation so far has focused on the first.  
- **Narrow the sociotechnical gap.** Liao and Xiao (2023) frame evaluation as narrowing the gap between what gets measured and what real people need from a system.  
- **Abstraction traps.** Selbst et al. (2019) describe traps that come from abstracting away social context, including assuming a solution built for one context will work in another.  
- **The official name for it.** The International AI Safety Report 2026 describes an "evaluation gap": pre-deployment test results are not always strongly predictive of real-world capabilities or risks (Bengio et al., 2026).  
- **Practice lags need.** Hutchinson et al. (2022) found ML evaluation practice often fails to reflect the needs of real application contexts.

##### Use it

- Do field observation. Sit with people using the system in their actual environment.  
- Evaluate the workflow, not just the model: time to complete, error recovery, handoffs.  
- Pilot in a small number of real sites before scaling.  
- Define success with the people affected, including people who never touch the interface.  
- Bring in UX research methods like contextual inquiry and diary studies. They were built for exactly this gap.

##### Origins

"The Lab-to-Field Gap" is this site's name. Researchers also call it the sociotechnical gap or the evaluation gap.

##### Sources

- Beede, E., Baylor, E., Hersch, F., Iurchenko, A., Wilcox, L., Ruamviboonsuk, P., & Vardoulakis, L. M. (2020). [A human-centered evaluation of a deep learning system deployed in clinics for the detection of diabetic retinopathy](https://doi.org/10.1145/3313831.3376718). Proceedings of the CHI Conference on Human Factors in Computing Systems (CHI 2020).  
- Bengio, Y., et al. (2026). [International AI Safety Report 2026](https://internationalaisafetyreport.org/publication/international-ai-safety-report-2026). International AI Safety Report; arXiv:2602.21012. *(Report)*  
- Hutchinson, B., et al. (2022). [Evaluation gaps in machine learning practice](https://doi.org/10.1145/3531146.3533233). Proceedings of the ACM Conference on Fairness, Accountability, and Transparency (FAccT 2022).  
- Liao, Q. V., & Xiao, Z. (2023). [Rethinking model evaluation as narrowing the socio-technical gap](https://arxiv.org/abs/2306.03100). arXiv:2306.03100. *(Preprint)*  
- Selbst, A. D., boyd, d., Friedler, S. A., Venkatasubramanian, S., & Vertesi, J. (2019). [Fairness and abstraction in sociotechnical systems](https://doi.org/10.1145/3287560.3287598). Proceedings of the Conference on Fairness, Accountability, and Transparency (FAT\* 2019).  
- Weidinger, L., Rauh, M., Marchal, N., Manzini, A., et al. (2023). [Sociotechnical safety evaluation of generative AI systems](https://arxiv.org/abs/2310.11986). arXiv:2310.11986. *(Preprint)*

#### The Team Is the System

> When people work with AI, evaluate the person and the AI together, not the AI alone.

##### Takeaways

- A strong model doesn't guarantee a strong human-AI team.  
- In a large meta-analysis, human-AI combinations did worse on average than the best of humans or AI alone, with losses on decision tasks and gains on creative tasks.  
- Explanations can raise trust without raising accuracy.  
- Measure overreliance (accepting wrong AI advice) and underreliance (ignoring right advice).

##### What it means

Most AI products put a person in the loop. That person decides whether to accept, edit, or ignore what the AI suggests. So the thing that produces outcomes is the pair, not the model. A model that's 90% accurate paired with a person who can't tell when it's wrong can produce worse results than either one alone.

##### The evidence

- **Combinations often underperform.** Vaccaro, Almaatouq, and Malone (2024) analyzed 106 experimental studies with 370 effect sizes. On average, human-AI combinations performed worse than the best of humans or AI alone (Hedges' g \= \-0.23). Combinations lost ground on decision-making tasks and gained on content creation tasks. When humans outperformed the AI alone, combining helped. When the AI outperformed humans alone, combining hurt.  
- **Explanations increase acceptance, right or wrong.** Bansal et al. (2021) found that AI explanations increased the chance people accepted the AI's recommendation regardless of whether it was correct. AI assistance did produce some complementary gains, but explanations didn't add to them.  
- **Friction can help.** Buçinca, Malaya, and Gajos (2021) found that cognitive forcing functions, which prompt people to think before seeing the AI's answer, reduced overreliance, though people rated those designs less favorably.  
- **An old problem.** Parasuraman and Riley (1997) described use, misuse, disuse, and abuse of automation decades before generative AI.  
- **Design guidance.** Amershi et al. (2019) proposed 18 guidelines for human-AI interaction, many of which, like making clear how well the system can do what it does, affect how teams perform.

##### Use it

- When possible, compare three conditions: human alone, AI alone, and human with AI.  
- Measure accuracy specifically on cases where the AI is wrong. That's where overreliance shows up.  
- Track time, effort, and confidence, not just final accuracy.  
- Test design choices like explanations, confidence displays, and forcing functions as experiments, not assumptions.

##### Origins

"The Team Is the System" is this site's name. The research draws on decades of human factors work on automation, plus newer human-AI interaction studies.

##### Sources

- Amershi, S., et al. (2019). [Guidelines for human-AI interaction](https://doi.org/10.1145/3290605.3300233). Proceedings of the CHI Conference on Human Factors in Computing Systems (CHI 2019).  
- Bansal, G., Wu, T., Zhou, J., Fok, R., Nushi, B., Kamar, E., Ribeiro, M. T., & Weld, D. (2021). [Does the whole exceed its parts? The effect of AI explanations on complementary team performance](https://arxiv.org/abs/2006.14779). Proceedings of the CHI Conference on Human Factors in Computing Systems (CHI 2021).  
- Buçinca, Z., Malaya, M. B., & Gajos, K. Z. (2021). [To trust or to think: Cognitive forcing functions can reduce overreliance on AI in AI-assisted decision-making](https://arxiv.org/abs/2102.09692). Proceedings of the ACM on Human-Computer Interaction, 5(CSCW1), Article 188\.  
- Parasuraman, R., & Riley, V. (1997). [Humans and automation: Use, misuse, disuse, abuse](https://doi.org/10.1518/001872097778543886). Human Factors, 39(2), 230-253.  
- Vaccaro, M., Almaatouq, A., & Malone, T. (2024). [When combinations of humans and AI are useful: A systematic review and meta-analysis](https://doi.org/10.1038/s41562-024-02024-1). Nature Human Behaviour, 8, 2293-2303.

#### The Jagged Frontier

> AI capability is uneven, and its edges don't line up with what people find hard.

##### Takeaways

- AI can excel at a task that seems hard and fail at one that seems easy.  
- People can't see where the edge is, so they carry trust from tasks inside it to tasks outside it.  
- Inside the frontier, AI help improves speed and quality. Outside it, AI help can make people worse.  
- Map the frontier for your own tasks with direct tests. Don't infer it from general benchmarks.

##### What it means

Human skill tends to be smooth: someone who can write a strong strategy memo can usually do the simpler tasks around it. AI capability is jagged. The same model can draft a solid analysis and then botch a detail any junior analyst would catch. General benchmark scores flatten this into one number, which makes them a poor guide to which of your tasks are safe to hand off.

##### The evidence

- **Field experiment with consultants.** Dell'Acqua et al. (2023) ran an experiment with 758 Boston Consulting Group consultants on 18 realistic tasks. On tasks inside the AI's frontier, consultants using GPT-4 completed 12.2% more tasks, worked 25.1% faster, and produced results rated more than 40% higher in quality. On a task outside the frontier, consultants using AI were 19 percentage points less likely to produce correct solutions than those without it. The study was later published in Organization Science (Dell'Acqua et al., 2026).  
- **Task type matters.** Vaccaro, Almaatouq, and Malone (2024) found human-AI combinations tended to lose ground on decision tasks and gain on creation tasks, another sign that value depends heavily on which task you're looking at.  
- **An older version of the idea.** Hans Moravec (1988) observed that it's comparatively easy to get computers to perform well on things like intelligence tests and board games, and hard to give them the perception and mobility skills of a one-year-old.

##### Use it

- List the tasks in your workflow and test the AI on each one directly, including the ones that seem trivial.  
- Share the map with users: where to rely on the AI and where to double-check.  
- Re-map after model updates. The frontier moves.  
- Design interfaces that make uncertainty visible near the edges.

##### Origins

The term comes from Fabrizio Dell'Acqua, Ethan Mollick, Karim Lakhani, and colleagues' field experiment, first released as a Harvard Business School working paper in 2023\.

##### Sources

- Dell'Acqua, F., McFowland III, E., Mollick, E., Lifshitz, H., Kellogg, K., Rajendran, S., Krayer, L., Candelon, F., & Lakhani, K. R. (2026). [Navigating the jagged technological frontier: Field experimental evidence of the effects of artificial intelligence on knowledge worker productivity and quality](https://doi.org/10.1287/orsc.2025.21838). Organization Science, 37(2).  
- Dell'Acqua, F., McFowland III, E., Mollick, E., Lifshitz-Assaf, H., Kellogg, K., Rajendran, S., Krayer, L., Candelon, F., & Lakhani, K. R. (2023). [Navigating the jagged technological frontier: Field experimental evidence of the effects of AI on knowledge worker productivity and quality](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4573321). Harvard Business School Working Paper 24-013. *(Working paper)*  
- Moravec, H. (1988). Mind children: The future of robot and human intelligence. Harvard University Press. *(Book)*  
- Vaccaro, M., Almaatouq, A., & Malone, T. (2024). [When combinations of humans and AI are useful: A systematic review and meta-analysis](https://doi.org/10.1038/s41562-024-02024-1). Nature Human Behaviour, 8, 2293-2303.

## Being Pragmatic

The laws on this site describe the ways evaluation goes wrong. This page is about doing it anyway, inside a team with deadlines, limited budget, and a model that changed last Tuesday.

Perfect evaluation doesn't exist. What you're after is evidence that's good enough for the decision in front of you, gathered in a way the team will keep doing next quarter. Research on how practitioners actually work backs this up. Teams start with informal checks, struggle to turn results into changes, and feel constant pressure to ship (van der Maden et al., 2026; Madaio et al., 2022). A pragmatic approach works with those realities instead of pretending they aren't there.

### Ten principles

#### 1\. Match the rigor to the stakes

Not every AI feature needs a full evaluation program. A tool that drafts internal meeting notes and a tool that flags patients for sepsis don't deserve the same process. The NIST AI Risk Management Framework (2023) says policies and resources should be prioritized by risk level and potential impact, and notes that trying to eliminate all negative risk can be counterproductive. The European Union's AI Act (2024) takes the same risk-based approach, with its heaviest requirements reserved for high-risk uses.

| Tier | Looks like | Minimum evidence before launch | Laws to lean on |
| :---- | :---- | :---- | :---- |
| Low | Internal, easy to undo, a person reviews every output | A saved set of real examples, a team review of outputs, a named owner | The Construct Gap, Criteria Drift |
| Medium | Customer-facing, reversible, moderate cost of errors | A locked test set, a rubric, a baseline, multiple runs, one or two slices, an eval card, a staged rollout | Prompt Sensitivity, Once Is Not Reliable, The Baseline Rule, The Averaging Trap |
| High | Affects health, money, safety, rights, or access; hard to reverse | Everything above, plus validated graders, confidence intervals, subgroup analysis, red teaming, a field pilot, independent review, and post-launch monitoring | All of them, especially The Functionality Fallacy, Presence, Not Absence, and The Lab-to-Field Gap |

Engineers building LLM features have asked this question directly: where's the line between enough evidence and overspending chasing perfection (Parnin et al., 2025)? Tiers give the team an answer they agreed on in advance, instead of relitigating it for every launch.

#### 2\. Start with vibe checks, then write them down

Every team starts by trying the thing and seeing how it feels. That's fine. In interviews with 19 practitioners building LLM products, van der Maden et al. (2026) found informal "vibe checks" described as "irreplaceable, they are the first line of evaluation." The problem isn't vibe checks. It's stopping there.

The move is to formalize gradually. Save the examples you tried. Write down what you were looking for. When the same note shows up three times, it's a criterion. Madaio et al. (2020) found that checklists can give teams infrastructure for formalizing ad hoc processes, as long as they're grounded in practitioners' real needs. Otherwise they get misused.

#### 3\. Tie every eval to a decision

Van der Maden et al. (2026) named the most common failure the results-actionability gap: teams collect evaluation data but can't turn it into concrete improvements. It affected 17 of their 19 participants. One put it plainly: "When you have an evaluation scale and you end up with a 4.6 out of ten, if you don't know what caused that, then it's very difficult to iterate on making it better."

Two habits help:

- **Write the decision rule first.** "If accuracy on refund requests is below 90%, we don't expand the rollout." "If the new prompt doesn't beat the old one by more than the error bars, we keep the old one."  
- **Change one thing at a time.** Prompt, model, retrieval settings, and temperature all interact. If you change three at once, a score change tells you almost nothing about what to fix.

#### 4\. Fit into rituals the team already has

New processes that feel like extra work die quietly. Rogers (2003) identified what speeds up adoption of a new practice: it's clearly better than what people do now, compatible with how they already work, simple to understand, easy to try on a small scale, and visible to others. Evaluation is no different.

- Add 15 minutes of output review to an existing sprint review or design critique instead of creating a new meeting.  
- Put the eval card in the launch review template that already exists.  
- Run a small canary eval in the same pipeline that runs other tests.  
- Share one interesting failure in the team channel each week. It makes the work visible without a status report.

#### 5\. Look at outputs together

The fastest way to build shared judgment is to read real outputs as a group: product, design, engineering, and someone with domain expertise. Disagreements about whether an output is "good" surface the definitions you haven't written yet (Wallach et al., 2025; Shankar et al., 2024).

Keep the session honest. Wu et al. (2019) found that the common practice of eyeballing a small sample of errors can lead to biased, incomplete conclusions. They recommend defining error groups precisely, looking at enough examples (including successes, not just failures), and testing your hypothesis about what causes an error instead of assuming it.

Bring in domain experts early. Madaio et al. (2022) found that lack of engagement with stakeholders and domain experts was one of the main organizational barriers to meaningful evaluation.

#### 6\. Give it an owner, not a police force

When evaluation is everyone's job, it's no one's. Rakova et al. (2021) interviewed practitioners across 19 organizations and found role uncertainty was a recurring barrier. As one put it, "Whose job is this?" Work fell through the cracks, depended on individual volunteers, and was hard to credit in performance reviews.

- Name an owner for each AI feature's evaluation. On a small team, that can be a hat someone wears, not a new role.  
- Put evaluation work in role expectations and recognize it in reviews.  
- The owner's job is to make evaluation easy for the team, not to approve or reject other people's work.

#### 7\. Make bad news safe to share

An eval that finds a problem is doing its job. If finding one feels like getting someone in trouble, people stop looking. Edmondson (1999) found that psychological safety, "a shared belief that the team is safe for interpersonal risk taking," was linked to learning behavior in work teams.

- Celebrate failures found before launch. That's the cheapest time to find them.  
- Run blameless reviews when something slips through. Google's site reliability practice treats postmortems as a way to learn from incidents, not to assign blame (Beyer et al., 2016).  
- Leaders go first: share a result that didn't go the way you hoped.

#### 8\. Spend the budget where it counts

Evaluation costs money and time, and the costs add up. Engineers building product copilots described tests that cost a cent or two each, which became real money at scale, and one was asked to stop running benchmarks because of the cost (Parnin et al., 2025).

Layer it:

- **Every change:** a small, fast canary set with automated checks.  
- **Every milestone:** the full locked test set with repeated runs and slices.  
- **High-stakes slices:** human review, every time.  
- **Before a big launch:** red teaming and a field pilot, scaled to the tier.

#### 9\. Assume production will surprise you

The title of one interview study says it: "We have no idea how models will behave in production until production" (Shankar et al., 2024). The engineers in that study evaluated throughout a multi-stage deployment and kept monitoring after launch, balancing velocity against visibility and versioning.

That's not an excuse to skip pre-launch testing. It's a reason to plan for what happens after.

- **Roll out in stages.** Internal users, then a small percentage of customers, then more. Controlled online experiments let you measure real impact while limiting exposure (Kohavi et al., 2020).  
- **Set an error budget.** Borrowed from site reliability engineering (Beyer et al., 2016): agree ahead of time on an acceptable failure rate, and on what the team does when it's exceeded.  
- **Don't wait for complaints.** In a survey of industry practitioners, about half said their teams had found serious fairness issues only after deploying a system. One engineer described the default as putting the model out there, and "then you'll know if there's fairness issues if someone raises hell online" (Holstein et al., 2019). Internal audits across the development lifecycle are the proactive alternative (Raji et al., 2020).

#### 10\. Use the laws as questions, not weapons

Nobody wants the coworker who quotes Goodhart's Law in every meeting. The laws work best as questions, asked at the right moment, about the two or three risks that matter for the decision at hand.

- Instead of "That's the Construct Gap," try "What would a user need to be able to do for this score to mean what we want?"  
- Instead of "No error bars, no result," try "How much would this number move if we ran it again?"  
- Instead of "That's contamination," try "Could the model have seen these questions before?"

And don't let the perfect eval block a good one. Breck et al. (2017) framed production readiness as a rubric teams score themselves against and improve over time. Treat evaluation maturity the same way.

### A maturity path

Most teams move through these stages. Van der Maden et al. (2026) describe it as a formalization journey. Skipping ahead rarely sticks, so aim for the next stage, not the last one.

| Stage | What it looks like | Next small step |
| :---- | :---- | :---- |
| 0\. Vibes | People try it and share impressions | Save the examples you tried and what you noticed |
| 1\. Saved examples | A shared doc or spreadsheet of real inputs and outputs | Write a one-sentence construct and a first rubric |
| 2\. Repeatable eval | A locked test set, a rubric, a baseline, a person responsible | Add multiple prompts and runs, and one slice |
| 3\. Built into the workflow | Automated canary checks, human spot checks, intervals, slices, eval cards in launch reviews | Add staged rollouts and production monitoring |
| 4\. Continuous | Monitoring, error budgets, periodic audits, rubrics that evolve with version history | Share what you learned with other teams |

### A starter plan for the first 30 days

**Week 1\. Look.** Pick one AI feature. Pull 30 to 50 real examples. Run a one-hour output review with product, design, engineering, and a domain expert. Note what's good, what's bad, and what people disagree about.

**Week 2\. Define.** Write the construct in one sentence. Draft a rubric from the week 1 notes. Pick a baseline. Write one decision rule.

**Week 3\. Measure.** Build a small locked test set. Run it with three prompt variants and three runs each. Compute simple confidence intervals. Break results down by one slice that matters.

**Week 4\. Embed.** Add an eval card to the launch review. Name an owner. Set a rerun trigger, like every model or prompt change. Share one finding with the wider team.

### Who does what

Small teams will combine these. What matters is that each job has a name next to it.

| Role | Owns |
| :---- | :---- |
| Product | The decision, the risk tier, and the thresholds |
| Design and UX research | Construct definitions, rubrics, user and field studies, human-AI team evaluation |
| Engineering and ML | The eval harness, versioning, automation, monitoring |
| Domain experts | Labels, edge cases, rubric review |
| Leadership | Time and budget, recognition, and making evaluation part of launch criteria |

### Common pushback, and how to answer it

| You hear | Try |
| :---- | :---- |
| "We don't have time." | Start with 30 examples and one hour. Finding the problem after launch costs more. |
| "The model changes every month anyway." | That's why you want a small canary set you can rerun in minutes. |
| "Our users will tell us if something's wrong." | Some will, often late and in public. User feedback is one input, not the whole picture. |
| "The benchmark says this model is the best." | Best at that benchmark. Let's check it on our data. |
| "Evaluation will slow us down." | Match the effort to the tier, and ship in stages so you learn while you ship. |
| "Quality is subjective. You can't measure it." | Then let's define what we mean, write it down, and see whether two people agree. |
| "The LLM judge is good enough." | It might be. Let's check it against 50 human labels first. |

### References

- Beyer, B., Jones, C., Petoff, J., & Murphy, N. R. (Eds.) (2016). [Site reliability engineering: How Google runs production systems](https://sre.google/sre-book/table-of-contents/). O'Reilly Media. *(Book)*  
- Breck, E., Cai, S., Nielsen, E., Salib, M., & Sculley, D. (2017). [The ML test score: A rubric for ML production readiness and technical debt reduction](https://research.google/pubs/the-ml-test-score-a-rubric-for-ml-production-readiness-and-technical-debt-reduction/). Proceedings of the IEEE International Conference on Big Data.  
- Edmondson, A. (1999). [Psychological safety and learning behavior in work teams](https://doi.org/10.2307/2666999). Administrative Science Quarterly, 44(2), 350-383.  
- European Union (2024). [Regulation (EU) 2024/1689 laying down harmonised rules on artificial intelligence (Artificial Intelligence Act)](https://eur-lex.europa.eu/eli/reg/2024/1689/oj). Official Journal of the European Union. *(Report)*  
- Holstein, K., Wortman Vaughan, J., Daumé III, H., Dudík, M., & Wallach, H. (2019). [Improving fairness in machine learning systems: What do industry practitioners need?](https://arxiv.org/abs/1812.05239) Proceedings of the CHI Conference on Human Factors in Computing Systems (CHI 2019).  
- Kohavi, R., Tang, D., & Xu, Y. (2020). Trustworthy online controlled experiments: A practical guide to A/B testing. Cambridge University Press. *(Book)*  
- Madaio, M. A., Stark, L., Wortman Vaughan, J., & Wallach, H. (2020). [Co-designing checklists to understand organizational challenges and opportunities around fairness in AI](https://doi.org/10.1145/3313831.3376445). Proceedings of the CHI Conference on Human Factors in Computing Systems (CHI 2020).  
- Madaio, M., Egede, L., Subramonyam, H., Wortman Vaughan, J., & Wallach, H. (2022). [Assessing the fairness of AI systems: AI practitioners' processes, challenges, and needs for support](https://doi.org/10.1145/3512899). Proceedings of the ACM on Human-Computer Interaction, 6(CSCW1), Article 52\.  
- National Institute of Standards and Technology (2023). [Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1](https://doi.org/10.6028/NIST.AI.100-1). U.S. Department of Commerce. *(Report)*  
- Parnin, C., Soares, G., Pandita, R., Gulwani, S., Rich, J., & Henley, A. Z. (2025). [Building your own product copilot: Challenges, opportunities, and needs](https://arxiv.org/abs/2312.14231). Proceedings of the IEEE International Conference on Software Analysis, Evolution and Reengineering (SANER 2025).  
- Raji, I. D., Smart, A., White, R. N., Mitchell, M., Gebru, T., et al. (2020). [Closing the AI accountability gap: Defining an end-to-end framework for internal algorithmic auditing](https://arxiv.org/abs/2001.00973). Proceedings of the Conference on Fairness, Accountability, and Transparency (FAT\* 2020).  
- Rakova, B., Yang, J., Cramer, H., & Chowdhury, R. (2021). [Where responsible AI meets reality: Practitioner perspectives on enablers for shifting organizational practices](https://doi.org/10.1145/3449081). Proceedings of the ACM on Human-Computer Interaction, 5(CSCW1).  
- Rogers, E. M. (2003). Diffusion of innovations (5th ed.). Free Press. *(Book)*  
- Shankar, S., Garcia, R., Hellerstein, J. M., & Parameswaran, A. G. (2024). ["We have no idea how models will behave in production until production": How engineers operationalize machine learning](https://doi.org/10.1145/3653697). Proceedings of the ACM on Human-Computer Interaction, 8(CSCW1), Article 206\.  
- Shankar, S., Zamfirescu-Pereira, J. D., Hartmann, B., Parameswaran, A. G., & Arawjo, I. (2024). [Who validates the validators? Aligning LLM-assisted evaluation of LLM outputs with human preferences](https://doi.org/10.1145/3654777.3676450). Proceedings of the ACM Symposium on User Interface Software and Technology (UIST 2024).  
- van der Maden, W., Sadek, M., Xiao, Z., Mottelson, A., Liao, Q. V., & Zhu, J. (2026). [Results-actionability gap: Understanding how practitioners evaluate LLM products in the wild](https://doi.org/10.1145/3772318.3791069). Proceedings of the CHI Conference on Human Factors in Computing Systems (CHI 2026).  
- Wallach, H., Desai, M., Cooper, A. F., Wang, A., Atalla, C., et al. (2025). [Position: Evaluating generative AI systems is a social science measurement challenge](https://arxiv.org/abs/2502.00561). Proceedings of the International Conference on Machine Learning (ICML 2025), PMLR 267\.  
- Wu, T., Ribeiro, M. T., Heer, J., & Weld, D. (2019). [Errudite: Scalable, reproducible, and testable error analysis](https://aclanthology.org/P19-1073/). Proceedings of ACL 2019\.

## Playbook

For how to introduce these practices to a team without slowing it down, see Being Pragmatic.

### 1\. Reading an AI claim

Ten questions for any benchmark result, vendor deck, or launch post.

1. **What decision is this number supposed to support?** If nobody can say, the number is marketing. *(The Functionality Fallacy)*  
2. **What exactly was measured?** Read some test items. Does the benchmark's name match its contents? *(The Construct Gap)*  
3. **Could the model have seen the test?** Check the benchmark's release date against the training cutoff. *(Data Contamination)*  
4. **How big is the test, and where are the error bars?** A 2-point gap on 200 items is probably noise. *(No Error Bars, No Result)*  
5. **Better than what?** Was there a simple baseline, and was it tuned fairly? *(The Baseline Rule)*  
6. **Who's hidden in the average?** Is there a breakdown by group, language, or input type? *(The Averaging Trap)*  
7. **How many tries did this take?** Prompts, variants, runs, and seeds all count. *(Prompt Sensitivity, Once Is Not Reliable, Campbell's Law)*  
8. **Who did the grading, and was the grader checked?** *(Judge Bias, The Gold Standard Myth)*  
9. **What did it cost to get this score?** *(The Cost Frontier)*  
10. **Has anyone independent reproduced it in a setting like yours?** *(The Reproducibility Rule, Distribution Shift, The Lab-to-Field Gap)*

### 2\. Building your own eval

A practical sequence for product teams. Scale each step to the stakes.

1. **Start with the decision.** Write down what you'll do differently depending on the result.  
2. **Define the construct in one sentence.** "Good" is not a definition. "Resolves the request without a follow-up" is.  
3. **Collect test cases from real use.** Include edge cases and known past failures. Keep a private, locked test set that never touches prompt tuning.  
4. **Read outputs before you write the rubric.** Expect the rubric to change, and version it (Shankar et al., 2024).  
5. **Pick metrics before running.** Include at least one continuous metric, plus cost and latency.  
6. **Set baselines.** The current workflow, a simple method, and the model you use today.  
7. **Vary prompts and repeat runs.** Three to five prompt variants and several samples per case is a reasonable floor (Sclar et al., 2024; Yao et al., 2025).  
8. **Validate your graders.** Measure agreement between human raters. If you use an LLM judge, check it against human labels first (Zheng et al., 2023).  
9. **Compute intervals and slice the results.** Report confidence intervals, paired comparisons, and the worst slice (Miller, 2024).  
10. **Probe for what the score can't show.** Try shortcut tests, red teaming, and serious elicitation effort.  
11. **Test people and AI together, in context.** When you can, compare human alone, AI alone, and human with AI (Vaccaro et al., 2024).  
12. **Document it, rerun it, monitor it.** Write an eval card, save raw outputs, rerun a canary set on every model update, and watch production after launch.

### 3\. Red flags

| You see | It might mean | Law |
| :---- | :---- | :---- |
| One headline number, no interval | The difference could be noise | No Error Bars, No Result |
| "Superhuman" on a benchmark that's several years old | Saturation, contamination, or both | Benchmark Saturation, Data Contamination |
| Big win on public benchmarks, nothing private | Memorization or overfitting to the public test | Data Contamination, Adaptive Overfitting |
| Results shown only on benchmarks where the system won | Selective reporting | The Benchmark Lottery |
| A model grading its own outputs | Self-preference bias | Judge Bias |
| Scores jumped after lots of prompt tweaking on the test set | Fitting to the test | Adaptive Overfitting, Goodhart's Law |
| "We found no evidence of dangerous capability X" | Limited elicitation effort | Presence, Not Absence |
| A great demo and no field pilot | Untested in real conditions | The Lab-to-Field Gap |
| Accuracy compared across systems with very different costs | An unfair comparison | The Cost Frontier |
| Explanations added mainly to raise user trust | Possible overreliance | The Team Is the System |
| High average accuracy, no subgroup breakdown | Hidden failures | The Averaging Trap |
| A single run per test case for an agent | Unknown reliability | Once Is Not Reliable |

### 4\. Eval card template

Copy this into any eval you run. It borrows from model cards (Mitchell et al., 2019).

EVAL CARD

Name / version:

Owner:

Date run:

&nbsp;

Decision this informs:

Construct (one sentence):

Intended use and users:

&nbsp;

System under test (model \+ version, system prompt, settings):

Baselines:

&nbsp;

Test data (source, size, date range, how it was protected from training and tuning):

Slices reported:

&nbsp;

Metrics (and why):

Grading (human raters, agreement, LLM judge validation):

Prompt variants and runs per case:

&nbsp;

Results (with 95% intervals and worst slice):

Cost and latency:

&nbsp;

Elicitation and red teaming effort:

Known limits and open questions:

Where raw outputs and code live:

Next rerun trigger:

### References

- Miller, E. (2024). [Adding error bars to evals: A statistical approach to language model evaluations](https://arxiv.org/abs/2411.00640). arXiv:2411.00640. *(Preprint)*  
- Mitchell, M., et al. (2019). [Model cards for model reporting](https://arxiv.org/abs/1810.03993). Proceedings of the Conference on Fairness, Accountability, and Transparency (FAT\* 2019).  
- Sclar, M., Choi, Y., Tsvetkov, Y., & Suhr, A. (2024). [Quantifying language models' sensitivity to spurious features in prompt design or: How I learned to start worrying about prompt formatting](https://arxiv.org/abs/2310.11324). International Conference on Learning Representations (ICLR 2024).  
- Shankar, S., Zamfirescu-Pereira, J. D., Hartmann, B., Parameswaran, A. G., & Arawjo, I. (2024). [Who validates the validators? Aligning LLM-assisted evaluation of LLM outputs with human preferences](https://doi.org/10.1145/3654777.3676450). Proceedings of the ACM Symposium on User Interface Software and Technology (UIST 2024).  
- Vaccaro, M., Almaatouq, A., & Malone, T. (2024). [When combinations of humans and AI are useful: A systematic review and meta-analysis](https://doi.org/10.1038/s41562-024-02024-1). Nature Human Behaviour, 8, 2293-2303.  
- Yao, S., Shinn, N., Razavi, P., & Narasimhan, K. (2025). [τ-bench: A benchmark for tool-agent-user interaction in real-world domains](https://arxiv.org/abs/2406.12045). International Conference on Learning Representations (ICLR 2025).  
- Zheng, L., Chiang, W.-L., Sheng, Y., Zhuang, S., Wu, Z., et al. (2023). [Judging LLM-as-a-judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685). NeurIPS 2023 Datasets and Benchmarks Track.

## Glossary

**Adaptive overfitting.** Fitting a system to a specific test set by repeatedly making choices based on its results. See *Adaptive Overfitting*.

**Aggregate metric.** A single number that summarizes performance across all test cases, like overall accuracy. See *The Averaging Trap*.

**AUC (area under the ROC curve).** A measure of how well a classifier separates positive from negative cases across all thresholds. 0.5 is chance, 1.0 is perfect.

**Baseline.** The comparison point for a result: a simpler method, an older model, or the current human workflow. See *The Baseline Rule*.

**Behavioral testing.** Checking specific behaviors with targeted test cases, like whether a model's answer stays the same when a name is changed (Ribeiro et al., 2020).

**Benchmark.** A fixed dataset and scoring method used to compare systems on a task.

**Calibration.** How well a system's confidence matches how often it's actually right. A calibrated model that says "90% sure" is right about 90% of the time. Modern neural networks are often overconfident (Guo et al., 2017).

**Capability evaluation.** Testing what a system can do, as opposed to how people use it or what effects it has.

**Complementary performance.** When a human-AI team does better than either the human or the AI alone (Bansal et al., 2021).

**Confidence interval.** A range that likely contains the true value of a measurement, given sampling noise. See *No Error Bars, No Result*.

**Construct.** An abstract quality you want to measure but can't observe directly, like reasoning or helpfulness (Cronbach & Meehl, 1955).

**Construct validity.** How well a measurement actually captures the construct it claims to measure (Messick, 1995). See *The Construct Gap*.

**Contamination.** When test data, or close copies of it, appear in a model's training data. See *Data Contamination*.

**Criteria drift.** The way evaluation criteria change as people grade real outputs. See *Criteria Drift*.

**Datasheet.** A standard document describing how a dataset was created, what's in it, and what it's suited for (Gebru et al., 2021).

**Disaggregated evaluation.** Reporting results separately for different groups or input types instead of only as an average.

**Distribution shift.** A difference between the data a system was built and tested on and the data it meets in use. See *Distribution Shift*.

**Dynamic benchmark.** A benchmark that keeps adding new examples, often written to defeat current models.

**Elicitation.** The effort put into drawing out a model's full capability, through prompting, tools, fine-tuning, or scaffolding. See *Presence, Not Absence*.

**Error analysis.** Grouping and studying a system's mistakes to understand their causes. Works best with precisely defined error groups, enough examples, and tested hypotheses (Wu et al., 2019). See *Being Pragmatic*.

**Error budget.** An agreed-on acceptable failure rate, with an agreed-on response when it's exceeded. Borrowed from site reliability engineering (Beyer et al., 2016). See *Being Pragmatic*.

**Evaluation awareness.** A model's ability to tell that it's being evaluated rather than used for real (Needham et al., 2025). See *Evaluation Awareness*.

**External validation.** Testing a system on data from a different setting than the one it was developed in, ideally by an independent team.

**Ground truth.** The answer treated as correct in an evaluation. Often a human judgment with its own error. See *The Gold Standard Myth*.

**Holdout set.** Data kept separate from training and tuning so it can give an unbiased estimate of performance (Dwork et al., 2015).

**Inter-rater agreement.** How often independent human raters give the same judgment. Low agreement means the task, the instructions, or the construct needs work.

**Leaderboard.** A public ranking of systems on one or more benchmarks. See *Campbell's Law*.

**LLM-as-a-judge.** Using a language model to grade or compare outputs from AI systems (Zheng et al., 2023). See *Judge Bias*.

**Model card.** A standard document describing a model's intended use, evaluation results, and limitations (Mitchell et al., 2019).

**Online controlled experiment.** Randomly exposing some users to a change and comparing outcomes against users who didn't get it, often called an A/B test (Kohavi et al., 2020).

**Overreliance.** Accepting AI output when it's wrong. Its opposite, underreliance, is ignoring AI output when it's right (Parasuraman & Riley, 1997). See *The Team Is the System*.

**Pairwise comparison.** Asking raters which of two outputs is better, instead of scoring each on its own. Used at scale by preference arenas (Chiang et al., 2024).

**Pareto frontier.** The set of options where you can't improve one metric, like accuracy, without making another, like cost, worse. See *The Cost Frontier*.

**pass@k and pass^k.** pass@k is the chance of at least one success in k attempts. pass^k is the chance of success on all k attempts, a measure of consistency (Yao et al., 2025). See *Once Is Not Reliable*.

**Prompt sensitivity.** How much a model's results change with small changes to how a prompt is worded or formatted. See *Prompt Sensitivity*.

**Red teaming.** Deliberately trying to make a system fail or cause harm, to find problems before others do.

**Reliability (measurement).** How consistent a measurement is when repeated. A measurement can be reliable and still not valid.

**Reward hacking.** When an optimized system finds a way to score well on its objective without doing what the objective was meant to encourage. See *Goodhart's Law*.

**Risk tier.** A category that sets how much evaluation a system needs, based on its potential impact. Risk-based prioritization is central to the NIST AI Risk Management Framework (2023). See *Being Pragmatic*.

**Sandbagging.** Strategic underperformance on an evaluation (van der Weij et al., 2025).

**Saturation.** When top systems score near the maximum on a benchmark, so it no longer separates them. See *Benchmark Saturation*.

**Shortcut learning.** Learning a pattern that predicts the right answer on the test without the intended skill (Geirhos et al., 2020). See *The Clever Hans Effect*.

**Sociotechnical evaluation.** Evaluating a system together with the people, workflows, and institutions around it. See *The Lab-to-Field Gap*.

**Staged rollout.** Releasing a system to progressively larger groups of users while monitoring results at each step.

**Statistical power.** The chance an experiment detects a real difference of a given size. Small test sets have low power. See *No Error Bars, No Result*.

**Validity.** How well the evidence supports the interpretations and uses of a score (Messick, 1995).

**Vibe check.** Informal, exploratory trying-out of an AI system. Practitioners describe it as the first line of evaluation (van der Maden et al., 2026). Useful as a start, risky as the whole process.

### References

- Bansal, G., Wu, T., Zhou, J., Fok, R., Nushi, B., Kamar, E., Ribeiro, M. T., & Weld, D. (2021). [Does the whole exceed its parts? The effect of AI explanations on complementary team performance](https://arxiv.org/abs/2006.14779). Proceedings of the CHI Conference on Human Factors in Computing Systems (CHI 2021).  
- Beyer, B., Jones, C., Petoff, J., & Murphy, N. R. (Eds.) (2016). [Site reliability engineering: How Google runs production systems](https://sre.google/sre-book/table-of-contents/). O'Reilly Media. *(Book)*  
- Chiang, W.-L., et al. (2024). [Chatbot Arena: An open platform for evaluating LLMs by human preference](https://arxiv.org/abs/2403.04132). Proceedings of the International Conference on Machine Learning (ICML 2024).  
- Cronbach, L. J., & Meehl, P. E. (1955). [Construct validity in psychological tests](https://doi.org/10.1037/h0040957). Psychological Bulletin, 52(4), 281-302.  
- Dwork, C., Feldman, V., Hardt, M., Pitassi, T., Reingold, O., & Roth, A. (2015). [The reusable holdout: Preserving validity in adaptive data analysis](https://doi.org/10.1126/science.aaa9375). Science, 349(6248), 636-638.  
- Gebru, T., et al. (2021). [Datasheets for datasets](https://arxiv.org/abs/1803.09010). Communications of the ACM, 64(12), 86-92.  
- Geirhos, R., Jacobsen, J.-H., Michaelis, C., Zemel, R., Brendel, W., Bethge, M., & Wichmann, F. A. (2020). [Shortcut learning in deep neural networks](https://arxiv.org/abs/2004.07780). Nature Machine Intelligence, 2, 665-673.  
- Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). [On calibration of modern neural networks](https://arxiv.org/abs/1706.04599). Proceedings of the International Conference on Machine Learning (ICML 2017).  
- Kohavi, R., Tang, D., & Xu, Y. (2020). Trustworthy online controlled experiments: A practical guide to A/B testing. Cambridge University Press. *(Book)*  
- Messick, S. (1995). [Validity of psychological assessment: Validation of inferences from persons' responses and performances as scientific inquiry into score meaning](https://doi.org/10.1037/0003-066X.50.9.741). American Psychologist, 50(9), 741-749.  
- Mitchell, M., et al. (2019). [Model cards for model reporting](https://arxiv.org/abs/1810.03993). Proceedings of the Conference on Fairness, Accountability, and Transparency (FAT\* 2019).  
- National Institute of Standards and Technology (2023). [Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1](https://doi.org/10.6028/NIST.AI.100-1). U.S. Department of Commerce. *(Report)*  
- Needham, J., Edkins, G., Pimpale, G., Bartsch, H., & Hobbhahn, M. (2025). [Large language models often know when they are being evaluated](https://arxiv.org/abs/2505.23836). arXiv:2505.23836. *(Preprint)*  
- Parasuraman, R., & Riley, V. (1997). [Humans and automation: Use, misuse, disuse, abuse](https://doi.org/10.1518/001872097778543886). Human Factors, 39(2), 230-253.  
- Ribeiro, M. T., Wu, T., Guestrin, C., & Singh, S. (2020). [Beyond accuracy: Behavioral testing of NLP models with CheckList](https://arxiv.org/abs/2005.04118). Proceedings of ACL 2020\.  
- van der Maden, W., Sadek, M., Xiao, Z., Mottelson, A., Liao, Q. V., & Zhu, J. (2026). [Results-actionability gap: Understanding how practitioners evaluate LLM products in the wild](https://doi.org/10.1145/3772318.3791069). Proceedings of the CHI Conference on Human Factors in Computing Systems (CHI 2026).  
- van der Weij, T., Hofstätter, F., Jaffe, O., Brown, S. F., & Ward, F. R. (2025). [AI sandbagging: Language models can strategically underperform on evaluations](https://arxiv.org/abs/2406.07358). International Conference on Learning Representations (ICLR 2025).  
- Wu, T., Ribeiro, M. T., Heer, J., & Weld, D. (2019). [Errudite: Scalable, reproducible, and testable error analysis](https://aclanthology.org/P19-1073/). Proceedings of ACL 2019\.  
- Yao, S., Shinn, N., Razavi, P., & Narasimhan, K. (2025). [τ-bench: A benchmark for tool-agent-user interaction in real-world domains](https://arxiv.org/abs/2406.12045). International Conference on Learning Representations (ICLR 2025).  
- Zheng, L., Chiang, W.-L., Sheng, Y., Zhuang, S., Wu, Z., et al. (2023). [Judging LLM-as-a-judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685). NeurIPS 2023 Datasets and Benchmarks Track.

## Bibliography

109 sources. Preprints, reports, working papers, and books are labeled. Everything else is peer-reviewed or a classic in its field.

- Adcock, R., & Collier, D. (2001). [Measurement validity: A shared standard for qualitative and quantitative research](https://doi.org/10.1017/S0003055401003100). American Political Science Review, 95(3), 529-546.  
  Cited in: The Construct Gap, Overview  
- Amershi, S., et al. (2019). [Guidelines for human-AI interaction](https://doi.org/10.1145/3290605.3300233). Proceedings of the CHI Conference on Human Factors in Computing Systems (CHI 2019).  
  Cited in: The Team Is the System  
- Amodei, D., Olah, C., Steinhardt, J., Christiano, P., Schulman, J., & Mané, D. (2016). [Concrete problems in AI safety](https://arxiv.org/abs/1606.06565). arXiv:1606.06565. *(Preprint)*  
  Cited in: Goodhart's Law  
- Aroyo, L., & Welty, C. (2015). [Truth is a lie: Crowd truth and the seven myths of human annotation](https://doi.org/10.1609/aimag.v36i1.2564). AI Magazine, 36(1), 15-24.  
  Cited in: The Gold Standard Myth  
- Bansal, G., Wu, T., Zhou, J., Fok, R., Nushi, B., Kamar, E., Ribeiro, M. T., & Weld, D. (2021). [Does the whole exceed its parts? The effect of AI explanations on complementary team performance](https://arxiv.org/abs/2006.14779). Proceedings of the CHI Conference on Human Factors in Computing Systems (CHI 2021).  
  Cited in: The Team Is the System, Glossary, Overview  
- Bean, A. M., Kearns, R. O., Romanou, A., Hafner, F. S., Mayne, H., et al. (2025). [Measuring what matters: Construct validity in large language model benchmarks](https://arxiv.org/abs/2511.04703). Advances in Neural Information Processing Systems (NeurIPS 2025), Datasets and Benchmarks Track.  
  Cited in: The Construct Gap  
- Beede, E., Baylor, E., Hersch, F., Iurchenko, A., Wilcox, L., Ruamviboonsuk, P., & Vardoulakis, L. M. (2020). [A human-centered evaluation of a deep learning system deployed in clinics for the detection of diabetic retinopathy](https://doi.org/10.1145/3313831.3376718). Proceedings of the CHI Conference on Human Factors in Computing Systems (CHI 2020).  
  Cited in: The Lab-to-Field Gap, Overview  
- Bengio, Y., et al. (2026). [International AI Safety Report 2026](https://internationalaisafetyreport.org/publication/international-ai-safety-report-2026). International AI Safety Report; arXiv:2602.21012. *(Report)*  
  Cited in: Goodhart's Law, Data Contamination, Evaluation Awareness, The Lab-to-Field Gap, Overview  
- Beyer, B., Jones, C., Petoff, J., & Murphy, N. R. (Eds.) (2016). [Site reliability engineering: How Google runs production systems](https://sre.google/sre-book/table-of-contents/). O'Reilly Media. *(Book)*  
  Cited in: Being Pragmatic, Glossary  
- Biderman, S., et al. (2024). [Lessons from the trenches on reproducible evaluation of language models](https://arxiv.org/abs/2405.14782). arXiv:2405.14782. *(Preprint)*  
  Cited in: Prompt Sensitivity, The Reproducibility Rule  
- Bouthillier, X., et al. (2021). [Accounting for variance in machine learning benchmarks](https://arxiv.org/abs/2103.03098). Proceedings of Machine Learning and Systems (MLSys 2021).  
  Cited in: No Error Bars, No Result  
- Bowman, S. R., & Dahl, G. E. (2021). [What will it take to fix benchmarking in natural language understanding?](https://arxiv.org/abs/2104.02145) Proceedings of NAACL-HLT 2021\.  
  Cited in: Benchmark Saturation  
- Breck, E., Cai, S., Nielsen, E., Salib, M., & Sculley, D. (2017). [The ML test score: A rubric for ML production readiness and technical debt reduction](https://research.google/pubs/the-ml-test-score-a-rubric-for-ml-production-readiness-and-technical-debt-reduction/). Proceedings of the IEEE International Conference on Big Data.  
  Cited in: Being Pragmatic  
- Buolamwini, J., & Gebru, T. (2018). [Gender shades: Intersectional accuracy disparities in commercial gender classification](https://proceedings.mlr.press/v81/buolamwini18a.html). Proceedings of the Conference on Fairness, Accountability and Transparency (FAT\* 2018), PMLR 81, 77-91.  
  Cited in: The Averaging Trap  
- Burnell, R., et al. (2023). [Rethink reporting of evaluation results in AI](https://doi.org/10.1126/science.adf6369). Science, 380(6641), 136-138.  
  Cited in: The Averaging Trap, Overview  
- Buçinca, Z., Malaya, M. B., & Gajos, K. Z. (2021). [To trust or to think: Cognitive forcing functions can reduce overreliance on AI in AI-assisted decision-making](https://arxiv.org/abs/2102.09692). Proceedings of the ACM on Human-Computer Interaction, 5(CSCW1), Article 188\.  
  Cited in: The Team Is the System  
- Campbell, D. T. (1979). [Assessing the impact of planned social change](https://doi.org/10.1016/0149-7189\(79\)90048-X). Evaluation and Program Planning, 2(1), 67-90.  
  Cited in: Campbell's Law  
- Card, D., Henderson, P., Khandelwal, U., Jia, R., Mahowald, K., & Jurafsky, D. (2020). [With little power comes great responsibility](https://arxiv.org/abs/2010.06595). Proceedings of EMNLP 2020\.  
  Cited in: No Error Bars, No Result  
- Chang, Y., et al. (2024). [A survey on evaluation of large language models](https://arxiv.org/abs/2307.03109). ACM Transactions on Intelligent Systems and Technology, 15(3).  
  Cited in: Overview  
- Chiang, W.-L., et al. (2024). [Chatbot Arena: An open platform for evaluating LLMs by human preference](https://arxiv.org/abs/2403.04132). Proceedings of the International Conference on Machine Learning (ICML 2024).  
  Cited in: Glossary, Overview  
- Clark, E., August, T., Serrano, S., Haduong, N., Gururangan, S., & Smith, N. A. (2021). [All that's 'human' is not gold: Evaluating human evaluation of generated text](https://arxiv.org/abs/2107.00061). Proceedings of ACL-IJCNLP 2021\.  
  Cited in: The Gold Standard Myth, Overview  
- Cronbach, L. J., & Meehl, P. E. (1955). [Construct validity in psychological tests](https://doi.org/10.1037/h0040957). Psychological Bulletin, 52(4), 281-302.  
  Cited in: The Construct Gap, Glossary  
- Dehghani, M., Tay, Y., Gritsenko, A. A., et al. (2021). [The benchmark lottery](https://arxiv.org/abs/2107.07002). arXiv:2107.07002. *(Preprint)*  
  Cited in: Campbell's Law, The Benchmark Lottery  
- Dell'Acqua, F., McFowland III, E., Mollick, E., Lifshitz, H., Kellogg, K., Rajendran, S., Krayer, L., Candelon, F., & Lakhani, K. R. (2026). [Navigating the jagged technological frontier: Field experimental evidence of the effects of artificial intelligence on knowledge worker productivity and quality](https://doi.org/10.1287/orsc.2025.21838). Organization Science, 37(2).  
  Cited in: The Jagged Frontier  
- Dell'Acqua, F., McFowland III, E., Mollick, E., Lifshitz-Assaf, H., Kellogg, K., Rajendran, S., Krayer, L., Candelon, F., & Lakhani, K. R. (2023). [Navigating the jagged technological frontier: Field experimental evidence of the effects of AI on knowledge worker productivity and quality](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4573321). Harvard Business School Working Paper 24-013. *(Working paper)*  
  Cited in: The Jagged Frontier  
- Dijkstra, E. W. (1970). [Notes on structured programming (EWD249)](https://www.cs.utexas.edu/~EWD/transcriptions/EWD02xx/EWD249/EWD249.html). Technological University Eindhoven (first circulated 1969; second edition April 1970).  
  Cited in: Presence, Not Absence  
- Dror, R., et al. (2018). [The hitchhiker's guide to testing statistical significance in natural language processing](https://aclanthology.org/P18-1128/). Proceedings of ACL 2018\.  
  Cited in: No Error Bars, No Result  
- Dwork, C., Feldman, V., Hardt, M., Pitassi, T., Reingold, O., & Roth, A. (2015). [The reusable holdout: Preserving validity in adaptive data analysis](https://doi.org/10.1126/science.aaa9375). Science, 349(6248), 636-638.  
  Cited in: Adaptive Overfitting, Glossary  
- Edmondson, A. (1999). [Psychological safety and learning behavior in work teams](https://doi.org/10.2307/2666999). Administrative Science Quarterly, 44(2), 350-383.  
  Cited in: Being Pragmatic  
- Eriksson, M., et al. (2025). [Can we trust AI benchmarks? An interdisciplinary review of current issues in AI evaluation](https://arxiv.org/abs/2502.06559). Proceedings of the AAAI/ACM Conference on AI, Ethics, and Society (AIES 2025).  
  Cited in: The Benchmark Lottery, Overview  
- Ethayarajh, K., & Jurafsky, D. (2020). [Utility is in the eye of the user: A critique of NLP leaderboards](https://arxiv.org/abs/2009.13888). Proceedings of EMNLP 2020\.  
  Cited in: Campbell's Law, The Cost Frontier, The Benchmark Lottery  
- European Union (2024). [Regulation (EU) 2024/1689 laying down harmonised rules on artificial intelligence (Artificial Intelligence Act)](https://eur-lex.europa.eu/eli/reg/2024/1689/oj). Official Journal of the European Union. *(Report)*  
  Cited in: Being Pragmatic  
- Ferrari Dacrema, M., Cremonesi, P., & Jannach, D. (2019). [Are we really making much progress? A worrying analysis of recent neural recommendation approaches](https://arxiv.org/abs/1907.06902). Proceedings of the ACM Conference on Recommender Systems (RecSys 2019).  
  Cited in: The Baseline Rule  
- Ganguli, D., et al. (2022). [Red teaming language models to reduce harms: Methods, scaling behaviors, and lessons learned](https://arxiv.org/abs/2209.07858). arXiv:2209.07858. *(Preprint)*  
  Cited in: Presence, Not Absence, Overview  
- Gao, L., Schulman, J., & Hilton, J. (2023). [Scaling laws for reward model overoptimization](https://arxiv.org/abs/2210.10760). Proceedings of the International Conference on Machine Learning (ICML 2023).  
  Cited in: Goodhart's Law  
- Gebru, T., et al. (2021). [Datasheets for datasets](https://arxiv.org/abs/1803.09010). Communications of the ACM, 64(12), 86-92.  
  Cited in: The Reproducibility Rule, Glossary  
- Geirhos, R., Jacobsen, J.-H., Michaelis, C., Zemel, R., Brendel, W., Bethge, M., & Wichmann, F. A. (2020). [Shortcut learning in deep neural networks](https://arxiv.org/abs/2004.07780). Nature Machine Intelligence, 2, 665-673.  
  Cited in: The Clever Hans Effect, Glossary  
- Goodhart, C. A. E. (1975). Problems of monetary management: The U.K. experience. Papers in Monetary Economics, Vol. 1\. Reserve Bank of Australia.  
  Cited in: Goodhart's Law  
- Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). [On calibration of modern neural networks](https://arxiv.org/abs/1706.04599). Proceedings of the International Conference on Machine Learning (ICML 2017).  
  Cited in: Glossary  
- Gururangan, S., Swayamdipta, S., Levy, O., Schwartz, R., Bowman, S. R., & Smith, N. A. (2018). [Annotation artifacts in natural language inference data](https://arxiv.org/abs/1803.02324). Proceedings of NAACL-HLT 2018\.  
  Cited in: The Clever Hans Effect  
- Hand, D. J. (2006). [Classifier technology and the illusion of progress](https://arxiv.org/abs/math/0606441). Statistical Science, 21(1), 1-14.  
  Cited in: The Baseline Rule, Distribution Shift  
- Holstein, K., Wortman Vaughan, J., Daumé III, H., Dudík, M., & Wallach, H. (2019). [Improving fairness in machine learning systems: What do industry practitioners need?](https://arxiv.org/abs/1812.05239) Proceedings of the CHI Conference on Human Factors in Computing Systems (CHI 2019).  
  Cited in: Being Pragmatic  
- Hutchinson, B., et al. (2022). [Evaluation gaps in machine learning practice](https://doi.org/10.1145/3531146.3533233). Proceedings of the ACM Conference on Fairness, Accountability, and Transparency (FAccT 2022).  
  Cited in: The Functionality Fallacy, The Lab-to-Field Gap, Overview  
- Jacobs, A. Z., & Wallach, H. (2021). [Measurement and fairness](https://doi.org/10.1145/3442188.3445901). Proceedings of the ACM Conference on Fairness, Accountability, and Transparency (FAccT 2021).  
  Cited in: The Construct Gap  
- Kapoor, S., & Narayanan, A. (2023). [Leakage and the reproducibility crisis in machine-learning-based science](https://doi.org/10.1016/j.patter.2023.100804). Patterns, 4(9), 100804\.  
  Cited in: Data Contamination  
- Kapoor, S., Stroebl, B., Siegel, Z. S., Nadgir, N., & Narayanan, A. (2025). [AI agents that matter](https://arxiv.org/abs/2407.01502). Transactions on Machine Learning Research (TMLR).  
  Cited in: Adaptive Overfitting, The Cost Frontier, The Reproducibility Rule, Overview  
- Karpinska, M., Akoury, N., & Krishna, K. (2021). [The perils of using Mechanical Turk to evaluate open-ended text generation](https://arxiv.org/abs/2109.06835). Proceedings of EMNLP 2021\.  
  Cited in: The Gold Standard Myth  
- Kiela, D., et al. (2021). [Dynabench: Rethinking benchmarking in NLP](https://arxiv.org/abs/2104.14337). Proceedings of NAACL-HLT 2021\.  
  Cited in: Benchmark Saturation, Overview  
- Koh, P. W., et al. (2021). [WILDS: A benchmark of in-the-wild distribution shifts](https://arxiv.org/abs/2012.07421). Proceedings of the International Conference on Machine Learning (ICML 2021).  
  Cited in: Distribution Shift  
- Kohavi, R., Tang, D., & Xu, Y. (2020). Trustworthy online controlled experiments: A practical guide to A/B testing. Cambridge University Press. *(Book)*  
  Cited in: Being Pragmatic, Glossary  
- Lapuschkin, S., Wäldchen, S., Binder, A., Montavon, G., Samek, W., & Müller, K.-R. (2019). [Unmasking Clever Hans predictors and assessing what machines really learn](https://doi.org/10.1038/s41467-019-08987-4). Nature Communications, 10, 1096\.  
  Cited in: The Clever Hans Effect  
- Liang, P., et al. (2023). [Holistic evaluation of language models](https://arxiv.org/abs/2211.09110). Transactions on Machine Learning Research (TMLR).  
  Cited in: The Metric Mirage, The Cost Frontier, The Benchmark Lottery  
- Liao, Q. V., & Xiao, Z. (2023). [Rethinking model evaluation as narrowing the socio-technical gap](https://arxiv.org/abs/2306.03100). arXiv:2306.03100. *(Preprint)*  
  Cited in: Criteria Drift, The Lab-to-Field Gap  
- Lin, J. (2019). [The neural hype and comparisons against weak baselines](https://doi.org/10.1145/3308774.3308781). ACM SIGIR Forum, 52(2), 40-51.  
  Cited in: The Baseline Rule  
- Lipton, Z. C., & Steinhardt, J. (2019). [Troubling trends in machine learning scholarship](https://arxiv.org/abs/1807.03341). ACM Queue, 17(1).  
  Cited in: Campbell's Law  
- Madaio, M. A., Stark, L., Wortman Vaughan, J., & Wallach, H. (2020). [Co-designing checklists to understand organizational challenges and opportunities around fairness in AI](https://doi.org/10.1145/3313831.3376445). Proceedings of the CHI Conference on Human Factors in Computing Systems (CHI 2020).  
  Cited in: Being Pragmatic  
- Madaio, M., Egede, L., Subramonyam, H., Wortman Vaughan, J., & Wallach, H. (2022). [Assessing the fairness of AI systems: AI practitioners' processes, challenges, and needs for support](https://doi.org/10.1145/3512899). Proceedings of the ACM on Human-Computer Interaction, 6(CSCW1), Article 52\.  
  Cited in: Being Pragmatic  
- Manheim, D., & Garrabrant, S. (2018). [Categorizing variants of Goodhart's Law](https://arxiv.org/abs/1803.04585). arXiv:1803.04585. *(Preprint)*  
  Cited in: Goodhart's Law  
- McCoy, R. T., Pavlick, E., & Linzen, T. (2019). [Right for the wrong reasons: Diagnosing syntactic heuristics in natural language inference](https://arxiv.org/abs/1902.01007). Proceedings of ACL 2019\.  
  Cited in: The Clever Hans Effect  
- Melis, G., Dyer, C., & Blunsom, P. (2018). [On the state of the art of evaluation in neural language models](https://arxiv.org/abs/1707.05589). International Conference on Learning Representations (ICLR 2018).  
  Cited in: The Baseline Rule  
- Messick, S. (1995). [Validity of psychological assessment: Validation of inferences from persons' responses and performances as scientific inquiry into score meaning](https://doi.org/10.1037/0003-066X.50.9.741). American Psychologist, 50(9), 741-749.  
  Cited in: The Construct Gap, Glossary, Overview  
- Miller, E. (2024). [Adding error bars to evals: A statistical approach to language model evaluations](https://arxiv.org/abs/2411.00640). arXiv:2411.00640. *(Preprint)*  
  Cited in: No Error Bars, No Result, Playbook  
- Mitchell, M., et al. (2019). [Model cards for model reporting](https://arxiv.org/abs/1810.03993). Proceedings of the Conference on Fairness, Accountability, and Transparency (FAT\* 2019).  
  Cited in: The Averaging Trap, The Reproducibility Rule, Playbook, Glossary, Overview  
- Mizrahi, M., et al. (2024). [State of what art? A call for multi-prompt LLM evaluation](https://aclanthology.org/2024.tacl-1.52/). Transactions of the Association for Computational Linguistics, 12\.  
  Cited in: Prompt Sensitivity  
- Moravec, H. (1988). Mind children: The future of robot and human intelligence. Harvard University Press. *(Book)*  
  Cited in: The Jagged Frontier  
- National Institute of Standards and Technology (2023). [Artificial Intelligence Risk Management Framework (AI RMF 1.0), NIST AI 100-1](https://doi.org/10.6028/NIST.AI.100-1). U.S. Department of Commerce. *(Report)*  
  Cited in: The Functionality Fallacy, Being Pragmatic, Glossary, Overview  
- Needham, J., Edkins, G., Pimpale, G., Bartsch, H., & Hobbhahn, M. (2025). [Large language models often know when they are being evaluated](https://arxiv.org/abs/2505.23836). arXiv:2505.23836. *(Preprint)*  
  Cited in: Evaluation Awareness, Glossary, Overview  
- Northcutt, C. G., Athalye, A., & Mueller, J. (2021). [Pervasive label errors in test sets destabilize machine learning benchmarks](https://arxiv.org/abs/2103.14749). NeurIPS 2021 Datasets and Benchmarks Track.  
  Cited in: Benchmark Saturation, The Gold Standard Myth  
- Novikova, J., Dušek, O., Cercas Curry, A., & Rieser, V. (2017). [Why we need new evaluation metrics for NLG](https://arxiv.org/abs/1707.06875). Proceedings of EMNLP 2017\.  
  Cited in: The Metric Mirage  
- Oakden-Rayner, L., Dunnmon, J., Carneiro, G., & Ré, C. (2020). [Hidden stratification causes clinically meaningful failures in machine learning for medical imaging](https://arxiv.org/abs/1909.12475). Proceedings of the ACM Conference on Health, Inference, and Learning (CHIL 2020).  
  Cited in: The Averaging Trap  
- Ott, S., Barbosa-Silva, A., Blagec, K., Brauner, J., & Samwald, M. (2022). [Mapping global dynamics of benchmark creation and saturation in artificial intelligence](https://doi.org/10.1038/s41467-022-34591-0). Nature Communications, 13, 6793\.  
  Cited in: Benchmark Saturation, Overview  
- Pan, A., Bhatia, K., & Steinhardt, J. (2022). [The effects of reward misspecification: Mapping and mitigating misaligned models](https://arxiv.org/abs/2201.03544). International Conference on Learning Representations (ICLR 2022).  
  Cited in: Goodhart's Law  
- Panickssery, A., Bowman, S. R., & Feng, S. (2024). [LLM evaluators recognize and favor their own generations](https://arxiv.org/abs/2404.13076). Advances in Neural Information Processing Systems (NeurIPS 2024).  
  Cited in: Judge Bias  
- Parasuraman, R., & Riley, V. (1997). [Humans and automation: Use, misuse, disuse, abuse](https://doi.org/10.1518/001872097778543886). Human Factors, 39(2), 230-253.  
  Cited in: The Team Is the System, Glossary  
- Parnin, C., Soares, G., Pandita, R., Gulwani, S., Rich, J., & Henley, A. Z. (2025). [Building your own product copilot: Challenges, opportunities, and needs](https://arxiv.org/abs/2312.14231). Proceedings of the IEEE International Conference on Software Analysis, Evolution and Reengineering (SANER 2025).  
  Cited in: Being Pragmatic  
- Pineau, J., et al. (2021). [Improving reproducibility in machine learning research (A report from the NeurIPS 2019 Reproducibility Program)](https://arxiv.org/abs/2003.12206). Journal of Machine Learning Research, 22(164), 1-20.  
  Cited in: The Reproducibility Rule  
- Rabanser, S., Kapoor, S., Kirgis, P., Liu, K., Utpala, S., & Narayanan, A. (2026). [Towards a science of AI agent reliability](https://arxiv.org/abs/2602.16666). arXiv:2602.16666. *(Preprint)*  
  Cited in: Once Is Not Reliable  
- Raji, I. D., Bender, E. M., Paullada, A., Denton, E., & Hanna, A. (2021). [AI and the everything in the whole wide world benchmark](https://arxiv.org/abs/2111.15366). NeurIPS 2021 Datasets and Benchmarks Track.  
  Cited in: The Construct Gap, Overview  
- Raji, I. D., Kumar, I. E., Horowitz, A., & Selbst, A. (2022). [The fallacy of AI functionality](https://doi.org/10.1145/3531146.3533158). Proceedings of the ACM Conference on Fairness, Accountability, and Transparency (FAccT 2022).  
  Cited in: The Functionality Fallacy, Overview  
- Raji, I. D., Smart, A., White, R. N., Mitchell, M., Gebru, T., et al. (2020). [Closing the AI accountability gap: Defining an end-to-end framework for internal algorithmic auditing](https://arxiv.org/abs/2001.00973). Proceedings of the Conference on Fairness, Accountability, and Transparency (FAT\* 2020).  
  Cited in: Being Pragmatic  
- Rakova, B., Yang, J., Cramer, H., & Chowdhury, R. (2021). [Where responsible AI meets reality: Practitioner perspectives on enablers for shifting organizational practices](https://doi.org/10.1145/3449081). Proceedings of the ACM on Human-Computer Interaction, 5(CSCW1).  
  Cited in: Being Pragmatic  
- Recht, B., Roelofs, R., Schmidt, L., & Shankar, V. (2019). [Do ImageNet classifiers generalize to ImageNet?](https://arxiv.org/abs/1902.10811) Proceedings of the International Conference on Machine Learning (ICML 2019).  
  Cited in: Adaptive Overfitting, Distribution Shift  
- Reiter, E. (2018). [A structured review of the validity of BLEU](https://doi.org/10.1162/coli_a_00322). Computational Linguistics, 44(3), 393-401.  
  Cited in: The Metric Mirage  
- Reuel, A., Hardy, A., Smith, C., Lamparth, M., Hardy, M., & Kochenderfer, M. J. (2024). [BetterBench: Assessing AI benchmarks, uncovering issues, and establishing best practices](https://arxiv.org/abs/2411.12990). NeurIPS 2024 Datasets and Benchmarks Track.  
  Cited in: No Error Bars, No Result, The Reproducibility Rule  
- Ribeiro, M. T., Wu, T., Guestrin, C., & Singh, S. (2020). [Beyond accuracy: Behavioral testing of NLP models with CheckList](https://arxiv.org/abs/2005.04118). Proceedings of ACL 2020\.  
  Cited in: The Clever Hans Effect, Glossary, Overview  
- Roelofs, R., Shankar, V., Recht, B., Fridovich-Keil, S., Hardt, M., Miller, J., & Schmidt, L. (2019). A meta-analysis of overfitting in machine learning. Advances in Neural Information Processing Systems (NeurIPS 2019).  
  Cited in: Adaptive Overfitting  
- Rogers, E. M. (2003). Diffusion of innovations (5th ed.). Free Press. *(Book)*  
  Cited in: Being Pragmatic  
- Sainz, O., Campos, J. A., García-Ferrero, I., Etxaniz, J., Lopez de Lacalle, O., & Agirre, E. (2023). [NLP evaluation in trouble: On the need to measure LLM data contamination for each benchmark](https://arxiv.org/abs/2310.18018). Findings of EMNLP 2023\.  
  Cited in: Data Contamination, Overview  
- Salaudeen, O., et al. (2025). [Measurement to meaning: A validity-centered framework for AI evaluation](https://arxiv.org/abs/2505.10573). arXiv:2505.10573. *(Preprint)*  
  Cited in: The Construct Gap  
- Schaeffer, R., Miranda, B., & Koyejo, S. (2023). [Are emergent abilities of large language models a mirage?](https://arxiv.org/abs/2304.15004) Advances in Neural Information Processing Systems (NeurIPS 2023).  
  Cited in: The Metric Mirage  
- Sclar, M., Choi, Y., Tsvetkov, Y., & Suhr, A. (2024). [Quantifying language models' sensitivity to spurious features in prompt design or: How I learned to start worrying about prompt formatting](https://arxiv.org/abs/2310.11324). International Conference on Learning Representations (ICLR 2024).  
  Cited in: Prompt Sensitivity, Playbook  
- Selbst, A. D., boyd, d., Friedler, S. A., Venkatasubramanian, S., & Vertesi, J. (2019). [Fairness and abstraction in sociotechnical systems](https://doi.org/10.1145/3287560.3287598). Proceedings of the Conference on Fairness, Accountability, and Transparency (FAT\* 2019).  
  Cited in: The Lab-to-Field Gap  
- Shankar, S., Garcia, R., Hellerstein, J. M., & Parameswaran, A. G. (2024). ["We have no idea how models will behave in production until production": How engineers operationalize machine learning](https://doi.org/10.1145/3653697). Proceedings of the ACM on Human-Computer Interaction, 8(CSCW1), Article 206\.  
  Cited in: Being Pragmatic  
- Shankar, S., Zamfirescu-Pereira, J. D., Hartmann, B., Parameswaran, A. G., & Arawjo, I. (2024). [Who validates the validators? Aligning LLM-assisted evaluation of LLM outputs with human preferences](https://doi.org/10.1145/3654777.3676450). Proceedings of the ACM Symposium on User Interface Software and Technology (UIST 2024).  
  Cited in: Judge Bias, Criteria Drift, Being Pragmatic, Playbook  
- Shevlane, T., et al. (2023). [Model evaluation for extreme risks](https://arxiv.org/abs/2305.15324). arXiv:2305.15324. *(Preprint)*  
  Cited in: Presence, Not Absence, Overview  
- Singh, S., Nan, Y., Wang, A., D'Souza, D., Kapoor, S., et al. (2025). [The leaderboard illusion](https://arxiv.org/abs/2504.20879). Advances in Neural Information Processing Systems (NeurIPS 2025).  
  Cited in: Goodhart's Law, Campbell's Law  
- Strathern, M. (1997). 'Improving ratings': Audit in the British university system. European Review, 5(3), 305-321.  
  Cited in: Goodhart's Law  
- Vaccaro, M., Almaatouq, A., & Malone, T. (2024). [When combinations of humans and AI are useful: A systematic review and meta-analysis](https://doi.org/10.1038/s41562-024-02024-1). Nature Human Behaviour, 8, 2293-2303.  
  Cited in: The Team Is the System, The Jagged Frontier, Playbook  
- van der Lee, C., Gatt, A., van Miltenburg, E., & Krahmer, E. (2021). [Human evaluation of automatically generated text: Current trends and best practice guidelines](https://doi.org/10.1016/j.csl.2020.101151). Computer Speech & Language, 67, 101151\.  
  Cited in: The Gold Standard Myth, Overview  
- van der Maden, W., Sadek, M., Xiao, Z., Mottelson, A., Liao, Q. V., & Zhu, J. (2026). [Results-actionability gap: Understanding how practitioners evaluate LLM products in the wild](https://doi.org/10.1145/3772318.3791069). Proceedings of the CHI Conference on Human Factors in Computing Systems (CHI 2026).  
  Cited in: Being Pragmatic, Glossary  
- van der Weij, T., Hofstätter, F., Jaffe, O., Brown, S. F., & Ward, F. R. (2025). [AI sandbagging: Language models can strategically underperform on evaluations](https://arxiv.org/abs/2406.07358). International Conference on Learning Representations (ICLR 2025).  
  Cited in: Presence, Not Absence, Evaluation Awareness, Glossary  
- Wallach, H., Desai, M., Cooper, A. F., Wang, A., Atalla, C., et al. (2025). [Position: Evaluating generative AI systems is a social science measurement challenge](https://arxiv.org/abs/2502.00561). Proceedings of the International Conference on Machine Learning (ICML 2025), PMLR 267\.  
  Cited in: The Construct Gap, Being Pragmatic, Overview  
- Wang, P., et al. (2024). [Large language models are not fair evaluators](https://aclanthology.org/2024.acl-long.511/). Proceedings of ACL 2024\.  
  Cited in: Judge Bias  
- Weidinger, L., Rauh, M., Marchal, N., Manzini, A., et al. (2023). [Sociotechnical safety evaluation of generative AI systems](https://arxiv.org/abs/2310.11986). arXiv:2310.11986. *(Preprint)*  
  Cited in: The Lab-to-Field Gap, Overview  
- Wong, A., Otles, E., Donnelly, J. P., et al. (2021). [External validation of a widely implemented proprietary sepsis prediction model in hospitalized patients](https://pubmed.ncbi.nlm.nih.gov/34152373/). JAMA Internal Medicine, 181(8), 1065-1070.  
  Cited in: The Functionality Fallacy, Distribution Shift  
- Wu, T., Ribeiro, M. T., Heer, J., & Weld, D. (2019). [Errudite: Scalable, reproducible, and testable error analysis](https://aclanthology.org/P19-1073/). Proceedings of ACL 2019\.  
  Cited in: Being Pragmatic, Glossary  
- Yao, S., Shinn, N., Razavi, P., & Narasimhan, K. (2025). [τ-bench: A benchmark for tool-agent-user interaction in real-world domains](https://arxiv.org/abs/2406.12045). International Conference on Learning Representations (ICLR 2025).  
  Cited in: Once Is Not Reliable, Playbook, Glossary  
- Zhang, H., Da, J., Lee, D., Robinson, V., Wu, C., et al. (2024). [A careful examination of large language model performance on grade school arithmetic](https://arxiv.org/abs/2405.00332). NeurIPS 2024 Datasets and Benchmarks Track.  
  Cited in: Data Contamination  
- Zheng, L., Chiang, W.-L., Sheng, Y., Zhuang, S., Wu, Z., et al. (2023). [Judging LLM-as-a-judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685). NeurIPS 2023 Datasets and Benchmarks Track.  
  Cited in: Judge Bias, Playbook, Glossary, Overview

&nbsp;