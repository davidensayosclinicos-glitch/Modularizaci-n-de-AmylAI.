import reflex as rx


def risk_diagram() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.p(
                        "Mapa de riesgo clínico",
                        class_name="text-base font-semibold text-[#173f46]",
                    ),
                    rx.el.p(
                        "Lectura orientativa por dimensión",
                        class_name="mt-1 text-sm text-[#71807a]",
                    ),
                ),
                rx.el.div(
                    rx.icon("info", class_name="h-4 w-4 text-[#8a9791]"),
                    class_name="flex h-8 w-8 items-center justify-center rounded-full border border-[#dce4dc] bg-[#fbfaf6]",
                ),
                class_name="flex items-start justify-between gap-4",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.span(
                                "Sin caso activo",
                                class_name="text-xs font-semibold uppercase tracking-[0.14em] text-[#ad7619]",
                            ),
                            rx.el.span(
                                "No calculado",
                                class_name="rounded-full bg-[#f4ead1] px-2.5 py-1 text-[11px] font-medium text-[#936518]",
                            ),
                            class_name="flex items-center justify-between gap-3",
                        ),
                        rx.el.p(
                            "—",
                            class_name="mt-4 text-6xl font-semibold tracking-tight text-[#174e50]",
                        ),
                        rx.el.p(
                            "El resultado aparecerá después de completar una evaluación.",
                            class_name="mt-2 max-w-xs text-sm leading-6 text-[#71807a]",
                        ),
                        class_name="relative z-10 flex flex-col items-center justify-center text-center",
                    ),
                    class_name="relative flex h-56 w-56 items-center justify-center rounded-full border-[18px] border-[#dfe9df] bg-[#fbfaf6]",
                ),
                rx.el.div(
                    class_name="absolute left-1/2 top-1/2 h-72 w-72 -translate-x-1/2 -translate-y-1/2 rounded-full border border-[#dce4dc]",
                ),
                rx.el.div(
                    class_name="absolute left-1/2 top-1/2 h-80 w-80 -translate-x-1/2 -translate-y-1/2 rounded-full border border-dashed border-[#dce4dc]",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.icon("heart-pulse", class_name="h-4 w-4"),
                        "Señales",
                        class_name="absolute -left-2 top-12 flex items-center gap-1.5 rounded-full border border-[#dce4dc] bg-[#fbfaf6] px-2.5 py-1.5 text-[11px] font-medium text-[#587069]",
                    ),
                    rx.el.div(
                        rx.icon("brain", class_name="h-4 w-4"),
                        "Contexto",
                        class_name="absolute -right-3 top-12 flex items-center gap-1.5 rounded-full border border-[#dce4dc] bg-[#fbfaf6] px-2.5 py-1.5 text-[11px] font-medium text-[#587069]",
                    ),
                    rx.el.div(
                        rx.icon("clipboard-check", class_name="h-4 w-4"),
                        "Historia",
                        class_name="absolute -bottom-1 left-1/2 flex -translate-x-1/2 items-center gap-1.5 rounded-full border border-[#dce4dc] bg-[#fbfaf6] px-2.5 py-1.5 text-[11px] font-medium text-[#587069]",
                    ),
                    class_name="absolute inset-0",
                ),
                class_name="relative mx-auto mt-10 flex h-[21rem] w-full max-w-[23rem] items-center justify-center",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        class_name="h-2.5 w-2.5 rounded-full bg-[#4c9b7b]"
                    ),
                    rx.el.span(
                        "Bajo", class_name="text-xs font-medium text-[#587069]"
                    ),
                    class_name="flex items-center gap-2",
                ),
                rx.el.div(
                    rx.el.div(
                        class_name="h-2.5 w-2.5 rounded-full bg-[#e0a53a]"
                    ),
                    rx.el.span(
                        "Moderado",
                        class_name="text-xs font-medium text-[#587069]",
                    ),
                    class_name="flex items-center gap-2",
                ),
                rx.el.div(
                    rx.el.div(
                        class_name="h-2.5 w-2.5 rounded-full bg-[#c96b54]"
                    ),
                    rx.el.span(
                        "Alto", class_name="text-xs font-medium text-[#587069]"
                    ),
                    class_name="flex items-center gap-2",
                ),
                class_name="flex flex-wrap items-center justify-center gap-5 border-t border-[#e5e9e3] pt-4",
            ),
            class_name="rounded-2xl border border-[#dce4dc] bg-[#fbfaf6] p-5 sm:p-6",
        ),
        class_name="w-full",
    )
