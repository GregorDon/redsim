import math
import pytest

from redsim.physics import radar_horizon_km

def test_known_value():
    #10 m mast, drone at 50m altitude ->42.16km
    assert radar_horizon_km(10,50) == pytest.approx(42.16, abs=0.01)

def test_target_on_ground_uses_radar_height_only():
    assert radar_horizon_km(10,0) == pytest.approx(4.12 * math.sqrt(10))

def test_higher_drone_is_seen_further_away():
    assert radar_horizon_km(10,300) > radar_horizon_km(10,50)