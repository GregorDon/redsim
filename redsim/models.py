import math
import random
from dataclasses import dataclass
from redsim.physics import radar_horizon_km

@dataclass
class Site:
    """A piece of CNI that Red wants to hit."""
    name: str
    x_km: float
    y_km: float
    value: float  # relative importance, e.g. 1.0 to 10.0


@dataclass
class Radar:
    """A Blue sensor. Detection is limited by both its instrumented
    range and the radar horizon."""
    name: str
    x_km: float
    y_km: float
    mast_height_m: float
    max_range_km: float

    def detection_range_km(self, target_altitude_m: float) -> float:
        """How far away this radar can see a target at a given altitude."""
        horizon = radar_horizon_km(self.mast_height_m, target_altitude_m)
        return min(horizon, self.max_range_km)

    def can_detect(self, x_km: float, y_km: float, altitude_m: float) -> bool:
        """True if a target at this position and altitude is detectable."""
        distance = math.hypot(x_km - self.x_km, y_km - self.y_km)
        return distance <= self.detection_range_km(altitude_m)


@dataclass
class DroneType:
    """A class of Red drone. All values are notional."""
    name: str
    speed_kmh: float
    cost: float          # notional cost units
    jammable: bool       # True if it relies on a radio link
    is_decoy: bool       # decoys draw fire but do no damage


@dataclass
class Effector:
    """Blue's counter-drone weapon."""
    name: str
    x_km: float
    y_km: float
    range_km: float          # how far away it can engage a drone
    p_kill: float            # probability one shot kills a drone, between 0 and 1
    magazine: int | None     # number of shots; None means unlimited (jammers)
    is_jammer: bool

    def in_range(self, drone: "Drone") -> bool:
        """True if the drone is close enough to engage"""
        distance = math.hypot(drone.x_km - self.x_km, drone.y_km - self.y_km)
        return distance <= self.range_km

    def engage(self, drone: "Drone", rng: random.Random) -> bool:
        """Fire one shot at the drone. Returns True if it was killed."""
        if self.magazine ==0:
            return False    #out of ammo
        if self.is_jammer and not drone.drone_type.jammable:
            return False   #jamming has no effect on the drone
        if self.magazine is not None:
            self.magazine -= 1
        if rng.random() < self.p_kill:
            drone.alive = False
            return True
        return False
    

@dataclass
class Drone:
    """One Red Drone in flight."""
    drone_type: DroneType
    x_km: float
    y_km: float
    altitude_m: float
    target: Site
    alive: bool = True
    arrived: bool = False

    def step(self, dt_s: float) -> None:
        """Fly towards the target for dt_s seconds"""
        if not self.alive or self.arrived:
            return

        dx = self.target.x_km - self.x_km
        dy = self.target.y_km - self.y_km
        distance = math.hypot(dx,dy)
        move = self.drone_type.speed_kmh * dt_s / 3600   #km covered in this step

        if move >= distance:
            self.x_km, self.y_km = self.target.x_km, self.target.y_km
            self.arrived = True
        else:
            self.x_km += dx / distance * move
            self.y_km += dy / distance * move

if __name__ == "__main__":
    site = Site(name="Substation A", x_km=30, y_km=0, value=8.0)
    radar = Radar(name="R1", x_km=30, y_km=0, mast_height_m=10, max_range_km=30)
    owa = DroneType(name="One-way-attack", speed_kmh=150, cost=1.0, jammable=False, is_decoy=False)
    drone = Drone(drone_type=owa, x_km=0, y_km=0, altitude_m=10, target=site)

    dt_s = 60   # time step: one minute
    t_s = 0
    first_detected_s = None

    while not drone.arrived:
        if first_detected_s is None and radar.can_detect(drone.x_km, drone.y_km, drone.altitude_m):
            first_detected_s = t_s
        drone.step(dt_s)
        t_s += dt_s

    print(f"First detected at t = {first_detected_s}")
    print(f"Arrived at t = {t_s} s")
    print(f"warning time: {t_s - first_detected_s} s")

