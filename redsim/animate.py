"""Animates one recorded raid and saves it as a GIF."""
import random
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.collections import LineCollection

from redsim.engine import run_scenario
from redsim.scenarios import build_scenario


def to_xy(points: list[tuple[float, float]]) -> np.ndarray:
    """List of (x, y) pairs -> 2-column array, as set_offsets wants. Copes with empty."""
    return np.array(points).reshape(-1, 2)


def animate_raid(history, shot_history, drones, radars, effectors, path, dt_s=10.0, trail_len=16):
    """Draw the fixed scene once, then move the drones frame by frame."""
    view_start_km = 0  # left edge of the map; drones appear from here
    sub_steps = 3 # in-between frames drawn per simulated step (smoothness)
    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(10, 6))
    sites = list({d.target.name: d.target for d in drones}.values())  # each site once

    # Fixed scene: drawn once 
    for r in radars:
        ax.add_patch(plt.Circle((r.x_km, r.y_km), r.max_range_km, fill=False,
                                color="tab:cyan", linestyle=":", alpha=0.6,
                                label=f"Radar max range ({r.max_range_km} km)"))
        ax.plot(r.x_km, r.y_km, marker="^", color="tab:cyan", markersize=10)

    for e in effectors:
        colour = "magenta" if e.is_jammer else "deepskyblue"
        style = "--" if e.is_jammer else "-"
        ax.add_patch(plt.Circle((e.x_km, e.y_km), e.range_km, color=colour, alpha=0.08))
        ax.add_patch(plt.Circle((e.x_km, e.y_km), e.range_km, fill=False,
                                color=colour, linestyle=style, label=e.name))

    for s in sites:
        ax.plot(s.x_km, s.y_km, marker="s", color="white", markersize=10)
        ax.annotate(f"{s.name} (value {s.value:.0f})", (s.x_km, s.y_km),
                    xytext=(12, 0), textcoords="offset points", va="center", fontsize=9)

    # Moving parts: start empty, filled in each frame 
    hit_glow = ax.scatter([], [], s=800, color="red", alpha=0.35)

    trails = []
    for f in history[0]:  # one trail per drone, coloured by type
        colour = "orange" if f["is_decoy"] else "red"
        line, = ax.plot([], [], color=colour, alpha=0.4, linewidth=1)
        trails.append(line)

    real = ax.scatter([], [], color="red", s=25, label="Real drone")
    decoy = ax.scatter([], [], color="orange", s=25, label="Decoy")
    dead = ax.scatter([], [], color="grey", marker="x", s=40, label="Killed")
    clock = ax.text(0.02, 0.97, "", transform=ax.transAxes, va="top",
                    family="monospace", fontsize=10,
                    bbox=dict(facecolor="black", alpha=0.7, edgecolor="grey"))
    
    # Shot lines: white for the gun, dotted magenta for the jammer
    gun_lines = LineCollection([], colors="white", linewidths=1.5, label="Gun shot")
    jam_lines = LineCollection([], colors="magenta", linewidths=1.2,
                               linestyles=":", label="Jamming")
    ax.add_collection(gun_lines)
    ax.add_collection(jam_lines)

    # Gun rounds: starting magazine, and how many fired by each frame
    start_rounds = sum(e.magazine for e in effectors if not e.is_jammer)
    fired_so_far = []
    total = 0
    for shots in shot_history:
        total += sum(not s["is_jammer"] for s in shots)
        fired_so_far.append(total)

    ax.set_xlim(-2, 40)
    ax.set_ylim(-3, max(d.y_km for d in drones) + 3)
    ax.set_aspect("equal")
    ax.set_xlabel("East (km)")
    ax.set_ylabel("North (km)")
    ax.set_title("Red drone attack with decoys vs Blue CNI targets")
    ax.legend(loc="upper right", fontsize=8, framealpha=0.8)

    def blend(k, t):
        """Each drone's position part-way (t from 0 to 1) from frame k to k+1."""
        a = history[k]
        b = history[min(k + 1, len(history) - 1)]  # don't run off the end
        return [((1 - t) * fa["x_km"] + t * fb["x_km"],
                 (1 - t) * fa["y_km"] + t * fb["y_km"])
                for fa, fb in zip(a, b)]

    def draw(n):
        k = n // sub_steps                 # which recorded frame we're after
        t = (n % sub_steps) / sub_steps    # how far towards the next one (0 to <1)
        frame = history[k]
        pos = blend(k, t)

        # Trails: recorded positions so far, plus the current in-between point
        start = max(0, k - trail_len)
        for j, line in enumerate(trails):
            xs = [history[m][j]["x_km"] for m in range(start, k + 1)] + [pos[j][0]]
            ys = [history[m][j]["y_km"] for m in range(start, k + 1)] + [pos[j][1]]
            line.set_data(xs, ys)

        # Drones: flying ones use the blended position
        flying = [(f, p) for f, p in zip(frame, pos) if f["alive"] and not f["arrived"]]
        real.set_offsets(to_xy([p for f, p in flying if not f["is_decoy"]]))
        decoy.set_offsets(to_xy([p for f, p in flying if f["is_decoy"]]))
        dead.set_offsets(to_xy([(f["x_km"], f["y_km"]) for f in frame if not f["alive"]]))

        # Sites hit by a real drone glow red
        hit_names = {f["target"] for f in frame if f["arrived"] and not f["is_decoy"]}
        hit_glow.set_offsets(to_xy([(s.x_km, s.y_km) for s in sites if s.name in hit_names]))

        # Shots fired during this step (k -> k+1)
        shots = shot_history[min(k + 1, len(shot_history) - 1)]
        gun_lines.set_segments([[(s["from_x"], s["from_y"]), (s["to_x"], s["to_y"])]
                                for s in shots if not s["is_jammer"]])
        jam_lines.set_segments([[(s["from_x"], s["from_y"]), (s["to_x"], s["to_y"])]
                                for s in shots if s["is_jammer"]])
        
        # Scoreboard
        kills = sum(not f["alive"] for f in frame)
        leakers = sum(f["arrived"] and not f["is_decoy"] for f in frame)
        rounds_left = start_rounds - fired_so_far[k]
        clock.set_text(f"T+{(k + t) * dt_s:4.0f} s\nKills:   {kills}\n"
                       f"Leakers: {leakers}\nRounds:  {rounds_left}/{start_rounds}")

    # Play every frame, then hold the last one for 1.5 s so the result is readable
    frames = list(range(len(history))) + [len(history) - 1] * 15
    anim = FuncAnimation(fig, draw, frames=frames, interval=100)
    anim.save(path, writer=PillowWriter(fps=10))
    plt.close(fig)

    # Skip the empty start, play every in-between frame, then hold the last for 1.5 s
    first = next(i for i, frame in enumerate(history)
                 if any(f["x_km"] >= view_start_km for f in frame))
    last = (len(history) - 1) * sub_steps
    fps = 10 * sub_steps  # same playback speed, more pictures
    frames = list(range(first * sub_steps, last + 1)) + [last] * (15 * sub_steps)

    anim = FuncAnimation(fig, draw, frames=frames, interval=1000 / fps)
    anim.save(path, writer=PillowWriter(fps=fps))
    plt.close(fig)

