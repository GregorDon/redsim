"""Turns results.csv into charts."""
from pathlib import Path
import seaborn as sns

import matplotlib.pyplot as plt
import pandas as pd


def plot_saturation(df: pd.DataFrame, path: str) -> None:
    """Average real leakers vs raid size, one line per decoy fraction."""
    table = df.groupby(["raid_size", "decoy_fraction"])["leakers"].mean().unstack()

    fig, ax = plt.subplots(figsize=(8, 5))
    for fraction in table.columns:
        ax.plot(table.index, table[fraction], marker="o",
                label=f"{fraction:.0%} decoys")

    ax.set_xlabel("Raid size (drones launched)")
    ax.set_ylabel("Average real drones leaking")
    ax.set_title("Saturation: when does Blue's defence break?")
    ax.plot(table.index, table.index, color = "grey", linestyle = "--", label = "No defence (0% decoys)")
    ax.legend()
    ax.grid(alpha=0.3)

    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_heatmap(df: pd.DataFrame, path: str) -> None:
    """Average value destroyed for every raid size and decoy fraction."""
    table = df.groupby(["decoy_fraction", "raid_size"])["value_destroyed"].mean().unstack()

    fig, ax = plt.subplots(figsize=(14, 4))
    sns.heatmap(table, ax=ax, cmap="Reds", annot=True, fmt=".1f",
                annot_kws={"size": 7},
                cbar_kws={"label": "Average value destroyed (max 13)"})

    ax.set_xlabel("Raid size (drones launched)")
    ax.set_ylabel("Decoy fraction")
    ax.set_title("Damage to Blue: raid size vs decoy mix")

    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def pareto_front(summary: pd.DataFrame) -> pd.DataFrame:
    """Raids where no cheaper raid does at least as much damage"""
    # Cheapest first; for equal cost, most damaging first
    ordered = summary.sort_values(["red_cost","damage"], ascending=[True,False])

    keep = []
    best_so_far = -1.0
    for _, row in ordered.iterrows():
        if row["damage"] > best_so_far:
            keep.append(row)
            best_so_far = row["damage"]
    return pd.DataFrame(keep)

def plot_cost_exchange(df: pd.DataFrame, path: str) -> None:
    """Red's spend vs damage done, with the Pareto front of best buys"""
    summary = (
        df.groupby(["raid_size", "decoy_fraction"])
                .agg(red_cost=("red_cost", "mean"), damage=("value_destroyed", "mean"))
        .reset_index()
    )

    front = pareto_front(summary)

    fig, ax = plt.subplots(figsize=(8, 5))
    points = ax.scatter(summary["red_cost"], summary["damage"],
                        c=summary["decoy_fraction"], cmap="viridis", s=25)
    fig.colorbar(points, ax=ax, label="Decoy fraction")
    ax.plot(front["red_cost"], front["damage"], color="red",
            label="Pareto front: best damage for the money")

    ax.set_xlabel("Red's cost (real drone = 1.0, decoy = 0.1)")
    ax.set_ylabel("Average value destroyed (max 13)")
    ax.set_title("Cost exchange: which raids give Red the best value?")
    ax.legend()
    ax.grid(alpha=0.3)

    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    Path("figures").mkdir(exist_ok=True)
    df = pd.read_csv("results.csv")
    plot_saturation(df, "figures/saturation.png")
    print("Saved figures/saturation.png")
    plot_heatmap(df, "figures/heatmap.png")
    plot_cost_exchange(df, "figures/cost_exchange.png")

    summary = (
        df.groupby(["raid_size", "decoy_fraction"])
        .agg(red_cost=("red_cost", "mean"),
             damage=("value_destroyed", "mean"),
             n_real=("n_real", "first"),
             n_decoys=("n_decoys", "first"))
        .reset_index()
    )
    print(pareto_front(summary).to_string(index=False))