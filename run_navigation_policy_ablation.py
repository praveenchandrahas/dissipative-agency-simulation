#!/usr/bin/env python3
"""Two-stage navigation-policy ablation on the no-direct-bonus v0.2 core."""
from __future__ import annotations
import json
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from entropy_agency_sim_v0_2 import Config, SCENARIOS, build_world, run_one

OUT = Path("navigation_policy_results")
SEED = 20261116
REPLICATES = 20
GENERATIONS = 220
INITIAL_POPULATION = 260
NOISE_LEVELS = {"low": 0.10, "medium": 0.50, "high": 1.50}
ENVIRONMENTS = {
    "strong_predictable": "strong_predictable_hotspots",
    "volatile_shifting": "volatile_shifting",
}
TREATMENTS = {
    "irradiance_only": {"information": True, "mobility": "directed", "mobility_trait": True,
                        "navigation_policy": "irradiance_only"},
    "density_aware": {"information": True, "mobility": "directed", "mobility_trait": True,
                      "navigation_policy": "density_aware"},
    "expected_payoff": {"information": True, "mobility": "directed", "mobility_trait": True,
                        "navigation_policy": "expected_payoff"},
    "random": {"information": False, "mobility": "random", "mobility_trait": True,
               "navigation_policy": "irradiance_only"},
}
CONTRASTS = [
    ("irradiance_only", "random", "Irradiance-only navigation versus random movement"),
    ("density_aware", "irradiance_only", "Incremental value of occupancy awareness"),
    ("expected_payoff", "density_aware", "Model-based payoff versus density heuristic"),
    ("expected_payoff", "irradiance_only", "Incremental value of expected-payoff navigation"),
]
# Late-window mean phenotypes from the previous 72-run canonical no-direct-bonus experiment.
# Columns: collector, sensing, processing, prediction, planning, action, cooperation,
# technology, and observed adult movement fraction. These are fixed only in Stage 1.
PROFILES = {
    ("strong_predictable", "low"):    [0.941674,0.290094,0.144016,0.176624,0.272710,0.193169,0.778804,0.654576,0.185223],
    ("strong_predictable", "medium"): [0.940671,0.158785,0.197703,0.185827,0.135401,0.164918,0.650942,0.683154,0.164502],
    ("strong_predictable", "high"):   [0.951325,0.123769,0.157575,0.174875,0.185231,0.245084,0.849132,0.751118,0.226170],
    ("volatile_shifting", "low"):     [0.933893,0.177309,0.163044,0.125447,0.116339,0.128810,0.800263,0.673137,0.128513],
    ("volatile_shifting", "medium"):  [0.937218,0.140765,0.206227,0.153519,0.210049,0.195041,0.895784,0.670935,0.183572],
    ("volatile_shifting", "high"):    [0.953706,0.153805,0.145592,0.183351,0.157774,0.180707,0.862104,0.805452,0.172732],
}
LATE_START = 200
METRICS = [
    "mean_gross_energy_units","mean_net_energy_units","biotic_power_harnessed_TW",
    "biotic_power_per_entity_GW","population","occupied_patch_fraction",
    "gross_energy_gini","mean_mobility_fraction","adult_move_opportunity_fraction",
    "mean_movement_field_gain_W_m2","mean_information_composite","mean_action",
]

def make_config(noise: float, stage: str) -> Config:
    common = dict(
        generations=GENERATIONS, replicates=REPLICATES, initial_population=INITIAL_POPULATION,
        seed=SEED, signal_noise_multiplier=noise,
        dispersal_base=0.035, dispersal_action_gain=0.0,
    )
    if stage == "fixed_mechanism":
        common.update(
            infrastructure_build_rate=0.0, infrastructure_decay=0.0,
            infrastructure_capacity_gain=0.0, max_biotic_albedo_reduction=0.0,
        )
    return Config(**common)

