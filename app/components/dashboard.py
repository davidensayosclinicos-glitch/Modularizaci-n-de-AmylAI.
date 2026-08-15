import reflex as rx

from app.components.risk_diagram import risk_diagram


def metric_card(
    icon: str,
    label: str,
    value: str,
    caption: str,
    icon_class: str,
    value_class: str,
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon(icon, class_name=icon_class),
                class_name="flex h-9 w-9 items-center justify-center rounded-xl bg-[#f2f5ef]",
            ),
            rx.el.span(
                "Resumen",
                class_name="text-[10px] font-semibold uppercase tracking-[0.14em] text-[#9aa39c]",
            ),
            class_name="flex items-center justify-between gap-3",
        ),
        rx.el.p(
            label,
            class_name="mt-4 text-sm font-medium text-[#66756f]",
        ),
        rx.el.p(
            value,
            class_name=value_class,
        ),
        rx.el.p(
            caption,
            class_name="mt-2 text-xs leading-5 text-[#89958e]",
        ),
        class_name="rounded-2xl border border-[#dce4dc] bg-[#fbfaf6] p-5",
    )


def workflow_card(
    icon: str,
    number: str,
    title: str,
    description: str,
    href: str,
) -> rx.Component:
    return rx.el.a(
        rx.el.div(
            rx.el.div(
                rx.icon(icon, class_name="h-5 w-5 text-[#174e50]"),
                class_name="flex h-10 w-10 items-center justify-center rounded-xl bg-[#e8eee9]",
            ),
            rx.el.span(
                number,
                class_name="text-[11px] font-semibold tracking-[0.14em] text-[#ad7619]",
            ),
            class_name="flex items-center justify-between",
        ),
        rx.el.h3(
            title,
            class_name="mt-5 text-sm font-semibold text-[#173f46]",
        ),
        rx.el.p(
            description,
            class_name="mt-2 text-xs leading-5 text-[#71807a]",
        ),
        rx.icon(
            "arrow-up-right",
            class_name="mt-5 h-4 w-4 text-[#8a9791] transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5",
        ),
        href=href,
        class_name="group rounded-2xl border border-[#dce4dc] bg-[#fbfaf6] p-5 transition-colors hover:border-[#a9c4b1] hover:bg-[#f7faf5]",
    )


