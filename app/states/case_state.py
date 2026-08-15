import asyncio
import logging
from datetime import datetime, timezone

_logger = logging.getLogger(__name__)

import reflex as rx

from app.models import (
    ClinicalCase,
    ClinicalMetadata,
    DiagnosticResult,
    ProcessingExecution,
)
from app.services.clinical_engine import (
    RED_FLAG_OPTIONS,
    RISK_FACTOR_OPTIONS,
    SEX_OPTIONS,
    SYMPTOM_OPTIONS,
    ScoreBreakdown,
    analyze_case,
)
from app.services.gemini_narrative import (
    GeminiError,
    generate_clinical_narrative,
)


class CaseState(rx.State):
    # Captura clínica
    case_reference: str = ""
    patient_reference: str = ""
    age_input: str = ""
    sex: str = ""
    chief_complaint: str = ""
    clinical_summary: str = ""
    selected_symptoms: list[str] = []
    selected_red_flags: list[str] = []
    selected_risk_factors: list[str] = []

    # Catálogos
    symptom_options: list[str] = SYMPTOM_OPTIONS
    red_flag_options: list[str] = RED_FLAG_OPTIONS
    risk_factor_options: list[str] = RISK_FACTOR_OPTIONS
    sex_options: list[tuple[str, str]] = SEX_OPTIONS

    # Estado del análisis
    is_analyzing: bool = False
    analysis_stage: str = ""
    has_result: bool = False
    validation_error: str = ""

    # Resultado local
    risk_level: str = "undetermined"
    risk_label: str = "No calculado"
    risk_score: float = 0.0
    expert_score: float = 0.0
    heuristic_score: float = 0.0
    confidence: float = 0.0
    data_completeness: float = 0.0
    diagnosis_label: str = ""
    local_narrative: str = ""
    evidence: list[str] = []
    recommendations: list[str] = []
    breakdown: list[ScoreBreakdown] = []

    # Capa LLM
    llm_narrative: str = ""
    llm_considerations: list[str] = []
    llm_differentials: list[str] = []
    llm_model: str = ""
    llm_error: str = ""
    llm_ok: bool = False

    # Persistencia
    is_saving: bool = False
    saved_case_id: int = 0
    save_error: str = ""

    @rx.var
    def analyzed_case_title(self) -> str:
        return self.case_reference or "Caso sin referencia"

    @rx.var
    def risk_score_display(self) -> str:
        if not self.has_result:
            return "—"
        return f"{self.risk_score:.0f}"

    @rx.var
    def confidence_display(self) -> str:
        if not self.has_result:
            return "—"
        return f"{self.confidence:.0f}%"

    @rx.var
    def symptom_count(self) -> int:
        return len(self.selected_symptoms)

    @rx.var
    def red_flag_count(self) -> int:
        return len(self.selected_red_flags)

    @rx.var
    def is_saved(self) -> bool:
        return self.saved_case_id > 0

    @rx.event
    def set_field(self, field: str, value: str):
        if field in {
            "case_reference",
            "patient_reference",
            "age_input",
            "sex",
            "chief_complaint",
            "clinical_summary",
        }:
            setattr(self, field, value)

    @rx.event
    def toggle_symptom(self, item: str):
        if item in self.selected_symptoms:
            self.selected_symptoms.remove(item)
        else:
            self.selected_symptoms.append(item)

    @rx.event
    def toggle_red_flag(self, item: str):
        if item in self.selected_red_flags:
            self.selected_red_flags.remove(item)
        else:
            self.selected_red_flags.append(item)

    @rx.event
    def toggle_risk_factor(self, item: str):
        if item in self.selected_risk_factors:
            self.selected_risk_factors.remove(item)
        else:
            self.selected_risk_factors.append(item)

    @rx.event
    def clear_case(self):
        self.case_reference = ""
        self.patient_reference = ""
        self.age_input = ""
        self.sex = ""
        self.chief_complaint = ""
        self.clinical_summary = ""
        self.selected_symptoms = []
        self.selected_red_flags = []
        self.selected_risk_factors = []
        self._clear_result()
        self.validation_error = ""

    def _clear_result(self):
        self.has_result = False
        self.risk_level = "undetermined"
        self.risk_label = "No calculado"
        self.risk_score = 0.0
        self.expert_score = 0.0
        self.heuristic_score = 0.0
        self.confidence = 0.0
        self.data_completeness = 0.0
        self.diagnosis_label = ""
        self.local_narrative = ""
        self.evidence = []
        self.recommendations = []
        self.breakdown = []
        self.llm_narrative = ""
        self.llm_considerations = []
        self.llm_differentials = []
        self.llm_model = ""
        self.llm_error = ""
        self.llm_ok = False
        self.saved_case_id = 0
        self.save_error = ""

    def _parsed_age(self) -> int | None:
        raw = self.age_input.strip()
        if not raw.isdigit():
            return None
        age = int(raw)
        if 0 < age < 120:
            return age
        return None

    @rx.event
    async def analyze(self):
        if not self.chief_complaint.strip() and not self.selected_symptoms:
            self.validation_error = "Registra el motivo de consulta o al menos un síntoma para analizar."
            return
        self.validation_error = ""
        self._clear_result()
        self.is_analyzing = True
        self.analysis_stage = "Ejecutando reglas clínicas locales..."
        payload = {
            "age": self._parsed_age(),
            "sex": self.sex,
            "chief_complaint": self.chief_complaint,
            "summary": self.clinical_summary,
            "symptoms": list(self.selected_symptoms),
            "red_flags": list(self.selected_red_flags),
            "risk_factors": list(self.selected_risk_factors),
        }
        yield

        result = analyze_case(
            payload["age"],
            payload["sex"],
            payload["chief_complaint"],
            payload["summary"],
            payload["symptoms"],
            payload["red_flags"],
            payload["risk_factors"],
        )

        self.risk_level = result["risk_level"]
        self.risk_label = result["risk_label"]
        self.risk_score = result["risk_score"]
        self.expert_score = result["expert_score"]
        self.heuristic_score = result["heuristic_score"]
        self.confidence = result["confidence"]
        self.data_completeness = result["data_completeness"]
        self.diagnosis_label = result["diagnosis_label"]
        self.local_narrative = result["local_narrative"]
        self.evidence = result["evidence"]
        self.recommendations = result["recommendations"]
        self.breakdown = result["breakdown"]
        self.has_result = True
        self.analysis_stage = "Enriqueciendo narrativa con Gemini..."
        yield

        try:
            narrative = await asyncio.to_thread(
                generate_clinical_narrative,
                payload["age"],
                payload["sex"],
                payload["chief_complaint"],
                payload["summary"],
                payload["symptoms"],
                payload["red_flags"],
                payload["risk_factors"],
                result["risk_label"],
                result["risk_score"],
                result["confidence"],
            )
        except GeminiError as exc:
            logging.exception("Unexpected error")
            _logger.warning(
                "Narrativa Gemini no disponible para este caso: %s", exc
            )
            self.llm_error = str(exc)
            self.llm_ok = False
            self.is_analyzing = False
            self.analysis_stage = ""
            yield rx.redirect("/diagnosis")
            return

        self.llm_narrative = narrative["narrative"]
        self.llm_considerations = narrative["considerations"]
        self.llm_differentials = narrative["differentials"]
        self.llm_model = narrative["model"]
        self.llm_ok = True
        self.llm_error = ""
        self.is_analyzing = False
        self.analysis_stage = ""
        yield rx.redirect("/diagnosis")

    @rx.event
    async def save_case(self):
        if not self.has_result:
            self.save_error = "Analiza el caso antes de guardarlo."
            return
        self.is_saving = True
        self.save_error = ""
        snapshot = {
            "case_reference": self.case_reference.strip(),
            "patient_reference": self.patient_reference.strip(),
            "age": self._parsed_age(),
            "sex": self.sex,
            "chief_complaint": self.chief_complaint.strip(),
            "summary": self.clinical_summary.strip(),
            "symptoms": list(self.selected_symptoms),
            "red_flags": list(self.selected_red_flags),
            "risk_factors": list(self.selected_risk_factors),
            "risk_level": self.risk_level,
            "risk_score": self.risk_score,
            "expert_score": self.expert_score,
            "heuristic_score": self.heuristic_score,
            "confidence": self.confidence,
            "completeness": self.data_completeness,
            "diagnosis_label": self.diagnosis_label,
            "local_narrative": self.local_narrative,
            "llm_narrative": self.llm_narrative,
            "llm_model": self.llm_model,
            "llm_ok": self.llm_ok,
            "llm_error": self.llm_error,
            "recommendations": list(self.recommendations),
            "evidence": list(self.evidence),
            "considerations": list(self.llm_considerations),
            "differentials": list(self.llm_differentials),
        }
        yield

        now = datetime.now(timezone.utc)
        async with rx.asession() as session:
            case = ClinicalCase(
                external_case_id=snapshot["case_reference"] or None,
                status="analyzed",
                source_type="manual",
                patient_reference=snapshot["patient_reference"] or None,
                patient_age=snapshot["age"],
                patient_sex=snapshot["sex"] or None,
                chief_complaint=snapshot["chief_complaint"],
                clinical_summary=snapshot["summary"],
                symptoms=snapshot["symptoms"],
                red_flags=snapshot["red_flags"],
                risk_factors=snapshot["risk_factors"],
                case_metadata={
                    "data_completeness": snapshot["completeness"],
                    "engine": "amylo_ai-rules-v1",
                },
            )
            session.add(case)
            await session.flush()
            session.add(
                ClinicalMetadata(
                    case_id=case.id,
                    encounter_date=now,
                    vital_signs={},
                    allergies=[],
                    current_medications=[],
                    medical_history=snapshot["risk_factors"],
                    surgical_history=[],
                    family_history=[],
                    social_history=[],
                    additional_metadata={"llm_model": snapshot["llm_model"]},
                    notes=snapshot["summary"],
                )
            )
            execution = ProcessingExecution(
                case_id=case.id,
                execution_type="diagnostic",
                status="completed"
                if snapshot["llm_ok"]
                else "completed_with_warnings",
                trigger_source="individual_ui",
                model_name=snapshot["llm_model"] or "local-rules",
                model_version="v1",
                input_count=1,
                output_count=1,
                error_message=snapshot["llm_error"],
                parameters={
                    "expert_weight": 65,
                    "heuristic_weight": 35,
                    "llm_enabled": snapshot["llm_ok"],
                },
                metrics={
                    "expert_score": snapshot["expert_score"],
                    "heuristic_score": snapshot["heuristic_score"],
                    "risk_score": snapshot["risk_score"],
                    "confidence": snapshot["confidence"],
                },
                started_at=now,
                finished_at=now,
            )
            session.add(execution)
            await session.flush()
            session.add(
                DiagnosticResult(
                    case_id=case.id,
                    execution_id=execution.id,
                    result_status="final",
                    risk_level=snapshot["risk_level"],
                    risk_score=snapshot["risk_score"],
                    confidence_score=snapshot["confidence"],
                    diagnosis_label=snapshot["diagnosis_label"][:256],
                    clinical_narrative=snapshot["llm_narrative"]
                    or snapshot["local_narrative"],
                    explanation="\n".join(snapshot["evidence"]),
                    red_flags=snapshot["red_flags"],
                    recommendations=snapshot["recommendations"],
                    result_payload={
                        "local_narrative": snapshot["local_narrative"],
                        "llm_considerations": snapshot["considerations"],
                        "llm_differentials": snapshot["differentials"],
                        "llm_ok": snapshot["llm_ok"],
                    },
                    generated_at=now,
                )
            )
            await session.commit()
            case_id = case.id

        self.saved_case_id = case_id
        self.is_saving = False
        yield rx.toast(
            f"Expediente guardado con ID {case_id}",
            duration=4000,
            close_button=True,
        )
