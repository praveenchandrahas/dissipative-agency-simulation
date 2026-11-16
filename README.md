# Dissipative Agency Simulation

An exploratory spatial eco-evolutionary simulation investigating whether increasingly capable energy-harvesting structures—and, under some environmental conditions, information-processing and agentic behaviour—can emerge through ordinary survival and reproduction in a planet-scale energy landscape.

The project operationalizes one part of the broader hypothesis: persistent free-energy gradients can support heritable structures that compete for access to usable energy; sensing, processing, prediction, planning and action may evolve when their harvesting benefits exceed their energetic costs.

**This is an exploratory toy model, not a validated biosphere or climate model, and it does not demonstrate a universal law that life or intelligence maximizes entropy production.** The model's limitations and assumptions are documented in [MODEL.md](MODEL.md).

## What is in this repository

- `entropy_agency_sim_v0_2.py` — main six-scenario simulation.
- `entropy_agency_v0_2_albedo_sensitivity.py` — albedo-feedback-off sensitivity experiment.
- `run_parameter_sweep.py` — reproducible multi-factor screening and bounded factorial parameter sweep.
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

Run the albedo-off sensitivity experiment:

```bash
python entropy_agency_v0_2_albedo_sensitivity.py \
  --generations 220 --replicates 3 --seed 20261116 \
  --output-dir results/albedo-off
```

## Parameter sweep

The sweep varies eight factors:

| Factor | Levels (low / nominal / high) | What changes |
|---|---|---|
| `spatial_contrast_scale` | 0.5 / 1.0 / 1.5 | Spatial contrast in local stellar irradiance |
| `seasonal_amplitude_scale` | 0.5 / 1.0 / 1.5 | Predictable seasonal energy redistribution |
| `weather_sigma_scale` | 0.5 / 1.0 / 1.5 | Stochastic weather volatility |
| `stellar_flux_multiplier` | 0.8 / 1.0 / 1.2 | Total incoming stellar energy flux |
| `cognitive_cost_multiplier` | 0.5 / 1.0 / 1.5 | Maintenance costs of sensing through action |
| `mutation_sd` | 0.0175 / 0.035 / 0.07 | Heritable variation per generation |
| `survival_gain` | 0.40 / 0.58 / 0.75 | Energy-dependent survival response |
| `birth_rate_gain` | 0.08 / 0.16 / 0.24 | Energy-dependent reproduction response |

### Screening design (recommended first)

One-factor-at-a-time (OFAT) screening runs a baseline plus low and high values for every selected factor. With all eight factors this is 17 parameter cases. This estimates main effects efficiently, but **does not estimate interactions between factors**.

```bash
python run_parameter_sweep.py \
  --design screening --factors all --scenarios all \
  --generations 100 --replicates 2 --seed 20261116 \
  --output-dir parameter_sweep_outputs
```

For a quick cognition-focused test:

```bash
python run_parameter_sweep.py \
  --design screening \
  --factors stellar_flux_multiplier,cognitive_cost_multiplier,spatial_contrast_scale \
  --scenarios cognition_pair \
  --generations 100 --replicates 3 \
  --output-dir parameter_sweep_cognition
```

### Factorial design (interaction exploration)

A 3-level full factorial estimates interactions, but is limited to four selected factors (up to 81 combinations):

```bash
python run_parameter_sweep.py \
  --design factorial \
  --factors stellar_flux_multiplier,cognitive_cost_multiplier,spatial_contrast_scale,mutation_sd \
  --scenarios cognition_pair \
  --generations 150 --replicates 4 \
  --max-cases 81 --output-dir parameter_sweep_factorial
```

The runner reuses the base seed and replicate indices across parameter cases, helping align stochastic comparisons. Outputs include the exact case table, per-replicate final outcomes, grouped means and standard deviations, marginal effects, a figure and a run manifest.

### Sweep output files

- `parameter_cases.csv` — every parameter configuration.
- `sweep_replicate_results.csv` — terminal metrics for each replicate and scenario.
- `sweep_summary.csv` — means and standard deviations by case and scenario.
- `sweep_effects.csv` — marginal changes from nominal parameter levels.
- `parameter_sweep_effects.png` — visual summary of responses.
- `sweep_manifest.json` — design, factors, levels, seed, run count and source commit.

## Run on GitHub Actions

The repository has three workflows:

- **CI** runs on pushes and pull requests. It compiles the simulation and sweep scripts, runs a small six-scenario test, then runs a miniature parameter sweep and validates both outputs.
- **Run simulations** manually executes the six-scenario experiment and optional albedo-off sensitivity.
- **Parameter sweep** manually executes screening or factorial designs.

To launch a sweep: open **Actions → Parameter sweep → Run workflow**. Choose the design, factors, scenarios, generations, replicates and seed. The default screening is 17 cases × 6 scenarios × 2 replicates = 204 scenario-replicate runs. The completed workflow page includes a summary; download the artifact for full CSV and plot outputs.

Limits protect hosted-runner capacity: 1–500 generations, 1–8 replicates, at most 81 cases and 1,500 scenario-replicate runs. Factorial designs are restricted to four factors. Sweep artifacts are retained for 90 days and are not automatically committed to `main`.

## Scientific guardrails

1. Entropy production is measured; it is **not** included in the evolutionary fitness function.
2. Biological chemical-energy throughput is kept separate from total planetary absorbed stellar power.
3. The abiotic reference receives the same external irradiance history and base albedo as the biological run.
4. The planetary radiative entropy estimate is a simplified global-mean blackbody diagnostic, not a complete calculation of planetary entropy production.
5. The life-induced albedo feedback is a contestable model assumption. The albedo-off sensitivity experiment is included because the planetary entropy difference depends on it.
6. Behavioural payoffs are explicitly specified by the modeller. This version tests a candidate mechanism; it does not derive intelligence from first principles.
7. Parameter sweeps identify model sensitivity, not real-world parameter values or a universal law. Screening and factorial designs answer different questions and should not be conflated.

## License

See [LICENSE](LICENSE).


## Research preprint

The v0.2 research paper, LaTeX source, and full supplementary results are in [paper/](paper/). The PDF and arXiv source archive are available directly in that directory. The data archive is provided as four parts; see [paper/supplementary/README.md](paper/supplementary/README.md) to reconstruct it. The manuscript has been prepared for arXiv submission but has not yet been submitted.
