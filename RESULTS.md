# Simulation v0.2 — Results and interpretation

## Executive result

The model demonstrates a plausible *conditional* route by which sensing, prediction, planning and action can evolve: those traits improve an entity's ability to exploit spatial and temporal energy gradients, and entities pay explicit maintenance costs for them. But the results do **not** show that greater agency necessarily increases total planetary energy dissipation.

In the strongest matched comparison, cognitive-enabled entities capture more energy per model entity, but the population becomes much smaller and more spatially concentrated. Total biological energy throughput falls. The model's planetary radiative entropy signal is even more qualified: it disappears entirely when the assumed biological albedo-darkening feedback is disabled.

That is useful. It identifies a possible failure in the original inference: selection can reward an individual strategy that increases its own access to energy without maximizing the total energy captured or dissipated by the whole planet.

## Experiment

- 384 spatial patches (16 × 24 grid).
- 220 generations per run.
- Six independent replicates for each of six scenarios: 36 main evolutionary runs.
- Three additional replicates for each member of the strong/predictable pair with life-induced albedo feedback disabled: six sensitivity runs.
- Same exogenous environmental sequence in matched cognitive-enabled and cognitive-disabled comparisons.
- No entropy-production term in fitness. Survival, reproduction and parent choice depend on individual net energy.

## Main scenario outcomes

Values below are means across six replicates at generation 220. `Agency` is the mean of the five behavioural traits (sensing, processing, prediction, planning and action). `Power/entity` refers to a **coarse-grained model entity**, not a biological individual.

| Scenario | Population | Agency | Biological throughput (TW) | Power/model entity (GW) | Occupied patches | Planetary radiative entropy difference |
|---|---:|---:|---:|---:|---:|---:|
| Weakly variable | 5,211 | 0.195 | 109.8 | 25.5 | 80.3% | +5.80% |
| Predictable seasonal shifts | 3,657 | 0.215 | 85.7 | 30.8 | 63.9% | +4.26% |
| Volatile shifting hotspots | 2,911 | 0.206 | 81.1 | 33.1 | 57.9% | +3.69% |
| Volatile / no cognition | 8,463 | 0.000 | 135.9 | 16.1 | 99.8% | +8.21% |
| Strong predictable hotspots | 1,107 | 0.258 | 41.9 | 42.2 | 29.2% | +1.68% |
| Strong hotspots / no cognition | 8,271 | 0.000 | 134.4 | 16.3 | 99.2% | +8.10% |

The variability is material. For example, strong-predictable cognitive runs have a standard deviation of about 1,021 entities in final population and 28.5 TW in aggregate biological throughput (six replicates). Do not treat the means as stable estimates of a real ecosystem.

## Matched cognitive ablations

The two most informative comparisons are the cognitive-enabled scenario against its matched no-cognition control. The no-cognition control still allows collector, cooperation and technology to evolve; it freezes sensing, processing, prediction, planning and action at zero.

### Strong, predictable hotspots

| Metric | Cognitive traits enabled | Cognitive traits disabled |
|---|---:|---:|
| Final population | 1,107 | 8,271 |
| Agency composite | 0.258 | 0.000 |
| Total biological throughput | 41.9 TW | 134.4 TW |
| Throughput per model entity | 42.2 GW | 16.3 GW |
| Gross-energy Gini | 0.539 | 0.243 |
| Top 10% share of gross energy | 39.4% | 16.3% |
| Spatial occupancy | 29.2% | 99.2% |
| Radiative entropy difference vs abiotic control | +1.68% | +8.10% |

All six paired replicates had higher throughput per model entity in the cognitive-enabled run. All six had lower aggregate biological throughput. Cognitive populations concentrated more strongly: their mean gross-energy Gini was more than twice that of the no-cognition control, and they occupied fewer patches.

### Volatile, shifting hotspots

| Metric | Cognitive traits enabled | Cognitive traits disabled |
|---|---:|---:|
| Final population | 2,911 | 8,463 |
| Agency composite | 0.206 | 0.000 |
| Total biological throughput | 81.1 TW | 135.9 TW |
| Throughput per model entity | 33.1 GW | 16.1 GW |
| Gross-energy Gini | 0.486 | 0.162 |
| Top 10% share of gross energy | 33.9% | 14.7% |
| Spatial occupancy | 57.9% | 99.8% |
| Radiative entropy difference vs abiotic control | +3.69% | +8.21% |

