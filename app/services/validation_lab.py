"""Laboratorio local de estrés y validación de AmylAI.

Genera cohortes sintéticas deterministas (sin servicios externos) y ejecuta
el mismo motor clínico local (`analyze_case`) sobre cada escenario para medir
sensibilidad, especificidad, precisión, calibración y discriminación.

Todo el cálculo es estadístico real sobre los resultados del motor: no hay
valores inventados ni respuestas simuladas.
"""

import random
from typing import TypedDict

from app.services.clinical_engine import analyze_case

_POSITIVE_SYMPTOMS: list[str] = [
    "Disnea de esfuerzo",
    "Edema periférico",
    "Síncope o presíncope",
    "Hipotensión ortostática",
    "Parestesias distales",
    "Síndrome del túnel carpiano bilateral",
    "Macroglosia",
    "Proteinuria conocida",
    "Palpitaciones",
    "Pérdida de peso involuntaria",
]

_CONTROL_SYMPTOMS: list[str] = [
    "Fatiga persistente",
    "Palpitaciones",
    "Diarrea o saciedad precoz",
    "Disnea de esfuerzo",
    "Edema periférico",
]

_POSITIVE_RED_FLAGS: list[str] = [
    "Disnea en reposo o ortopnea",
    "Insuficiencia cardíaca descompensada",
    "Arritmia sostenida documentada",
    "Síncope de esfuerzo",
    "Deterioro renal rápido",
    "Hipotensión sintomática severa",
]

_POSITIVE_RISK_FACTORS: list[str] = [
    "Gammapatía monoclonal conocida",
    "Hipertrofia ventricular no explicada",
    "NT-proBNP elevado",
    "Troponina persistentemente elevada",
    "Antecedente familiar de amiloidosis",
    "Mieloma múltiple",
    "Edad mayor de 65 años",
]

_CONTROL_RISK_FACTORS: list[str] = [
    "Enfermedad inflamatoria crónica",
    "Edad mayor de 65 años",
]

_POSITIVE_PHRASES: list[str] = [
    "Ecocardiograma con hipertrofia ventricular no explicada y patrón de strain apical preservado.",
    "Estudio de cadenas ligeras alterado con sospecha de depósito de transtiretina.",
    "Proteinuria significativa en rango nefrótico con función renal en descenso.",
    "Neuropatía distal progresiva con antecedente de túnel carpiano bilateral.",
    "Resonancia cardíaca con realce tardío difuso sugerente de amiloidosis.",
]

_CONTROL_PHRASES: list[str] = [
    "Estudio cardiológico sin hallazgos estructurales relevantes.",
    "Cuadro compatible con desacondicionamiento físico y anemia leve corregida.",
    "Control ambulatorio sin cambios respecto a la evaluación previa.",
    "Síntomas atribuibles a proceso viral autolimitado ya resuelto.",
    "Función renal y marcadores cardíacos dentro de rangos habituales.",
]

_SEX_VALUES: list[str] = ["female", "male", "unspecified"]

_SEX_LABELS: dict[str, str] = {
    "female": "Femenino",
    "male": "Masculino",
    "unspecified": "No especificado",
}

_OUTCOME_LABELS: dict[str, str] = {
    "tp": "Verdadero positivo",
    "fp": "Falso positivo",
    "tn": "Verdadero negativo",
    "fn": "Falso negativo",
}


class Scenario(TypedDict):
    id: int
    reference: str
    cohort: str
    age: int
    sex_display: str
    symptoms: list[str]
    red_flags: list[str]
    risk_factors: list[str]
    truth: int
    predicted: int
    risk_level: str
    risk_label: str
    risk_score: float
    confidence: float
    completeness: float
    diagnosis_label: str
    outcome: str
    outcome_label: str


class Metrics(TypedDict):
    sensitivity: float
    specificity: float
    precision: float
    npv: float
    accuracy: float
    f1: float
    auc: float
    brier: float
    calibration_error: float
    tp: int
    fp: int
    tn: int
    fn: int
    positives: int
    controls: int
    mean_score_positive: float
    mean_score_control: float
    mean_confidence: float
    total: int


class CalibrationPoint(TypedDict):
    bucket: str
    expected: float
    observed: float
    count: int


class RocPoint(TypedDict):
    threshold: float
    fpr: float
    tpr: float


class DistributionRow(TypedDict):
    level: str
    positivos: int
    controles: int


EMPTY_METRICS: Metrics = {
    "sensitivity": 0.0,
    "specificity": 0.0,
    "precision": 0.0,
    "npv": 0.0,
    "accuracy": 0.0,
    "f1": 0.0,
    "auc": 0.0,
    "brier": 0.0,
    "calibration_error": 0.0,
    "tp": 0,
    "fp": 0,
    "tn": 0,
    "fn": 0,
    "positives": 0,
    "controls": 0,
    "mean_score_positive": 0.0,
    "mean_score_control": 0.0,
    "mean_confidence": 0.0,
    "total": 0,
}


