from typing import TypedDict

import reflex as rx


class GuideSection(TypedDict):
    id: str
    label: str
    icon: str
    caption: str


class GuideItem(TypedDict):
    icon: str
    title: str
    body: str


GUIDE_SECTIONS: list[GuideSection] = [
    {
        "id": "use",
        "label": "Uso clínico",
        "icon": "stethoscope",
        "caption": "Cómo integrar AmylAI en la consulta",
    },
    {
        "id": "flags",
        "label": "Señales de alerta",
        "icon": "circle-alert",
        "caption": "Red flags que cambian la conducta",
    },
    {
        "id": "interpretation",
        "label": "Interpretación",
        "icon": "scan-search",
        "caption": "Leer puntuación, nivel y confianza",
    },
    {
        "id": "limits",
        "label": "Límites",
        "icon": "shield-alert",
        "caption": "Qué no hace el sistema",
    },
    {
        "id": "traceability",
        "label": "Trazabilidad",
        "icon": "history",
        "caption": "Registro, evidencia y auditoría",
    },
]

_CONTENT: dict[str, list[GuideItem]] = {
    "use": [
        {
            "icon": "clipboard-list",
            "title": "1. Captura estructurada",
            "body": "Registra edad, sexo, motivo de consulta y resumen clínico antes de marcar hallazgos. El motor pondera texto y selección estructurada, por lo que un relato pobre reduce la confianza del resultado.",
        },
        {
            "icon": "list-checks",
            "title": "2. Marca los hallazgos reales",
            "body": "Selecciona solo síntomas, red flags y factores de riesgo verificados en la evaluación. Marcar hallazgos dudosos desplaza el nivel de riesgo sin sustento clínico.",
        },
        {
            "icon": "scan-search",
            "title": "3. Revisa el resultado completo",
            "body": "Lee la puntuación junto al desglose, la evidencia y las recomendaciones. El nivel de riesgo por sí solo no es una conclusión clínica.",
        },
        {
            "icon": "layers-3",
            "title": "4. Usa lotes para cohortes",
            "body": "Para revisiones retrospectivas o cribados, carga CSV o PDF en el módulo de lotes: cada registro se normaliza y se evalúa con el mismo motor local.",
        },
    ],
    "flags": [
        {
            "icon": "heart-pulse",
            "title": "Compromiso cardíaco agudo",
            "body": "Disnea en reposo u ortopnea, insuficiencia cardíaca descompensada y arritmia sostenida documentada elevan la puntuación de forma inmediata y priorizan valoración urgente.",
        },
        {
            "icon": "activity",
            "title": "Inestabilidad hemodinámica",
            "body": "Síncope de esfuerzo e hipotensión sintomática severa sugieren disfunción autonómica o restrictiva avanzada; documenta la maniobra y la respuesta antes del alta.",
        },
        {
            "icon": "droplets",
            "title": "Deterioro renal rápido",
            "body": "Una caída acelerada de la función renal con proteinuria orienta a compromiso multisistémico y obliga a completar estudio de cadenas ligeras.",
        },
        {
            "icon": "triangle-alert",
            "title": "Regla práctica",
            "body": "Una red flag activa nunca se compensa con una puntuación baja: revisa el caso manualmente antes de cerrar el expediente.",
        },
    ],
    "interpretation": [
        {
            "icon": "gauge",
            "title": "Puntuación combinada",
            "body": "El resultado mezcla el algoritmo experto (65%) y la heurística textual (35%). Bajo <36, moderado 36-65 y alto ≥66 sobre 100.",
        },
        {
            "icon": "brain",
            "title": "Confianza y completitud",
            "body": "La confianza depende de cuántos campos clínicos están completos. Un riesgo alto con confianza baja significa «falta información», no «caso descartable».",
        },
        {
            "icon": "sparkles",
            "title": "Capa de lenguaje",
            "body": "La narrativa asistida solo redacta e integra el caso; no modifica la puntuación. Si el modelo falla, el resultado local sigue siendo válido y se muestra el error.",
        },
        {
            "icon": "list-checks",
            "title": "Evidencia línea por línea",
            "body": "Cada hallazgo suma o resta puntos de forma visible. Si un punto de la evidencia no coincide con la clínica, corrige la captura y vuelve a analizar.",
        },
    ],
    "limits": [
        {
            "icon": "ban",
            "title": "No es un diagnóstico",
            "body": "AmylAI produce una lectura orientativa de sospecha. No confirma amiloidosis ni sustituye biopsia, imagen o estudio hematológico.",
        },
        {
            "icon": "pill",
            "title": "No indica tratamiento",
            "body": "El sistema no propone fármacos ni dosis. Las recomendaciones son pasos de estudio y seguimiento.",
        },
        {
            "icon": "file-warning",
            "title": "Depende de la calidad del dato",
            "body": "PDF escaneados sin texto extraíble o CSV con columnas incompletas generan registros con error explícito; nunca se rellenan con valores inventados.",
        },
        {
            "icon": "users",
            "title": "Población y validación",
            "body": "Los umbrales provienen de reglas expertas, no de una cohorte prospectiva. Valida el comportamiento en tu población con el módulo de estrés antes de usarlo como apoyo rutinario.",
        },
    ],
    "traceability": [
        {
            "icon": "database",
            "title": "Todo queda registrado",
            "body": "Cada caso guardado crea el expediente, su metadato clínico, la ejecución del motor y el resultado diagnóstico con evidencia y recomendaciones.",
        },
        {
            "icon": "file-search",
            "title": "Importaciones auditables",
            "body": "Cada archivo cargado guarda nombre, formato, checksum, filas totales, procesadas y con error, con estado final de la importación.",
        },
        {
            "icon": "git-compare",
            "title": "Reproducibilidad",
            "body": "Se almacenan modelo, versión, pesos y métricas de cada ejecución, de modo que un resultado antiguo puede explicarse tal como se generó.",
        },
        {
            "icon": "shield-check",
            "title": "Entorno protegido",
            "body": "El motor de reglas y la ingesta funcionan de forma local; solo la narrativa opcional usa un modelo externo y su estado se muestra siempre en el expediente.",
        },
    ],
}


class GuideState(rx.State):
    section: str = "use"
    sections: list[GuideSection] = GUIDE_SECTIONS

    @rx.event
    def select_section(self, section_id: str):
        self.section = section_id

    @rx.var
    def section_label(self) -> str:
        for item in self.sections:
            if item["id"] == self.section:
                return item["label"]
        return ""

    @rx.var
    def section_caption(self) -> str:
        for item in self.sections:
            if item["id"] == self.section:
                return item["caption"]
        return ""

    @rx.var
    def items(self) -> list[GuideItem]:
        return _CONTENT.get(self.section, [])
