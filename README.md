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

## Next steps
- Adaptive Red (e.g. genetic algorithm)
- Scenario configs in YAML