def dashboard_overview() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.span(
                        "Vista general",
                        class_name="rounded-full bg-[#e6f0e7] px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.13em] text-[#2d7a68]",
                    ),
                    rx.el.h2(
                        "Un punto de partida claro para cada caso.",
                        class_name="mt-4 max-w-2xl text-2xl font-semibold leading-tight tracking-tight text-[#173f46] sm:text-3xl",
                    ),
                    rx.el.p(
                        "Centraliza la captura clínica, la revisión diagnóstica y la trazabilidad de cada evaluación en un mismo expediente digital.",
                        class_name="mt-3 max-w-2xl text-sm leading-6 text-[#66756f] sm:text-base",
                    ),
                    class_name="max-w-3xl",
                ),
                rx.el.div(
                    rx.el.a(
                        rx.icon("user-round-plus", class_name="h-4 w-4"),
                        "Nueva evaluación",
                        href="/individual",
                        class_name="flex items-center justify-center gap-2 rounded-xl bg-[#174e50] px-4 py-2.5 text-sm font-semibold text-[#fbfaf6] transition-colors hover:bg-[#123f41]",
                    ),
                    rx.el.a(
                        rx.icon("upload", class_name="h-4 w-4"),
                        "Revisar lotes",
                        href="/batches",
                        class_name="flex items-center justify-center gap-2 rounded-xl border border-[#c8d7cb] bg-[#fbfaf6] px-4 py-2.5 text-sm font-semibold text-[#174e50] transition-colors hover:bg-[#eef4ed]",
                    ),
                    class_name="mt-6 flex flex-wrap gap-3",
                ),
                class_name="flex flex-col justify-between gap-5 lg:flex-row lg:items-end",
            ),
            class_name="rounded-2xl border border-[#dce4dc] bg-[#e7efe7] p-6 sm:p-8",
        ),
        rx.el.div(
            metric_card(
                "clipboard-list",
                "Casos activos",
                "0",
                "Sin expedientes cargados en esta sesión",
                "h-4 w-4 text-[#2d7a68]",
                "mt-1 text-3xl font-semibold tracking-tight text-[#174e50]",
            ),
            metric_card(
                "circle-alert",
                "Riesgo alto",
                "0",
                "Pendiente de evaluación clínica",
                "h-4 w-4 text-[#c96b54]",
                "mt-1 text-3xl font-semibold tracking-tight text-[#9b5545]",
            ),
            metric_card(
                "clock-3",
                "Pendientes",
                "0",
                "No hay tareas clínicas abiertas",
                "h-4 w-4 text-[#d59a2b]",
                "mt-1 text-3xl font-semibold tracking-tight text-[#936518]",
            ),
            metric_card(
                "layers-3",
                "Importaciones",
                "0",
                "Listo para recibir datos por lote",
                "h-4 w-4 text-[#607c84]",
                "mt-1 text-3xl font-semibold tracking-tight text-[#41616a]",
            ),
            class_name="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4",
        ),
        rx.el.div(
            rx.el.div(
                risk_diagram(),
                class_name="min-w-0 lg:col-span-2",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.p(
                                "Cola clínica",
                                class_name="text-base font-semibold text-[#173f46]",
                            ),
                            rx.el.span(
                                "0 abiertas",
                                class_name="rounded-full bg-[#f0f2ed] px-2.5 py-1 text-[11px] font-medium text-[#738079]",
                            ),
                            class_name="flex items-center justify-between gap-3",
                        ),
                        rx.el.div(
                            rx.icon(
                                "circle_check",
                                class_name="h-5 w-5 text-[#3d9678]",
                            ),
                            rx.el.div(
                                rx.el.p(
                                    "Todo en orden",
                                    class_name="text-sm font-semibold text-[#36544e]",
                                ),
                                rx.el.p(
                                    "No hay revisiones pendientes todavía.",
                                    class_name="mt-1 text-xs leading-5 text-[#7b8982]",
                                ),
                            ),
                            class_name="mt-6 flex items-start gap-3 rounded-xl border border-dashed border-[#cddbcf] bg-[#f6faf5] p-4",
                        ),
                        rx.el.a(
                            "Ver el flujo clínico",
                            rx.icon("chevron-right", class_name="h-4 w-4"),
                            href="/individual",
                            class_name="mt-5 flex items-center gap-1 text-sm font-semibold text-[#2d7a68] hover:text-[#174e50]",
                        ),
                        class_name="rounded-2xl border border-[#dce4dc] bg-[#fbfaf6] p-5 sm:p-6",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.icon(
                                "notebook-pen",
                                class_name="h-4 w-4 text-[#ad7619]",
                            ),
                            rx.el.p(
                                "Nota de expediente",
                                class_name="text-xs font-semibold uppercase tracking-[0.12em] text-[#936518]",
                            ),
                            class_name="flex items-center gap-2",
                        ),
                        rx.el.p(
                            "La vista de riesgo es orientativa y no sustituye el juicio clínico. Completa la evaluación para activar señales y recomendaciones.",
                            class_name="mt-3 text-sm leading-6 text-[#66756f]",
                        ),
                        class_name="rounded-2xl border border-[#eadbb8] bg-[#fbf6e9] p-5 sm:p-6",
                    ),
                    class_name="flex flex-col gap-4",
                ),
                class_name="min-w-0",
            ),
            class_name="grid grid-cols-1 gap-4 xl:grid-cols-3",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    "Rutas de trabajo",
                    class_name="text-base font-semibold text-[#173f46]",
                ),
                rx.el.p(
                    "Accesos directos para continuar el flujo del expediente.",
                    class_name="mt-1 text-sm text-[#71807a]",
                ),
                class_name="mb-5",
            ),
            rx.el.div(
                workflow_card(
                    "user-round",
                    "01",
                    "Evaluación individual",
                    "Captura el contexto y los hallazgos de un caso.",
                    "/individual",
                ),
                workflow_card(
                    "scan-search",
                    "02",
                    "Diagnóstico",
                    "Revisa el resultado, la explicación y las señales clínicas.",
                    "/diagnosis",
                ),
                workflow_card(
                    "layers-3",
                    "03",
                    "Procesamiento por lotes",
                    "Prepara importaciones y revisa el estado de cada registro.",
                    "/batches",
                ),
                workflow_card(
                    "database",
                    "04",
                    "Base de datos clínica",
                    "Consulta la trazabilidad de casos, ejecuciones y resultados.",
                    "/database",
                ),
                class_name="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4",
            ),
            class_name="rounded-2xl border border-[#dce4dc] bg-[#fbfaf6] p-5 sm:p-6",
        ),
        class_name="flex w-full flex-col gap-5",
    )
