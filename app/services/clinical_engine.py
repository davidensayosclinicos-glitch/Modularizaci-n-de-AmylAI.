"""Motor clínico local de AmylAI (algoritmo experto + heurística).

Lógica adaptada de los módulos `amylo_ai` para funcionar sin rutas externas:
todas las reglas, pesos y umbrales viven aquí y no dependen de archivos
del ZIP original.
"""

from typing import TypedDict

SYMPTOM_OPTIONS: list[str] = [
    "Disnea de esfuerzo",
    "Edema periférico",
    "Fatiga persistente",
    "Palpitaciones",
    "Síncope o presíncope",
    "Hipotensión ortostática",
    "Parestesias distales",
    "Síndrome del túnel carpiano bilateral",
    "Pérdida de peso involuntaria",
    "Macroglosia",
    "Proteinuria conocida",
    "Diarrea o saciedad precoz",
]

RED_FLAG_OPTIONS: list[str] = [
    "Dolor torácico en reposo",
    "Disnea en reposo o ortopnea",
    "Síncope de esfuerzo",
    "Arritmia sostenida documentada",
    "Deterioro renal rápido",
    "Insuficiencia cardíaca descompensada",
    "Hipotensión sintomática severa",
]

RISK_FACTOR_OPTIONS: list[str] = [
    "Antecedente familiar de amiloidosis",
    "Gammapatía monoclonal conocida",
    "Mieloma múltiple",
    "Enfermedad inflamatoria crónica",
    "Hipertrofia ventricular no explicada",
    "NT-proBNP elevado",
    "Troponina persistentemente elevada",
    "Edad mayor de 65 años",
]

SEX_OPTIONS: list[tuple[str, str]] = [
    ("Femenino", "female"),
    ("Masculino", "male"),
    ("No especificado", "unspecified"),
]

_SYMPTOM_WEIGHTS: dict[str, int] = {
    "Disnea de esfuerzo": 8,
    "Edema periférico": 7,
    "Fatiga persistente": 4,
    "Palpitaciones": 5,
    "Síncope o presíncope": 9,
    "Hipotensión ortostática": 8,
    "Parestesias distales": 6,
    "Síndrome del túnel carpiano bilateral": 9,
    "Pérdida de peso involuntaria": 6,
    "Macroglosia": 10,
    "Proteinuria conocida": 9,
    "Diarrea o saciedad precoz": 5,
}

_RED_FLAG_WEIGHTS: dict[str, int] = {
    "Dolor torácico en reposo": 16,
    "Disnea en reposo o ortopnea": 18,
    "Síncope de esfuerzo": 20,
    "Arritmia sostenida documentada": 18,
    "Deterioro renal rápido": 16,
    "Insuficiencia cardíaca descompensada": 22,
    "Hipotensión sintomática severa": 18,
}

_RISK_FACTOR_WEIGHTS: dict[str, int] = {
    "Antecedente familiar de amiloidosis": 12,
    "Gammapatía monoclonal conocida": 14,
    "Mieloma múltiple": 15,
    "Enfermedad inflamatoria crónica": 8,
    "Hipertrofia ventricular no explicada": 13,
    "NT-proBNP elevado": 11,
    "Troponina persistentemente elevada": 11,
    "Edad mayor de 65 años": 6,
}

_HEURISTIC_KEYWORDS: dict[str, int] = {
    "amiloid": 14,
    "hipertrofia": 10,
    "insuficiencia cardíaca": 10,
    "insuficiencia cardiaca": 10,
    "proteinuria": 9,
    "nefrótico": 9,
    "neuropatía": 8,
    "neuropatia": 8,
    "túnel carpiano": 8,
    "tunel carpiano": 8,
    "monoclonal": 10,
    "cadenas ligeras": 11,
    "ttr": 9,
    "transtiretina": 12,
    "biopsia": 6,
    "realce tardío": 8,
    "strain": 6,
    "edema": 5,
    "disnea": 5,
    "síncope": 8,
    "sincope": 8,
}


class ScoreBreakdown(TypedDict):
    label: str
    detail: str
    score: float
    weight: float


