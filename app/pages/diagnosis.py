import reflex as rx

from app.components.clinical_shell import clinical_shell
from app.components.risk_gauge import risk_gauge
from app.states.case_state import CaseState
from app.services.clinical_engine import ScoreBreakdown


def empty_state() -> rx.Component:
    return rx.el.div(
        rx.icon("scan-search", class_name="h-7 w-7 text-[#2d7a68]"),
        rx.el.p(
            "Sin caso analizado",
            class_name="mt-4 text-base font-semibold text-[#36544e]",
        ),
        rx.el.p(
            "Completa una evaluación individual para generar resultado, evidencia y recomendaciones.",
            class_name="mt-2 max-w-md text-center text-sm leading-6 text-[#71807a]",
        ),
        rx.el.a(
            rx.icon("user-round-plus", class_name="h-4 w-4"),
            "Abrir evaluación individual",
            href="/individual",
            class_name="mt-5 flex items-center gap-2 rounded-xl bg-[#174e50] px-4 py-2.5 text-sm font-semibold text-[#fbfaf6] hover:bg-[#123f41]",
        ),
        class_name="flex min-h-64 flex-col items-center justify-center rounded-2xl border-2 border-dashed border-[#cddbcf] bg-[#f6faf5] px-5 py-8",
    )


def result_panel() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon("scan-search", class_name="h-5 w-5 text-[#174e50]"),
                rx.el.p(
                    "Resultado del caso",
                    class_name="text-base font-semibold text-[#173f46]",
                ),
                class_name="flex items-center gap-2",
            ),
            rx.el.span(
                CaseState.analyzed_case_title,
                class_name="rounded-full bg-[#f0f2ed] px-2.5 py-1 text-[11px] font-medium text-[#738079]",
            ),
            class_name="flex items-center justify-between gap-4",
        ),
        rx.el.div(
            rx.el.p(
                "Diagnóstico orientativo",
                class_name="text-xs font-semibold uppercase tracking-[0.14em] text-[#9aa39c]",
            ),
            rx.el.p(
                CaseState.diagnosis_label,
                class_name="mt-2 text-2xl font-semibold leading-tight text-[#173f46]",
            ),
            rx.el.p(
                CaseState.local_narrative,
                class_name="mt-3 max-w-2xl text-sm leading-6 text-[#71807a]",
            ),
            class_name="mt-7 border-l-2 border-[#dfe9df] pl-4",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.p("Riesgo", class_name="text-xs text-[#71807a]"),
                rx.el.p(
                    CaseState.risk_label,
                    class_name="mt-1 text-lg font-semibold text-[#936518]",
                ),
            ),
            rx.el.div(
                rx.el.p("Puntuación", class_name="text-xs text-[#71807a]"),
                rx.el.p(
                    f"{CaseState.risk_score:.0f}/100",
                    class_name="mt-1 text-lg font-semibold text-[#174e50]",
                ),
            ),
            rx.el.div(
                rx.el.p("Confianza", class_name="text-xs text-[#71807a]"),
                rx.el.p(
                    CaseState.confidence_display,
                    class_name="mt-1 text-lg font-semibold text-[#2d7a68]",
                ),
            ),
            rx.el.div(
                rx.el.p("Completitud", class_name="text-xs text-[#71807a]"),
                rx.el.p(
                    f"{CaseState.data_completeness:.0f}%",
                    class_name="mt-1 text-lg font-semibold text-[#41616a]",
                ),
            ),
            class_name="mt-7 grid grid-cols-2 gap-4 border-t border-[#e5e9e3] pt-5 sm:grid-cols-4",
        ),
        class_name="rounded-2xl border border-[#dce4dc] bg-[#fbfaf6] p-5 sm:p-6",
    )


def breakdown_row(item: ScoreBreakdown) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.p(
                item["label"],
                class_name="text-sm font-semibold text-[#36544e]",
            ),
            rx.el.span(
                f"peso {item['weight']:.0f}%",
                class_name="ml-auto rounded-full bg-[#f0f2ed] px-2 py-0.5 text-[11px] font-medium text-[#738079]",
            ),
            rx.el.span(
                f"{item['score']:.0f}/100",
                class_name="text-sm font-semibold text-[#174e50]",
            ),
            class_name="flex items-center gap-3",
        ),
        rx.el.p(
            item["detail"], class_name="mt-1 text-xs leading-5 text-[#71807a]"
        ),
        rx.el.div(
            rx.el.div(
                class_name="h-full rounded-full bg-[#2d7a68]",
                style={"width": f"{item['score']}%"},
            ),
            class_name="mt-3 h-2 w-full overflow-hidden rounded-full bg-[#e6ebe4]",
        ),
        class_name="rounded-xl border border-[#dce4dc] bg-[#fbfaf6] p-4",
    )


