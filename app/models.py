import reflex as rx
from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    ForeignKey,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


ClinicalJsonValue = str | int | float | bool | list[str] | None
ClinicalJson = dict[str, ClinicalJsonValue]


class ClinicalCase(Base):
    __tablename__ = "clinical_case"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    external_case_id: Mapped[str | None] = mapped_column(
        String(128), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(
        String(32), default="draft", nullable=False, index=True
    )
    source_type: Mapped[str] = mapped_column(
        String(32), default="manual", nullable=False
    )
    patient_reference: Mapped[str | None] = mapped_column(
        String(256), nullable=True
    )
    patient_age: Mapped[int | None] = mapped_column(nullable=True)
    patient_sex: Mapped[str | None] = mapped_column(String(32), nullable=True)
    chief_complaint: Mapped[str] = mapped_column(
        Text, default="", nullable=False
    )
    clinical_summary: Mapped[str] = mapped_column(
        Text, default="", nullable=False
    )
    symptoms: Mapped[list[str]] = mapped_column(
        JSON, default=list, nullable=False
    )
    red_flags: Mapped[list[str]] = mapped_column(
        JSON, default=list, nullable=False
    )
    risk_factors: Mapped[list[str]] = mapped_column(
        JSON, default=list, nullable=False
    )
    case_metadata: Mapped[ClinicalJson] = mapped_column(
        JSON, default=dict, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utc_now,
        onupdate=_utc_now,
        nullable=False,
    )

    clinical_metadata: Mapped["ClinicalMetadata | None"] = relationship(
        back_populates="case",
        uselist=False,
        cascade="all, delete-orphan",
    )
    imports: Mapped[list["ClinicalImport"]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
    )
    import_records: Mapped[list["ClinicalImportRecord"]] = relationship(
        back_populates="case",
    )
    executions: Mapped[list["ProcessingExecution"]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
    )
    diagnostic_results: Mapped[list["DiagnosticResult"]] = relationship(
        back_populates="case",
        cascade="all, delete-orphan",
    )


class ClinicalMetadata(Base):
    __tablename__ = "clinical_metadata"
    __table_args__ = (
        UniqueConstraint("case_id", name="uq_clinical_metadata_case_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(
        ForeignKey("clinical_case.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    encounter_reference: Mapped[str | None] = mapped_column(
        String(128), nullable=True
    )
    encounter_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    provider_reference: Mapped[str | None] = mapped_column(
        String(256), nullable=True
    )
    department: Mapped[str | None] = mapped_column(String(128), nullable=True)
    language: Mapped[str | None] = mapped_column(String(32), nullable=True)
    pregnancy_status: Mapped[str | None] = mapped_column(
        String(32), nullable=True
    )
    smoking_status: Mapped[str | None] = mapped_column(
        String(32), nullable=True
    )
    alcohol_use: Mapped[str | None] = mapped_column(String(32), nullable=True)
    vital_signs: Mapped[ClinicalJson] = mapped_column(
        JSON, default=dict, nullable=False
    )
    allergies: Mapped[list[str]] = mapped_column(
        JSON, default=list, nullable=False
    )
    current_medications: Mapped[list[str]] = mapped_column(
        JSON, default=list, nullable=False
    )
    medical_history: Mapped[list[str]] = mapped_column(
        JSON, default=list, nullable=False
    )
    surgical_history: Mapped[list[str]] = mapped_column(
        JSON, default=list, nullable=False
    )
    family_history: Mapped[list[str]] = mapped_column(
        JSON, default=list, nullable=False
    )
    social_history: Mapped[list[str]] = mapped_column(
        JSON, default=list, nullable=False
    )
    additional_metadata: Mapped[ClinicalJson] = mapped_column(
        JSON, default=dict, nullable=False
    )
    notes: Mapped[str] = mapped_column(Text, default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utc_now,
        onupdate=_utc_now,
        nullable=False,
    )

    case: Mapped[ClinicalCase] = relationship(
        back_populates="clinical_metadata"
    )


class ClinicalImport(Base):
    __tablename__ = "clinical_import"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_id: Mapped[int | None] = mapped_column(
        ForeignKey("clinical_case.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    source_format: Mapped[str] = mapped_column(
        String(16), default="csv", nullable=False
    )
    original_filename: Mapped[str] = mapped_column(
        String(512), default="", nullable=False
    )
    storage_key: Mapped[str] = mapped_column(
        String(1024), default="", nullable=False
    )
    checksum: Mapped[str | None] = mapped_column(
        String(128), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(
        String(32), default="received", nullable=False, index=True
    )
    row_count: Mapped[int] = mapped_column(default=0, nullable=False)
    processed_row_count: Mapped[int] = mapped_column(default=0, nullable=False)
    error_row_count: Mapped[int] = mapped_column(default=0, nullable=False)
    error_message: Mapped[str] = mapped_column(Text, default="", nullable=False)
    import_metadata: Mapped[ClinicalJson] = mapped_column(
        JSON, default=dict, nullable=False
    )
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utc_now,
        onupdate=_utc_now,
        nullable=False,
    )

    case: Mapped["ClinicalCase | None"] = relationship(back_populates="imports")
    records: Mapped[list["ClinicalImportRecord"]] = relationship(
        back_populates="clinical_import",
        cascade="all, delete-orphan",
    )
    executions: Mapped[list["ProcessingExecution"]] = relationship(
        back_populates="clinical_import",
    )


class ClinicalImportRecord(Base):
    __tablename__ = "clinical_import_record"
    __table_args__ = (
        UniqueConstraint(
            "import_id",
            "record_number",
            name="uq_clinical_import_record_number",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    import_id: Mapped[int] = mapped_column(
        ForeignKey("clinical_import.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    case_id: Mapped[int | None] = mapped_column(
        ForeignKey("clinical_case.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    record_number: Mapped[int] = mapped_column(default=0, nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), default="pending", nullable=False, index=True
    )
    raw_payload: Mapped[ClinicalJson] = mapped_column(
        JSON, default=dict, nullable=False
    )
    normalized_payload: Mapped[ClinicalJson] = mapped_column(
        JSON, default=dict, nullable=False
    )
    error_message: Mapped[str] = mapped_column(Text, default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utc_now,
        onupdate=_utc_now,
        nullable=False,
    )

    clinical_import: Mapped[ClinicalImport] = relationship(
        back_populates="records"
    )
    case: Mapped["ClinicalCase | None"] = relationship(
        back_populates="import_records"
    )


class ProcessingExecution(Base):
    __tablename__ = "processing_execution"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_id: Mapped[int | None] = mapped_column(
        ForeignKey("clinical_case.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    import_id: Mapped[int | None] = mapped_column(
        ForeignKey("clinical_import.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    execution_type: Mapped[str] = mapped_column(
        String(32), default="diagnostic", nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(32), default="queued", nullable=False, index=True
    )
    trigger_source: Mapped[str] = mapped_column(
        String(32), default="system", nullable=False
    )
    model_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    input_count: Mapped[int] = mapped_column(default=0, nullable=False)
    output_count: Mapped[int] = mapped_column(default=0, nullable=False)
    error_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    error_message: Mapped[str] = mapped_column(Text, default="", nullable=False)
    parameters: Mapped[ClinicalJson] = mapped_column(
        JSON, default=dict, nullable=False
    )
    metrics: Mapped[ClinicalJson] = mapped_column(
        JSON, default=dict, nullable=False
    )
    queued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, nullable=False
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utc_now,
        onupdate=_utc_now,
        nullable=False,
    )

    case: Mapped["ClinicalCase | None"] = relationship(
        back_populates="executions"
    )
    clinical_import: Mapped["ClinicalImport | None"] = relationship(
        back_populates="executions"
    )
    diagnostic_results: Mapped[list["DiagnosticResult"]] = relationship(
        back_populates="execution",
    )


class DiagnosticResult(Base):
    __tablename__ = "diagnostic_result"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    case_id: Mapped[int] = mapped_column(
        ForeignKey("clinical_case.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    execution_id: Mapped[int | None] = mapped_column(
        ForeignKey("processing_execution.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    result_status: Mapped[str] = mapped_column(
        String(32), default="pending", nullable=False, index=True
    )
    risk_level: Mapped[str] = mapped_column(
        String(32), default="undetermined", nullable=False, index=True
    )
    risk_score: Mapped[float | None] = mapped_column(nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(nullable=True)
    diagnosis_code: Mapped[str | None] = mapped_column(
        String(64), nullable=True
    )
    diagnosis_label: Mapped[str] = mapped_column(
        String(256), default="", nullable=False
    )
    clinical_narrative: Mapped[str] = mapped_column(
        Text, default="", nullable=False
    )
    explanation: Mapped[str] = mapped_column(Text, default="", nullable=False)
    red_flags: Mapped[list[str]] = mapped_column(
        JSON, default=list, nullable=False
    )
    recommendations: Mapped[list[str]] = mapped_column(
        JSON, default=list, nullable=False
    )
    result_payload: Mapped[ClinicalJson] = mapped_column(
        JSON, default=dict, nullable=False
    )
    generated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utc_now,
        onupdate=_utc_now,
        nullable=False,
    )

    case: Mapped[ClinicalCase] = relationship(
        back_populates="diagnostic_results"
    )
    execution: Mapped["ProcessingExecution | None"] = relationship(
        back_populates="diagnostic_results"
    )


__all__ = [
    "Base",
    "ClinicalCase",
    "ClinicalImport",
    "ClinicalImportRecord",
    "ClinicalMetadata",
    "DiagnosticResult",
    "ProcessingExecution",
]
