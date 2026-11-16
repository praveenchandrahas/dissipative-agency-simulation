# Simulation v0.2 — The emergence of dissipative agency

## Purpose

This is an exploratory, spatial eco-evolutionary model built to interrogate one part of the proposed hypothesis:

> In environments with persistent free-energy gradients, heritable structures that improve access to usable energy can be selected. Some of the ways of improving access may involve sensing, information processing, prediction, planning and action. These capabilities may therefore evolve as costly strategies for energy acquisition.

The simulation does **not** put entropy production into the fitness function. Entities survive and reproduce according to their own energy economics. Planetary energy absorption and radiative entropy production are measured separately, and an abiotic control is run under the same external forcing.

This is a toy model for hypothesis exploration. It is not a validated model of Earth's biosphere, a climate model, or evidence that life or intelligence universally maximizes entropy production.

## What is represented

- A planet divided into 384 spatial patches (16 latitude bands × 24 longitude bands).
- Spatially and temporally varying stellar energy input. The global mean incident stellar flux is normalized within each scenario, then scaled by the configurable `stellar_flux_multiplier` (1.0 is the v0.2 reference). Parameter sweeps use this multiplier to vary total stellar energy supply while preserving the spatial pattern.
- A population of coarse-grained ecological entities or lineages. An entity is not a cell, organism, species, or civilization in a one-to-one sense.
- Eight heritable traits: collector, sensing, processing, prediction, planning, action, cooperation and technology.
- Mutation, differential survival, reproduction and local dispersal.
- Patch-level shared capacity and persistent infrastructure.
- An abiotic planetary baseline with the same incident radiation and base albedo.
- A simplified planetary radiative entropy estimate.

### Meaning of the traits

| Trait | Modelled function |
|---|---|
| Collector | Increases the entity's physical harvesting area/capacity. |
| Sensing | Reduces noise in observations of local energy availability. |
| Processing | Helps extract useful signals from noisy observations. |
| Prediction | Improves estimates of near-future resource availability. |
| Planning | Controls how much future opportunity is weighted against current opportunity. |
| Action | Enables active movement toward a selected neighbouring patch; it also increases dispersal. |
| Cooperation | Increases the local benefit of shared harvesting capacity. |
| Technology | Multiplies harvesting capacity and contributes to persistent infrastructure. |

Action does not yet represent general-purpose manipulation of the environment, tool invention or engineering. It is principally a movement/actuation trait in this version.

## Model structure and equations

### 1. Spatial energy landscape

For patch `j` and generation `t`, local incident irradiance is generated from a geographic pattern, a periodic forcing term and spatially correlated weather. The field is rescaled each generation so that its spatial mean equals the fixed global mean top-of-atmosphere flux:

`mean_j(F[j,t]) = S0 / 4`.

Thus, environmental scenarios change the location and predictability of energy opportunities, not the total incident stellar power. The weather field has a persistence parameter and is smoothed across neighbouring patches.

The periodic forcing uses a 36-generation cycle. Since one generation is used as one model year for power conversion, this is an abstract slow cycle (36 model years), not a literal simulation of Earth's annual seasons.

### 2. Harvesting capacity

For entity `i` in patch `j`, capacity is the product of physical collector area and local social/technological multipliers:

`collector_area_i = 0.18 + 1.55 * collector_i`

`local_cooperation_i = mean(cooperation of entities in patch j)`

`technology_multiplier_i = 1 + 1.35 * technology_i * local_cooperation_i`

`cooperation_multiplier_i = 1 + 0.85 * cooperation_i * local_cooperation_i`

`infrastructure_multiplier_i = 1 + 0.22 * infrastructure_j`

`capacity_i = collector_area_i * technology_multiplier_i * cooperation_multiplier_i * infrastructure_multiplier_i * behaviour_multiplier_i`

Capacity is bounded for numerical stability.

### 3. Behavioural sophistication

The behavioural multiplier is deliberately explicit so that separate cognitive-like traits have interpretable pathways to resource acquisition:

`behaviour_gain_i = 0.35 * spatial_opportunity * mean(sensing_i, processing_i)`

`                 + 0.30 * temporal_opportunity * forecastability * mean(prediction_i, planning_i)`

`                 + 0.22 * (spatial_opportunity + temporal_opportunity) * action_i`

`behaviour_multiplier_i = 1 + behaviour_gain_i`.

Sensing and processing reduce observation noise. Prediction and processing reduce forecast noise. Planning determines the weight assigned to forecast observations. Action determines whether the entity moves to the highest-scoring patch among its current patch and eight neighbours.

This is a designed candidate mechanism, not a general theory of intelligence. The functional relationship between traits and performance is specified by the modeller. A later version should compare alternative functional forms and allow capabilities to be learned or discovered rather than directly parameterized.