def llm_panel() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("sparkles", class_name="h-4 w-4 text-[#ad7619]"),
            rx.el.p(
                "Capa de lenguaje (Gemini)",
                class_name="text-sm font-semibold text-[#36544e]",
            ),
            rx.cond(
                CaseState.llm_ok,
                rx.el.span(
                    CaseState.llm_model,
                    class_name="ml-auto rounded-full bg-[#e6f0e7] px-2.5 py-1 text-[11px] font-semibold text-[#2d7a68]",
                ),
                rx.el.span(
                    "No disponible",
                    class_name="ml-auto rounded-full bg-[#f8e3dc] px-2.5 py-1 text-[11px] font-semibold text-[#9b5545]",
                ),
            ),
            class_name="flex items-center gap-2",
        ),
        rx.cond(
            CaseState.llm_error != "",
            rx.el.div(
                rx.icon("triangle-alert", class_name="h-4 w-4 text-[#c96b54]"),
                rx.el.div(
                    rx.el.p(
                        "Error del modelo",
                        class_name="text-sm font-semibold text-[#9b5545]",
                    ),
                    rx.el.p(
                        CaseState.llm_error,
                        class_name="mt-1 text-xs leading-5 text-[#8a5a4d]",
                    ),
                    rx.el.p(
                        "El resultado mostrado proviene solo del algoritmo experto y la heurística local.",
                        class_name="mt-2 text-xs leading-5 text-[#8a5a4d]",
                    ),
                ),
                class_name="mt-3 flex items-start gap-3 rounded-xl border border-[#ecd5cd] bg-[#fdf3ef] p-4",
            ),
            rx.el.div(
                rx.el.p(
                    CaseState.llm_narrative,
                    class_name="text-sm leading-6 text-[#66756f]",
                ),
                rx.cond(
                    CaseState.llm_considerations.length() > 0,
                    rx.el.div(
                        rx.el.p(
                            "Consideraciones",
                            class_name="text-xs font-semibold uppercase tracking-[0.12em] text-[#936518]",
                        ),
                        rx.el.ul(
                            rx.foreach(
                                CaseState.llm_considerations,
                                lambda item: rx.el.li(
                                    item,
                                    class_name="mt-1.5 text-sm leading-6 text-[#66756f]",
                                ),
                            ),
                            class_name="mt-2 list-disc pl-5",
                        ),
                        class_name="mt-4",
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    CaseState.llm_differentials.length() > 0,
                    rx.el.div(
                        rx.el.p(
                            "Diferenciales a descartar",
                            class_name="text-xs font-semibold uppercase tracking-[0.12em] text-[#936518]",
                        ),
                        rx.el.div(
                            rx.foreach(
                                CaseState.llm_differentials,
                                lambda item: rx.el.span(
                                    item,
                                    class_name="w-fit rounded-full border border-[#eadbb8] bg-[#fbf6e9] px-3 py-1 text-xs font-medium text-[#936518]",
                                ),
                            ),
                            class_name="mt-2 flex flex-wrap gap-2",
                        ),
                        class_name="mt-4",
                    ),
                    rx.fragment(),
                ),
                class_name="mt-3 rounded-xl border border-[#d8e4d9] bg-[#edf5ed] p-4",
            ),
        ),
        class_name="rounded-2xl border border-[#dce4dc] bg-[#fbfaf6] p-5 sm:p-6",
    )


def evidence_panel() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("list-checks", class_name="h-4 w-4 text-[#607c84]"),
            rx.el.p(
                "Evidencia y trazabilidad del cálculo",
                class_name="text-sm font-semibold text-[#36544e]",
            ),
            class_name="flex items-center gap-2",
        ),
        rx.el.div(
            rx.foreach(
                CaseState.evidence,
                lambda item: rx.el.div(
                    rx.icon(
                        "chevron-right",
                        class_name="mt-0.5 h-3.5 w-3.5 text-[#8a9791]",
                    ),
                    rx.el.span(
                        item, class_name="text-sm leading-6 text-[#66756f]"
                    ),
                    class_name="flex items-start gap-2 border-b border-[#eef1ec] py-2 last:border-b-0",
                ),
            ),
            class_name="mt-3",
        ),
        class_name="rounded-2xl border border-[#dce4dc] bg-[#fbfaf6] p-5 sm:p-6",
    )


