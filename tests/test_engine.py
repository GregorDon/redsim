import random

from redsim.engine import run_scenario
from redsim.models import Drone, DroneType, Effector, Radar, Site


def test_no_defences_all_drones_leak():
    site = Site(name="Substation A", x_km=30, y_km=0, value=8.0)
    owa = DroneType(name="One-way attack", speed_kmh=150, cost=1.0,
                    jammable=False, is_decoy=False)                 
    drones = [Drone(drone_type=owa, x_km=0, y_km=0, altitude_m=50, target=site)
              for _ in range(3)]

    result = run_scenario(drones, [], [], random.Random(42))

    assert result.leakers == 3
    assert result.kills == 0


def test_run_does_not_change_inputs():
    site = Site(name="Substation A", x_km=30, y_km=0, value=8.0)
    owa = DroneType(name="One-way attack", speed_kmh=150, cost=1.0,
                    jammable=False, is_decoy=False)
    gun = Effector(name="Gun 1", x_km=30, y_km=0, range_km=3, 
                   p_kill=0.5, magazine =4, is_jammer=False)            
    drones = [Drone(drone_type=owa, x_km=0, y_km=0, altitude_m=50, target=site)
              for _ in range(3)]

    result = run_scenario(drones, [], [gun], random.Random(42))

    assert gun.magazine == 4

def test_large_raid_all_leak_without_defences():
    site = Site(name="Substation A", x_km=30, y_km=0, value=8.0)
    owa = DroneType(name="One-way attack", speed_kmh=150, cost=1.0,
                    jammable=False, is_decoy=False)           
    drones = [Drone(drone_type=owa, x_km=0, y_km=0, altitude_m=50, target=site)
            for _ in range(30)]

    result = run_scenario(drones, [], [], random.Random(42))

    assert result.leakers == 30
    assert result.kills == 0


def test_gun_engages_nearest_threat_first():
    site = Site(name="Substation A", x_km=30, y_km=0, value=8.0)
    owa = DroneType(name="One-way attack", speed_kmh=150, cost=1.0,
                    jammable=False, is_decoy=False)
    decoy = DroneType(name="Decoy", speed_kmh=150, cost=0.1,
                    jammable=True, is_decoy=True)
    drones = [
        Drone(drone_type=decoy, x_km=20, y_km=0, altitude_m=100, target=site),  # first, but further
        Drone(drone_type=owa, x_km=25, y_km=0, altitude_m=100, target=site),    # second, but closer
    ]
    radar = Radar(name="R1", x_km=30, y_km=0, mast_height_m=10, max_range_km=30)
    gun = Effector(name="Gun 1", x_km=30, y_km=0, range_km=15,
                p_kill=1.0, magazine=1, is_jammer=False)

    result = run_scenario(drones, [radar], [gun], random.Random(0))

    assert result.leakers == 0


def test_record_gives_one_snapshot_per_drone_per_step():
    # Arrange: 3 undefended drones, 30 km out at 150 km/h
    site = Site(name="Substation A", x_km=30, y_km=0, value=8.0)
    owa = DroneType(name="One-way attack", speed_kmh=150, cost=1.0,
                    jammable=False, is_decoy=False)
    drones = [Drone(drone_type=owa, x_km=0, y_km=0, altitude_m=50, target=site)
              for _ in range(3)]

    # Act: run with recording switched on, and store the result
    result = run_scenario(drones, [], [], random.Random(0), record=True)

    # Assert: 30 km at 150 km/h is 720 s, so 72 steps of 10 s, plus the start frame
    assert len(result.history) == 73
    assert all(len(frame) == 3 for frame in result.history)


def test_no_history_by_default():
    # Arrange: one undefended drone
    site = Site(name="Substation A", x_km=30, y_km=0, value=8.0)
    owa = DroneType(name="One-way attack", speed_kmh=150, cost=1.0,
                    jammable=False, is_decoy=False)
    drones = [Drone(drone_type=owa, x_km=0, y_km=0, altitude_m=50, target=site)]

    # Act: run without asking to record
    result = run_scenario(drones, [], [], random.Random(0))

    # Assert: nothing was recorded
    assert result.history == []

def test_record_logs_one_certain_shot():
    # Arrange: one drone, a radar, and a gun with 1 round that can't miss
    site = Site(name="Substation A", x_km=30, y_km=0, value=8.0)
    owa = DroneType(name="One-way attack", speed_kmh=150, cost=1.0,
                    jammable=False, is_decoy=False)
    drones = [Drone(drone_type=owa, x_km=0, y_km=0, altitude_m=50, target=site)]
    radar = Radar(name="R1", x_km=30, y_km=0, mast_height_m=10, max_range_km=30)
    gun = Effector(name="Gun 1", x_km=30, y_km=0, range_km=3,
                   p_kill=1.0, magazine=1, is_jammer=False)

    # Act: run with recording on, and store the result
    result = run_scenario(drones, [radar], [gun], random.Random(0), record=True)

    # Assert: the two lists line up, and exactly one shot was logged, a hit
    all_shots = [s for step in result.shot_history for s in step]
    assert len(result.shot_history) == len(result.history)
    assert len(all_shots) == 1
    assert all_shots[0]["hit"] is True