### 4. Finite chemical-energy pool and competition

For patch `j`, absorbed stellar power is converted into an abstract chemical resource pool:

`R_j = absorbed_power_j * generation_seconds * eta / resource_unit_joules`.

The resource efficiency `eta` is set to 0.001 (0.1%) as a deliberately stylized assumption. This represents a coarse-grained potential chemical-energy pool, not a detailed photosynthesis model.

The fraction captured by all entities in a patch is:

`capture_fraction_j = 1 - exp(-0.115 * total_capacity_j)`.

Captured energy is shared among local entities in proportion to their individual capacity. This makes energy finite at the patch level: entities compete for the same pool rather than receiving an unlimited reward for having more capacity.

### 5. Maintenance, survival and reproduction

Each entity pays baseline metabolic cost plus trait-specific costs:

`maintenance_i = baseline_cost + sum_k(trait_cost_k * trait_ik^2) + movement_cost_i`.

Net energy is gross captured energy minus maintenance. Survival probability and birth rate increase sigmoidally with net energy. Parent choice is weighted by relative net energy, and offspring inherit mutated versions of parental traits. No entropy-production term appears in survival, reproduction or parent choice.

Cooperative technological entities can invest part of their positive net surplus into patch infrastructure. Infrastructure persists and decays over time, and increases the harvesting capacity of later entities using that patch.

The 20,000-entity population ceiling is a computational safety cap, not a biological carrying-capacity law. It was not reached in the full v0.2 run.

### 6. Planetary albedo feedback

The model includes one explicitly contestable planetary feedback. Occupied patches gain biological cover according to:

`cover_j = 1 - exp(-0.085 * total_collector_area_j)`.

Biological cover lowers local albedo by up to 0.085. This can increase the planet's absorbed stellar power. This is not a universal property of life: ecosystems can darken or brighten surfaces depending on vegetation, snow, clouds, aerosols, water and land cover. In v0.2, it is a simple pathway that makes biological coverage affect planetary absorption.

### 7. Radiative entropy estimate

The model computes a global-mean radiative entropy-production estimate from the flux-weighted planetary albedo `A`.

`F_abs = (1 - A) * S0 / 4`

`T_eq = (F_abs / sigma)^(1/4)`

The outgoing blackbody entropy flux is approximated as:

`F_S,out = (4/3) * sigma * T_eq^3`.

The absorbed stellar entropy flux is approximated using a blackbody star and the diluted stellar radiation field. The planetary estimate is the outgoing radiative entropy flux minus the incoming absorbed-radiation entropy flux, multiplied by planetary area.

This is a global-mean blackbody approximation. It omits atmospheric structure, spectral windows, reflected-light entropy, detailed scattering, clouds, spatial temperature variation, transport, chemical free-energy storage and internal entropy production pathways. It should be interpreted as a diagnostic of the model's simplified planetary radiative balance, not as a complete calculation of entropy production on a real planet.

### 8. Abiotic control

Each run has a matched abiotic reference with the same incident irradiance history and the same underlying/base albedo, but with biological cover removed. This isolates the effect of the model's life-induced albedo feedback on total absorbed power and the radiative entropy estimate.

Biological chemical-energy throughput is reported separately. It is a pathway through which some of the absorbed solar energy is captured; it is **not** added to absorbed solar power as if it were a second energy source.

## Scenarios

The full experiment contains six scenarios, each with six independent evolutionary replicates:

| Scenario | Spatial contrast | Seasonal forcing amplitude | Weather noise | Weather persistence | Cognitive traits |
|---|---:|---:|---:|---:|---|
| Weakly variable | 0.05 | 0.06 | 0.035 | 0.88 | Enabled |
| Predictable seasonal shifts | 0.18 | 0.32 | 0.055 | 0.88 | Enabled |
| Volatile shifting hotspots | 0.24 | 0.27 | 0.21 | 0.42 | Enabled |
| Volatile / no cognition | 0.24 | 0.27 | 0.21 | 0.42 | Disabled |
| Strong predictable hotspots | 0.55 | 0.55 | 0.08 | 0.95 | Enabled |
| Strong hotspots / no cognition | 0.55 | 0.55 | 0.08 | 0.95 | Disabled |

Cognition-disabled controls fix sensing, processing, prediction, planning and action to zero. Collector, cooperation and technology can still evolve in these controls. These are therefore controls for the five modelled cognitive/behavioural traits, not controls with all technology or cooperation removed.

The cognitive-enabled and cognitive-disabled comparisons use matched exogenous weather/irradiance sequences within each replicate group.

## Results at a glance