def pad_extinct_run(frame: pd.DataFrame, scenario_key: str, replicate: int, end_generation: int) -> pd.DataFrame:
    if frame.empty:
        return frame
    last_gen = int(frame["generation"].max())
    if last_gen >= end_generation:
        return frame
    rows = []
    for gen in range(last_gen + 1, end_generation + 1):
        row = {c: np.nan for c in frame.columns}
        row.update({
            "scenario_key": scenario_key, "replicate": replicate, "generation": gen,
            "population": 0, "mean_gross_energy_units": 0.0, "mean_net_energy_units": 0.0,
            "biotic_power_harnessed_TW": 0.0, "biotic_power_harnessed_W": 0.0,
            "total_biotic_harvest_units": 0.0, "occupied_patch_fraction": 0.0,
            "gross_energy_gini": np.nan, "mean_mobility_fraction": 0.0,
            "mean_information_composite": np.nan, "mean_action": np.nan,
            "adult_move_opportunity_fraction": 0.0, "mean_movement_field_gain_W_m2": np.nan,
            "biotic_power_per_entity_GW": np.nan,
        })
        rows.append(row)
    return pd.concat([frame, pd.DataFrame(rows)], ignore_index=True)

def late_window_means(data: pd.DataFrame) -> pd.DataFrame:
    # For short CI smoke runs, use the available horizon rather than an empty
    # generation >= 200 selection. Full experiments still use generations 200-220.
    window_start = min(LATE_START, max(0, GENERATIONS - 20))
    subset = data[data.generation >= window_start]
    group = ["stage","environment_label","noise_level","treatment","replicate"]
    metrics = [m for m in METRICS if m in subset.columns]
    late = subset.groupby(group, as_index=False)[metrics].mean()
    terminal = data[data.generation == GENERATIONS][group + ["population"]].rename(
        columns={"population":"final_population"}
    )
    return late.merge(terminal, on=group, how="left")

def paired_effects(late: pd.DataFrame) -> pd.DataFrame:
    rows = []
    metrics = [
        "mean_gross_energy_units","mean_net_energy_units","biotic_power_harnessed_TW",
        "biotic_power_per_entity_GW","population","occupied_patch_fraction",
        "gross_energy_gini","mean_mobility_fraction","adult_move_opportunity_fraction",
        "mean_movement_field_gain_W_m2",
    ]
    for stage in ("fixed_mechanism","evolutionary"):
        for env in ENVIRONMENTS:
            for noise in NOISE_LEVELS:
                block = late[(late.stage==stage)&(late.environment_label==env)&(late.noise_level==noise)]
                wide = block.pivot(index="replicate",columns="treatment",values=metrics)
                for a,b,label in CONTRASTS:
                    for metric in metrics:
                        if (metric,a) not in wide.columns or (metric,b) not in wide.columns:
                            continue
                        delta = (wide[(metric,a)] - wide[(metric,b)]).dropna().to_numpy()
                        n = len(delta)
                        if n == 0:
                            continue
                        mean = float(delta.mean())
                        sd = float(delta.std(ddof=1)) if n > 1 else float("nan")
                        tcrit = 2.093024 if n == 20 else (2.262157 if n == 10 else 1.96)
                        half = tcrit * sd / np.sqrt(n) if n > 1 else float("nan")
                        rows.append({
                            "stage":stage,"environment":env,"noise_level":noise,
                            "contrast":f"{a} - {b}","contrast_question":label,
                            "metric":metric,"n":n,"mean_paired_delta":mean,
                            "ci95_low":mean-half if n>1 else np.nan,
                            "ci95_high":mean+half if n>1 else np.nan,
                            "positive_replicates":int(np.sum(delta>0)),
                            "negative_replicates":int(np.sum(delta<0)),
                        })
    return pd.DataFrame(rows)

