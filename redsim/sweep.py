import random
import pandas as pd
from dataclasses import asdict

from redsim.engine import run_scenario
from redsim.scenarios import build_scenario


def run_sweep(
    raid_sizes: list[int],
    decoy_fractions: list[float],
    n_runs: int,
) -> list[dict]:
    """Run every combination of dials n_runs times. One row per run."""
    rows = []
    for raid_size in raid_sizes:
        for decoy_fraction in decoy_fractions:
            for seed in range(n_runs):
                layout_rng = random.Random(seed + 1_000_000)    #seed used to shuffle drones before raid
                drones, radars, effectors = build_scenario(raid_size, decoy_fraction, layout_rng)
                red_cost = sum(d.drone_type.cost for d in drones)
                n_decoys = sum(d.drone_type.is_decoy for d in drones)
                n_real = raid_size - n_decoys
                result = run_scenario(drones, radars, effectors,
                                      random.Random(seed))


                # One row: result + dials that produced it
                row = asdict(result)
                row["raid_size"] = raid_size
                row["decoy_fraction"] = decoy_fraction
                row["seed"] = seed
                row["n_decoys"] = n_decoys
                row["n_real"] = n_real
                row["red_cost"] = red_cost
                rows.append(row)

    return rows


if __name__ == "__main__":
    rows = run_sweep(
        raid_sizes=list(range(1, 25)),
        decoy_fractions=[0.0, 0.25, 0.5],
        n_runs=200,
    )
    df = pd.DataFrame(rows)
    df.to_csv("results.csv", index=False)

    print(len(df), "runs saved to results.csv")
    print(df.head())
    print(df.groupby(["raid_size", "decoy_fraction"])["leakers"].mean().unstack())
    print(df[df["raid_size"] == 2][["raid_size", "decoy_fraction", "n_decoys", "n_real"]].drop_duplicates())