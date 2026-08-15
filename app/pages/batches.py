import reflex as rx

from app.components.clinical_shell import clinical_shell
from app.components.clinical_ui import (
    panel,
    panel_heading,
    risk_pill,
    stat_tile,
    status_pill,
)
from app.states.batch_state import (
    BATCH_UPLOAD_ID,
    BatchRecordView,
    BatchState,
)

_FILTERS: list[tuple[str, str]] = [
    ("Todos", "all"),
    ("Riesgo alto", "high"),
    ("Riesgo moderado", "moderate"),
    ("Riesgo bajo", "low"),
    ("Con error", "error"),
]


def upload_panel() -> rx.Component:
    return panel(
        panel_heading(
            "upload",
            "Entrada de datos clínicos",
            "Carga un CSV o PDF con casos y ejecuta el motor local sobre cada registro.",
            rx.cond(BatchState.has_staged_file, "Archivo listo", "Sin archivo"),
        ),
        rx.upload.root(
            rx.el.div(
                rx.icon("cloud-upload", class_name="h-7 w-7 text-[#2d7a68]"),
                rx.el.p(
                    "Suelta aquí un CSV o PDF clínico",
                    class_name="mt-4 text-base font-semibold text-[#36544e]",
                ),
                rx.el.p(
                    "También puedes hacer clic para seleccionar el archivo desde el equipo.",
                    class_name="mt-2 max-w-md text-center text-sm leading-6 text-[#71807a]",
                ),
                rx.el.div(
                    rx.el.span(
                        "CSV",
                        class_name="rounded-full bg-[#e6f0e7] px-2.5 py-1 text-[11px] font-semibold text-[#2d7a68]",
                    ),
                    rx.el.span(
                        "PDF",
                        class_name="rounded-full bg-[#f4ead1] px-2.5 py-1 text-[11px] font-semibold text-[#936518]",
                    ),
                    class_name="mt-5 flex gap-2",
                ),
                class_name="flex min-h-56 w-full cursor-pointer flex-col items-center justify-center px-5 py-8 text-center",
            ),
            id=BATCH_UPLOAD_ID,
            accept={
                "text/csv": [".csv"],
                "application/pdf": [".pdf"],
                "text/plain": [".txt"],
            },
            max_files=1,
            multiple=False,
            on_drop=BatchState.handle_upload(
                rx.upload_files(
                    upload_id=BATCH_UPLOAD_ID,
                    on_upload_progress=BatchState.handle_upload_progress,
                )
            ),
            class_name="flex w-full items-center justify-center rounded-2xl border-2 border-dashed border-[#cddbcf] bg-[#f6faf5]",
        ),
        rx.cond(
            BatchState.is_uploading,
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        class_name="h-full rounded-full bg-[#2d7a68]",
                        style={"width": f"{BatchState.upload_progress}%"},
                    ),
                    class_name="h-2 w-full overflow-hidden rounded-full bg-[#e6ebe4]",
                ),
                rx.el.div(
                    rx.el.span(
                        f"Cargando {BatchState.upload_progress}%",
                        class_name="text-xs font-medium text-[#526761]",
                    ),
                    rx.el.button(
                        "Cancelar",
                        type="button",
                        on_click=BatchState.cancel_upload,
                        class_name="text-xs font-semibold text-[#9b5545]",
                    ),
                    class_name="mt-2 flex items-center justify-between",
                ),
                class_name="mt-4",
            ),
            rx.fragment(),
        ),
        rx.cond(
            BatchState.has_staged_file,
            rx.el.div(
                rx.icon("file-text", class_name="h-4 w-4 text-[#174e50]"),
                rx.el.div(
                    rx.el.p(
                        BatchState.staged_filename,
                        class_name="truncate text-sm font-semibold text-[#36544e]",
                    ),
                    rx.el.p(
                        f"{BatchState.staged_format.upper()} · {BatchState.staged_size_kb:.1f} KB",
                        class_name="mt-0.5 text-xs text-[#77837d]",
                    ),
                    class_name="min-w-0",
                ),
                status_pill(BatchState.import_status),
                class_name="mt-4 flex items-center gap-3 rounded-xl border border-[#d8e4d9] bg-[#edf5ed] p-4",
            ),
            rx.fragment(),
        ),
        rx.cond(
            BatchState.upload_error != "",
            rx.el.p(
                BatchState.upload_error,
                class_name="mt-3 rounded-xl border border-[#ecd5cd] bg-[#fdf3ef] px-3 py-2 text-xs font-medium text-[#9b5545]",
            ),
            rx.fragment(),
        ),
        rx.cond(
            BatchState.is_processing,
            rx.el.div(
                rx.spinner(size="2"),
                rx.el.span(
                    BatchState.stage,
                    class_name="text-xs font-medium text-[#526761]",
                ),
                class_name="mt-4 flex items-center gap-2 rounded-xl border border-[#d8e4d9] bg-[#edf5ed] px-3 py-2",
            ),
            rx.fragment(),
        ),
        rx.el.div(
            rx.el.button(
                rx.icon("play", class_name="h-4 w-4"),
                rx.cond(
                    BatchState.is_processing,
                    "Procesando...",
                    "Procesar lote",
                ),
                type="button",
                disabled=BatchState.is_processing,
                on_click=BatchState.process_batch,
                class_name="flex items-center justify-center gap-2 rounded-xl bg-[#174e50] px-4 py-2.5 text-sm font-semibold text-[#fbfaf6] transition-colors hover:bg-[#123f41] disabled:opacity-60",
            ),
            rx.el.button(
                rx.icon("eraser", class_name="h-4 w-4"),
                "Limpiar",
                type="button",
                on_click=[
                    BatchState.clear_batch,
                    rx.clear_selected_files(BATCH_UPLOAD_ID),
                ],
                class_name="flex items-center justify-center gap-2 rounded-xl border border-[#c8d7cb] bg-[#fbfaf6] px-4 py-2.5 text-sm font-semibold text-[#174e50] transition-colors hover:bg-[#eef4ed]",
            ),
            rx.el.a(
                rx.icon("database", class_name="h-4 w-4"),
                "Ver base de datos",
                href="/database",
                class_name="flex items-center justify-center gap-2 rounded-xl border border-[#c8d7cb] bg-[#fbfaf6] px-4 py-2.5 text-sm font-semibold text-[#174e50] transition-colors hover:bg-[#eef4ed]",
            ),
            class_name="mt-5 flex flex-wrap gap-3",
        ),
    )


