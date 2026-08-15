import reflex as rx

from app.states.case_state import CaseState


def _legend() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(class_name="h-2.5 w-2.5 rounded-full bg-[#4c9b7b]"),
            rx.el.span("Bajo", class_name="text-xs font-medium text-[#587069]"),
            class_name="flex items-center gap-2",
        ),
        rx.el.div(
            rx.el.div(class_name="h-2.5 w-2.5 rounded-full bg-[#e0a53a]"),
            rx.el.span(
                "Moderado", class_name="text-xs font-medium text-[#587069]"
            ),
            class_name="flex items-center gap-2",
        ),
        rx.el.div(
            rx.el.div(class_name="h-2.5 w-2.5 rounded-full bg-[#c96b54]"),
            rx.el.span("Alto", class_name="text-xs font-medium text-[#587069]"),
            class_name="flex items-center gap-2",
        ),
        class_name="flex flex-wrap items-center justify-center gap-5 border-t border-[#e5e9e3] pt-4",
    )


def _satellite(
    icon: str, label: str, value: str, position: str
) -> rx.Component:
    return rx.el.div(
        rx.icon(icon, class_name="h-4 w-4"),
        rx.el.span(label, class_name="font-medium"),
        rx.el.span(
            value,
            class_name="rounded-full bg-[#eef3ec] px-1.5 py-0.5 font-semibold text-[#174e50]",
        ),
        class_name=position,
    )


def risk_gauge() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.p(
                        "Mapa de riesgo clínico",
                        class_name="text-base font-semibold text-[#173f46]",
                    ),
                    rx.el.p(
                        CaseState.analyzed_case_title,
                        class_name="mt-1 text-sm text-[#71807a]",
                    ),
                ),
                rx.el.span(
                    CaseState.risk_label,
                    class_name=rx.match(
                        CaseState.risk_level,
                        (
                            "low",
                            "rounded-full bg-[#e6f0e7] px-2.5 py-1 text-[11px] font-semibold text-[#2d7a68]",
                        ),
                        (
                            "moderate",
                            "rounded-full bg-[#f4ead1] px-2.5 py-1 text-[11px] font-semibold text-[#936518]",
                        ),
                        (
                            "high",
                            "rounded-full bg-[#f8e3dc] px-2.5 py-1 text-[11px] font-semibold text-[#9b5545]",
                        ),
                        "rounded-full bg-[#f0f2ed] px-2.5 py-1 text-[11px] font-semibold text-[#738079]",
                    ),
                ),
                class_name="flex items-start justify-between gap-4",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.span(
                            rx.cond(
                                CaseState.has_result,
                                "Puntuación combinada",
                                "Sin caso activo",
                            ),
                            class_name="text-xs font-semibold uppercase tracking-[0.14em] text-[#ad7619]",
                        ),
                        rx.el.p(
                            CaseState.risk_score_display,
                            class_name="mt-3 text-6xl font-semibold tracking-tight text-[#174e50]",
                        ),
                        rx.el.p(
                            rx.cond(
                                CaseState.has_result,
                                CaseState.diagnosis_label,
                                "El resultado aparecerá después de completar una evaluación.",
                            ),
                            class_name="mt-2 max-w-[15rem] text-sm leading-6 text-[#71807a]",
                        ),
                        class_name="relative z-10 flex flex-col items-center justify-center px-4 text-center",
                    ),
                    class_name=rx.match(
                        CaseState.risk_level,
                        (
                            "low",
                            "relative flex h-56 w-56 items-center justify-center rounded-full border-[18px] border-[#4c9b7b] bg-[#fbfaf6]",
                        ),
                        (
                            "moderate",
                            "relative flex h-56 w-56 items-center justify-center rounded-full border-[18px] border-[#e0a53a] bg-[#fbfaf6]",
                        ),
                        (
                            "high",
                            "relative flex h-56 w-56 items-center justify-center rounded-full border-[18px] border-[#c96b54] bg-[#fbfaf6]",
                        ),
                        "relative flex h-56 w-56 items-center justify-center rounded-full border-[18px] border-[#dfe9df] bg-[#fbfaf6]",
                    ),
                ),
                rx.el.div(
                    class_name="absolute left-1/2 top-1/2 h-72 w-72 -translate-x-1/2 -translate-y-1/2 rounded-full border border-[#dce4dc]",
                ),
                rx.el.div(
                    class_name="absolute left-1/2 top-1/2 h-80 w-80 -translate-x-1/2 -translate-y-1/2 rounded-full border border-dashed border-[#dce4dc]",
                ),
                rx.el.div(
                    _satellite(
                        "heart-pulse",
                        "Síntomas",
                        CaseState.symptom_count.to_string(),
                        "absolute -left-3 top-10 flex items-center gap-1.5 rounded-full border border-[#dce4dc] bg-[#fbfaf6] px-2.5 py-1.5 text-[11px] text-[#587069]",
                    ),
                    _satellite(
                        "circle-alert",
                        "Red flags",
                        CaseState.red_flag_count.to_string(),
                        "absolute -right-3 top-10 flex items-center gap-1.5 rounded-full border border-[#dce4dc] bg-[#fbfaf6] px-2.5 py-1.5 text-[11px] text-[#587069]",
                    ),
                    _satellite(
                        "brain",
                        "Confianza",
                        CaseState.confidence_display,
                        "absolute -bottom-1 left-1/2 flex -translate-x-1/2 items-center gap-1.5 rounded-full border border-[#dce4dc] bg-[#fbfaf6] px-2.5 py-1.5 text-[11px] text-[#587069]",
                    ),
                    class_name="absolute inset-0",
                ),
                class_name="relative mx-auto mt-10 flex h-[21rem] w-full max-w-[23rem] items-center justify-center",
            ),
            _legend(),
            class_name="rounded-2xl border border-[#dce4dc] bg-[#fbfaf6] p-5 sm:p-6",
        ),
        class_name="w-full",
    )
