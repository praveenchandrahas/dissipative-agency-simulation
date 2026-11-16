# Dissipative Agency Simulation

An exploratory spatial eco-evolutionary simulation investigating whether increasingly capable energy-harvesting structures—and, under some environmental conditions, information-processing and agentic behaviour—can emerge through ordinary survival and reproduction in a planet-scale energy landscape.

The project operationalizes one part of the broader hypothesis: persistent free-energy gradients can support heritable structures that compete for access to usable energy; sensing, processing, prediction, planning and action may evolve when their harvesting benefits exceed their energetic costs.

**This is an exploratory toy model, not a validated biosphere or climate model, and it does not demonstrate a universal law that life or intelligence maximizes entropy production.** The model's limitations and assumptions are documented in [MODEL.md](MODEL.md).

## What is in this repository

- `entropy_agency_sim_v0_2.py` — main six-scenario simulation.
- `entropy_agency_v0_2_albedo_sensitivity.py` — albedo-feedback-off sensitivity experiment.
- `requirements.txt` — Python dependencies.
- `MODEL.md` — model design, equations, assumptions and limitations.
- `RESULTS.md` — interpretation of the recorded v0.2 exploratory run.
- `results/` — compact recorded CSV summaries.

## Run locally

Requires Python 3.10+.

```bash
python -m pip install -r requirements.txt
python entropy_agency_sim_v0_2.py --output-dir results
```

Run the sensitivity experiment:

```bash
python entropy_agency_v0_2_albedo_sensitivity.py \
  --generations 220 --replicates 3 --seed 20261116 \
  --output-dir results/albedo-off
```

## Run on GitHub Actions

The repository has two workflows:

### Continuous integration

The **CI** workflow runs automatically on every push to `main` and every pull request targeting `main`. It installs the Python dependencies, compiles both scripts, executes a short six-scenario smoke run, and validates the generated data.

### Full simulation runs

1. Open the repository's **Actions** tab.
2. Select **Run simulations**.
3. Choose **Run workflow**.
4. Set generations, replicates and seed. Keep the albedo-off sensitivity enabled for a matched sensitivity run.
5. Open the completed workflow run. Its summary table is displayed on the run page.
6. Download the `dissipative-agency-results-…` artifact for the CSV files, plots and run manifest.

The manual workflow defaults to 220 generations and 6 independent replicates per scenario. It also runs the albedo-off sensitivity by default. Inputs are bounded to 1–500 generations and 1–12 replicates to keep execution within the hosted runner's limits.

Simulation outputs are retained as GitHub Actions artifacts for 30 days. They are not automatically committed to `main`; each artifact contains a manifest recording the source commit, run ID, parameters and seed so that results can be traced and reproduced.

## Scientific guardrails

1. Entropy production is measured; it is **not** included in the evolutionary fitness function.
2. Biological chemical-energy throughput is kept separate from total planetary absorbed stellar power.
3. The abiotic reference receives the same external irradiance history and base albedo as the biological run.
4. The planetary radiative entropy estimate is a simplified global-mean blackbody diagnostic, not a complete calculation of planetary entropy production.
5. The life-induced albedo feedback is a contestable model assumption. The albedo-off sensitivity experiment is included precisely because the headline planetary entropy difference depends on it.
6. Behavioural payoffs are explicitly specified by the modeller. This version tests a candidate mechanism; it does not derive intelligence from first principles.

## Status

Version 0.2 is a baseline exploratory implementation. The next scientifically valuable steps are to derive agency from an explicit noisy information-and-control problem, add competing abiotic dissipation pathways, improve the planetary energy/entropy ledger, and run broad parameter sweeps before extending the model toward technological civilizations or Kardashev-scale energy use.

## License

No license has been selected for this standalone repository yet. Choose one in GitHub before inviting reuse or contributions.
