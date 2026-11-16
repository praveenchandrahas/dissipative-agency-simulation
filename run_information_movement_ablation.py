#!/usr/bin/env python3
"""Two-stage information-versus-movement ablation on the no-direct-bonus v0.2 core."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from entropy_agency_sim_v0_2 import Config, SCENARIOS, build_world, run_one

OUT = Path("information_movement_results")
OUT.mkdir(exist_ok=True)
SEED = 20261119
REPLICATES = 20
GENERATIONS = 220
INITIAL_POPULATION = 260
NOISE_LEVELS = {"low": 0.10, "medium": 0.50, "high": 1.50}
ENVIRONMENTS = {
    "strong_predictable": "strong_predictable_hotspots",
    "volatile_shifting": "volatile_shifting",
}
TREATMENTS = {
    "informed_directed": {"information": True, "mobility": "directed", "mobility_trait": True},
    "uninformed_random": {"information": False, "mobility": "random", "mobility_trait": True},
    "informed_stationary": {"information": True, "mobility": "stationary", "mobility_trait": False},
    "uninformed_stationary": {"information": False, "mobility": "stationary", "mobility_trait": False},
}
CONTRASTS = [
    ("informed_directed", "uninformed_random", "Information value among movers"),
    ("uninformed_random", "uninformed_stationary", "Random movement value without information"),
    ("informed_directed", "informed_stationary", "Movement value with information"),
    ("informed_stationary", "uninformed_stationary", "Information maintenance cost without adult movement"),
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
    "gross_energy_gini","mean_mobility_fraction","mean_information_composite","mean_action",
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
            "biotic_power_per_entity_GW": np.nan,
        })
        rows.append(row)
    return pd.concat([frame, pd.DataFrame(rows)], ignore_index=True)

def late_window_means(data: pd.DataFrame) -> pd.DataFrame:
    subset = data[data.generation >= LATE_START]
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
        "gross_energy_gini","mean_mobility_fraction",
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
                    move_p = fixed_move_p if spec["mobility"] != "stationary" else None
                    frame, _ = run_one(
                        scenario_key, rep, cfg, world, keep_snapshot=False,
                        information_enabled=spec["information"], mobility_mode=spec["mobility"],
                        mobility_trait_enabled=spec["mobility_trait"],
                        fixed_move_probability=move_p, evolutionary=False,
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
                        mobility_trait_enabled=spec["mobility_trait"], fixed_move_probability=None,
                        evolutionary=True,
                    )
                    frame = pad_extinct_run(frame, scenario_key, rep, GENERATIONS)
                    frame["stage"]="evolutionary"; frame["environment_label"]=env_label
                    frame["noise_level"]=noise_label; frame["noise_multiplier"]=noise
                    frame["treatment"]=treatment; frame["fixed_move_probability"]=np.nan
                    all_frames.append(frame)

    data = pd.concat(all_frames, ignore_index=True)
    data.to_csv(OUT/"timeseries.csv",index=False)
    late = late_window_means(data)
    late.to_csv(OUT/"replicate_late_window.csv",index=False)
    summary = late.groupby(["stage","environment_label","noise_level","treatment"])[
        [m for m in METRICS if m in late.columns] + ["final_population"]
    ].agg(["mean","std"])
    summary.columns = ["_".join(str(x) for x in c if str(x)!="") for c in summary.columns]
    summary.to_csv(OUT/"summary.csv")
    effects = paired_effects(late)
    effects.to_csv(OUT/"paired_effects.csv",index=False)

    fig, axes = plt.subplots(2,1,figsize=(12,8),sharex=True)
    for ax, stage, title in zip(
        axes, ["fixed_mechanism","evolutionary"],
        ["Stage 1: fixed movement frequency and fixed population","Stage 2: heritable information and mobility"],
    ):
        block = late[late.stage==stage]
        xlabels=[]; vals_a=[]; vals_b=[]
        for env in ENVIRONMENTS:
            for noise in NOISE_LEVELS:
                z=block[(block.environment_label==env)&(block.noise_level==noise)]
                for treatment in ["informed_directed","uninformed_random"]:
                    v=z[z.treatment==treatment]["biotic_power_per_entity_GW"].mean()
                    (vals_a if treatment=="informed_directed" else vals_b).append(float(v) if pd.notna(v) else np.nan)
                xlabels.append(env.replace("_"," ")+"\n"+noise)
        x=np.arange(len(xlabels)); width=.36
        ax.bar(x-width/2,vals_a,width,label="Informed, directed movement")
        ax.bar(x+width/2,vals_b,width,label="Uninformed, random movement")
        ax.set_title(title); ax.set_ylabel("Power per entity (GW)"); ax.grid(axis="y",alpha=.2)
        ax.set_xticks(x,xlabels)
        ax.legend(frameon=False,ncol=2,fontsize=8)
    fig.tight_layout(); fig.savefig(OUT/"informed_vs_random.png",dpi=170); plt.close(fig)

    meta={
      "seed":SEED,"replicates_per_condition":REPLICATES,"generations":GENERATIONS,
      "initial_population":INITIAL_POPULATION,"environments":list(ENVIRONMENTS),
      "signal_noise_multipliers":NOISE_LEVELS,"treatments":TREATMENTS,
      "design":{
        "stage_1":"Fixed population, no mutation/reproduction; traits frozen at previous canonical run's late-window mean phenotype. Informed and random movers share the same per-entity movement-gate RNG and fixed movement probability. Albedo and infrastructure feedback disabled.",
        "stage_2":"Evolutionary four-treatment factorial. Information traits (sensing, processing, prediction, planning) and adult mobility trait (action) are independently enabled. Directed movers navigate using information; uninformed movers move randomly. Adult mobility is absent in stationary arms.",
        "offspring_dispersal":"Set to a common fixed baseline probability (0.035) in every Stage-2 treatment; no action-dependent offspring dispersal.",
        "fitness":"Survival, reproduction and parent selection remain based on individual net energy; no entropy term is added.",
        "primary_stage_1_contrast":"informed_directed minus uninformed_random: same starting state, same adult movement opportunity and same movement cost; only destination information differs.",
        "primary_stage_2_contrast":"informed_directed minus uninformed_random: both information and mobility can evolve; estimates the evolutionary consequence of the factorial treatment, not a fixed-rate navigation effect.",
      },
      "interpretation_guardrail":"Biological capture/throughput is not planetary entropy production. This experiment does not establish that intelligence is inevitable or that evolution maximizes global dissipation.",
      "source":"entropy_agency_sim_v0_2.py from the no-direct-bonus canonical branch, with independent information/mobility controls added.",
    }
    (OUT/"metadata.json").write_text(json.dumps(meta,indent=2))
    report = [
      "# Information-versus-movement ablation", "",
      "## Design", "",
      f"- Two stages; {REPLICATES} replicates per condition; {GENERATIONS} generations in each run.",
      "- Two environments (strong predictable hotspots; volatile shifting hotspots).",
      "- Three signal/noise levels (0.10, 0.50, 1.50 times the spatial standard deviation).",
      "- Four treatments: informed directed movement, uninformed random movement, information without adult movement, and neither.",
      "- Stage 1 holds population size and traits fixed; informed and random movers receive exactly matched adult movement opportunities and costs.",
      "- Stage 2 allows information traits and the adult mobility trait to evolve independently. Offspring dispersal is held at the same baseline probability in every treatment.", "",
      "## What the contrasts mean", "",
      "- Informed directed minus uninformed random: the value of information for choosing destinations.",
      "- Uninformed random minus uninformed stationary: the effect of random adult exploration without useful information.",
      "- Informed directed minus informed stationary: the effect of adult movement when information is available.",
      "- Informed stationary minus uninformed stationary: information-related maintenance cost when it cannot guide adult movement.", "",
      "Stage 1 is the primary mechanism-isolation test. Stage 2 asks which capabilities are retained by selection when they can evolve. The two stages should not be conflated.", "",
      "## Results", "",
      "Paired effect estimates, confidence intervals, replicate-level values and full time series are in paired_effects.csv, replicate_late_window.csv, summary.csv and timeseries.csv.", "",
      "## Important boundaries", "",
      "- Stage 1 uses homogeneous fixed trait profiles taken from the late-window mean phenotype of the preceding canonical no-direct-bonus experiment. It tests a representative already-evolved phenotype, not the origin of that phenotype.",
      "- Stage 1 freezes population size and disables albedo and infrastructure feedback to isolate navigation and immediate resource access.",
      "- Stage 2 restores evolutionary dynamics and the model's ecological feedbacks. It still uses the existing simplified eco-evolutionary model.",
      "- The model's action trait is adult mobility in this experiment; offspring dispersal is a separate, fixed process.",
      "- Captured biological energy is not equivalent to entropy production. No planetary entropy conclusion should be drawn from these results.",
      "",
      "The paper has not been modified by this experiment.",
    ]
    (OUT/"REPORT.md").write_text("\n".join(report)+"\n")
    print("Completed all runs. Results:",OUT.resolve(),flush=True)

if __name__=="__main__":
    main()
