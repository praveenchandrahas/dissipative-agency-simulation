# Research preprint: Energy Capture, Agency, and Planetary Entropy

**Author:** Praveen Chandrahas  
**Version:** 1.1 preprint, revised 23 November 2026 (version 1.0: 16 November 2026)  
**Status:** prepared for arXiv submission; not yet submitted and no arXiv identifier assigned.

## What changed in version 1.1

- **Follow-up analyses** (new Section 7). Same v0.2 source, 20 replicates, 660 generations. Carriers of the cognitive traits displace non-carriers on a shared planet while aggregate throughput falls (43.9 against 134.7 TW in the strong environment). Neutral marker traits rise about as far as the agency-like traits by generation 220. Generation 220 is the low point of a transient: the action trait falls from 0.24–0.26 to about 0.04 by generation 660, and throughput partly recovers.
- **Revised motivating conjecture** (Introduction). Structures, living or not, persist when they drain a gradient well enough to meet their costs. Entropy production follows rather than being selected. What heredity with variation adds is improvement, which should pay most in changing environments.
- **Energy origins** (Section 2.1). Usable gradients come largely from gravitational and nuclear disequilibria; stellar radiation is one product, and an unlocked one.
- **Implications** (Section 8.5) answer the reformulated questions where the follow-ups and related experiments now speak to them, including one result that cautions against the revised conjecture.
- **Limitations** add the horizon and the missing neutral baseline. The abstract and conclusion summarise the follow-ups.
- Every v1.0 result, table and figure is unchanged. Version 1.0 is kept as [archive/main-v1.0.pdf](archive/main-v1.0.pdf).

## Main files

- [main.pdf](main.pdf) — 16-page manuscript, version 1.1.
- [archive/main-v1.0.pdf](archive/main-v1.0.pdf) — the 14-page version 1.0.
- [arxiv-source.zip](arxiv-source.zip) — self-contained LaTeX source, bibliography, compiled BBL, and all five paper figures.
- [figures/](figures/) — original v0.2 simulation plots (the publication figures are also inside the arXiv source archive).
- [supplementary/](supplementary/) — complete supplementary data archive, split into GitHub-friendly parts, with a join script and checksum.

Suggested arXiv classification: primary **physics.bio-ph**; cross-list **q-bio.PE**. These are suggestions only; the author must choose the categories during arXiv submission.

## Recorded results included

The paper reports the recorded v0.2 experiment: six environmental scenarios, six replicates per scenario, 220 evolutionary generations (generation indices 0--220), plus an albedo-feedback-off sensitivity experiment with three replicates in each of two matched scenarios.

The supplementary data archive contains the 7,956-row main time series, the final scenario summary, cognition-ablation replicate outcomes, albedo-off time series and summary, model metadata, and the exact source snapshot used for the recorded v0.2 data. The original simulation plots are under figures/.

## Parameter sweeps

The repository now contains the reusable parameter-sweep runner and its GitHub Actions workflow. **No full parameter sweep has yet been executed.** The small five-case/two-scenario/two-generation parameter sweep in GitHub Actions is a CI smoke test only; it is not a scientific result and is not included as evidence in the manuscript.

## Scientific scope

This is an exploratory model paper, not a validated climate or biosphere model. The manuscript distinguishes the second law from the debated maximum-entropy-production hypothesis, and individual selection from global entropy optimization. Its radiative entropy metric is a simplified global-mean blackbody diagnostic. In v0.2 the modelled planetary entropy difference depends on the explicitly imposed life-induced albedo feedback and vanishes when that feedback is disabled. The paper does not claim to prove a universal law, the inevitability of intelligence, or first-principles emergence of cognition.

Before submitting, the author should review the full manuscript, references, authorship statement, acknowledgements, license requirements, and arXiv category selection.