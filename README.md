# Laws of AI Evaluation

**Live site: [lawsofaievaluation.com](https://lawsofaievaluation.com)**

Principles for judging whether an AI system actually holds up. The site collects 26 short, sourced laws about the reliable ways AI evaluation goes wrong, such as benchmark contamination, prompt sensitivity, judge bias, and the gap between lab results and real use. Each law links to the research behind it and comes with questions you can ask.

It is written for people who build, buy, or design with AI, and for anyone who wants to read an AI claim more critically.

## What is on the site

- **26 laws**, each with a plain-terms summary, the evidence, questions to ask, where the law does not apply, and sources.
- **Tools:** a claim checker, a "find your laws" situation finder, a printable checklist builder, a quick brief, a design rubric, and a readiness review.
- **Use it now:** friendly questions to ask when someone shares an AI result at work.
- **Guide pages:** overview, field guide, being pragmatic, glossary, bibliography, and [methodology](https://lawsofaievaluation.com/methodology).

## Status

This is an independent, self-published reference built from published research. It has not been through formal peer review. See the [methodology](https://lawsofaievaluation.com/methodology) for how sources were chosen and checked, and what the guide does not claim.

## Corrections

Found a mistake or a better source? Open an [issue](https://github.com/joealfonso/laws-of-ai-evaluation/issues/new), or use the "Report it" link at the bottom of any law page. Corrections are recorded in the [changelog](https://lawsofaievaluation.com/changelog).

## Building the site

The site is static. Pages are generated from the files in `data/` and `content/`.

```bash
python3 build/build.py
```

The default social share image and the per-law images are generated with `python3 build/make_og.py` (needs Pillow).

## License

Content is licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

Maintained by [Joseph Alfonso](https://josephalfonso.com).