def status_panel() -> rx.Component:
    return panel(
        panel_heading(
            "layers-3",
            "Estado de la importación",
            "Progreso, contadores y avisos de normalización del archivo actual.",
            rx.cond(
                BatchState.import_id > 0,
                f"Importación #{BatchState.import_id}",
                "Sin importación",
            ),
        ),
        rx.el.div(
            rx.el.div(
                class_name="h-full rounded-full bg-[#2d7a68]",
                style={"width": f"{BatchState.progress_percent}%"},
            ),
            class_name="h-2 w-full overflow-hidden rounded-full bg-[#e6ebe4]",
        ),
        rx.el.p(
            f"{BatchState.progress_percent:.0f}% de {BatchState.total_count} registros",
            class_name="mt-2 text-xs font-medium text-[#77837d]",
        ),
        rx.el.div(
            stat_tile(
                "Registros",
                BatchState.total_count.to_string(),
                "mt-2 text-2xl font-semibold text-[#41616a]",
            ),
            stat_tile(
                "Procesados",
                BatchState.processed_count.to_string(),
                "mt-2 text-2xl font-semibold text-[#2d7a68]",
            ),
            stat_tile(
                "Con error",
                BatchState.error_count.to_string(),
                "mt-2 text-2xl font-semibold text-[#9b5545]",
            ),
            stat_tile(
                "Riesgo alto",
                BatchState.high_risk_count.to_string(),
                "mt-2 text-2xl font-semibold text-[#936518]",
            ),
            class_name="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4",
        ),
        rx.cond(
            BatchState.warnings.length() > 0,
            rx.el.div(
                rx.el.p(
                    "Avisos de normalización",
                    class_name="text-xs font-semibold uppercase tracking-[0.12em] text-[#936518]",
                ),
                rx.el.ul(
                    rx.foreach(
                        BatchState.warnings,
                        lambda item: rx.el.li(
                            item,
                            class_name="mt-1.5 text-sm leading-6 text-[#66756f]",
                        ),
                    ),
                    class_name="mt-2 list-disc pl-5",
                ),
                class_name="mt-5 rounded-xl border border-[#eadbb8] bg-[#fbf6e9] p-4",
            ),
            rx.fragment(),
        ),
    )


