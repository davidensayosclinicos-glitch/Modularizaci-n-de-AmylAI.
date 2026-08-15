from typing import TypedDict

import reflex as rx
from sqlalchemy import text


class CaseRow(TypedDict):
    id: int
    reference: str
    patient_reference: str
    status: str
    source_type: str
    age_display: str
    risk_level: str
    risk_score: float
    diagnosis_label: str
    created_at: str


class ImportRow(TypedDict):
    id: int
    filename: str
    source_format: str
    status: str
    row_count: int
    processed_row_count: int
    error_row_count: int
    received_at: str


class ResultRow(TypedDict):
    id: int
    case_id: int
    reference: str
    risk_level: str
    risk_score: float
    confidence: float
    diagnosis_label: str
    generated_at: str


class CaseDetail(TypedDict):
    id: int
    reference: str
    patient_reference: str
    status: str
    source_type: str
    age_display: str
    sex_display: str
    chief_complaint: str
    clinical_summary: str
    symptoms: list[str]
    red_flags: list[str]
    risk_factors: list[str]
    risk_level: str
    risk_label: str
    risk_score: float
    confidence: float
    diagnosis_label: str
    narrative: str
    explanation: str
    recommendations: list[str]
    created_at: str


_EMPTY_DETAIL: CaseDetail = {
    "id": 0,
    "reference": "",
    "patient_reference": "",
    "status": "",
    "source_type": "",
    "age_display": "—",
    "sex_display": "—",
    "chief_complaint": "",
    "clinical_summary": "",
    "symptoms": [],
    "red_flags": [],
    "risk_factors": [],
    "risk_level": "undetermined",
    "risk_label": "No calculado",
    "risk_score": 0.0,
    "confidence": 0.0,
    "diagnosis_label": "",
    "narrative": "",
    "explanation": "",
    "recommendations": [],
    "created_at": "",
}

_RISK_LABELS: dict[str, str] = {
    "high": "Riesgo alto",
    "moderate": "Riesgo moderado",
    "low": "Riesgo bajo",
}

_SEX_LABELS: dict[str, str] = {
    "female": "Femenino",
    "male": "Masculino",
    "unspecified": "No especificado",
}


def _fmt_dt(value) -> str:
    if value is None:
        return "—"
    return value.strftime("%Y-%m-%d %H:%M")


