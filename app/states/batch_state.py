import hashlib
import logging
from datetime import datetime, timezone
from typing import TypedDict

import reflex as rx

from app.models import (
    ClinicalCase,
    ClinicalImport,
    ClinicalImportRecord,
    DiagnosticResult,
    ProcessingExecution,
)
from app.services.batch_ingest import parse_clinical_file
from app.services.clinical_engine import analyze_case

BATCH_UPLOAD_ID = "clinical_batch_upload"


class BatchRecordView(TypedDict):
    record_number: int
    reference: str
    patient_reference: str
    age_display: str
    sex_display: str
    chief_complaint: str
    diagnosis_label: str
    risk_level: str
    risk_label: str
    risk_score: float
    confidence: float
    symptom_count: int
    red_flag_count: int
    status: str
    error: str
    case_id: int


class BatchState(rx.State):
    # Carga
    upload_progress: int = 0
    is_uploading: bool = False
    staged_filename: str = ""
    staged_format: str = ""
    staged_size_kb: float = 0.0
    upload_error: str = ""

    # Procesamiento
    is_processing: bool = False
    stage: str = ""
    processed_count: int = 0
    error_count: int = 0
    total_count: int = 0
    warnings: list[str] = []
    import_id: int = 0
    import_status: str = "idle"
    records: list[BatchRecordView] = []
    selected_record: int = 0
    risk_filter: str = "all"

    @rx.var
    def has_staged_file(self) -> bool:
        return self.staged_filename != ""

    @rx.var
    def has_records(self) -> bool:
        return len(self.records) > 0

    @rx.var
    def progress_percent(self) -> float:
        if self.total_count == 0:
            return 0.0
        return round(
            (self.processed_count + self.error_count) / self.total_count * 100,
            1,
        )

    @rx.var
    def high_risk_count(self) -> int:
        return len([r for r in self.records if r["risk_level"] == "high"])

    @rx.var
    def filtered_records(self) -> list[BatchRecordView]:
        if self.risk_filter == "all":
            return self.records
        if self.risk_filter == "error":
            return [r for r in self.records if r["status"] == "error"]
        return [r for r in self.records if r["risk_level"] == self.risk_filter]

    @rx.var
    def selected_record_view(self) -> BatchRecordView:
        for record in self.records:
            if record["record_number"] == self.selected_record:
                return record
        if self.records:
            return self.records[0]
        return {
            "record_number": 0,
            "reference": "",
            "patient_reference": "",
            "age_display": "—",
            "sex_display": "—",
            "chief_complaint": "",
            "diagnosis_label": "",
            "risk_level": "undetermined",
            "risk_label": "No calculado",
            "risk_score": 0.0,
            "confidence": 0.0,
            "symptom_count": 0,
            "red_flag_count": 0,
            "status": "pending",
            "error": "",
            "case_id": 0,
        }

    @rx.event
    def set_risk_filter(self, value: str):
        self.risk_filter = value

    @rx.event
    def select_record(self, record_number: int):
        self.selected_record = record_number

    @rx.event
    def handle_upload_progress(self, progress: dict[str, float]):
        self.is_uploading = True
        self.upload_progress = round(float(progress["progress"]) * 100)
        if self.upload_progress >= 100:
            self.is_uploading = False

    @rx.event
    def cancel_upload(self):
        self.is_uploading = False
        self.upload_progress = 0
        return rx.cancel_upload(BATCH_UPLOAD_ID)

    @rx.event
    def clear_batch(self):
        self.staged_filename = ""
        self.staged_format = ""
        self.staged_size_kb = 0.0
        self.upload_error = ""
        self.upload_progress = 0
        self.records = []
        self.warnings = []
        self.processed_count = 0
        self.error_count = 0
        self.total_count = 0
        self.import_id = 0
        self.import_status = "idle"
        self.stage = ""
        self.selected_record = 0
        self.risk_filter = "all"

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        if not files:
            self.upload_error = "No se recibió ningún archivo."
            return
        file = files[0]
        data = await file.read()
        upload_dir = rx.get_upload_dir()
        upload_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        stored_name = f"{stamp}_{file.name}"
        (upload_dir / stored_name).write_bytes(data)

        self.records = []
        self.warnings = []
        self.processed_count = 0
        self.error_count = 0
        self.total_count = 0
        self.import_id = 0
        self.selected_record = 0
        self.upload_error = ""
        self.staged_filename = stored_name
        self.staged_size_kb = round(len(data) / 1024, 1)
        lower = file.name.lower()
        if lower.endswith(".pdf"):
            self.staged_format = "pdf"
        elif lower.endswith(".csv") or lower.endswith(".txt"):
            self.staged_format = "csv"
        else:
            self.staged_format = "unknown"
            self.upload_error = (
                "Formato no soportado. Carga un archivo CSV o PDF clínico."
            )
        self.import_status = "received"
        self.is_uploading = False
        self.upload_progress = 100

    @rx.event
    async def process_batch(self):
        if not self.staged_filename:
            self.upload_error = "Carga primero un archivo CSV o PDF."
            return
        self.upload_error = ""
        self.is_processing = True
        self.import_status = "processing"
        self.stage = "Leyendo y normalizando el archivo..."
        self.records = []
        self.processed_count = 0
        self.error_count = 0
        self.total_count = 0
        filename = self.staged_filename
        yield

        path = rx.get_upload_dir() / filename
        try:
            data = path.read_bytes()
        except OSError as exc:
            logging.exception(f"Error: {exc}")
            self.is_processing = False
            self.import_status = "failed"
            self.upload_error = f"No se pudo leer el archivo cargado: {exc}"
            self.stage = ""
            return

        source_format, parsed, warnings = parse_clinical_file(filename, data)
        self.warnings = warnings
        self.total_count = len(parsed)
        checksum = hashlib.sha256(data).hexdigest()
        if not parsed:
            self.is_processing = False
            self.import_status = "failed"
            self.stage = ""
            self.upload_error = (
                "No se pudo extraer ningún registro clínico del archivo."
            )
            return

        self.stage = f"Evaluando {len(parsed)} registros con el motor local..."
        yield

        now = datetime.now(timezone.utc)
        views: list[BatchRecordView] = []
        async with rx.asession() as session:
            clinical_import = ClinicalImport(
                source_format=source_format,
                original_filename=filename,
                storage_key=str(path),
                checksum=checksum,
                status="processing",
                row_count=len(parsed),
                import_metadata={
                    "warnings": warnings,
                    "engine": "amylo_ai-rules-v1",
                },
                received_at=now,
            )
            session.add(clinical_import)
            await session.flush()
            import_id = clinical_import.id

            execution = ProcessingExecution(
                import_id=import_id,
                execution_type="batch",
                status="running",
                trigger_source="batch_ui",
                model_name="local-rules",
                model_version="v1",
                input_count=len(parsed),
                parameters={"expert_weight": 65, "heuristic_weight": 35},
                started_at=now,
            )
            session.add(execution)
            await session.flush()

            processed = 0
            errors = 0
            for record in parsed:
                if record["error"]:
                    errors += 1
                    session.add(
                        ClinicalImportRecord(
                            import_id=import_id,
                            record_number=record["record_number"],
                            status="error",
                            raw_payload={"text": record["raw_text"]},
                            normalized_payload={},
                            error_message=record["error"],
                        )
                    )
                    views.append(
                        {
                            "record_number": record["record_number"],
                            "reference": record["reference"],
                            "patient_reference": record["patient_reference"],
                            "age_display": "—",
                            "sex_display": "—",
                            "chief_complaint": record["chief_complaint"],
                            "diagnosis_label": "",
                            "risk_level": "undetermined",
                            "risk_label": "No calculado",
                            "risk_score": 0.0,
                            "confidence": 0.0,
                            "symptom_count": 0,
                            "red_flag_count": 0,
                            "status": "error",
                            "error": record["error"],
                            "case_id": 0,
                        }
                    )
                    continue

                result = analyze_case(
                    record["age"],
                    record["sex"],
                    record["chief_complaint"],
                    record["summary"],
                    record["symptoms"],
                    record["red_flags"],
                    record["risk_factors"],
                )
                case = ClinicalCase(
                    external_case_id=record["reference"][:128] or None,
                    status="analyzed",
                    source_type=source_format,
                    patient_reference=record["patient_reference"][:256] or None,
                    patient_age=record["age"],
                    patient_sex=record["sex"] or None,
                    chief_complaint=record["chief_complaint"],
                    clinical_summary=record["summary"],
                    symptoms=record["symptoms"],
                    red_flags=record["red_flags"],
                    risk_factors=record["risk_factors"],
                    case_metadata={
                        "data_completeness": result["data_completeness"],
                        "import_id": import_id,
                        "engine": "amylo_ai-rules-v1",
                    },
                )
                session.add(case)
                await session.flush()
                session.add(
                    ClinicalImportRecord(
                        import_id=import_id,
                        case_id=case.id,
                        record_number=record["record_number"],
                        status="processed",
                        raw_payload={"text": record["raw_text"]},
                        normalized_payload={
                            "reference": record["reference"],
                            "risk_level": result["risk_level"],
                            "risk_score": result["risk_score"],
                        },
                    )
                )
                session.add(
                    DiagnosticResult(
                        case_id=case.id,
                        execution_id=execution.id,
                        result_status="final",
                        risk_level=result["risk_level"],
                        risk_score=result["risk_score"],
                        confidence_score=result["confidence"],
                        diagnosis_label=result["diagnosis_label"][:256],
                        clinical_narrative=result["local_narrative"],
                        explanation="\n".join(result["evidence"]),
                        red_flags=record["red_flags"],
                        recommendations=result["recommendations"],
                        result_payload={
                            "expert_score": result["expert_score"],
                            "heuristic_score": result["heuristic_score"],
                            "source": source_format,
                        },
                        generated_at=now,
                    )
                )
                processed += 1
                views.append(
                    {
                        "record_number": record["record_number"],
                        "reference": record["reference"],
                        "patient_reference": record["patient_reference"],
                        "age_display": str(record["age"])
                        if record["age"] is not None
                        else "—",
                        "sex_display": {
                            "female": "Femenino",
                            "male": "Masculino",
                        }.get(record["sex"], "No especificado"),
                        "chief_complaint": record["chief_complaint"],
                        "diagnosis_label": result["diagnosis_label"],
                        "risk_level": result["risk_level"],
                        "risk_label": result["risk_label"],
                        "risk_score": result["risk_score"],
                        "confidence": result["confidence"],
                        "symptom_count": len(record["symptoms"]),
                        "red_flag_count": len(record["red_flags"]),
                        "status": "processed",
                        "error": "",
                        "case_id": case.id,
                    }
                )

            clinical_import.status = (
                "completed" if errors == 0 else "completed_with_errors"
            )
            clinical_import.processed_row_count = processed
            clinical_import.error_row_count = errors
            clinical_import.completed_at = datetime.now(timezone.utc)
            execution.status = "completed"
            execution.output_count = processed
            execution.finished_at = datetime.now(timezone.utc)
            execution.metrics = {
                "processed": processed,
                "errors": errors,
                "rows": len(parsed),
            }
            await session.commit()

        self.records = views
        self.processed_count = processed
        self.error_count = errors
        self.import_id = import_id
        self.import_status = (
            "completed" if errors == 0 else "completed_with_errors"
        )
        self.selected_record = views[0]["record_number"] if views else 0
        self.is_processing = False
        self.stage = ""
        yield rx.toast(
            f"Importación #{import_id}: {processed} procesados, {errors} con error",
            duration=5000,
            close_button=True,
        )
