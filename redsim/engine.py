"""this is the engagement loop and runs one raid from launch to finish"""
import copy
import random
from dataclasses import dataclass

from redsim.models import Drone, Effector, Radar

@dataclass
class ScenarioResult:
    """what happened in one raid"""
    kills: int
    leakers: int    # real (non-decoy) drones that reached their target
    value_destroyed: float # each site counted once, however many hits
    rounds_used: int    # interceptors fired (jammers not counted)

def run_scenario(
        drones: list[Drone],
        radars: list[Radar],
        effectors: list[Effector],
        rng: random.Random,
        dt_s: float = 10.0,
        max_time_s: float = 3600.0,
    )   -> ScenarioResult:
        """Fly every drone until dead or arrived, with Blue shooting back"""
        drones = copy.deepcopy(drones)
        effectors = copy.deepcopy(effectors)
        start_mags = [e.magazine for e in effectors]

        t_s = 0.0
        while t_s < max_time_s:
              active = [d for d in drones if d.alive and not d.arrived]
              if not active:
                    break

              #1. Sense: a drone is visible if ANY radar can see it
              detected = [
                    d for d in active
                    if any(r.can_detect(d.x_km, d.y_km,d.altitude_m)for r in radars)
              ]

              #2.Shoot: each effector takes one shot per time step
              for effector in effectors:
                    for drone in detected:
                          if drone.alive and effector.in_range(drone):
                                effector.engage(drone, rng)
                                break

              #3. Move
              for drone in active:
                    drone.step(dt_s)
                    t_s += dt_s

        real_hits = [d for d in drones if d.arrived and not d.drone_type.is_decoy]
        sites_hit = {d.target.name: d.target.value for d in real_hits}
        rounds_used = sum(
              start - e.magazine
              for start, e in zip(start_mags, effectors)
              if start is not None
        )

        return ScenarioResult(
              kills = sum(not d.alive for d in drones),
              leakers = len(real_hits),
              value_destroyed=sum(sites_hit.values()),
              rounds_used= rounds_used,
        )

if __name__ == "__main__":
      from redsim.models import DroneType, Site

      site = Site(name="Substation A", x_km=30, y_km=0, value=8.0)
      radar = Radar(name="R1", x_km=30, y_km=0, mast_height_m=10, max_range_km=30)
      gun = Effector(name="Gun 1", x_km=30, y_km=0, range_km=3, p_kill=0.5, magazine =4, is_jammer=False)
      owa = DroneType(name="One-way-attack", speed_kmh=150, cost=1.0,jammable=False, is_decoy=False)
      raid = [Drone(drone_type=owa, x_km=0, y_km=y, altitude_m=50, target=site)
              for y in (-2, -1, 0, 1, 2)]

      for seed in range(3):
            result = run_scenario(raid, [radar], [gun], random.Random(seed))
            print(f"Seed {seed}: {result}")