Again, per-entity throughput is higher in cognitive-enabled runs, but aggregate biological throughput is lower. The volatile cognitive runs show substantial variation, so this pattern should be treated as a result of the current model rather than a robust general law.

## The decisive albedo-off sensitivity

The normal v0.2 model allows biological cover to lower surface albedo by up to 0.085. This is a deliberately contestable assumption: the effect of ecosystems on albedo can be positive or negative depending on the surface and climate context.

The strong/predictable pair was rerun with that feedback set to zero, using three replicates per scenario:

| Metric | Cognitive traits enabled | Cognitive traits disabled |
|---|---:|---:|
| Biological throughput | 31.0 TW | 120.9 TW |
| Throughput per model entity | 39.8 GW | 17.3 GW |
| Mean biological albedo | 0.297751 | 0.297751 |
| Mean abiotic albedo | 0.297751 | 0.297751 |
| Estimated radiative entropy difference | 0.00% | 0.00% |

This means the planetary entropy difference in the standard experiment is generated by the model's assumed change in albedo. Biological capture and processing, by themselves, do not increase this global radiative entropy metric when the absorbed stellar energy is held the same.

This is not a finding that life has no effect on entropy production in the real world. It is a finding about the current model's accounting: the model does not yet represent biological chemical transformations, respiration, heat transfer, atmospheric composition, hydrological changes or other pathways in enough physical detail to calculate their planetary entropy consequences.

## What the model supports — and what it does not

### It supports, conditionally

- A costly behavioural capability can spread under selection when the model gives it an energy-acquisition advantage.
- Different components of behavioural sophistication can have distinct roles: observation quality, signal processing, forecasting, planning and movement.
- Cooperation and technology-like capacity can increase shared harvesting capacity and support persistent infrastructure.
- Individual and aggregate outcomes can diverge. A strategy that raises energy throughput per entity need not maximize total planetary throughput.

### It does not establish

- That life must emerge from abiotic chemistry because of entropy production.
- That intelligence is an inevitable or universal evolutionary outcome.
- That natural selection maximizes global entropy production.
- That more sophisticated agency always captures more total free energy.
- That the calculated entropy percentages approximate Earth's real planetary entropy production.
- That the model's technology trait is equivalent to a technological civilization or a Kardashev type.

## Interpretation for the original hypothesis

The most important conclusion is a refinement, not a confirmation:

**Evolution may favour local strategies that increase access to free energy, but this does not imply that evolution favours the globally most dissipative arrangement.**

In v0.2, individual-level selection favours some cognitive capabilities because those capabilities help entities locate and exploit hotspots. Yet this strategy produces concentration, unequal energy distribution and lower population-wide coverage. Distributed, less cognitively sophisticated collectors produce greater aggregate throughput in these runs.

The Universe does not appear in the model as an optimizer. The only optimizer is the local selection process encoded in the reproduction rule. Whether that local process leads to greater global dissipation depends on ecological coupling, competition, spatial coverage, external forcing, environmental feedback and the available strategies.

## What should change in v0.3

1. Replace the hand-written behavioural advantage with an explicit decision problem: agents must infer gradients from observations and choose actions under uncertainty. Compare evolved information-processing strategies with random, reactive and fixed-rule baselines.
2. Add sensitivity sweeps for the maintenance costs of each capability, the benefits of movement, weather predictability, local resource sharing, patch capacity and migration.
3. Separate the effects of cognition, cooperation and technology with factorial ablations, rather than only the five-trait cognitive ablation used here.
4. Let life both darken and brighten surfaces, with context-dependent albedo parameters; include a no-albedo-feedback baseline in the main experiment, not just a targeted sensitivity run.
5. Build an explicit energy and entropy ledger for chemical storage, respiration, waste heat, evaporation, atmospheric transport and radiative export. The planetary entropy metric should be based on a more complete physical boundary model.
6. Add abiotic dissipative alternatives (for example, convection, weathering, atmospheric circulation and hydrological cycling) so that biological structures compete with or modify existing dissipation pathways rather than being compared with an unrealistically inert planet.
7. Only after these tests add cultural transmission, cumulative technology, large-scale infrastructure and civilization-level power capture.

The next serious test is not whether an agent can evolve a higher agency score. It is whether agent strategies that emerge from explicit information constraints consistently increase **total** entropy production after all alternative dissipation pathways and ecological feedbacks are accounted for.