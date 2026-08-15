import reflex as rx

from app.components.clinical_shell import clinical_shell
from app.components.clinical_ui import (
    panel,
    panel_heading,
    risk_pill,
    select_field,
    stat_tile,
    status_pill,
)
from app.states.database_state import (
    CaseRow,
    DatabaseState,
    ImportRow,
    ResultRow,
)


def _risk_label(level: rx.Var) -> rx.Var:
    return rx.match(
        level,
        ("high", "Riesgo alto"),
        ("moderate", "Riesgo moderado"),
        ("low", "Riesgo bajo"),
        "No calculado",
    )


def filters_panel() -> rx.Component:
    return panel(
        panel_heading(
            "filter",
            "Consulta clínica",
            "Filtra el expediente por texto, nivel de riesgo, origen y estado.",
            rx.cond(DatabaseState.is_loading, "Cargando...", "Actualizado"),
        ),
        rx.el.div(
            rx.el.label(
                rx.el.span(
                    "Búsqueda",
                    class_name="mb-2 block text-xs font-semibold text-[#526761]",
                ),
                rx.el.div(
                    rx.el.input(
                        placeholder="Referencia, paciente, motivo o resumen...",
                        default_value=DatabaseState.search_text,
                        on_change=DatabaseState.set_search_text.debounce(400),
                        class_name="w-full rounded-xl border border-[#cedbd0] bg-[#fbfaf6] py-2.5 pl-9 pr-3.5 text-sm text-[#173f46] outline-hidden placeholder:text-[#a1aaa4] focus:border-[#3d9678] focus:ring-2 focus:ring-[#dcefe0]",
                    ),
                    rx.icon(
                        "search",
                        class_name="pointer-events-none absolute left-3 top-3 h-4 w-4 text-[#8a9791]",
                    ),
                    class_name="relative",
                ),
                class_name="block",
            ),
            select_field(
                "Riesgo",
                DatabaseState.risk_filter,
                DatabaseState.risk_options,
                DatabaseState.set_risk_filter,
            ),
            select_field(
                "Origen",
                DatabaseState.source_filter,
                DatabaseState.source_options,
                DatabaseState.set_source_filter,
            ),
            select_field(
                "Estado",
                DatabaseState.status_filter,
                DatabaseState.status_options,
                DatabaseState.set_status_filter,
            ),
            class_name="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4",
        ),
        rx.el.div(
            rx.el.button(
                rx.icon("rotate-ccw", class_name="h-4 w-4"),
                "Limpiar filtros",
                type="button",
                on_click=DatabaseState.clear_filters,
                class_name="flex items-center gap-2 rounded-xl border border-[#c8d7cb] bg-[#fbfaf6] px-4 py-2.5 text-sm font-semibold text-[#174e50] hover:bg-[#eef4ed]",
            ),
            rx.el.button(
                rx.icon("refresh-cw", class_name="h-4 w-4"),
                "Actualizar",
                type="button",
                on_click=DatabaseState.load_data,
                class_name="flex items-center gap-2 rounded-xl bg-[#174e50] px-4 py-2.5 text-sm font-semibold text-[#fbfaf6] hover:bg-[#123f41]",
            ),
            class_name="mt-5 flex flex-wrap gap-3",
        ),
    )


def kpi_row() -> rx.Component:
    return rx.el.div(
        stat_tile(
            "Casos en vista",
            DatabaseState.total_cases.to_string(),
            "mt-2 text-3xl font-semibold text-[#174e50]",
        ),
        stat_tile(
            "Con resultado",
            DatabaseState.total_results.to_string(),
            "mt-2 text-3xl font-semibold text-[#2d7a68]",
        ),
        stat_tile(
            "Riesgo alto",
            DatabaseState.high_risk_cases.to_string(),
            "mt-2 text-3xl font-semibold text-[#9b5545]",
        ),
        stat_tile(
            "Importaciones",
            DatabaseState.total_imports.to_string(),
            "mt-2 text-3xl font-semibold text-[#41616a]",
        ),
        class_name="grid grid-cols-2 gap-4 md:grid-cols-4",
    )


def _th(label: str) -> rx.Component:
    return rx.el.th(
        label,
        class_name="px-4 py-3 text-left text-[11px] font-semibold uppercase tracking-[0.12em] text-[#8a9791]",
    )


