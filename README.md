# redsim: counter-drone raid simulator

Monte Carlo simulation of Red drone raids against Blue critical
national infrastructure, defended by radars and counter-drone effectors.

## How it works
- Each time step: Blue senses, Blue engages, then drones move.

## Running it
    python -m redsim.engine
    python -m pytest -v

## Assumptions and limitations
- Drones fly straight at their target at constant speed and altitude.
- Each effector engages the first detected drone in range, one shot
  per time step. A jammer can waste its turn on an unjammable drone,
  so unjammable drones screening jammable ones degrade the jammer. (probably RedCell intel/outcome)
- The gun fires once per time step, so dt_s sets its rate of fire. At 10 s steps, the defence saturates on rate of fire, not ammo.
- build_scenario replaces real drones with decoys rather than adding them on top, so the decoy fraction also cuts   Red’s real drone count.
- Real drones are assumed unjammable; decoys are jammable.
- Launch positions spread 1 km apart in y, so bigger raids fly longer, angled paths.

## Next steps
- Adaptive Red (e.g. genetic algorithm)
- Scenario configs in YAML