# Supplementary data archive

The archive is split into four parts so each Git object remains below the GitHub connector per-upload transfer limit.

Join the parts from this directory:

```bash
./join-data-bundle.sh
```

This produces data_bundle.tar.xz, verifies its SHA-256 checksum, and lists its contents. Extract it with:

```bash
tar -xJf data_bundle.tar.xz
```

The archive contains:
- Raw main v0.2 generation-level time series (7,956 rows).
- Final scenario summary.
- Cognitive-ablation replicate outcomes.
- Albedo-off sensitivity time series and summary.
- Model configuration and scenario metadata.
- Exact recorded v0.2 simulation and sensitivity source snapshots, plus requirements.
- GitHub Actions CI validation record.

The original v0.2 PNG plots are stored separately in the sibling repository directory ../figures/. The five publication figures are included in ../arxiv-source.zip.

The SHA-256 of the reconstructed archive is:

e5b289037a90d7243c6f2ade081bcc58ff508da2b358b7e06fec6f7d59ee5901

No full parameter sweep has been executed yet. The five-case/two-scenario/two-generation parameter sweep in CI is only a software smoke test.