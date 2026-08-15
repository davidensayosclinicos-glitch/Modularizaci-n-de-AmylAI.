import reflex as rx

from app.components.clinical_shell import clinical_shell
from app.components.risk_gauge import risk_gauge
from app.states.case_state import CaseState


def text_field(
    label: str,
    placeholder: str,
    field: str,
    value: rx.Var,
    input_type: str = "text",
) -> rx.Component:
    return rx.el.label(
        rx.el.span(
            label, class_name="mb-2 block text-xs font-semibold text-[#526761]"
        ),
        rx.el.input(
            type=input_type,
            placeholder=placeholder,
            default_value=value,
            on_change=lambda v: CaseState.set_field(field, v).debounce(400),
            class_name="w-full rounded-xl border border-[#cedbd0] bg-[#fbfaf6] px-3.5 py-2.5 text-sm text-[#173f46] outline-hidden transition-colors placeholder:text-[#a1aaa4] focus:border-[#3d9678] focus:ring-2 focus:ring-[#dcefe0]",
        ),
        class_name="block",
    )


def chip(
    label: str, selected: rx.Var, on_click: rx.event.EventType
) -> rx.Component:
    return rx.el.button(
        rx.cond(
            selected,
            rx.icon("check", class_name="h-3.5 w-3.5"),
            rx.icon("plus", class_name="h-3.5 w-3.5"),
        ),
        rx.el.span(label),
        type="button",
        on_click=on_click,
        class_name=rx.cond(
            selected,
            "flex w-fit items-center gap-1.5 rounded-full border border-[#2d7a68] bg-[#e6f0e7] px-3 py-1.5 text-xs font-semibold text-[#174e50] transition-colors",
            "flex w-fit items-center gap-1.5 rounded-full border border-[#d5ded6] bg-[#fbfaf6] px-3 py-1.5 text-xs font-medium text-[#66756f] transition-colors hover:border-[#a9c4b1] hover:bg-[#f2f7f1]",
        ),
    )


def chip_group(
    icon: str,
    title: str,
    caption: str,
    container_class: str,
    options: rx.Var,
    selected: rx.Var,
    handler,
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name="h-4 w-4 text-[#2d7a68]"),
            rx.el.p(title, class_name="text-sm font-semibold text-[#36544e]"),
            rx.el.span(
                selected.length().to_string(),
                class_name="ml-auto rounded-full bg-[#f0f2ed] px-2.5 py-1 text-[11px] font-semibold text-[#738079]",
            ),
            class_name="flex items-center gap-2",
        ),
        rx.el.p(caption, class_name="mt-1 text-xs leading-5 text-[#71807a]"),
        rx.el.div(
            rx.foreach(
                options,
                lambda item: chip(item, selected.contains(item), handler(item)),
            ),
            class_name="mt-3 flex flex-wrap gap-2",
        ),
        class_name=container_class,
    )


