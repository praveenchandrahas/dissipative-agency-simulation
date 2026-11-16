#!/usr/bin/env python3
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from entropy_agency_sim_v0_2 import Config, build_world, run_one

OUT=Path("no_direct_bonus_results"); OUT.mkdir(exist_ok=True)
NOISE={"low":0.10,"medium":0.50,"high":1.50}
PAIRS=[("strong_predictable_hotspots","strong_predictable_no_cognition","strong_predictable"),
       ("volatile_shifting","volatile_no_cognition","volatile_shifting")]
REPLICATES=6; SEED=20261118
base=Config(generations=220,replicates=REPLICATES,seed=SEED)
world=build_world(base); runs=[]
for noise,scale in NOISE.items():
  for enabled,disabled,label in PAIRS:
    for rep in range(REPLICATES):
      cfg=Config(generations=220,replicates=REPLICATES,seed=SEED,signal_noise_multiplier=scale)
      for key,treatment in [(enabled,"cognitive"),(disabled,"no_cognition")]:
        print(f"{label} | {noise} | replicate {rep+1}/{REPLICATES} | {treatment}",flush=True)
        frame,_=run_one(key,rep,cfg,world,keep_snapshot=False)
        frame["environment_label"]=label; frame["noise_level"]=noise
        frame["noise_multiplier"]=scale; frame["treatment"]=treatment
        runs.append(frame)
df=pd.concat(runs,ignore_index=True); df.to_csv(OUT/"timeseries.csv",index=False)
late=df[df.generation>=200].groupby(["environment_label","noise_level","treatment","replicate"],as_index=False).mean(numeric_only=True)
late.to_csv(OUT/"replicate_late_window.csv",index=False)
metrics=["population","biotic_power_harnessed_TW","biotic_power_per_entity_GW","mean_agency_composite",
"mean_sensing","mean_processing","mean_prediction","mean_planning","mean_action","mean_collector",
"mean_cooperation","mean_technology","mean_behaviour_gain","mean_mobility_fraction","occupied_patch_fraction","gross_energy_gini"]
metrics=[m for m in metrics if m in late.columns]
summary=late.groupby(["environment_label","noise_level","treatment"])[metrics].agg(["mean","std"]).reset_index()
summary.columns=["_".join([str(x) for x in c if str(x)!=""]) if isinstance(c,tuple) else c for c in summary.columns]
summary.to_csv(OUT/"summary.csv",index=False)
keys=["environment_label","noise_level","replicate"]
cog=late[late.treatment=="cognitive"][keys+metrics].rename(columns={m:m+"_cognitive" for m in metrics})
ctl=late[late.treatment=="no_cognition"][keys+metrics].rename(columns={m:m+"_no_cognition" for m in metrics})
paired=cog.merge(ctl,on=keys,how="inner")
for m in metrics: paired["delta_"+m]=paired[m+"_cognitive"]-paired[m+"_no_cognition"]
paired.to_csv(OUT/"paired_deltas.csv",index=False)
effects=[]
for (env,noise),g in paired.groupby(["environment_label","noise_level"]):
  vals=g["delta_biotic_power_per_entity_GW"].to_numpy(); n=len(vals)
  mean=float(vals.mean()); sd=float(vals.std(ddof=1)); tcrit=2.571 if n==6 else 1.96
  ci=tcrit*sd/np.sqrt(n)
  effects.append({"environment":env,"noise_level":noise,"n":n,"delta_power_per_entity_GW_mean":mean,
                  "ci95_low":mean-ci,"ci95_high":mean+ci,"positive_replicates":int((vals>0).sum())})
pd.DataFrame(effects).to_csv(OUT/"paired_effects_summary.csv",index=False)
for env,_,label in PAIRS:
  fig,axs=plt.subplots(1,3,figsize=(15,4.8),sharey=True)
  for ax,(noise,scale) in zip(axs,NOISE.items()):
    sub=df[(df.scenario_key==env)&(df.noise_level==noise)&(df.treatment=="cognitive")]
    for metric,name in [("mean_sensing","Sensing"),("mean_processing","Processing"),("mean_prediction","Prediction"),("mean_planning","Planning"),("mean_action","Action")]:
      z=sub.groupby("generation")[metric].mean(); ax.plot(z.index,z.values,label=name)
    ax.set_title(f"{noise} noise ({scale} × field SD)"); ax.set_xlabel("Generation"); ax.grid(alpha=.2)
  axs[0].set_ylabel("Mean trait value (0–1)"); axs[-1].legend(frameon=False,fontsize=8)
  fig.suptitle("No direct cognitive bonus — "+label.replace("_"," ").title())
  fig.tight_layout(); fig.savefig(OUT/f"traits_{env}.png",dpi=170); plt.close(fig)
meta={"canonical_source":"entropy_agency_sim_v0_2.py, modified on this branch",
"intervention":"Removed behaviour_multiplier from harvesting capacity; capacity depends only on collector, technology, cooperation and infrastructure.",
"noise":"Observation/prediction noise scaled by spatial SD of current/forecast absorbed irradiance and the signal/noise multiplier.",
"noise_multipliers":NOISE,"environments":[p[2] for p in PAIRS],"replicates":REPLICATES,
"generations":220,"seed":SEED,"matched_initialization":"Paired treatments share initial population and stochastic seed streams within environment and replicate.",
"caveat":"Cognition-disabled controls clamp sensing, processing, prediction, planning and action to zero. Interpret results alongside population caps and replicate variation."}
(OUT/"metadata.json").write_text(json.dumps(meta,indent=2))
print("Results written to",OUT.resolve())
