""" Builds ready to run scenarios from a few Red dials. Blue is fixed"""
from redsim.models import Drone, DroneType, Effector, Radar, Site

# Two drone types available to Red
OWA = DroneType(name="One-way-attack", speed_kmh=150, cost=1.0,
                jammable=False, is_decoy=False)
DECOY = DroneType(name="Decoy", speed_kmh=150, cost=0.1,
                  jammable=True, is_decoy=True)

def build_scenario(
    raid_size: int,
    decoy_fraction: float,
) -> tuple[list[Drone], list[Radar], list[Effector]]:
    """Fixed Blue defence vs a Red raid of raid_size Drones"""
    site_a = Site(name="Substation A", x_km=30, y_km=0, value=8.0)
    site_b = Site(name ="Water plant", x_km=30, y_km=4,value=5.0)
    sites = [site_a, site_b]

    radars = [Radar(name="R1", x_km=30, y_km=2, mast_height_m=10, max_range_km=30)]

    effectors = [
        Effector(name="Gun 1", x_km=30, y_km=2, range_km=3,
                 p_kill= 0.5, magazine=8, is_jammer=False),
        Effector(name="Jammer 1", x_km=30,y_km=2, range_km=4,
                 p_kill=0.3, magazine=None, is_jammer=True),
    ]


    # Red Cell scenario variables
    n_decoys = int(round(raid_size * decoy_fraction))

    drones = [] 
    for i in range(raid_size):    # first drones are decoys, rest are real    
        if i < n_decoys:
            drone_type = DECOY
        else:
            drone_type = OWA

        target = sites[i % 2]     # alternates between two sites
        drones.append(Drone(drone_type=drone_type, x_km=0, y_km=i,
                            altitude_m=50, target=target))

        
    return drones, radars, effectors

if __name__ == "__main__":
    drones, radars, effectors = build_scenario(raid_size=6, decoy_fraction=0.5)
    for d in drones:
        print(d.drone_type.name, d.y_km, d.target.name)