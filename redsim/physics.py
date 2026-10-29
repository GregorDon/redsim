import math


def radar_horizon_km(radar_height_m: float, target_height_m: float) -> float:
    """Maximum line-of-sight distance (km) between a radar and a target,
    using the standard 4/3 Earth radius approximation."""
    return 4.12 * (math.sqrt(radar_height_m) + math.sqrt(target_height_m))


if __name__ == "__main__":
    print(radar_horizon_km(10, 50))