The main run used 220 generations and six replicates per scenario (36 evolutionary runs). There is also a three-replicate sensitivity run for the strong/predictable pair with biological albedo feedback switched off.

Key findings from this particular parameterization:

- Collector capacity, cooperation and technology evolve in both cognitive-enabled and cognitive-disabled scenarios.
- Cognitive traits evolve to non-zero values in all five cognitive-enabled environmental scenarios. The composite final mean ranges from about 0.195 to 0.258 across scenario means.
- In the strong/predictable matched comparison, cognitive-enabled runs have a higher mean captured energy per model entity (about 42.2 GW) than the no-cognition control (about 16.3 GW), but substantially lower aggregate biological throughput (about 41.9 TW versus 134.4 TW).
- The cognitive-enabled population is smaller and more spatially concentrated in that comparison. Its final mean population is about 1,107 versus 8,271; it occupies about 29% of patches versus 99%; its gross-energy Gini is about 0.539 versus 0.243.
- In the volatile matched comparison, the same direction appears: higher captured energy per model entity under cognitive traits, but lower total biological throughput and lower spatial coverage.
- In this version, the model therefore does not support the simple claim that more agency necessarily produces greater aggregate planetary energy throughput. It produces a counterexample under the chosen local payoff and migration rules.
- The estimated planetary radiative entropy difference is highly dependent on the explicit albedo-darkening assumption. When that feedback is switched off, the biological and abiotic albedos are identical and the estimated difference in planetary radiative entropy production is zero, despite non-zero biological energy throughput.

These are exploratory model outcomes, not empirical estimates or universal conclusions. Six replicates per scenario are a small sample; some cognitive-enabled populations show large run-to-run variation.

## Important limitations and next steps

1. **The agency payoff is hand-specified.** The model encodes how information and action can improve harvesting. It demonstrates that selection can enrich traits with an energy payoff under these assumptions; it does not derive intelligence from first principles.
2. **Population-level outcomes are sensitive to movement and local competition.** Cognitive agents can concentrate in hotspots. The model's local resource sharing then creates high per-entity capture but lower total coverage and population.
3. **There is no realistic ecosystem.** There are no trophic levels, predators, decomposers, nutrient cycles, water limitation, atmospheric chemistry, coevolutionary niches or explicit extinction/recolonization dynamics.
4. **The planetary energy balance is crude.** There is no atmosphere or climate feedback model, and the entropy estimate is a global-mean blackbody approximation.
5. **Albedo change is not universal.** Life-induced darkening is a single assumed effect. A stronger test would include both darkening and brightening pathways, with empirically motivated biome-dependent parameters.
6. **The chemical resource pool is a proxy.** The 0.1% conversion factor is a modelling assumption, not calibrated to global primary production.
7. **Scale is not yet civilization.** Technology is a heritable capacity multiplier and infrastructure investment, not cumulative culture, scientific institutions, manufacturing, energy grids or autonomous industrial systems.
8. **No spontaneous origin of life is modelled.** The simulation begins with a population of entities. Abiogenesis and the origin of self-replication are outside the current model.
9. **Time is abstract.** One generation is one model year for power conversion, but the biological generational timescale is not species-specific. The 36-generation periodic forcing is likewise an abstract environmental cycle.

A rigorous v0.3 should first replace hand-coded agency payoffs with an explicit agent decision problem; add sensitivity sweeps over maintenance costs, movement, local competition, cooperation and patch-level resource sharing; model albedo pathways both ways; and compare several different abiotic dissipation pathways. Only after those checks should the model be expanded toward technological civilizations and Kardashev-scale energy systems.

## Running the simulation

Requires Python 3.10+ and `numpy`, `pandas`, `matplotlib`.

```bash
python3 -m pip install numpy pandas matplotlib
python3 entropy_agency_sim_v0_2.py --output-dir entropy_agency_v0_2_results
```

Optional targeted sensitivity run (run from the extracted project directory):

```bash
python3 entropy_agency_v0_2_albedo_sensitivity.py
```

The main script writes:

- `entropy_agency_v0_2_timeseries.csv`
- `entropy_agency_v0_2_final_summary.csv`
- `entropy_agency_v0_2_cognitive_ablation.csv`
- `entropy_agency_v0_2_metadata.json`
- trajectory and comparison PNG plots

The sensitivity script writes the albedo-off time series and summary CSV.

## File guide

- `entropy_agency_sim_v0_2.py` — complete simulation implementation.
- `entropy_agency_v0_2_albedo_sensitivity.py` — no-albedo-feedback sensitivity experiment.
- `entropy_agency_v0_2_results_report.md` — concise interpretation of the run.
- `entropy_agency_v0_2_results/` — raw time series, summaries, metadata and figures.