#!/usr/bin/env python3
"""Targeted sensitivity test with life-induced albedo feedback disabled.

This reruns the strong/predictable hotspot pair with the same evolutionary
model as v0.2, but sets max_biotic_albedo_reduction to zero. It is designed to
run both locally and from GitHub Actions.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import entropy_agency_sim_v0_2 as sim


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generations", type=int, default=220)
    parser.add_argument("--replicates", type=int, default=3)
    parser.add_argument("--seed", type=int, default=20261116)
    parser.add_argument("--output-dir", type=Path, default=Path("entropy_agency_v0_2_sensitivity_outputs"))
    args = parser.parse_args()

    if args.generations < 1:
        parser.error("--generations must be at least 1")
    if args.replicates < 1:
        parser.error("--replicates must be at least 1")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    cfg = sim.Config(
        generations=args.generations,
        replicates=args.replicates,
        seed=args.seed,
        max_biotic_albedo_reduction=0.0,
    )
    world = sim.build_world(cfg)
    rows = []
    for scenario_key in ["strong_predictable_hotspots", "strong_predictable_no_cognition"]:
        for replicate in range(cfg.replicates):
            print(
                f"Albedo-off run: {scenario_key}, replicate {replicate + 1}/{cfg.replicates} ...",
                flush=True,
            )
            df, _ = sim.run_one(scenario_key, replicate, cfg, world, keep_snapshot=False)
            rows.append(df)

    raw = pd.concat(rows, ignore_index=True)
    raw.to_csv(args.output_dir / "entropy_agency_v0_2_albedo_off_timeseries.csv", index=False)
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
    summary.to_csv(args.output_dir / "entropy_agency_v0_2_albedo_off_summary.csv", index=False)
    print("\nAlbedo-off sensitivity summary:")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
