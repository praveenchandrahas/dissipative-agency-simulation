#!/usr/bin/env python3
"""Reproducible parameter screening for the dissipative-agency simulation.

Default design is one-factor-at-a-time screening: a baseline plus low/high
values for each selected factor. This estimates main effects, not interactions.
A 3-level full factorial is available for at most four selected factors.
"""
from __future__ import annotations

import argparse
import copy
import itertools
import json
import math
import os
import re
import sys
from dataclasses import asdict, replace
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import entropy_agency_sim_v0_2 as sim


FACTOR_SPECS: dict[str, dict[str, Any]] = {
    "spatial_contrast_scale": {
        "levels": (0.5, 1.0, 1.5), "nominal": 1.0,
        "description": "Scale spatial contrast in the stellar-energy landscape.",
    },
    "seasonal_amplitude_scale": {
        "levels": (0.5, 1.0, 1.5), "nominal": 1.0,
        "description": "Scale the amplitude of predictable seasonal energy redistribution.",
    },
    "weather_sigma_scale": {
        "levels": (0.5, 1.0, 1.5), "nominal": 1.0,
        "description": "Scale stochastic weather volatility while preserving persistence.",
    },
    "stellar_flux_multiplier": {
        "levels": (0.8, 1.0, 1.2), "nominal": 1.0,
        "description": "Scale total incident stellar energy flux relative to the v0.2 reference.",
    },
    "cognitive_cost_multiplier": {
        "levels": (0.5, 1.0, 1.5), "nominal": 1.0,
        "description": "Scale maintenance costs of sensing, processing, prediction, planning and action.",
    },
    "mutation_sd": {
        "levels": (0.0175, 0.035, 0.07), "nominal": 0.035,
        "description": "Standard deviation of heritable trait mutation.",
    },
    "survival_gain": {
        "levels": (0.40, 0.58, 0.75), "nominal": 0.58,
        "description": "Strength of the energy-dependent survival advantage.",
    },
    "birth_rate_gain": {
        "levels": (0.08, 0.16, 0.24), "nominal": 0.16,
        "description": "Strength of the energy-dependent reproduction response.",
    },
}

METRICS = [
    "population",
    "mean_collector",
    "mean_sensing",
    "mean_processing",
    "mean_prediction",
    "mean_planning",
    "mean_action",
    "mean_agency_composite",
    "mean_cooperation",
    "mean_technology",
    "mean_infrastructure",
    "mean_behaviour_gain",
    "gross_energy_gini",
    "top10_gross_energy_share",
    "occupied_patch_fraction",
    "mean_survival_probability",
    "birth_rate_per_entity",
    "biotic_power_harnessed_TW",
    "biotic_power_per_entity_GW",
    "biotic_capture_fraction_of_photo_pool",
    "biotic_power_as_fraction_of_absorbed",
    "delta_radiative_entropy_percent",
    "extra_absorbed_power_vs_abiotic_W",
]


