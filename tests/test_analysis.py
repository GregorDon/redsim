import pandas as pd

from redsim.analysis import pareto_front


def test_pareto_front_drops_bad_buys():
    # Three raids. Cost 2 does LESS damage than the cheaper cost 1,
 
    summary = pd.DataFrame({"red_cost": [1.0, 2.0, 3.0],
                            "damage":   [5.0, 4.0, 8.0]})

    # Run the function, and store the table it gives back as "front"
    front = pareto_front(summary)

    # Only the cost 1 and cost 3 raids are left
    assert list(front["red_cost"]) == [1.0, 3.0]