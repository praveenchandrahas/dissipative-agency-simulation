#!/usr/bin/env python3
"""Targeted sensitivity test: remove the life-induced albedo feedback.

Runs the strong/predictable hotspot pair with the same evolutionary model as
v0.2, but sets max_biotic_albedo_reduction to zero. This isolates whether
biological capture by itself changes the global-mean radiative entropy metric.
"""
from pathlib import Path
import pandas as pd
import entropy_agency_sim_v0_2 as sim

OUT = Path("entropy_agency_v0_2_results")
OUT.mkdir(exist_ok=True)

cfg = sim.Config(generations=220, replicates=3, max_biotic_albedo_reduction=0.0)
world = sim.build_world(cfg)
rows = []
for scenario_key in ["strong_predictable_hotspots", "strong_predictable_no_cognition"]:
    for replicate in range(cfg.replicates):
        print(f"Albedo-off run: {scenario_key}, replicate {replicate + 1}/{cfg.replicates}", flush=True)
        df, _ = sim.run_one(scenario_key, replicate, cfg, world, keep_snapshot=False)
        rows.append(df)
raw = pd.concat(rows, ignore_index=True)
raw.to_csv(OUT / "entropy_agency_v0_2_albedo_off_timeseries.csv", index=False)
final = raw.sort_values("generation").groupby(["scenario_key", "replicate"], as_index=False).tail(1)
summary = final.groupby(["scenario_key", "scenario"]).agg(
    replicates=("replicate", "nunique"),
    final_population_mean=("population", "mean"),
    agency_mean=("mean_agency_composite", "mean"),
    biotic_power_TW_mean=("biotic_power_harnessed_TW", "mean"),
    biotic_power_per_entity_GW_mean=("biotic_power_per_entity_GW", "mean"),
    albedo_biotic_mean=("global_albedo_biotic", "mean"),
    albedo_abiotic_mean=("global_albedo_abiotic", "mean"),
    entropy_delta_percent_mean=("delta_radiative_entropy_percent", "mean"),
).reset_index()
summary.to_csv(OUT / "entropy_agency_v0_2_albedo_off_summary.csv", index=False)
print(summary.to_string(index=False))