def slug(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return value or "case"


def parse_factors(raw: str) -> list[str]:
    if raw.strip().lower() == "all":
        return list(FACTOR_SPECS)
    factors = [item.strip() for item in raw.split(",") if item.strip()]
    if not factors:
        raise ValueError("Select at least one factor or use --factors all.")
    unknown = sorted(set(factors) - set(FACTOR_SPECS))
    if unknown:
        raise ValueError(f"Unknown factors: {', '.join(unknown)}")
    if len(set(factors)) != len(factors):
        raise ValueError("Factor names must not be repeated.")
    return factors


def make_cases(design: str, factors: list[str]) -> list[dict[str, Any]]:
    nominal = {name: FACTOR_SPECS[name]["nominal"] for name in factors}
    cases: list[dict[str, Any]] = []

    def append_case(params: dict[str, float], changed_factor: str, changed_value: float | str) -> None:
        if changed_factor == "baseline":
            case_id = "baseline"
            label = "Baseline"
        elif changed_factor == "factorial":
            case_id = "factorial-" + "-".join(
                f"{slug(k)}-{float(v):g}" for k, v in params.items()
            )
            label = ", ".join(f"{k}={v:g}" for k, v in params.items())
        else:
            case_id = f"{slug(changed_factor)}-{float(changed_value):g}"
            label = f"{changed_factor} = {float(changed_value):g}"
        cases.append({
            "case_id": case_id,
            "case_label": label,
            "changed_factor": changed_factor,
            "changed_value": changed_value,
            "parameters": dict(params),
        })

    if design == "screening":
        append_case(nominal, "baseline", "nominal")
        for factor in factors:
            levels = FACTOR_SPECS[factor]["levels"]
            for value in (levels[0], levels[-1]):
                params = dict(nominal)
                params[factor] = value
                append_case(params, factor, value)
    elif design == "factorial":
        if len(factors) > 4:
            raise ValueError(
                "Three-level factorial design is limited to four factors (3^4 = 81 cases). "
                "Use screening or select at most four factors."
            )
        level_lists = [FACTOR_SPECS[factor]["levels"] for factor in factors]
        for values in itertools.product(*level_lists):
            params = dict(zip(factors, values))
            append_case(params, "factorial", "mixed")
    else:
        raise ValueError(f"Unsupported design: {design}")

    # Case IDs must be unique, including for custom subsets.
    ids = [case["case_id"] for case in cases]
    if len(ids) != len(set(ids)):
        raise ValueError("The selected design generated duplicate case IDs.")
    return cases


def config_for_case(base: sim.Config, params: dict[str, float]) -> sim.Config:
    trait_costs = list(base.trait_costs)
    cognitive_multiplier = float(params.get("cognitive_cost_multiplier", 1.0))
    for index in range(1, 6):  # sensing through action; collector/cooperation/technology stay unchanged
        trait_costs[index] *= cognitive_multiplier

    return replace(
        base,
        mutation_sd=float(params.get("mutation_sd", base.mutation_sd)),
        survival_gain=float(params.get("survival_gain", base.survival_gain)),
        birth_rate_gain=float(params.get("birth_rate_gain", base.birth_rate_gain)),
        stellar_flux_multiplier=float(params.get("stellar_flux_multiplier", base.stellar_flux_multiplier)),
        trait_costs=tuple(trait_costs),
    )


def scenarios_for_case(original: dict[str, dict[str, Any]], params: dict[str, float]) -> dict[str, dict[str, Any]]:
    scenarios = copy.deepcopy(original)
    spatial = float(params.get("spatial_contrast_scale", 1.0))
    seasonal = float(params.get("seasonal_amplitude_scale", 1.0))
    weather = float(params.get("weather_sigma_scale", 1.0))
    for definition in scenarios.values():
        definition["spatial_contrast"] *= spatial
        definition["seasonal_amplitude"] *= seasonal
        definition["weather_sigma"] *= weather
    return scenarios


def run_sweep(args: argparse.Namespace) -> Path:
    factors = parse_factors(args.factors)
    cases = make_cases(args.design, factors)
    scenario_keys = (
        list(sim.SCENARIOS)
        if args.scenarios == "all"
        else ["strong_predictable_hotspots", "strong_predictable_no_cognition"]
    )
    run_count = len(cases) * len(scenario_keys) * args.replicates
    if len(cases) > args.max_cases:
        raise ValueError(
            f"Design needs {len(cases)} cases, exceeding --max-cases={args.max_cases}."
        )
    if run_count > args.max_runs:
        raise ValueError(
            f"Design needs {run_count} scenario-replicate runs, exceeding --max-runs={args.max_runs}."
        )

    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    original_scenarios = copy.deepcopy(sim.SCENARIOS)
    base = sim.Config(
        generations=args.generations,
        replicates=args.replicates,
        seed=args.seed,
    )
    world = sim.build_world(base)
    run_rows: list[dict[str, Any]] = []
    case_rows: list[dict[str, Any]] = []

    print(
        f"Design={args.design}; factors={factors}; cases={len(cases)}; "
        f"scenarios={len(scenario_keys)}; replicates={args.replicates}; runs={run_count}",
        flush=True,
    )

    try:
        for case_index, case in enumerate(cases, start=1):
            params = case["parameters"]
            sim.SCENARIOS = scenarios_for_case(original_scenarios, params)
            config = config_for_case(base, params)
            case_rows.append({
                "case_id": case["case_id"],
                "case_label": case["case_label"],
                "changed_factor": case["changed_factor"],
                "changed_value": case["changed_value"],
                **{f"param_{key}": value for key, value in params.items()},
            })
            print(
                f"\n[{case_index}/{len(cases)}] {case['case_label']}",
                flush=True,
            )

            for scenario_key in scenario_keys:
                for replicate in range(args.replicates):
                    print(
                        f"  {scenario_key}, replicate {replicate + 1}/{args.replicates}",
                        flush=True,
                    )
                    # Common random-number strategy: the same base seed and replicate
                    # indices are reused across parameter cases; environment and
                    # evolutionary random streams remain separated inside run_one.
                    frame, _ = sim.run_one(
                        scenario_key, replicate, config, world, keep_snapshot=False
                    )
                    if frame.empty:
                        raise RuntimeError(
                            f"No output rows for {case['case_id']} / {scenario_key} / {replicate}"
                        )
                    final = frame.iloc[-1].to_dict()
                    final.update({
                        "case_id": case["case_id"],
                        "case_label": case["case_label"],
                        "design": args.design,
                        "changed_factor": case["changed_factor"],
                        "changed_value": case["changed_value"],
                        "seed_base": args.seed,
                        **{f"param_{key}": value for key, value in params.items()},
                    })
                    run_rows.append(final)
    finally:
        sim.SCENARIOS = original_scenarios

    runs = pd.DataFrame(run_rows)
    cases_df = pd.DataFrame(case_rows)
    group_keys = ["case_id", "case_label", "changed_factor", "scenario_key", "scenario"]
    aggregations: dict[str, tuple[str, str]] = {}
    for metric in METRICS:
        if metric in runs.columns:
            aggregations[f"{metric}_mean"] = (metric, "mean")
            aggregations[f"{metric}_sd"] = (metric, "std")
    summary = runs.groupby(group_keys, as_index=False).agg(**aggregations)
    summary = summary.merge(cases_df, on=["case_id", "case_label", "changed_factor", "changed_value"], how="left") if "changed_value" in summary.columns else summary.merge(
        cases_df, on=["case_id", "case_label", "changed_factor"], how="left"
    )

    # Long-form marginal effects. For screening, each factor is compared only
    # against its own low/high case and the single baseline. For factorial
    # designs, effects are marginal means across the other selected factors.
    effect_rows: list[dict[str, Any]] = []
    metrics_for_effects = [
        "population", "mean_collector", "mean_agency_composite",
        "biotic_power_harnessed_TW", "biotic_power_per_entity_GW",
        "delta_radiative_entropy_percent", "occupied_patch_fraction",
        "gross_energy_gini", "mean_cooperation", "mean_technology",
    ]
    for factor in factors:
        levels = FACTOR_SPECS[factor]["levels"]
        for level_index, value in enumerate(levels):
            selected = summary[np.isclose(summary[f"param_{factor}"].astype(float), float(value))]
            if args.design == "screening":
                selected = selected[
                    (selected["changed_factor"] == factor) |
                    (selected["case_id"] == "baseline")
                ]
            if selected.empty:
                continue
            marginal = selected.groupby(["scenario_key", "scenario"], as_index=False)[
                [f"{metric}_mean" for metric in metrics_for_effects if f"{metric}_mean" in selected.columns]
            ].mean()

            center = summary[np.isclose(summary[f"param_{factor}"].astype(float), float(FACTOR_SPECS[factor]["nominal"]))]
            if args.design == "screening":
                center = center[center["case_id"] == "baseline"]
            center_marginal = center.groupby("scenario_key").mean(numeric_only=True)

            for _, row in marginal.iterrows():
                if row["scenario_key"] not in center_marginal.index:
                    continue
                reference = center_marginal.loc[row["scenario_key"]]
                for metric in metrics_for_effects:
                    column = f"{metric}_mean"
                    if column not in row.index or column not in reference.index:
                        continue
                    value_mean = float(row[column])
                    reference_mean = float(reference[column])
                    effect_rows.append({
                        "factor": factor,
                        "factor_value": float(value),
                        "level_index": level_index,
                        "scenario_key": row["scenario_key"],
                        "scenario": row["scenario"],
                        "metric": metric,
                        "mean_at_value": value_mean,
                        "center_mean": reference_mean,
                        "delta_from_center": value_mean - reference_mean,
                    })

    effects = pd.DataFrame(effect_rows)
    runs.to_csv(output / "sweep_replicate_results.csv", index=False)
    summary.to_csv(output / "sweep_summary.csv", index=False)
    cases_df.to_csv(output / "parameter_cases.csv", index=False)
    effects.to_csv(output / "sweep_effects.csv", index=False)

    metadata = {
        "model": "dissipative-agency-simulation",
        "simulation_version": "0.2-with-configurable-stellar-flux",
        "design": args.design,
        "factors": {
            factor: {
                "description": FACTOR_SPECS[factor]["description"],
                "levels": list(FACTOR_SPECS[factor]["levels"]),
                "nominal": FACTOR_SPECS[factor]["nominal"],
            }
            for factor in factors
        },
        "scenarios": scenario_keys,
        "generations": args.generations,
        "replicates": args.replicates,
        "seed": args.seed,
        "case_count": len(cases),
        "scenario_replicate_run_count": run_count,
        "git_sha": os.environ.get("GITHUB_SHA", "local-or-unspecified"),
        "notes": [
            "Screening design is one-factor-at-a-time and does not estimate interactions.",
            "Factorial design uses three levels per factor and is limited to four factors.",
            "Matched replicate indices reuse the same base seeds across parameter cases.",
            "Entropy production is measured, not rewarded by the fitness function.",
            "These are exploratory model sensitivities, not empirical parameter estimates.",
        ],
    }
    (output / "sweep_manifest.json").write_text(json.dumps(metadata, indent=2) + "\n")
    make_effect_plot(effects, factors, output / "parameter_sweep_effects.png")
    print("\nSweep summary:", flush=True)
    print(summary.to_string(index=False), flush=True)
    print(f"\nOutputs written to: {output.resolve()}", flush=True)
    return output


def make_effect_plot(effects: pd.DataFrame, factors: list[str], path: Path) -> None:
    if effects.empty:
        return
    plot_metrics = [
        ("mean_agency_composite", "Mean agency composite (cognitive scenarios only)"),
        ("mean_collector", "Mean collector trait"),
        ("biotic_power_harnessed_TW", "Total biotic throughput (TW)"),
        ("delta_radiative_entropy_percent", "Radiative entropy difference (%)"),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    axes = axes.ravel()
    for ax, (metric, title) in zip(axes, plot_metrics):
        data = effects[effects["metric"] == metric].copy()
        if metric == "mean_agency_composite":
            data = data[~data["scenario_key"].str.endswith("no_cognition")]
        for factor in factors:
            part = data[data["factor"] == factor]
            if part.empty:
                continue
            agg = part.groupby("level_index")["delta_from_center"].mean()
            ax.plot(
                agg.index,
                agg.values,
                marker="o",
                linewidth=1.5,
                label=factor,
            )
        ax.axhline(0.0, linewidth=0.8, linestyle="--", alpha=0.6)
        ax.set_xticks([0, 1, 2], ["Low", "Nominal", "High"])
        ax.set_title(title)
        ax.set_ylabel("Difference from nominal-level mean")
        ax.grid(alpha=0.22)
    axes[0].legend(fontsize=7, frameon=False)
    fig.suptitle(
        "Parameter sensitivity: marginal differences from each factor's nominal level",
        fontsize=13,
    )
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--design", choices=["screening", "factorial"], default="screening")
    parser.add_argument("--factors", default="all", help="Comma-separated factor names, or 'all'.")
    parser.add_argument("--scenarios", choices=["all", "cognition_pair"], default="all")
    parser.add_argument("--generations", type=int, default=100)
    parser.add_argument("--replicates", type=int, default=2)
    parser.add_argument("--seed", type=int, default=20261116)
    parser.add_argument("--max-cases", type=int, default=25)
    parser.add_argument("--max-runs", type=int, default=1500)
    parser.add_argument("--output-dir", type=Path, default=Path("parameter_sweep_outputs"))
    args = parser.parse_args()

    if not 1 <= args.generations <= 500:
        parser.error("--generations must be between 1 and 500")
    if not 1 <= args.replicates <= 8:
        parser.error("--replicates must be between 1 and 8")
    if not 0 <= args.seed <= 2_147_483_647:
        parser.error("--seed must be between 0 and 2147483647")
    if not 1 <= args.max_cases <= 81:
        parser.error("--max-cases must be between 1 and 81")
    if args.max_runs < 1:
        parser.error("--max-runs must be positive")

    try:
        run_sweep(args)
    except (ValueError, RuntimeError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
