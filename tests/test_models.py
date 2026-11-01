from redsim.models import Drone,DroneType, Radar, Site, Effector
import random

def test_low_drone_hidden_below_horizon():
    radar = Radar(name="R1", x_km=0, y_km=0, mast_height_m=10, max_range_km=30)
    assert not radar.can_detect(x_km=28, y_km=0, altitude_m=10)

def test_higher_drone_detected_at_same_distance():
    radar = Radar(name="R1", x_km=0, y_km=0, mast_height_m=10, max_range_km=30)
    assert radar.can_detect(x_km=28, y_km=0, altitude_m=100)

def test_drone_arrives_exactly_on_target():
    site = Site(name="Substation A", x_km=30, y_km=0, value=8.0)
    owa = DroneType(name="One-way-attack", speed_kmh=150, cost=1.0, 
                    jammable=False, is_decoy=False)
    drone = Drone(drone_type=owa, x_km=0, y_km=0, altitude_m=10, target=site)
   

    for _ in range(20):
        drone.step(60)
    assert drone.arrived
    assert drone.x_km == site.x_km
    assert drone.y_km == site.y_km

def test_certain_kill_uses_one_round():
    site = Site(name="Substation A", x_km=30, y_km=0, value=8.0)
    owa = DroneType(name="One-way-attack", speed_kmh=150, cost=1.0, 
                    jammable=False, is_decoy=False)
    drone = Drone(drone_type=owa, x_km=0, y_km=0, altitude_m=10, target=site)
    weapon = Effector(name="missile", x_km=30, y_km=0, range_km=5,
                      p_kill=1.0, magazine=3, is_jammer=False)               
    rng = random.Random(42)

    weapon.engage(drone, rng)

    assert not drone.alive
    assert weapon.magazine == 2

def test_jammer_cannot_kill_unjammable_drone():
    site = Site(name="Substation A", x_km=30, y_km=0, value=8.0)
    owa = DroneType(name="One-way-attack", speed_kmh=150, cost=1.0, 
                    jammable=False, is_decoy=False)
    drone = Drone(drone_type=owa, x_km=0, y_km=0, altitude_m=10, target=site)
    jammer = Effector(name="jammer", x_km=30, y_km=0, range_km=5, 
                      p_kill=1.0, magazine=None, is_jammer=True)                    
    rng = random.Random(42)
    
    jammer.engage(drone, rng)
    
    assert drone.alive

def test_jammer_kills_jammable_drone():
    site = Site(name="Substation A", x_km=30, y_km=0, value=8.0)
    owa = DroneType(name="One-way-attack", speed_kmh=150, cost=1.0, jammable=True, is_decoy=False)
    drone = Drone(drone_type=owa, x_km=0, y_km=0, altitude_m=10, target=site)
    jammer = Effector(name="jammer", x_km=30, y_km=0, range_km=5, p_kill=1.0, magazine=None, is_jammer=True)                    
    rng = random.Random(42)
    
    jammer.engage(drone, rng)
    
    assert not drone.alive