def _sample(
    rng: random.Random, pool: list[str], low: int, high: int
) -> list[str]:
    count = rng.randint(low, min(high, len(pool)))
    if count <= 0:
        return []
    return rng.sample(pool, count)


def _summary(rng: random.Random, positive: bool, symptoms: list[str]) -> str:
    phrases = _POSITIVE_PHRASES if positive else _CONTROL_PHRASES
    picked = rng.sample(phrases, 2)
    detail = ", ".join(symptoms[:3]).lower() or "sin hallazgos estructurados"
    return f"{picked[0]} {picked[1]} Hallazgos registrados: {detail}."


def _build_case(
    rng: random.Random, index: int, positive: bool
) -> tuple[Scenario, dict[str, str]]:
    if positive:
        age = rng.randint(58, 88)
        symptoms = _sample(rng, _POSITIVE_SYMPTOMS, 3, 6)
        red_flags = _sample(rng, _POSITIVE_RED_FLAGS, 0, 2)
        risk_factors = _sample(rng, _POSITIVE_RISK_FACTORS, 1, 3)
        complaint = (
            "Disnea progresiva con hallazgos multisistémicos en estudio."
        )
    else:
        age = rng.randint(28, 74)
        symptoms = _sample(rng, _CONTROL_SYMPTOMS, 0, 2)
        red_flags = []
        risk_factors = _sample(rng, _CONTROL_RISK_FACTORS, 0, 1)
        complaint = "Consulta por síntomas inespecíficos de curso benigno."
    sex = rng.choice(_SEX_VALUES)
    summary = _summary(rng, positive, symptoms)
    scenario: Scenario = {
        "id": index,
        "reference": f"SYN-{index:04d}",
        "cohort": "Cohorte con enfermedad" if positive else "Cohorte control",
        "age": age,
        "sex_display": _SEX_LABELS[sex],
        "symptoms": symptoms,
        "red_flags": red_flags,
        "risk_factors": risk_factors,
        "truth": 1 if positive else 0,
        "predicted": 0,
        "risk_level": "undetermined",
        "risk_label": "No calculado",
        "risk_score": 0.0,
        "confidence": 0.0,
        "completeness": 0.0,
        "diagnosis_label": "",
        "outcome": "tn",
        "outcome_label": _OUTCOME_LABELS["tn"],
    }
    payload = {
        "sex": sex,
        "complaint": complaint,
        "summary": summary,
    }
    return scenario, payload


def _roc(
    scored: list[tuple[float, int]], positives: int, controls: int
) -> list[RocPoint]:
    points: list[RocPoint] = []
    for step in range(0, 105, 5):
        threshold = float(step)
        tp = sum(
            1 for score, truth in scored if score >= threshold and truth == 1
        )
        fp = sum(
            1 for score, truth in scored if score >= threshold and truth == 0
        )
        tpr = tp / positives if positives else 0.0
        fpr = fp / controls if controls else 0.0
        points.append(
            {
                "threshold": threshold,
                "tpr": round(tpr * 100, 1),
                "fpr": round(fpr * 100, 1),
            }
        )
    points.sort(key=lambda p: (p["fpr"], p["tpr"]))
    return points


def _auc(points: list[RocPoint]) -> float:
    area = 0.0
    for first, second in zip(points, points[1:]):
        width = (second["fpr"] - first["fpr"]) / 100
        height = (second["tpr"] + first["tpr"]) / 200
        area += width * height
    return round(min(max(area, 0.0), 1.0) * 100, 1)


def _calibration(
    scored: list[tuple[float, int]],
) -> tuple[list[CalibrationPoint], float]:
    buckets: list[CalibrationPoint] = []
    total_gap = 0.0
    total_count = 0
    for start in range(0, 100, 20):
        end = start + 20
        group = [
            (score, truth)
            for score, truth in scored
            if score >= start and (score < end or (end == 100 and score <= 100))
        ]
        if not group:
            buckets.append(
                {
                    "bucket": f"{start}-{end}",
                    "expected": round((start + end) / 2, 1),
                    "observed": 0.0,
                    "count": 0,
                }
            )
            continue
        expected = sum(score for score, _ in group) / len(group)
        observed = sum(truth for _, truth in group) / len(group) * 100
        total_gap += abs(expected - observed) * len(group)
        total_count += len(group)
        buckets.append(
            {
                "bucket": f"{start}-{end}",
                "expected": round(expected, 1),
                "observed": round(observed, 1),
                "count": len(group),
            }
        )
    error = round(total_gap / total_count, 1) if total_count else 0.0
    return buckets, error