def filter_chip(option: tuple[str, str]) -> rx.Component:
    return rx.el.button(
        option[0],
        type="button",
        on_click=lambda: BatchState.set_risk_filter(option[1]),
        class_name=rx.cond(
            BatchState.risk_filter == option[1],
            "w-fit rounded-full border border-[#2d7a68] bg-[#e6f0e7] px-3 py-1.5 text-xs font-semibold text-[#174e50]",
            "w-fit rounded-full border border-[#d5ded6] bg-[#fbfaf6] px-3 py-1.5 text-xs font-medium text-[#66756f] hover:border-[#a9c4b1] hover:bg-[#f2f7f1]",
        ),
    )


def record_row(item: BatchRecordView) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            item["record_number"].to_string(),
            class_name="px-4 py-3 text-sm text-[#77837d]",
        ),
        rx.el.td(
            rx.el.p(
                item["reference"],
                class_name="text-sm font-semibold text-[#174e50]",
            ),
            rx.el.p(
                item["chief_complaint"],
                class_name="mt-0.5 line-clamp-1 max-w-[18rem] text-xs text-[#8a9791]",
            ),
            class_name="px-4 py-3",
        ),
        rx.el.td(
            item["age_display"], class_name="px-4 py-3 text-sm text-[#66756f]"
        ),
        rx.el.td(
            risk_pill(item["risk_level"], item["risk_label"]),
            class_name="px-4 py-3",
        ),
        rx.el.td(
            f"{item['risk_score']:.0f}/100",
            class_name="px-4 py-3 text-sm font-semibold text-[#174e50]",
        ),
        rx.el.td(
            f"{item['symptom_count']} / {item['red_flag_count']}",
            class_name="px-4 py-3 text-sm text-[#66756f]",
        ),
        rx.el.td(status_pill(item["status"]), class_name="px-4 py-3"),
        on_click=lambda: BatchState.select_record(item["record_number"]),
        class_name=rx.cond(
            BatchState.selected_record == item["record_number"],
            "cursor-pointer border-b border-[#eef1ec] bg-[#eef5ee]",
            "cursor-pointer border-b border-[#eef1ec] hover:bg-[#f6faf5]",
        ),
    )


def records_panel() -> rx.Component:
    return panel(
        panel_heading(
            "list-checks",
            "Registros revisables",
            "Selecciona un registro para revisar el detalle del resultado local.",
            f"{BatchState.filtered_records.length()} en vista",
        ),
        rx.el.div(
            rx.foreach(_FILTERS, filter_chip),
            class_name="mb-4 flex flex-wrap gap-2",
        ),
        rx.cond(
            BatchState.has_records,
            rx.el.div(
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            rx.el.th(
                                "#",
                                class_name="px-4 py-3 text-left text-[11px] font-semibold uppercase tracking-[0.12em] text-[#8a9791]",
                            ),
                            rx.el.th(
                                "Caso",
                                class_name="px-4 py-3 text-left text-[11px] font-semibold uppercase tracking-[0.12em] text-[#8a9791]",
                            ),
                            rx.el.th(
                                "Edad",
                                class_name="px-4 py-3 text-left text-[11px] font-semibold uppercase tracking-[0.12em] text-[#8a9791]",
                            ),
                            rx.el.th(
                                "Riesgo",
                                class_name="px-4 py-3 text-left text-[11px] font-semibold uppercase tracking-[0.12em] text-[#8a9791]",
                            ),
                            rx.el.th(
                                "Score",
                                class_name="px-4 py-3 text-left text-[11px] font-semibold uppercase tracking-[0.12em] text-[#8a9791]",
                            ),
                            rx.el.th(
                                "Sínt./Flags",
                                class_name="px-4 py-3 text-left text-[11px] font-semibold uppercase tracking-[0.12em] text-[#8a9791]",
                            ),
                            rx.el.th(
                                "Estado",
                                class_name="px-4 py-3 text-left text-[11px] font-semibold uppercase tracking-[0.12em] text-[#8a9791]",
                            ),
                            class_name="border-b border-[#dce4dc] bg-[#f3f6f1]",
                        )
                    ),
                    rx.el.tbody(
                        rx.foreach(BatchState.filtered_records, record_row)
                    ),
                    class_name="table-auto w-full",
                ),
                class_name="overflow-x-auto rounded-xl border border-[#dce4dc]",
            ),
            rx.el.div(
                rx.icon("inbox", class_name="h-6 w-6 text-[#8a9791]"),
                rx.el.p(
                    "Sin registros procesados",
                    class_name="mt-3 text-sm font-semibold text-[#36544e]",
                ),
                rx.el.p(
                    "Carga un archivo y ejecuta el procesamiento para revisar los resultados.",
                    class_name="mt-1 text-sm leading-6 text-[#71807a]",
                ),
                class_name="flex min-h-40 flex-col items-center justify-center rounded-xl border border-dashed border-[#cddbcf] bg-[#f6faf5] p-6 text-center",
            ),
        ),
    )