class DatabaseState(rx.State):
    search_text: str = ""
    risk_filter: str = "all"
    source_filter: str = "all"
    status_filter: str = "all"

    is_loading: bool = False
    total_cases: int = 0
    total_results: int = 0
    total_imports: int = 0
    high_risk_cases: int = 0

    cases: list[CaseRow] = []
    imports: list[ImportRow] = []
    results: list[ResultRow] = []
    detail: CaseDetail = _EMPTY_DETAIL
    selected_case_id: int = 0

    risk_options: list[tuple[str, str]] = [
        ("Todos los riesgos", "all"),
        ("Riesgo alto", "high"),
        ("Riesgo moderado", "moderate"),
        ("Riesgo bajo", "low"),
    ]
    source_options: list[tuple[str, str]] = [
        ("Todos los orígenes", "all"),
        ("Manual", "manual"),
        ("CSV", "csv"),
        ("PDF", "pdf"),
    ]
    status_options: list[tuple[str, str]] = [
        ("Todos los estados", "all"),
        ("Analizado", "analyzed"),
        ("Borrador", "draft"),
    ]

    @rx.var
    def has_cases(self) -> bool:
        return len(self.cases) > 0

    @rx.var
    def has_detail(self) -> bool:
        return self.detail["id"] > 0

    @rx.event
    def set_search_text(self, value: str):
        self.search_text = value
        return DatabaseState.load_data

    @rx.event
    def set_risk_filter(self, value: str):
        self.risk_filter = value
        return DatabaseState.load_data

    @rx.event
    def set_source_filter(self, value: str):
        self.source_filter = value
        return DatabaseState.load_data

    @rx.event
    def set_status_filter(self, value: str):
        self.status_filter = value
        return DatabaseState.load_data

    @rx.event
    def clear_filters(self):
        self.search_text = ""
        self.risk_filter = "all"
        self.source_filter = "all"
        self.status_filter = "all"
        return DatabaseState.load_data

    def _where(self) -> tuple[str, dict[str, str]]:
        where = "WHERE 1=1"
        params: dict[str, str] = {}
        if self.search_text.strip():
            where += (
                " AND (LOWER(COALESCE(c.external_case_id, '')) LIKE :q"
                " OR LOWER(COALESCE(c.patient_reference, '')) LIKE :q"
                " OR LOWER(c.chief_complaint) LIKE :q"
                " OR LOWER(c.clinical_summary) LIKE :q)"
            )
            params["q"] = f"%{self.search_text.strip().lower()}%"
        if self.risk_filter != "all":
            where += " AND COALESCE(d.risk_level, 'undetermined') = :risk"
            params["risk"] = self.risk_filter
        if self.source_filter != "all":
            where += " AND c.source_type = :source"
            params["source"] = self.source_filter
        if self.status_filter != "all":
            where += " AND c.status = :status"
            params["status"] = self.status_filter
        return where, params

    @rx.event(background=True)
    async def load_data(self):
        async with self:
            self.is_loading = True
            where, params = self._where()

        base_join = """
            FROM clinical_case c
            LEFT JOIN diagnostic_result d
                ON d.id = (
                    SELECT MAX(d2.id) FROM diagnostic_result d2
                    WHERE d2.case_id = c.id
                )
        """

        async with rx.asession() as session:
            kpi = (
                await session.execute(
                    text(
                        f"""
                        SELECT
                            COUNT(*),
                            SUM(CASE WHEN d.id IS NOT NULL THEN 1 ELSE 0 END),
                            SUM(CASE WHEN d.risk_level = 'high' THEN 1 ELSE 0 END)
                        {base_join}
                        {where}
                        """
                    ),
                    params,
                )
            ).first()
            case_rows = (
                await session.execute(
                    text(
                        f"""
                        SELECT
                            c.id,
                            COALESCE(c.external_case_id, ''),
                            COALESCE(c.patient_reference, ''),
                            c.status,
                            c.source_type,
                            c.patient_age,
                            COALESCE(d.risk_level, 'undetermined'),
                            COALESCE(d.risk_score, 0),
                            COALESCE(d.diagnosis_label, ''),
                            c.created_at
                        {base_join}
                        {where}
                        ORDER BY c.created_at DESC, c.id DESC
                        LIMIT 100
                        """
                    ),
                    params,
                )
            ).all()
            result_rows = (
                await session.execute(
                    text(
                        f"""
                        SELECT
                            d.id,
                            c.id,
                            COALESCE(c.external_case_id, ''),
                            d.risk_level,
                            COALESCE(d.risk_score, 0),
                            COALESCE(d.confidence_score, 0),
                            COALESCE(d.diagnosis_label, ''),
                            d.generated_at
                        {base_join}
                        {where}
                          AND d.id IS NOT NULL
                        ORDER BY d.id DESC
                        LIMIT 50
                        """
                    ),
                    params,
                )
            ).all()
            import_rows = (
                await session.execute(
                    text(
                        """
                        SELECT id, original_filename, source_format, status,
                               row_count, processed_row_count, error_row_count,
                               received_at
                        FROM clinical_import
                        ORDER BY id DESC
                        LIMIT 25
                        """
                    )
                )
            ).all()
            import_total = (
                await session.execute(
                    text("SELECT COUNT(*) FROM clinical_import")
                )
            ).first()

        async with self:
            self.total_cases = int(kpi[0]) if kpi else 0
            self.total_results = int(kpi[1] or 0) if kpi else 0
            self.high_risk_cases = int(kpi[2] or 0) if kpi else 0
            self.total_imports = int(import_total[0]) if import_total else 0
            self.cases = [
                {
                    "id": int(r[0]),
                    "reference": str(r[1]) or f"Caso #{int(r[0])}",
                    "patient_reference": str(r[2]) or "—",
                    "status": str(r[3]),
                    "source_type": str(r[4]),
                    "age_display": str(int(r[5])) if r[5] is not None else "—",
                    "risk_level": str(r[6]),
                    "risk_score": float(r[7]),
                    "diagnosis_label": str(r[8]) or "Sin resultado registrado",
                    "created_at": _fmt_dt(r[9]),
                }
                for r in case_rows
            ]
            self.results = [
                {
                    "id": int(r[0]),
                    "case_id": int(r[1]),
                    "reference": str(r[2]) or f"Caso #{int(r[1])}",
                    "risk_level": str(r[3]),
                    "risk_score": float(r[4]),
                    "confidence": float(r[5]),
                    "diagnosis_label": str(r[6]),
                    "generated_at": _fmt_dt(r[7]),
                }
                for r in result_rows
            ]
            self.imports = [
                {
                    "id": int(r[0]),
                    "filename": str(r[1]) or "—",
                    "source_format": str(r[2]),
                    "status": str(r[3]),
                    "row_count": int(r[4] or 0),
                    "processed_row_count": int(r[5] or 0),
                    "error_row_count": int(r[6] or 0),
                    "received_at": _fmt_dt(r[7]),
                }
                for r in import_rows
            ]
            self.is_loading = False
            keep = self.selected_case_id

        if keep and any(c["id"] == keep for c in self.cases):
            yield DatabaseState.load_case(keep)
        else:
            async with self:
                self.selected_case_id = 0
                self.detail = _EMPTY_DETAIL

    @rx.event(background=True)
    async def load_case(self, case_id: int):
        async with rx.asession() as session:
            row = (
                await session.execute(
                    text(
                        """
                        SELECT
                            c.id,
                            COALESCE(c.external_case_id, ''),
                            COALESCE(c.patient_reference, ''),
                            c.status,
                            c.source_type,
                            c.patient_age,
                            COALESCE(c.patient_sex, ''),
                            c.chief_complaint,
                            c.clinical_summary,
                            c.created_at,
                            COALESCE(d.risk_level, 'undetermined'),
                            COALESCE(d.risk_score, 0),
                            COALESCE(d.confidence_score, 0),
                            COALESCE(d.diagnosis_label, ''),
                            COALESCE(d.clinical_narrative, ''),
                            COALESCE(d.explanation, '')
                        FROM clinical_case c
                        LEFT JOIN diagnostic_result d
                            ON d.id = (
                                SELECT MAX(d2.id) FROM diagnostic_result d2
                                WHERE d2.case_id = c.id
                            )
                        WHERE c.id = :case_id
                        """
                    ),
                    {"case_id": case_id},
                )
            ).first()
            lists = (
                await session.execute(
                    text(
                        """
                        SELECT c.symptoms, c.red_flags, c.risk_factors,
                               COALESCE(d.recommendations, '[]')
                        FROM clinical_case c
                        LEFT JOIN diagnostic_result d
                            ON d.id = (
                                SELECT MAX(d2.id) FROM diagnostic_result d2
                                WHERE d2.case_id = c.id
                            )
                        WHERE c.id = :case_id
                        """
                    ),
                    {"case_id": case_id},
                )
            ).first()

        if row is None:
            async with self:
                self.detail = _EMPTY_DETAIL
                self.selected_case_id = 0
            return

        def _as_list(value) -> list[str]:
            if isinstance(value, list):
                return [str(v) for v in value]
            return []

        async with self:
            self.selected_case_id = case_id
            self.detail = {
                "id": int(row[0]),
                "reference": str(row[1]) or f"Caso #{int(row[0])}",
                "patient_reference": str(row[2]) or "—",
                "status": str(row[3]),
                "source_type": str(row[4]),
                "age_display": str(int(row[5])) if row[5] is not None else "—",
                "sex_display": _SEX_LABELS.get(row[6], "No especificado"),
                "chief_complaint": str(row[7]) or "—",
                "clinical_summary": str(row[8]) or "—",
                "symptoms": _as_list(lists[0]) if lists else [],
                "red_flags": _as_list(lists[1]) if lists else [],
                "risk_factors": _as_list(lists[2]) if lists else [],
                "risk_level": str(row[10]),
                "risk_label": _RISK_LABELS.get(row[10], "No calculado"),
                "risk_score": float(row[11]),
                "confidence": float(row[12]),
                "diagnosis_label": str(row[13]) or "Sin resultado registrado",
                "narrative": str(row[14]) or "—",
                "explanation": str(row[15]) or "—",
                "recommendations": _as_list(lists[3]) if lists else [],
                "created_at": _fmt_dt(row[9]),
            }
