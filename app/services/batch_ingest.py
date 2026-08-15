"""Procesamiento local real de archivos clínicos CSV y PDF.

- CSV: se interpreta con el módulo estándar `csv`, tolerando distintos
  nombres de columna y separadores de listas (`;`, `|`, `,`).
- PDF: se extrae texto con `pypdf` y cada bloque de caso se normaliza
  detectando campos etiquetados y coincidencias con los catálogos clínicos.

No se usa ningún servicio externo en esta capa.
"""

import csv
import io
import logging
import re
from typing import TypedDict

from pypdf import PdfReader

from app.services.clinical_engine import (
    RED_FLAG_OPTIONS,
    RISK_FACTOR_OPTIONS,
    SYMPTOM_OPTIONS,
)

_LIST_SEPARATORS = re.compile(r"[;|]|,\s")

_REFERENCE_KEYS = ("case_id", "case_reference", "referencia", "caso", "id")
_PATIENT_KEYS = ("patient", "patient_reference", "paciente", "expediente")
_AGE_KEYS = ("age", "edad", "años", "anos")
_SEX_KEYS = ("sex", "sexo", "genero", "género")
_COMPLAINT_KEYS = ("chief_complaint", "motivo", "motivo_consulta", "queja")
_SUMMARY_KEYS = ("summary", "resumen", "clinical_summary", "nota", "historia")
_SYMPTOM_KEYS = ("symptoms", "sintomas", "síntomas", "hallazgos")
_RED_FLAG_KEYS = ("red_flags", "red flags", "alertas", "banderas")
_RISK_KEYS = ("risk_factors", "factores", "antecedentes", "riesgo")

_SEX_MAP = {
    "f": "female",
    "femenino": "female",
    "female": "female",
    "mujer": "female",
    "m": "male",
    "masculino": "male",
    "male": "male",
    "hombre": "male",
}


class ParsedRecord(TypedDict):
    record_number: int
    reference: str
    patient_reference: str
    age: int | None
    sex: str
    chief_complaint: str
    summary: str
    symptoms: list[str]
    red_flags: list[str]
    risk_factors: list[str]
    error: str
    raw_text: str


def _norm_key(key: str) -> str:
    return key.strip().lower().replace("-", "_").replace(" ", "_")


def _pick(row: dict[str, str], keys: tuple[str, ...]) -> str:
    for raw_key, value in row.items():
        if raw_key is None:
            continue
        norm = _norm_key(raw_key)
        for key in keys:
            if norm == _norm_key(key):
                return str(value or "").strip()
    for raw_key, value in row.items():
        if raw_key is None:
            continue
        norm = _norm_key(raw_key)
        for key in keys:
            if _norm_key(key) in norm:
                return str(value or "").strip()
    return ""


def _split_list(value: str) -> list[str]:
    if not value:
        return []
    parts = [p.strip() for p in _LIST_SEPARATORS.split(value)]
    return [p for p in parts if p]


def _match_catalog(items: list[str], catalog: list[str]) -> list[str]:
    matched: list[str] = []
    for item in items:
        low = item.lower()
        best = ""
        for option in catalog:
            if option.lower() == low:
                best = option
                break
            if low and (low in option.lower() or option.lower() in low):
                best = option
        if best and best not in matched:
            matched.append(best)
    return matched


def _detect_in_text(text: str, catalog: list[str]) -> list[str]:
    low = text.lower()
    found: list[str] = []
    for option in catalog:
        tokens = [t for t in option.lower().split() if len(t) > 4]
        if option.lower() in low or (
            tokens and all(t in low for t in tokens[:2])
        ):
            found.append(option)
    return found


def _parse_age(value: str) -> int | None:
    digits = re.findall(r"\d+", value or "")
    if not digits:
        return None
    age = int(digits[0])
    if 0 < age < 120:
        return age
    return None


def _parse_sex(value: str) -> str:
    key = (value or "").strip().lower()
    return _SEX_MAP.get(key, "unspecified" if key else "")