def record_detail_panel() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("file-search", class_name="h-4 w-4 text-[#174e50]"),
            rx.el.p(
                "Detalle del registro",
                class_name="text-sm font-semibold text-[#36544e]",
            ),
            class_name="flex items-center gap-2",
        ),
        rx.cond(
            BatchState.has_records,
            rx.el.div(
                rx.el.p(
                    BatchState.selected_record_view["reference"],
                    class_name="mt-4 text-lg font-semibold text-[#173f46]",
                ),
                rx.el.p(
                    BatchState.selected_record_view["diagnosis_label"],
                    class_name="mt-1 text-sm leading-6 text-[#66756f]",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.p("Riesgo", class_name="text-xs text-[#71807a]"),
                        risk_pill(
                            BatchState.selected_record_view["risk_level"],
                            BatchState.selected_record_view["risk_label"],
                        ),
                        class_name="flex flex-col gap-1.5",
                    ),
                    rx.el.div(
                        rx.el.p(
                            "Puntuación", class_name="text-xs text-[#71807a]"
                        ),
                        rx.el.p(
                            f"{BatchState.selected_record_view['risk_score']:.0f}/100",
                            class_name="text-sm font-semibold text-[#174e50]",
                        ),
                    ),
                    rx.el.div(
                        rx.el.p(
                            "Confianza", class_name="text-xs text-[#71807a]"
                        ),
                        rx.el.p(
                            f"{BatchState.selected_record_view['confidence']:.0f}%",
                            class_name="text-sm font-semibold text-[#2d7a68]",
                        ),
                    ),
                    rx.el.div(
                        rx.el.p(
                            "Paciente", class_name="text-xs text-[#71807a]"
                        ),
                        rx.el.p(
                            BatchState.selected_record_view["sex_display"],
                            class_name="text-sm font-semibold text-[#41616a]",
                        ),
                    ),
                    class_name="mt-5 grid grid-cols-2 gap-4 border-t border-[#e5e9e3] pt-4",
                ),
                rx.el.p(
                    BatchState.selected_record_view["chief_complaint"],
                    class_name="mt-5 border-l-2 border-[#dfe9df] pl-3 text-sm leading-6 text-[#71807a]",
                ),
                rx.cond(
                    BatchState.selected_record_view["error"] != "",
                    rx.el.p(
                        BatchState.selected_record_view["error"],
                        class_name="mt-4 rounded-xl border border-[#ecd5cd] bg-[#fdf3ef] px-3 py-2 text-xs font-medium text-[#9b5545]",
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    BatchState.selected_record_view["case_id"] > 0,
                    rx.el.p(
                        f"Guardado como caso #{BatchState.selected_record_view['case_id']}",
                        class_name="mt-4 w-fit rounded-full border border-[#c8ddc9] bg-[#eef6ee] px-3 py-1.5 text-xs font-semibold text-[#2d7a68]",
                    ),
                    rx.fragment(),
                ),
            ),
            rx.el.p(
                "Aún no hay registros para revisar.",
                class_name="mt-4 text-sm leading-6 text-[#71807a]",
            ),
        ),
        class_name="rounded-2xl border border-[#eadbb8] bg-[#fbf6e9] p-5 sm:p-6",
    )


def batches_page() -> rx.Component:
    return clinical_shell(
        "Procesamiento por lotes",
        "03 · Ingesta clínica",
        rx.el.div(
            rx.el.div(
                upload_panel(),
                status_panel(),
                class_name="grid grid-cols-1 gap-5 xl:grid-cols-2",
            ),
            rx.el.div(
                rx.el.div(records_panel(), class_name="min-w-0"),
                rx.el.div(record_detail_panel(), class_name="min-w-0"),
                class_name="grid grid-cols-1 gap-5 xl:grid-cols-[minmax(0,1.3fr)_minmax(20rem,0.7fr)]",
            ),
            class_name="flex w-full flex-col gap-5",
        ),
    )
