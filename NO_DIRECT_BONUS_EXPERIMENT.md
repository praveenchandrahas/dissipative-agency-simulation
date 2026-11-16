# No-direct-behavioural-bonus experiment

This branch applies the blind-review intervention directly to the canonical v0.2 simulation.

## Intervention
The direct behavioural-gain multiplier is removed from harvesting capacity. Sensing, processing, prediction, planning and action remain heritable and costly; they influence noisy patch observations, forecasts, planning weights and movement only.

## Signal/noise sweep
- Relative observation/prediction noise multipliers: 0.10, 0.50, 1.50 times spatial field standard deviation.
- Environments: strong predictable hotspots; volatile shifting hotspots.
- Treatments: cognition enabled versus cognition-disabled control.
- Six replicates per treatment, environment and noise level; 220 generations per run.
- Paired treatments share the initial population draw and exogenous environment stream.

Run: python run_no_direct_bonus_experiment.py

Outputs are written to no_direct_bonus_results/. GitHub Actions runs this experiment on pushes to this branch and uploads the complete outputs as an artifact. This is an exploratory mechanism-isolation experiment; energy capture is not equated with entropy production.
