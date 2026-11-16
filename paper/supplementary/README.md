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

The original v0.2 PNG plots are available separately in ../figures/. The five figures used in the manuscript are also included in ../arxiv-source.zip.

The SHA-256 of the reconstructed archive is:

52bf2a5c23197fa312da2ce2b9da723f185275a230511bd7939b85672443cecb

No full parameter sweep has been executed yet. The five-case/two-scenario/two-generation parameter sweep in CI is only a software smoke test.