def recommendations_panel() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("clipboard-check", class_name="h-4 w-4 text-[#2d7a68]"),
            rx.el.p(
                "Recomendaciones",
                class_name="text-sm font-semibold text-[#36544e]",
            ),
            class_name="flex items-center gap-2",
        ),
        rx.el.ul(
            rx.foreach(
                CaseState.recommendations,
                lambda item: rx.el.li(
                    item,
                    class_name="mt-1.5 text-sm leading-6 text-[#66756f]",
                ),
            ),
            class_name="mt-3 list-disc pl-5",
        ),
        class_name="rounded-2xl border border-[#d8e4d9] bg-[#edf5ed] p-5 sm:p-6",
    )


def persistence_panel() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("database", class_name="h-4 w-4 text-[#174e50]"),
            rx.el.p(
                "Guardar en base de datos clínica",
                class_name="text-sm font-semibold text-[#36544e]",
            ),
            class_name="flex items-center gap-2",
        ),
        rx.el.p(
            "Se registra el expediente, la ejecución del motor y el resultado diagnóstico con su evidencia.",
            class_name="mt-2 text-sm leading-6 text-[#66756f]",
        ),
        rx.cond(
            CaseState.save_error != "",
            rx.el.p(
                CaseState.save_error,
                class_name="mt-3 rounded-xl border border-[#ecd5cd] bg-[#fdf3ef] px-3 py-2 text-xs font-medium text-[#9b5545]",
            ),
            rx.fragment(),
        ),
        rx.cond(
            CaseState.is_saved,
            rx.el.div(
                rx.icon("circle_check", class_name="h-4 w-4 text-[#3d9678]"),
                rx.el.span(
                    f"Guardado con ID {CaseState.saved_case_id}",
                    class_name="text-xs font-semibold text-[#2d7a68]",
                ),
                class_name="mt-3 flex w-fit items-center gap-2 rounded-full border border-[#c8ddc9] bg-[#eef6ee] px-3 py-1.5",
            ),
            rx.fragment(),
        ),
        rx.el.div(
            rx.el.button(
                rx.icon("save", class_name="h-4 w-4"),
                rx.cond(
                    CaseState.is_saving, "Guardando...", "Guardar expediente"
                ),
                type="button",
                disabled=CaseState.is_saving,
                on_click=CaseState.save_case,
                class_name="flex items-center justify-center gap-2 rounded-xl bg-[#174e50] px-4 py-2.5 text-sm font-semibold text-[#fbfaf6] hover:bg-[#123f41] disabled:opacity-60",
            ),
            rx.el.a(
                rx.icon("pencil", class_name="h-4 w-4"),
                "Editar caso",
                href="/individual",
                class_name="flex items-center justify-center gap-2 rounded-xl border border-[#c8d7cb] bg-[#fbfaf6] px-4 py-2.5 text-sm font-semibold text-[#174e50] hover:bg-[#eef4ed]",
            ),
            class_name="mt-4 flex flex-wrap gap-3",
        ),
        class_name="rounded-2xl border border-[#eadbb8] bg-[#fbf6e9] p-5 sm:p-6",
    )


def diagnosis_content() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            result_panel(),
            rx.el.div(risk_gauge(), class_name="min-w-0"),
            class_name="grid grid-cols-1 gap-5 xl:grid-cols-2",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    "Desglose del razonamiento",
                    class_name="text-base font-semibold text-[#173f46]",
                ),
                rx.el.p(
                    "Contribución del algoritmo experto, la heurística textual y la capa de lenguaje.",
                    class_name="mt-1 text-sm text-[#71807a]",
                ),
                class_name="mb-4",
            ),
            rx.el.div(
                rx.foreach(CaseState.breakdown, breakdown_row),
                class_name="grid grid-cols-1 gap-4 md:grid-cols-2",
            ),
            class_name="rounded-2xl border border-[#dce4dc] bg-[#fbfaf6] p-5 sm:p-6",
        ),
        llm_panel(),
        rx.el.div(
            evidence_panel(),
            rx.el.div(
                recommendations_panel(),
                persistence_panel(),
                class_name="flex min-w-0 flex-col gap-4",
            ),
            class_name="grid grid-cols-1 gap-5 xl:grid-cols-[minmax(0,1.1fr)_minmax(20rem,0.9fr)]",
        ),
        class_name="flex w-full flex-col gap-5",
    )


def diagnosis_page() -> rx.Component:
    return clinical_shell(
        "Revisión diagnóstica",
        "02 · Interpretación clínica",
        rx.cond(CaseState.has_result, diagnosis_content(), empty_state()),
    )
