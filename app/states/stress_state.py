import asyncio

import reflex as rx

from app.services.validation_lab import (
    EMPTY_METRICS,
    CalibrationPoint,
    DistributionRow,
    Metrics,
    RocPoint,
    Scenario,
    run_validation,
)


class StressState(rx.State):
    scenario_count: str = "120"
    seed: str = "42"
    positive_ratio: str = "50"
    threshold: str = "50"

    is_running: bool = False
    has_run: bool = False
    stage: str = ""
    outcome_filter: str = "all"

    scenarios: list[Scenario] = []
    metrics: Metrics = EMPTY_METRICS
    calibration: list[CalibrationPoint] = []
    roc: list[RocPoint] = []
    distribution: list[DistributionRow] = []

    count_options: list[tuple[str, str]] = [
        ("60 escenarios", "60"),
        ("120 escenarios", "120"),
        ("240 escenarios", "240"),
        ("360 escenarios", "360"),
    ]
    ratio_options: list[tuple[str, str]] = [
        ("30% con enfermedad", "30"),
        ("40% con enfermedad", "40"),
        ("50% con enfermedad", "50"),
        ("60% con enfermedad", "60"),
    ]
    outcome_options: list[tuple[str, str]] = [
        ("Todos los escenarios", "all"),
        ("Verdaderos positivos", "tp"),
        ("Falsos positivos", "fp"),
        ("Falsos negativos", "fn"),
        ("Verdaderos negativos", "tn"),
    ]

    @rx.var
    def threshold_value(self) -> float:
        raw = self.threshold.strip()
        if not raw.isdigit():
            return 50.0
        return float(max(5, min(95, int(raw))))

    @rx.var
    def filtered_scenarios(self) -> list[Scenario]:
        if self.outcome_filter == "all":
            return self.scenarios[:40]
        return [
            s for s in self.scenarios if s["outcome"] == self.outcome_filter
        ][:40]

    @rx.var
    def visible_count(self) -> int:
        return len(self.filtered_scenarios)

    @rx.var
    def error_rate(self) -> float:
        total = self.metrics["total"]
        if total == 0:
            return 0.0
        return round((self.metrics["fp"] + self.metrics["fn"]) / total * 100, 1)

    @rx.event
    def set_outcome_filter(self, value: str):
        self.outcome_filter = value

    @rx.event
    def set_scenario_count(self, value: str):
        self.scenario_count = value
        return StressState.run_suite

    @rx.event
    def set_positive_ratio(self, value: str):
        self.positive_ratio = value
        return StressState.run_suite

    @rx.event
    def set_seed(self, value: str):
        self.seed = value

    @rx.event
    def set_threshold(self, value: str):
        self.threshold = value

    @rx.event
    def shuffle_seed(self):
        raw = self.seed.strip()
        current = int(raw) if raw.isdigit() else 42
        self.seed = str((current * 7 + 13) % 9991)
        return StressState.run_suite

    @rx.event
    def reset_suite(self):
        self.scenario_count = "120"
        self.seed = "42"
        self.positive_ratio = "50"
        self.threshold = "50"
        self.outcome_filter = "all"
        return StressState.run_suite

    @rx.event
    async def run_suite(self):
        self.is_running = True
        self.stage = (
            "Generando cohorte sintética y evaluando con el motor local..."
        )
        raw_seed = self.seed.strip()
        seed = int(raw_seed) if raw_seed.isdigit() else 42
        count = (
            int(self.scenario_count) if self.scenario_count.isdigit() else 120
        )
        ratio = (
            int(self.positive_ratio) if self.positive_ratio.isdigit() else 50
        )
        threshold = self.threshold_value
        yield

        (
            scenarios,
            metrics,
            calibration,
            roc,
            distribution,
        ) = await asyncio.to_thread(
            run_validation, count, seed, ratio, threshold
        )

        self.scenarios = scenarios
        self.metrics = metrics
        self.calibration = calibration
        self.roc = roc
        self.distribution = distribution
        self.has_run = True
        self.is_running = False
        self.stage = ""