def main():
    global REPLICATES, GENERATIONS, INITIAL_POPULATION, OUT
    parser = argparse.ArgumentParser(description="Two-stage navigation-policy ablation")
    parser.add_argument("--smoke", action="store_true", help="Run a short 1-replicate smoke test")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    if args.smoke:
        REPLICATES, GENERATIONS, INITIAL_POPULATION = 1, 12, 80
    OUT = Path(args.output_dir or ("navigation_policy_smoke" if args.smoke else "navigation_policy_results"))
    OUT.mkdir(exist_ok=True)
    world = build_world(Config())
    all_frames = []
    total_runs = 2 * len(ENVIRONMENTS) * len(NOISE_LEVELS) * len(TREATMENTS) * REPLICATES
    completed = 0

    # Stage 1: fixed population, fixed phenotype, matched adult movement opportunity.
    for env_label, scenario_key in ENVIRONMENTS.items():
        for noise_label, noise in NOISE_LEVELS.items():
            profile = np.asarray(PROFILES[(env_label, noise_label)], dtype=float)
            fixed_move_p = float(profile[8])
            base_trait_vector = profile[:8]
            cfg = make_config(noise, "fixed_mechanism")
            for rep in range(REPLICATES):
                init_rng = np.random.default_rng(SEED + 100_003*rep + 17_029*list(ENVIRONMENTS).index(env_label) + 733*list(NOISE_LEVELS).index(noise_label))
                initial_traits = np.tile(base_trait_vector, (INITIAL_POPULATION,1))
                initial_locations = init_rng.integers(0, world["cells"], size=INITIAL_POPULATION, dtype=np.int32)
                for treatment, spec in TREATMENTS.items():
                    completed += 1
                    print(f"[{completed}/{total_runs}] fixed_mechanism | {env_label} | {noise_label} | {treatment} | rep {rep+1}", flush=True)
                    move_p = fixed_move_p
                    frame, _ = run_one(
                        scenario_key, rep, cfg, world, keep_snapshot=False,
                        information_enabled=True, mobility_mode=spec["mobility"],
                        mobility_trait_enabled=True,
                        fixed_move_probability=move_p, evolutionary=False,
                        navigation_policy=spec["navigation_policy"],
                        initial_traits=initial_traits, initial_locations=initial_locations,
                    )
                    frame = pad_extinct_run(frame, scenario_key, rep, GENERATIONS)
                    frame["stage"]="fixed_mechanism"; frame["environment_label"]=env_label
                    frame["noise_level"]=noise_label; frame["noise_multiplier"]=noise
                    frame["treatment"]=treatment; frame["fixed_move_probability"]=fixed_move_p
                    all_frames.append(frame)

    # Stage 2: information and adult mobility evolve independently.
    for env_label, scenario_key in ENVIRONMENTS.items():
        for noise_label, noise in NOISE_LEVELS.items():
            cfg = make_config(noise, "evolutionary")
            for rep in range(REPLICATES):
                for treatment, spec in TREATMENTS.items():
                    completed += 1
                    print(f"[{completed}/{total_runs}] evolutionary | {env_label} | {noise_label} | {treatment} | rep {rep+1}", flush=True)
                    frame, _ = run_one(
                        scenario_key, rep, cfg, world, keep_snapshot=False,
                        information_enabled=spec["information"], mobility_mode=spec["mobility"],
                        mobility_trait_enabled=True, fixed_move_probability=None,
                        evolutionary=True, navigation_policy=spec["navigation_policy"],
                    )
                    frame = pad_extinct_run(frame, scenario_key, rep, GENERATIONS)
                    frame["stage"]="evolutionary"; frame["environment_label"]=env_label
                    frame["noise_level"]=noise_label; frame["noise_multiplier"]=noise
                    frame["treatment"]=treatment; frame["fixed_move_probability"]=np.nan
                    all_frames.append(frame)

    data = pd.concat(all_frames, ignore_index=True)
    data.to_csv(OUT/"timeseries.csv",index=False)
    late = late_window_means(data)
    # Stage-1 validity checks: all four policies have identical per-agent
    # movement opportunities and realized movement frequency for each replicate.
    fixed = late[late.stage=="fixed_mechanism"]
    moving_policies = list(TREATMENTS)
    for metric in ["mean_mobility_fraction","adult_move_opportunity_fraction"]:
        check = fixed.pivot(
            index=["environment_label","noise_level","replicate"],
            columns="treatment", values=metric
        )
        reference = check["irradiance_only"].to_numpy()
        for policy in moving_policies:
            if not np.allclose(reference, check[policy].to_numpy(), atol=1e-12, rtol=0):
                raise RuntimeError(f"Stage-1 matched movement validation failed for {metric}: {policy}")
    # The model records no realised movement at generation 0 by convention,
    # while it still records that generation's movement opportunities. The
    # primary comparisons are cross-policy equality, not equality between
    # these two differently defined time-series metrics.
    late.to_csv(OUT/"replicate_late_window.csv",index=False)
    summary = late.groupby(["stage","environment_label","noise_level","treatment"])[
        [m for m in METRICS if m in late.columns] + ["final_population"]
    ].agg(["mean","std"])
    summary.columns = ["_".join(str(x) for x in c if str(x)!="") for c in summary.columns]
    summary.to_csv(OUT/"summary.csv")
    effects = paired_effects(late)
    effects.to_csv(OUT/"paired_effects.csv",index=False)

    fig, axes = plt.subplots(2,1,figsize=(14,9),sharex=True)
    policy_labels = {
        "irradiance_only": "Irradiance only",
        "density_aware": "Density aware",
        "expected_payoff": "Expected payoff",
        "random": "Random",
    }
    xlabels = [
        env.replace("_"," ")+"\n"+noise
        for env in ENVIRONMENTS for noise in NOISE_LEVELS
    ]
    x = np.arange(len(xlabels))
    width = 0.19
    for ax, stage, title in zip(
        axes, ["fixed_mechanism","evolutionary"],
        ["Stage 1: fixed population, phenotype and movement rate",
         "Stage 2: evolutionary policy comparison"],
    ):
        block = late[late.stage==stage]
        for j, treatment in enumerate(TREATMENTS):
            vals = []
            for env in ENVIRONMENTS:
                for noise in NOISE_LEVELS:
                    z=block[(block.environment_label==env)&(block.noise_level==noise)
                            &(block.treatment==treatment)]
                    v=z["biotic_power_per_entity_GW"].mean()
                    vals.append(float(v) if pd.notna(v) else np.nan)
            ax.bar(x+(j-1.5)*width, vals, width, label=policy_labels[treatment])
        ax.set_title(title); ax.set_ylabel("Power per entity (GW)")
        ax.grid(axis="y",alpha=.2); ax.set_xticks(x,xlabels)
        ax.legend(frameon=False,ncol=4,fontsize=8)
    fig.tight_layout(); fig.savefig(OUT/"navigation_policy_power.png",dpi=170); plt.close(fig)

    meta={
      "seed":SEED,"replicates_per_condition":REPLICATES,"generations":GENERATIONS,
      "initial_population":INITIAL_POPULATION,"environments":list(ENVIRONMENTS),
      "signal_noise_multipliers":NOISE_LEVELS,"treatments":TREATMENTS,
      "design":{
        "stage_1":"Fixed population, no mutation/reproduction; each environment/noise cell uses one frozen phenotype and one starting spatial state per replicate. All four policies share the same movement-gate RNG stream, fixed movement probability, movement cost and eight-neighbour destination set. Current patch is excluded for every policy, so all movement opportunities become actual moves. All four fixed-stage arms retain the same information traits and maintenance costs. Albedo and infrastructure feedback are disabled.",
        "stage_2":"Evolutionary four-policy comparison. Irradiance-only, density-aware and expected-payoff navigation use information traits; random movement does not. Adult action/mobility can evolve in every policy. The four navigation policies use the same eight-neighbour destinations and exclude the current patch.",
        "policy_definitions":"irradiance_only ranks destinations by noisy present and forecast absorbed irradiance. density_aware discounts those signals by a noisy local-occupancy estimate relative to mean occupancy. expected_payoff estimates the model's own finite-pool, per-agent gross-energy share at each destination, accounting for current residents' estimated capacity, the focal agent's capacity, local cover/albedo and the capture saturation function. random chooses uniformly among the same eight neighbours.",
        "expected_payoff_limit":"The payoff estimate is one-step and uses pre-movement resident occupancy/capacity; it does not solve the simultaneous multi-agent destination-allocation equilibrium. It uses the model's known capture and capacity equations, so it is a model-based oracle-like policy rather than a claim about realistic animal cognition.",
        "offspring_dispersal":"Set to a common fixed baseline probability (0.035) in every Stage-2 treatment; no action-dependent offspring dispersal.",
        "fitness":"Survival, reproduction and parent selection remain based on individual net energy; no entropy term is added.",
        "primary_stage_1_contrast":"irradiance_only minus random: same starting state, exactly matched realized adult movement frequency, same movement cost; only destination information differs. Current patch is excluded from both destination sets in Stage 1.",
        "primary_stage_2_contrast":"irradiance_only minus random: both information and mobility can evolve; estimates the evolutionary consequence of the factorial treatment, not a fixed-rate navigation effect.",
      },
      "interpretation_guardrail":"Biological capture/throughput is not planetary entropy production. This experiment does not establish that intelligence is inevitable or that evolution maximizes global dissipation.",
      "source":"entropy_agency_sim_v0_2.py from the no-direct-bonus branch, with controlled navigation-policy comparisons added.",
    }
    (OUT/"metadata.json").write_text(json.dumps(meta,indent=2))
    report = [
      "# Navigation-policy ablation", "",
      "## Design", "",
      f"- Two stages; {REPLICATES} paired replicates per condition; {GENERATIONS} generations in each run.",
      "- Two environments: strong predictable hotspots and volatile shifting hotspots.",
      "- Three signal-noise multipliers: 0.10, 0.50 and 1.50.",
      "- Four policies: irradiance-only, density-aware, expected-payoff and random.",
      "- Stage 1 freezes population size and every trait. All policies share the same starting locations, movement-gate random stream, movement probability and movement costs. All use the same eight-neighbour destination set; the current patch is excluded so movement opportunities always result in movement.",
      "- Stage 1 gives all four arms the same fixed information traits and costs. The random policy simply does not use the information.",
      "- Stage 2 allows adult mobility/action and the other heritable model traits to evolve. Information traits are enabled for the three informed policies and disabled for random movement. Offspring dispersal remains fixed at 0.035 in all arms.", "",
      "## Policy definitions", "",
      "- **Irradiance-only:** ranks the eight neighbouring patches by noisy current and forecast absorbed irradiance.",
      "- **Density-aware:** discounts the irradiance score by an imperfect local-occupancy estimate, favouring less crowded patches.",
      "- **Expected-payoff:** estimates the focal agent's share of the model's finite local resource pool, including resident capacity, the focal agent's capacity, capture saturation and albedo/cover feedback.",
      "- **Random:** chooses uniformly among the same eight neighbouring patches.", "",
      "The expected-payoff policy uses the model's known energy-allocation equations and is therefore an oracle-like upper-bound policy for this simplified model, not a realistic claim about what organisms can compute. It estimates candidate payoffs using pre-movement occupancy and does not solve the simultaneous multi-agent destination-allocation problem.", "",
      "## Contrasts", "",
      "- Irradiance-only versus random: value of selecting bright patches.",
      "- Density-aware versus irradiance-only: incremental effect of occupancy awareness.",
      "- Expected-payoff versus density-aware: value of model-based resource-share accounting over a simple crowding heuristic.",
      "- Expected-payoff versus irradiance-only: total incremental value of accounting for expected capture share.", "",
      "Stage 1 is the primary mechanism-isolation test. Stage 2 tests how these strategy packages perform when mobility and other traits can evolve; it is not a fixed-rate navigation comparison.", "",
      "## Results", "",
      "Paired effect estimates, confidence intervals, replicate-level values and full time series are in paired_effects.csv, replicate_late_window.csv, summary.csv and timeseries.csv.", "",
      "## Important boundaries", "",
      "- Stage 1's fixed phenotypes are taken from the late-window mean phenotype of the previous canonical no-direct-bonus experiment. It tests navigation by a representative already-evolved phenotype, not the origin of information processing.",
      "- Stage 1 disables albedo and infrastructure feedback to isolate immediate navigation and resource-access mechanisms.",
      "- Stage 2 restores evolution and the model's ecological feedbacks; other heritable traits can mediate observed differences.",
      "- Fitness remains based on individual net energy. No entropy term is included.",
      "- Captured biological energy is not planetary entropy production. The experiment cannot establish that life or intelligence is inevitable or that evolution maximizes global dissipation.",
      "",
      "The paper has not been modified by this experiment.",
    ]
    (OUT/"REPORT.md").write_text("\n".join(report)+"\n")
    print("Completed all runs. Results:",OUT.resolve(),flush=True)

if __name__=="__main__":
    main()