def capture_panel() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                "Nuevo expediente",
                class_name="text-lg font-semibold text-[#173f46]",
            ),
            rx.el.p(
                "Captura el caso clínico y ejecuta el motor de reglas con narrativa asistida.",
                class_name="mt-1 text-sm leading-6 text-[#71807a]",
            ),
            class_name="mb-5",
        ),
        rx.el.div(
            text_field(
                "Referencia del caso",
                "Ej. AMY-2026-001",
                "case_reference",
                CaseState.case_reference,
            ),
            text_field(
                "Referencia del paciente",
                "Identificador interno",
                "patient_reference",
                CaseState.patient_reference,
            ),
            text_field(
                "Edad", "Años", "age_input", CaseState.age_input, "number"
            ),
            rx.el.label(
                rx.el.span(
                    "Sexo",
                    class_name="mb-2 block text-xs font-semibold text-[#526761]",
                ),
                rx.el.div(
                    rx.el.select(
                        rx.el.option("Seleccionar", value=""),
                        rx.foreach(
                            CaseState.sex_options,
                            lambda option: rx.el.option(
                                option[0], value=option[1]
                            ),
                        ),
                        value=CaseState.sex,
                        on_change=lambda v: CaseState.set_field("sex", v),
                        class_name="w-full appearance-none rounded-xl border border-[#cedbd0] bg-[#fbfaf6] px-3.5 py-2.5 text-sm text-[#173f46] outline-hidden focus:border-[#3d9678] focus:ring-2 focus:ring-[#dcefe0]",
                    ),
                    rx.icon(
                        "chevron-down",
                        class_name="pointer-events-none absolute right-3 top-3 h-4 w-4 text-[#8a9791]",
                    ),
                    class_name="relative",
                ),
                class_name="block",
            ),
            class_name="grid grid-cols-1 gap-4 sm:grid-cols-2",
        ),
        rx.el.div(
            rx.el.label(
                rx.el.span(
                    "Motivo de consulta",
                    class_name="mb-2 block text-xs font-semibold text-[#526761]",
                ),
                rx.el.textarea(
                    placeholder="Describe el motivo principal de la evaluación...",
                    default_value=CaseState.chief_complaint,
                    on_change=CaseState.set_field("chief_complaint").debounce(
                        400
                    ),
                    class_name="min-h-24 w-full resize-y rounded-xl border border-[#cedbd0] bg-[#fbfaf6] px-3.5 py-3 text-sm text-[#173f46] outline-hidden placeholder:text-[#a1aaa4] focus:border-[#3d9678] focus:ring-2 focus:ring-[#dcefe0]",
                ),
                class_name="block",
            ),
            rx.el.label(
                rx.el.span(
                    "Resumen clínico",
                    class_name="mb-2 block text-xs font-semibold text-[#526761]",
                ),
                rx.el.textarea(
                    placeholder="Antecedentes, hallazgos de laboratorio, imagen y evolución...",
                    default_value=CaseState.clinical_summary,
                    on_change=CaseState.set_field("clinical_summary").debounce(
                        400
                    ),
                    class_name="min-h-32 w-full resize-y rounded-xl border border-[#cedbd0] bg-[#fbfaf6] px-3.5 py-3 text-sm text-[#173f46] outline-hidden placeholder:text-[#a1aaa4] focus:border-[#3d9678] focus:ring-2 focus:ring-[#dcefe0]",
                ),
                class_name="mt-5 block",
            ),
            class_name="mt-5",
        ),
        class_name="rounded-2xl border border-[#dce4dc] bg-[#fbfaf6] p-5 sm:p-6",
    )


def signals_panel() -> rx.Component:
    return rx.el.div(
        chip_group(
            "heart-pulse",
            "Síntomas y señales",
            "Selecciona los hallazgos presentes en la evaluación.",
            "rounded-xl border border-[#dce4dc] bg-[#fbfaf6] p-4",
            CaseState.symptom_options,
            CaseState.selected_symptoms,
            CaseState.toggle_symptom,
        ),
        chip_group(
            "circle-alert",
            "Señales de alerta (red flags)",
            "Marcadores que elevan el riesgo de forma inmediata.",
            "mt-4 rounded-xl border border-[#ecd5cd] bg-[#fdf3ef] p-4",
            CaseState.red_flag_options,
            CaseState.selected_red_flags,
            CaseState.toggle_red_flag,
        ),
        chip_group(
            "notebook-tabs",
            "Factores de riesgo y antecedentes",
            "Contexto que modifica la interpretación clínica.",
            "mt-4 rounded-xl border border-[#eadbb8] bg-[#fbf6e9] p-4",
            CaseState.risk_factor_options,
            CaseState.selected_risk_factors,
            CaseState.toggle_risk_factor,
        ),
        class_name="rounded-2xl border border-[#dce4dc] bg-[#fbfaf6] p-5 sm:p-6",
    )