def case_row(item: CaseRow) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            rx.el.p(
                item["reference"],
                class_name="text-sm font-semibold text-[#174e50]",
            ),
            rx.el.p(
                item["diagnosis_label"],
                class_name="mt-0.5 line-clamp-1 max-w-[20rem] text-xs text-[#8a9791]",
            ),
            class_name="px-4 py-3",
        ),
        rx.el.td(
            item["patient_reference"],
            class_name="px-4 py-3 text-sm text-[#66756f]",
        ),
        rx.el.td(
            item["age_display"], class_name="px-4 py-3 text-sm text-[#66756f]"
        ),
        rx.el.td(
            risk_pill(item["risk_level"], _risk_label(item["risk_level"])),
            class_name="px-4 py-3",
        ),
        rx.el.td(
            f"{item['risk_score']:.0f}",
            class_name="px-4 py-3 text-sm font-semibold text-[#174e50]",
        ),
        rx.el.td(
            item["source_type"], class_name="px-4 py-3 text-sm text-[#66756f]"
        ),
        rx.el.td(status_pill(item["status"]), class_name="px-4 py-3"),
        rx.el.td(
            item["created_at"], class_name="px-4 py-3 text-sm text-[#8a9791]"
        ),
        on_click=lambda: DatabaseState.load_case(item["id"]),
        class_name=rx.cond(
            DatabaseState.selected_case_id == item["id"],
            "cursor-pointer border-b border-[#eef1ec] bg-[#eef5ee]",
            "cursor-pointer border-b border-[#eef1ec] hover:bg-[#f6faf5]",
        ),
    )


def cases_panel() -> rx.Component:
    return panel(
        panel_heading(
            "database",
            "Casos clínicos",
            "Expedientes persistidos con su resultado diagnóstico más reciente.",
            f"{DatabaseState.cases.length()} listados",
        ),
        rx.cond(
            DatabaseState.has_cases,
            rx.el.div(
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            _th("Caso"),
                            _th("Paciente"),
                            _th("Edad"),
                            _th("Riesgo"),
                            _th("Score"),
                            _th("Origen"),
                            _th("Estado"),
                            _th("Creado"),
                            class_name="border-b border-[#dce4dc] bg-[#f3f6f1]",
                        )
                    ),
                    rx.el.tbody(rx.foreach(DatabaseState.cases, case_row)),
                    class_name="table-auto w-full",
                ),
                class_name="overflow-x-auto rounded-xl border border-[#dce4dc]",
            ),
            rx.el.div(
                rx.icon("inbox", class_name="h-6 w-6 text-[#8a9791]"),
                rx.el.p(
                    "Sin casos para estos filtros",
                    class_name="mt-3 text-sm font-semibold text-[#36544e]",
                ),
                rx.el.p(
                    "Ajusta la búsqueda o carga un lote clínico para poblar la base.",
                    class_name="mt-1 text-sm leading-6 text-[#71807a]",
                ),
                class_name="flex min-h-40 flex-col items-center justify-center rounded-xl border border-dashed border-[#cddbcf] bg-[#f6faf5] p-6 text-center",
            ),
        ),
    )


def import_row(item: ImportRow) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.p(
                f"#{item['id']} · {item['filename']}",
                class_name="truncate text-sm font-semibold text-[#174e50]",
            ),
            status_pill(item["status"]),
            class_name="flex items-center justify-between gap-3",
        ),
        rx.el.p(
            f"{item['source_format'].upper()} · {item['processed_row_count']}/{item['row_count']} procesados · {item['error_row_count']} con error",
            class_name="mt-1 text-xs text-[#77837d]",
        ),
        rx.el.p(item["received_at"], class_name="mt-1 text-xs text-[#9aa39c]"),
        class_name="border-b border-[#eef1ec] py-3 last:border-b-0",
    )


def imports_panel() -> rx.Component:
    return panel(
        panel_heading(
            "layers-3",
            "Importaciones",
            "Trazabilidad de archivos recibidos y su estado de procesamiento.",
            DatabaseState.total_imports.to_string(),
        ),
        rx.cond(
            DatabaseState.imports.length() > 0,
            rx.el.div(rx.foreach(DatabaseState.imports, import_row)),
            rx.el.p(
                "Todavía no se han registrado importaciones.",
                class_name="text-sm leading-6 text-[#71807a]",
            ),
        ),
    )


def result_row(item: ResultRow) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.p(
                item["reference"],
                class_name="truncate text-sm font-semibold text-[#174e50]",
            ),
            risk_pill(item["risk_level"], _risk_label(item["risk_level"])),
            class_name="flex items-center justify-between gap-3",
        ),
        rx.el.p(
            item["diagnosis_label"],
            class_name="mt-1 line-clamp-2 text-xs leading-5 text-[#77837d]",
        ),
        rx.el.p(
            f"{item['risk_score']:.0f}/100 · confianza {item['confidence']:.0f}% · {item['generated_at']}",
            class_name="mt-1 text-xs text-[#9aa39c]",
        ),
        on_click=lambda: DatabaseState.load_case(item["case_id"]),
        class_name="cursor-pointer border-b border-[#eef1ec] py-3 last:border-b-0 hover:bg-[#f6faf5]",
    )


