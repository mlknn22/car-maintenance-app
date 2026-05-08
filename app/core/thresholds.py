from dataclasses import dataclass


@dataclass(frozen=True)
class Thresholds:
    coolant_warn: float = 100.0
    coolant_crit: float = 110.0

    battery_running_warn: float = 13.0
    battery_running_crit: float = 12.0

    battery_idle_warn: float = 12.0
    battery_idle_crit: float = 11.5

    overrev_crit: float = 6500.0

    cold_rev_rpm: float = 3000.0
    cold_rev_coolant_max: float = 60.0

    engine_running_rpm: float = 500.0


DEFAULT_THRESHOLDS = Thresholds()
