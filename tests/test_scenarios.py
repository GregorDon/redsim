from redsim.scenarios import build_scenario

def test_build_scenario_counts():
    drones, radars, effectors = build_scenario(raid_size=10, decoy_fraction=0.3)

    assert len(drones) == 10
    assert sum(d.drone_type.is_decoy for d in drones) == 3



def test_build_scenario_no_decoys():
    drones, radars, effectors = build_scenario(raid_size=10, decoy_fraction=0.0)

    assert len(drones) == 10
    assert sum(d.drone_type.is_decoy for d in drones) == 0