class AnalysisResult(TypedDict):
    risk_level: str
    risk_label: str
    risk_score: float
    expert_score: float
    heuristic_score: float
    confidence: float
    diagnosis_label: str
    evidence: list[str]
    recommendations: list[str]
    breakdown: list[ScoreBreakdown]
    data_completeness: float
    local_narrative: str


def _clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def _expert_score(
    age: int | None,
    symptoms: list[str],
    red_flags: list[str],
    risk_factors: list[str],
) -> tuple[float, list[str]]:
    evidence: list[str] = []
    score = 0.0
    for item in symptoms:
        weight = _SYMPTOM_WEIGHTS.get(item, 4)
        score += weight
        evidence.append(f"Síntoma: {item} (+{weight})")
    for item in red_flags:
        weight = _RED_FLAG_WEIGHTS.get(item, 15)
        score += weight
        evidence.append(f"Red flag: {item} (+{weight})")
    for item in risk_factors:
        weight = _RISK_FACTOR_WEIGHTS.get(item, 8)
        score += weight
        evidence.append(f"Factor de riesgo: {item} (+{weight})")
    if age is not None:
        if age >= 75:
            score += 10
            evidence.append("Edad ≥ 75 años (+10)")
        elif age >= 65:
            score += 6
            evidence.append("Edad ≥ 65 años (+6)")
        elif age < 40:
            score -= 4
            evidence.append("Edad < 40 años (-4)")
    if len(symptoms) >= 4:
        score += 6
        evidence.append("Patrón multisistémico: 4 o más síntomas (+6)")
    if red_flags and len(symptoms) >= 2:
        score += 5
        evidence.append("Red flag con síntomas asociados (+5)")
    return _clamp(score), evidence


def _heuristic_score(
    chief_complaint: str,
    summary: str,
    symptoms: list[str],
    red_flags: list[str],
) -> tuple[float, list[str]]:
    text = f"{chief_complaint} {summary}".lower()
    evidence: list[str] = []
    score = 0.0
    for keyword, weight in _HEURISTIC_KEYWORDS.items():
        if keyword in text:
            score += weight
            evidence.append(f"Texto clínico menciona «{keyword}» (+{weight})")
    density = len(symptoms) * 5 + len(red_flags) * 9
    score += density
    if density:
        evidence.append(f"Densidad de hallazgos estructurados (+{density:.0f})")
    words = len([w for w in text.split() if w])
    if words < 12:
        score -= 6
        evidence.append("Relato clínico breve, señal poco informativa (-6)")
    return _clamp(score), evidence


def _completeness(
    age: int | None,
    sex: str,
    chief_complaint: str,
    summary: str,
    symptoms: list[str],
    red_flags: list[str],
    risk_factors: list[str],
) -> float:
    filled = 0
    total = 7
    filled += 1 if age is not None else 0
    filled += 1 if sex else 0
    filled += 1 if chief_complaint.strip() else 0
    filled += 1 if len(summary.strip()) >= 30 else 0
    filled += 1 if symptoms else 0
    filled += 1 if red_flags or risk_factors else 0
    filled += 1 if len(symptoms) >= 3 else 0
    return round(filled / total * 100, 1)


def _level(score: float) -> tuple[str, str]:
    if score >= 66:
        return "high", "Riesgo alto"
    if score >= 36:
        return "moderate", "Riesgo moderado"
    return "low", "Riesgo bajo"


def _diagnosis_label(level: str, symptoms: list[str]) -> str:
    cardiac = {
        "Disnea de esfuerzo",
        "Edema periférico",
        "Palpitaciones",
        "Síncope o presíncope",
    }
    renal = {"Proteinuria conocida"}
    neuro = {
        "Parestesias distales",
        "Síndrome del túnel carpiano bilateral",
        "Hipotensión ortostática",
    }
    pattern = []
    if cardiac.intersection(symptoms):
        pattern.append("cardíaco")
    if renal.intersection(symptoms):
        pattern.append("renal")
    if neuro.intersection(symptoms):
        pattern.append("neurológico")
    domain = " y ".join(pattern) if pattern else "inespecífico"
    if level == "high":
        return (
            f"Sospecha alta de compromiso {domain} compatible con amiloidosis"
        )
    if level == "moderate":
        return f"Sospecha intermedia con patrón {domain}"
    return f"Baja probabilidad actual, patrón {domain}"


