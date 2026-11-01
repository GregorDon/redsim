"""this is the engagement loop and runs one raid from launch to finish
DESCRIPTION
this is the scenario function, the main engine of the program. This takes copies of drones and effectors, runs them over a time period and plays out the detect > shoot > move logic
a while loop checks that the engine can run so long as the current time is below the max time, and while the drones are still alive and at least one hasn't arrived.
we put a drone in a detected list if any radar can see it, and use that list as the drones to shoot at with the effectors, then the remaining alive drones move.
We use real hits to determine if drones struck their target (if not a decoy), and sites hit to count the sites that were hit. In this block we also keep a value of magazine amount start state - end state.
we use a zip, to combine the magazine amount per effector into a tuple which is used to count amount of rounds used by each effectors - Jammers are "None" so don't deplete magazine.  
we then return the scenario results which we will use to do analysis on. 
the main code here runs a scenario 3 times (using range 3), trying drones at different y positions from -2km to 2km. """

import copy
import random
import math
from dataclasses import dataclass, field

from redsim.models import Drone, Effector, Radar

# creates a dataclass to hold the results of each scenario run by the engine

@dataclass
class ScenarioResult:
    """what happened in one raid"""
    kills: int
    leakers: int    # real (non-decoy) drones that reached their target
    value_destroyed: float # each site counted once, however many hits
    rounds_used: int    # interceptors fired (jammers not counted)
    history: list = field(default_factory=list)  # snapshots per step, if recorded
    shot_history: list = field(default_factory=list)  # shots per step, if recorded

def distance_to_target_km(drone: Drone) -> float:
    """How far a drone still has to fly. Used to rank threats."""
    return math.hypot(drone.target.x_km - drone.x_km,
                      drone.target.y_km - drone.y_km)

def snapshot(drones: list[Drone]) -> list[dict]:
    """Where every drone is right now, and its status. One animation frame."""
    return [
        {"x_km": d.x_km, "y_km": d.y_km, "alive": d.alive,
         "arrived": d.arrived, "is_decoy": d.drone_type.is_decoy, "target": d.target.name}
        for d in drones
    ]

def run_scenario(
        drones: list[Drone],
        radars: list[Radar],
        effectors: list[Effector],
        rng: random.Random,
        dt_s: float = 10.0,
        max_time_s: float = 3600.0,
        record: bool = False,
    )   -> ScenarioResult:
        """Fly every drone until dead or arrived, with Blue shooting back"""
        drones = copy.deepcopy(drones)
        effectors = copy.deepcopy(effectors)
        start_mags = [e.magazine for e in effectors]
        history = [snapshot(drones)] if record else []
        shot_history = [[]] if record else []  # no shots at launch

        t_s = 0.0
        if record:
            history = [snapshot(drones)] if record else []
        while t_s < max_time_s:
              active = [d for d in drones if d.alive and not d.arrived]  # build a fresh list each step of drones still in flight
              if not active:
                    break           # empty list counts as False, exit the loop if True.

              #1. Sense: a drone is visible if ANY radar can see it
              detected = [
                    d for d in active
                    if any(r.can_detect(d.x_km, d.y_km,d.altitude_m)for r in radars)
                    
              ]
              # Rank threats: engage the drone closest to its target first
              detected.sort(key=distance_to_target_km)
              
              #2. Shoot: each effector takes one shot per time step
              step_shots = []
              for effector in effectors:
                    for drone in detected:
                          if drone.alive and effector.in_range(drone):
                                mag_before = effector.magazine
                                effector.engage(drone, rng)
                                # Record it if the jammer worked or a round was spent
                                if record and (effector.is_jammer
                                               or effector.magazine != mag_before):
                                      step_shots.append({
                                            "from_x": effector.x_km, "from_y": effector.y_km,
                                            "to_x": drone.x_km, "to_y": drone.y_km,
                                            "is_jammer": effector.is_jammer,
                                            "hit": not drone.alive,
                                      })
                                break
              #3. Move
              for drone in active:
                    drone.step(dt_s)
              t_s += dt_s
              if record:
                  history.append(snapshot(drones))
                  shot_history.append(step_shots)

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
              history=history,
              shot_history=shot_history,
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
