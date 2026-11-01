import pytest
from redsim.sweep import run_sweep
from redsim.scenarios import DECOY, OWA

def test_sweep_row_count():
    rows = run_sweep(raid_sizes=[4,8], decoy_fractions=[0.0, 0.5], n_runs=3)

    assert len(rows) == 12 


def test_sweep_red_cost():
    rows = run_sweep(raid_sizes=[4], decoy_fractions=[0.5], n_runs=1)

    assert rows[0]["red_cost"] == pytest.approx(2.2)


