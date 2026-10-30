import random

from redsim.engine import run_scenario
from redsim.models import Drone, DroneType, Effector, Radar, Site


def test_no_defences_all_drones_leak():
    site = Site(name="Substation A", x_km=30, y_km=0, value=8.0)
    owa = DroneType(name="One-way attack", speed_kmh=150, cost=1.0,jammable=False, is_decoy=False)                 
    drones = [Drone(drone_type=owa, x_km=0, y_km=0, altitude_m=50, target=site)
              for _ in range(3)]

    result = run_scenario(drones, [], [], random.Random(42))

    assert result.leakers == 3
    assert result.kills == 0


def test_run_does_not_change_inputs():
    site = Site(name="Substation A", x_km=30, y_km=0, value=8.0)
    owa = DroneType(name="One-way attack", speed_kmh=150, cost=1.0,jammable=False, is_decoy=False)
    gun = Effector(name="Gun 1", x_km=30, y_km=0, range_km=3, p_kill=0.5, magazine =4, is_jammer=False)            
    drones = [Drone(drone_type=owa, x_km=0, y_km=0, altitude_m=50, target=site)
              for _ in range(3)]

    result = run_scenario(drones, [], [gun], random.Random(42))

    assert gun.magazine == 4
 