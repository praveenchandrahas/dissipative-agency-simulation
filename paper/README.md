# Research preprint: Energy Capture, Agency, and Planetary Entropy

**Author:** Praveen Chandrahas  
**Version:** 1.0 preprint, 16 November 2026  
**Status:** prepared for arXiv submission; not yet submitted and no arXiv identifier assigned.

## Main files

- [main.pdf](main.pdf) — 14-page manuscript.
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