def actions_panel() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("scan-search", class_name="h-5 w-5 text-[#2d7a68]"),
            rx.el.p(
                "Ejecutar evaluación",
                class_name="text-sm font-semibold text-[#36544e]",
            ),
            class_name="flex items-center gap-2",
        ),
        rx.el.p(
            "El motor local calcula reglas y heurística; Gemini añade la narrativa clínica.",
            class_name="mt-2 text-sm leading-6 text-[#66756f]",
        ),
        rx.cond(
            CaseState.validation_error != "",
            rx.el.p(
                CaseState.validation_error,
                class_name="mt-3 rounded-xl border border-[#ecd5cd] bg-[#fdf3ef] px-3 py-2 text-xs font-medium text-[#9b5545]",
            ),
            rx.fragment(),
        ),
        rx.cond(
            CaseState.is_analyzing,
            rx.el.div(
                rx.spinner(size="2"),
                rx.el.span(
                    CaseState.analysis_stage,
                    class_name="text-xs font-medium text-[#526761]",
                ),
                class_name="mt-3 flex items-center gap-2 rounded-xl border border-[#d8e4d9] bg-[#edf5ed] px-3 py-2",
            ),
            rx.fragment(),
        ),
        rx.el.div(
            rx.el.button(
                rx.icon("play", class_name="h-4 w-4"),
                rx.cond(
                    CaseState.is_analyzing, "Analizando...", "Analizar caso"
                ),
                type="button",
                disabled=CaseState.is_analyzing,
                on_click=CaseState.analyze,
                class_name="flex items-center justify-center gap-2 rounded-xl bg-[#174e50] px-4 py-2.5 text-sm font-semibold text-[#fbfaf6] transition-colors hover:bg-[#123f41] disabled:opacity-60",
            ),
            rx.el.button(
                rx.icon("eraser", class_name="h-4 w-4"),
                "Limpiar",
                type="button",
                on_click=CaseState.clear_case,
                class_name="flex items-center justify-center gap-2 rounded-xl border border-[#c8d7cb] bg-[#fbfaf6] px-4 py-2.5 text-sm font-semibold text-[#174e50] transition-colors hover:bg-[#eef4ed]",
            ),
            rx.el.a(
                rx.icon("arrow-right", class_name="h-4 w-4"),
                "Ir a diagnóstico",
                href="/diagnosis",
                class_name="flex items-center justify-center gap-2 rounded-xl border border-[#c8d7cb] bg-[#fbfaf6] px-4 py-2.5 text-sm font-semibold text-[#174e50] transition-colors hover:bg-[#eef4ed]",
            ),
            class_name="mt-4 flex flex-wrap gap-3",
        ),
        rx.cond(
            CaseState.has_result,
            rx.el.div(
                rx.el.div(
                    rx.el.p("Riesgo", class_name="text-xs text-[#71807a]"),
                    rx.el.p(
                        CaseState.risk_label,
                        class_name="mt-1 text-sm font-semibold text-[#174e50]",
                    ),
                ),
                rx.el.div(
                    rx.el.p(
                        "Completitud de datos",
                        class_name="text-xs text-[#71807a]",
                    ),
                    rx.el.p(
                        f"{CaseState.data_completeness:.0f}%",
                        class_name="mt-1 text-sm font-semibold text-[#936518]",
                    ),
                ),
                class_name="mt-5 grid grid-cols-2 gap-4 border-t border-[#e5e9e3] pt-4",
            ),
            rx.fragment(),
        ),
        class_name="rounded-2xl border border-[#d8e4d9] bg-[#edf5ed] p-5 sm:p-6",
    )


def individual_page() -> rx.Component:
    return clinical_shell(
        "Evaluación individual",
        "01 · Captura clínica",
        rx.el.div(
            rx.el.div(
                capture_panel(),
                signals_panel(),
                class_name="flex min-w-0 flex-col gap-4",
            ),
            rx.el.div(
                actions_panel(),
                risk_gauge(),
                class_name="flex min-w-0 flex-col gap-4",
            ),
            class_name="grid grid-cols-1 gap-5 xl:grid-cols-[minmax(0,1.3fr)_minmax(22rem,0.7fr)]",
        ),
    )