def results_panel() -> rx.Component:
    return panel(
        panel_heading(
            "scan-search",
            "Resultados diagnósticos",
            "Últimos resultados generados por el motor clínico.",
            DatabaseState.results.length().to_string(),
        ),
        rx.cond(
            DatabaseState.results.length() > 0,
            rx.el.div(rx.foreach(DatabaseState.results, result_row)),
            rx.el.p(
                "No hay resultados para los filtros activos.",
                class_name="text-sm leading-6 text-[#71807a]",
            ),
        ),
    )


def _chip_list(title: str, items: rx.Var, chip_class: str) -> rx.Component:
    return rx.el.div(
        rx.el.p(
            title,
            class_name="text-[11px] font-semibold uppercase tracking-[0.12em] text-[#8a9791]",
        ),
        rx.cond(
            items.length() > 0,
            rx.el.div(
                rx.foreach(
                    items, lambda item: rx.el.span(item, class_name=chip_class)
                ),
                class_name="mt-2 flex flex-wrap gap-2",
            ),
            rx.el.p("Sin registros", class_name="mt-2 text-xs text-[#9aa39c]"),
        ),
        class_name="mt-4",
    )


def detail_panel() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("file-search", class_name="h-4 w-4 text-[#174e50]"),
            rx.el.p(
                "Detalle del expediente",
                class_name="text-sm font-semibold text-[#36544e]",
            ),
            class_name="flex items-center gap-2",
        ),
        rx.cond(
            DatabaseState.has_detail,
            rx.el.div(
                rx.el.div(
                    rx.el.p(
                        DatabaseState.detail["reference"],
                        class_name="text-lg font-semibold text-[#173f46]",
                    ),
                    risk_pill(
                        DatabaseState.detail["risk_level"],
                        DatabaseState.detail["risk_label"],
                    ),
                    class_name="mt-4 flex items-center justify-between gap-3",
                ),
                rx.el.p(
                    DatabaseState.detail["diagnosis_label"],
                    class_name="mt-1 text-sm leading-6 text-[#66756f]",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.p(
                            "Paciente", class_name="text-xs text-[#71807a]"
                        ),
                        rx.el.p(
                            DatabaseState.detail["patient_reference"],
                            class_name="text-sm font-semibold text-[#174e50]",
                        ),
                    ),
                    rx.el.div(
                        rx.el.p("Edad", class_name="text-xs text-[#71807a]"),
                        rx.el.p(
                            DatabaseState.detail["age_display"],
                            class_name="text-sm font-semibold text-[#174e50]",
                        ),
                    ),
                    rx.el.div(
                        rx.el.p("Sexo", class_name="text-xs text-[#71807a]"),
                        rx.el.p(
                            DatabaseState.detail["sex_display"],
                            class_name="text-sm font-semibold text-[#174e50]",
                        ),
                    ),
                    rx.el.div(
                        rx.el.p("Origen", class_name="text-xs text-[#71807a]"),
                        rx.el.p(
                            DatabaseState.detail["source_type"],
                            class_name="text-sm font-semibold text-[#174e50]",
                        ),
                    ),
                    rx.el.div(
                        rx.el.p(
                            "Puntuación", class_name="text-xs text-[#71807a]"
                        ),
                        rx.el.p(
                            f"{DatabaseState.detail['risk_score']:.0f}/100",
                            class_name="text-sm font-semibold text-[#936518]",
                        ),
                    ),
                    rx.el.div(
                        rx.el.p(
                            "Confianza", class_name="text-xs text-[#71807a]"
                        ),
                        rx.el.p(
                            f"{DatabaseState.detail['confidence']:.0f}%",
                            class_name="text-sm font-semibold text-[#2d7a68]",
                        ),
                    ),
                    class_name="mt-5 grid grid-cols-2 gap-4 border-t border-[#e5e9e3] pt-4 sm:grid-cols-3",
                ),
                rx.el.div(
                    rx.el.p(
                        "Motivo de consulta",
                        class_name="text-[11px] font-semibold uppercase tracking-[0.12em] text-[#8a9791]",
                    ),
                    rx.el.p(
                        DatabaseState.detail["chief_complaint"],
                        class_name="mt-1 text-sm leading-6 text-[#66756f]",
                    ),
                    rx.el.p(
                        "Resumen clínico",
                        class_name="mt-4 text-[11px] font-semibold uppercase tracking-[0.12em] text-[#8a9791]",
                    ),
                    rx.el.p(
                        DatabaseState.detail["clinical_summary"],
                        class_name="mt-1 max-h-40 overflow-auto text-sm leading-6 text-[#66756f]",
                    ),
                    class_name="mt-5 border-l-2 border-[#dfe9df] pl-3",
                ),
                _chip_list(
                    "Síntomas",
                    DatabaseState.detail["symptoms"],
                    "w-fit rounded-full border border-[#d5ded6] bg-[#fbfaf6] px-3 py-1 text-xs font-medium text-[#66756f]",
                ),
                _chip_list(
                    "Red flags",
                    DatabaseState.detail["red_flags"],
                    "w-fit rounded-full border border-[#ecd5cd] bg-[#fdf3ef] px-3 py-1 text-xs font-medium text-[#9b5545]",
                ),
                _chip_list(
                    "Factores de riesgo",
                    DatabaseState.detail["risk_factors"],
                    "w-fit rounded-full border border-[#eadbb8] bg-[#fbf6e9] px-3 py-1 text-xs font-medium text-[#936518]",
                ),
                rx.el.div(
                    rx.el.p(
                        "Narrativa registrada",
                        class_name="text-[11px] font-semibold uppercase tracking-[0.12em] text-[#8a9791]",
                    ),
                    rx.el.p(
                        DatabaseState.detail["narrative"],
                        class_name="mt-1 text-sm leading-6 text-[#66756f]",
                    ),
                    class_name="mt-5 rounded-xl border border-[#d8e4d9] bg-[#edf5ed] p-4",
                ),
                rx.cond(
                    DatabaseState.detail["recommendations"].length() > 0,
                    rx.el.div(
                        rx.el.p(
                            "Recomendaciones",
                            class_name="text-[11px] font-semibold uppercase tracking-[0.12em] text-[#936518]",
                        ),
                        rx.el.ul(
                            rx.foreach(
                                DatabaseState.detail["recommendations"],
                                lambda item: rx.el.li(
                                    item,
                                    class_name="mt-1.5 text-sm leading-6 text-[#66756f]",
                                ),
                            ),
                            class_name="mt-2 list-disc pl-5",
                        ),
                        class_name="mt-4 rounded-xl border border-[#eadbb8] bg-[#fbf6e9] p-4",
                    ),
                    rx.fragment(),
                ),
                rx.el.div(
                    rx.el.p(
                        "Evidencia del cálculo",
                        class_name="text-[11px] font-semibold uppercase tracking-[0.12em] text-[#8a9791]",
                    ),
                    rx.el.p(
                        DatabaseState.detail["explanation"],
                        class_name="mt-1 max-h-48 overflow-auto whitespace-pre-line text-xs leading-5 text-[#77837d]",
                    ),
                    class_name="mt-4 rounded-xl border border-[#dce4dc] bg-[#fbfaf6] p-4",
                ),
            ),
            rx.el.div(
                rx.el.p(
                    "Selecciona un caso de la tabla para revisar su expediente completo.",
                    class_name="mt-4 text-sm leading-6 text-[#71807a]",
                ),
                rx.el.a(
                    "Cargar un lote clínico",
                    rx.icon("arrow-up-right", class_name="h-4 w-4"),
                    href="/batches",
                    class_name="mt-4 flex w-fit items-center gap-1 text-sm font-semibold text-[#2d7a68]",
                ),
            ),
        ),
        class_name="rounded-2xl border border-[#dce4dc] bg-[#fbfaf6] p-5 sm:p-6",
    )


def database_page() -> rx.Component:
    return clinical_shell(
        "Base de datos clínica",
        "04 · Trazabilidad",
        rx.el.div(
            filters_panel(),
            kpi_row(),
            rx.el.div(
                rx.el.div(
                    cases_panel(),
                    rx.el.div(
                        results_panel(),
                        imports_panel(),
                        class_name="grid grid-cols-1 gap-5 md:grid-cols-2",
                    ),
                    class_name="flex min-w-0 flex-col gap-5",
                ),
                rx.el.div(detail_panel(), class_name="min-w-0"),
                class_name="grid grid-cols-1 gap-5 xl:grid-cols-[minmax(0,1.35fr)_minmax(22rem,0.65fr)]",
            ),
            class_name="flex w-full flex-col gap-5",
        ),
    )