def run_validation(
    scenario_count: int,
    seed: int,
    positive_ratio: int,
    threshold: float,
) -> tuple[
    list[Scenario],
    Metrics,
    list[CalibrationPoint],
    list[RocPoint],
    list[DistributionRow],
]:
    count = max(20, min(400, scenario_count))
    ratio = max(10, min(90, positive_ratio))
    rng = random.Random(seed)
    positives_target = round(count * ratio / 100)
    flags = [True] * positives_target + [False] * (count - positives_target)
    rng.shuffle(flags)

    scenarios: list[Scenario] = []
    scored: list[tuple[float, int]] = []
    for index, positive in enumerate(flags, start=1):
        scenario, payload = _build_case(rng, index, positive)
        result = analyze_case(
            scenario["age"],
            payload["sex"],
            payload["complaint"],
            payload["summary"],
            scenario["symptoms"],
            scenario["red_flags"],
            scenario["risk_factors"],
        )
        scenario["risk_level"] = result["risk_level"]
        scenario["risk_label"] = result["risk_label"]
        scenario["risk_score"] = result["risk_score"]
        scenario["confidence"] = result["confidence"]
        scenario["completeness"] = result["data_completeness"]
        scenario["diagnosis_label"] = result["diagnosis_label"]
        predicted = 1 if result["risk_score"] >= threshold else 0
        scenario["predicted"] = predicted
        if predicted == 1 and scenario["truth"] == 1:
            scenario["outcome"] = "tp"
        elif predicted == 1 and scenario["truth"] == 0:
            scenario["outcome"] = "fp"
        elif predicted == 0 and scenario["truth"] == 1:
            scenario["outcome"] = "fn"
        else:
            scenario["outcome"] = "tn"
        scenario["outcome_label"] = _OUTCOME_LABELS[scenario["outcome"]]
        scenarios.append(scenario)
        scored.append((result["risk_score"], scenario["truth"]))

    tp = sum(1 for s in scenarios if s["outcome"] == "tp")
    fp = sum(1 for s in scenarios if s["outcome"] == "fp")
    fn = sum(1 for s in scenarios if s["outcome"] == "fn")
    tn = sum(1 for s in scenarios if s["outcome"] == "tn")
    positives = tp + fn
    controls = tn + fp
    sensitivity = tp / positives * 100 if positives else 0.0
    specificity = tn / controls * 100 if controls else 0.0
    precision = tp / (tp + fp) * 100 if (tp + fp) else 0.0
    npv = tn / (tn + fn) * 100 if (tn + fn) else 0.0
    accuracy = (tp + tn) / len(scenarios) * 100 if scenarios else 0.0
    f1 = (
        2 * precision * sensitivity / (precision + sensitivity)
        if (precision + sensitivity)
        else 0.0
    )
    brier = (
        sum((score / 100 - truth) ** 2 for score, truth in scored) / len(scored)
        if scored
        else 0.0
    )
    roc = _roc(scored, positives, controls)
    calibration, calibration_error = _calibration(scored)
    pos_scores = [s["risk_score"] for s in scenarios if s["truth"] == 1]
    ctl_scores = [s["risk_score"] for s in scenarios if s["truth"] == 0]

    metrics: Metrics = {
        "sensitivity": round(sensitivity, 1),
        "specificity": round(specificity, 1),
        "precision": round(precision, 1),
        "npv": round(npv, 1),
        "accuracy": round(accuracy, 1),
        "f1": round(f1, 1),
        "auc": _auc(roc),
        "brier": round(brier, 3),
        "calibration_error": calibration_error,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "positives": positives,
        "controls": controls,
        "mean_score_positive": round(sum(pos_scores) / len(pos_scores), 1)
        if pos_scores
        else 0.0,
        "mean_score_control": round(sum(ctl_scores) / len(ctl_scores), 1)
        if ctl_scores
        else 0.0,
        "mean_confidence": round(
            sum(s["confidence"] for s in scenarios) / len(scenarios), 1
        )
        if scenarios
        else 0.0,
        "total": len(scenarios),
    }

    distribution: list[DistributionRow] = []
    for level, label in (
        ("low", "Riesgo bajo"),
        ("moderate", "Riesgo moderado"),
        ("high", "Riesgo alto"),
    ):
        distribution.append(
            {
                "level": label,
                "positivos": sum(
                    1
                    for s in scenarios
                    if s["risk_level"] == level and s["truth"] == 1
                ),
                "controles": sum(
                    1
                    for s in scenarios
                    if s["risk_level"] == level and s["truth"] == 0
                ),
            }
        )

    return scenarios, metrics, calibration, roc, distribution