def _recommendations(
    level: str, red_flags: list[str], risk_factors: list[str]
) -> list[str]:
    items: list[str] = []
    if level == "high":
        items.append(
            "Priorizar valoración especializada en las próximas 24-72 horas."
        )
        items.append(
            "Solicitar NT-proBNP, troponina, función renal y proteinuria de 24 h."
        )
        items.append(
            "Considerar ecocardiograma con strain y estudio de cadenas ligeras."
        )
    elif level == "moderate":
        items.append("Programar reevaluación clínica dirigida en 2-4 semanas.")
        items.append(
            "Completar laboratorio básico y electrocardiograma comparativo."
        )
    else:
        items.append(
            "Seguimiento clínico habitual con vigilancia de nuevos síntomas."
        )
    if red_flags:
        items.append(
            "Documentar y reevaluar las señales de alerta activas antes del alta."
        )
    if "Gammapatía monoclonal conocida" in risk_factors or (
        "Mieloma múltiple" in risk_factors
    ):
        items.append(
            "Coordinar con hematología por antecedente de discrasia de células plasmáticas."
        )
    if "Antecedente familiar de amiloidosis" in risk_factors:
        items.append(
            "Valorar estudio genético de transtiretina y consejo familiar."
        )
    items.append(
        "El resultado es orientativo y no sustituye el juicio clínico."
    )
    return items


def _local_narrative(
    age: int | None,
    sex: str,
    level_label: str,
    score: float,
    symptoms: list[str],
    red_flags: list[str],
) -> str:
    sex_text = {
        "female": "paciente femenina",
        "male": "paciente masculino",
    }.get(sex, "paciente")
    age_text = f" de {age} años" if age is not None else ""
    symptom_text = (
        ", ".join(symptoms[:4]).lower()
        if symptoms
        else "sin síntomas estructurados"
    )
    flag_text = (
        f" Presenta señales de alerta: {', '.join(red_flags).lower()}."
        if red_flags
        else " No se registraron señales de alerta."
    )
    return (
        f"{sex_text.capitalize()}{age_text} con {symptom_text}."
        f"{flag_text} El algoritmo experto y la heurística textual sitúan el caso "
        f"en {level_label.lower()} con una puntuación combinada de {score:.0f}/100."
    )


def analyze_case(
    age: int | None,
    sex: str,
    chief_complaint: str,
    summary: str,
    symptoms: list[str],
    red_flags: list[str],
    risk_factors: list[str],
) -> AnalysisResult:
    expert, expert_evidence = _expert_score(
        age, symptoms, red_flags, risk_factors
    )
    heuristic, heuristic_evidence = _heuristic_score(
        chief_complaint, summary, symptoms, red_flags
    )
    combined = _clamp(expert * 0.65 + heuristic * 0.35)
    level, level_label = _level(combined)
    completeness = _completeness(
        age, sex, chief_complaint, summary, symptoms, red_flags, risk_factors
    )
    confidence = round(
        _clamp(
            35
            + completeness * 0.35
            + min(len(symptoms), 6) * 3
            + min(len(red_flags), 3) * 2,
            0,
            95,
        ),
        1,
    )
    breakdown: list[ScoreBreakdown] = [
        {
            "label": "Algoritmo experto",
            "detail": "Reglas clínicas ponderadas sobre síntomas, red flags y factores de riesgo.",
            "score": round(expert, 1),
            "weight": 65.0,
        },
        {
            "label": "Heurística textual",
            "detail": "Análisis de palabras clave y densidad de hallazgos en el relato clínico.",
            "score": round(heuristic, 1),
            "weight": 35.0,
        },
    ]
    return {
        "risk_level": level,
        "risk_label": level_label,
        "risk_score": round(combined, 1),
        "expert_score": round(expert, 1),
        "heuristic_score": round(heuristic, 1),
        "confidence": confidence,
        "diagnosis_label": _diagnosis_label(level, symptoms),
        "evidence": expert_evidence + heuristic_evidence,
        "recommendations": _recommendations(level, red_flags, risk_factors),
        "breakdown": breakdown,
        "data_completeness": completeness,
        "local_narrative": _local_narrative(
            age, sex, level_label, combined, symptoms, red_flags
        ),
    }