def parse_csv(data: bytes) -> tuple[list[ParsedRecord], list[str]]:
    warnings: list[str] = []
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        logging.exception("Unexpected error")
        text = data.decode("latin-1", errors="replace")
        warnings.append(
            "El archivo no estaba en UTF-8; se interpretó como latin-1."
        )
    sample = text[:4096]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
        delimiter = dialect.delimiter
    except csv.Error:
        logging.exception("Unexpected error")
        delimiter = ","
        warnings.append(
            "No se detectó el delimitador; se asumió coma como separador."
        )
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    records: list[ParsedRecord] = []
    for index, row in enumerate(reader, start=1):
        clean_row = {k: (v or "") for k, v in row.items() if k is not None}
        complaint = _pick(clean_row, _COMPLAINT_KEYS)
        summary = _pick(clean_row, _SUMMARY_KEYS)
        symptoms = _match_catalog(
            _split_list(_pick(clean_row, _SYMPTOM_KEYS)), SYMPTOM_OPTIONS
        )
        red_flags = _match_catalog(
            _split_list(_pick(clean_row, _RED_FLAG_KEYS)), RED_FLAG_OPTIONS
        )
        risk_factors = _match_catalog(
            _split_list(_pick(clean_row, _RISK_KEYS)), RISK_FACTOR_OPTIONS
        )
        blob = " ".join(str(v) for v in clean_row.values())
        if not symptoms:
            symptoms = _detect_in_text(blob, SYMPTOM_OPTIONS)
        if not red_flags:
            red_flags = _detect_in_text(blob, RED_FLAG_OPTIONS)
        if not risk_factors:
            risk_factors = _detect_in_text(blob, RISK_FACTOR_OPTIONS)
        error = ""
        if not complaint and not summary and not symptoms:
            error = "Registro sin motivo de consulta, resumen ni síntomas reconocibles."
        records.append(
            {
                "record_number": index,
                "reference": _pick(clean_row, _REFERENCE_KEYS)
                or f"CSV-{index:03d}",
                "patient_reference": _pick(clean_row, _PATIENT_KEYS),
                "age": _parse_age(_pick(clean_row, _AGE_KEYS)),
                "sex": _parse_sex(_pick(clean_row, _SEX_KEYS)),
                "chief_complaint": complaint,
                "summary": summary or blob[:2000],
                "symptoms": symptoms,
                "red_flags": red_flags,
                "risk_factors": risk_factors,
                "error": error,
                "raw_text": blob[:4000],
            }
        )
    if not records:
        warnings.append("El CSV no contenía filas de datos.")
    return records, warnings


def _labeled(text: str, labels: tuple[str, ...]) -> str:
    for label in labels:
        match = re.search(rf"{label}\s*[:\-]\s*(.+)", text, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return ""


def parse_pdf(data: bytes) -> tuple[list[ParsedRecord], list[str]]:
    warnings: list[str] = []
    try:
        reader = PdfReader(io.BytesIO(data))
        pages = [(page.extract_text() or "").strip() for page in reader.pages]
    except Exception as exc:
        logging.exception(f"Error: {exc}")
        return [], [f"No se pudo leer el PDF: {exc}"]

    blocks: list[str] = []
    for page_text in pages:
        if not page_text:
            continue
        chunks = re.split(r"\n(?=Caso\s|CASO\s|Paciente\s)", page_text)
        blocks.extend([c.strip() for c in chunks if c.strip()])
    if not blocks:
        warnings.append(
            "El PDF no contiene texto extraíble (posible documento escaneado)."
        )
        return [], warnings

    records: list[ParsedRecord] = []
    for index, block in enumerate(blocks, start=1):
        complaint = _labeled(block, ("motivo de consulta", "motivo", "queja"))
        summary = _labeled(block, ("resumen clínico", "resumen", "nota"))
        if not summary:
            summary = block[:2000]
        symptoms = _match_catalog(
            _split_list(_labeled(block, ("síntomas", "sintomas"))),
            SYMPTOM_OPTIONS,
        ) or _detect_in_text(block, SYMPTOM_OPTIONS)
        red_flags = _match_catalog(
            _split_list(_labeled(block, ("red flags", "alertas"))),
            RED_FLAG_OPTIONS,
        ) or _detect_in_text(block, RED_FLAG_OPTIONS)
        risk_factors = _match_catalog(
            _split_list(
                _labeled(block, ("factores de riesgo", "antecedentes"))
            ),
            RISK_FACTOR_OPTIONS,
        ) or _detect_in_text(block, RISK_FACTOR_OPTIONS)
        if not complaint:
            first_line = block.splitlines()[0].strip()
            complaint = first_line[:200]
        error = ""
        if not symptoms and not red_flags and len(block) < 40:
            error = "Bloque de texto insuficiente para evaluación clínica."
        records.append(
            {
                "record_number": index,
                "reference": _labeled(block, ("caso", "referencia"))
                or f"PDF-{index:03d}",
                "patient_reference": _labeled(
                    block, ("paciente", "expediente")
                ),
                "age": _parse_age(_labeled(block, ("edad",))),
                "sex": _parse_sex(_labeled(block, ("sexo",))),
                "chief_complaint": complaint,
                "summary": summary,
                "symptoms": symptoms,
                "red_flags": red_flags,
                "risk_factors": risk_factors,
                "error": error,
                "raw_text": block[:4000],
            }
        )
    return records, warnings


def parse_clinical_file(
    filename: str, data: bytes
) -> tuple[str, list[ParsedRecord], list[str]]:
    lower = filename.lower()
    if lower.endswith(".pdf"):
        records, warnings = parse_pdf(data)
        return "pdf", records, warnings
    if lower.endswith(".csv") or lower.endswith(".txt"):
        records, warnings = parse_csv(data)
        return "csv", records, warnings
    return (
        "unknown",
        [],
        [f"Formato no soportado para «{filename}». Usa CSV o PDF."],
    )