def rank_seeds(raid_size: int, decoy_fraction: float, n_seeds: int = 200):
    """Run one raid with many seeds (no recording). Most kills first."""
    scores = []
    for seed in range(n_seeds):
        drones, radars, effectors = build_scenario(raid_size, decoy_fraction,
                                                   random.Random(seed + 1_000_000))
        result = run_scenario(drones, radars, effectors, random.Random(seed))
        scores.append((result.kills, result.leakers, seed))
    scores.sort(reverse=True)
    return scores


if __name__ == "__main__":
    scores = rank_seeds(17, 0.25)
    average_kills = sum(k for k, _, _ in scores) / len(scores)
    print(f"Average kills: {average_kills:.1f}")
    print("Best for Blue:", scores[:3])
    print("Worst for Blue:", scores[-3:])

    seed = 6
    drones, radars, effectors = build_scenario(17, 0.5, random.Random(seed + 1_000_000))
    result = run_scenario(drones, radars, effectors, random.Random(seed), record=True)
    print(f"kills={result.kills}  leakers={result.leakers}  "
          f"value_destroyed={result.value_destroyed}")

    Path("figures").mkdir(exist_ok=True)
    animate_raid(result.history, result.shot_history, drones, radars, effectors, "figures/raid.gif")
    print("Saved figures/raid.gif")