import reflex as rx


def nav_link(icon: str, label: str, href: str) -> rx.Component:
    return rx.el.a(
        rx.icon(icon, class_name="h-4 w-4 shrink-0"),
        rx.el.span(label),
        href=href,
        class_name="group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-[#6b7775] transition-colors hover:bg-[#e8eee9] hover:text-[#174e50]",
    )


def clinical_shell(
    title: str, eyebrow: str, content: rx.Component
) -> rx.Component:
    return rx.el.div(
        rx.el.aside(
            rx.el.div(
                rx.el.a(
                    rx.el.div(
                        rx.icon(
                            "heart-pulse", class_name="h-5 w-5 text-[#f5b544]"
                        ),
                        class_name="flex h-10 w-10 items-center justify-center rounded-xl bg-[#174e50]",
                    ),
                    rx.el.div(
                        rx.el.p(
                            "AmylAI",
                            class_name="text-base font-semibold tracking-tight text-[#174e50]",
                        ),
                        rx.el.p(
                            "Clinical workspace",
                            class_name="text-[10px] font-medium uppercase tracking-[0.16em] text-[#8a9791]",
                        ),
                        class_name="min-w-0",
                    ),
                    href="/",
                    class_name="flex items-center gap-3 border-b border-[#dce4dc] px-5 py-5",
                ),
                rx.el.div(
                    rx.el.p(
                        "Workspace",
                        class_name="px-3 text-[10px] font-semibold uppercase tracking-[0.18em] text-[#9aa39c]",
                    ),
                    rx.el.nav(
                        nav_link("layout-dashboard", "Tablero clínico", "/"),
                        nav_link("user-round", "Individual", "/individual"),
                        nav_link("scan-search", "Diagnóstico", "/diagnosis"),
                        nav_link("layers-3", "Lotes", "/batches"),
                        nav_link("database", "Base de datos", "/database"),
                        rx.el.div(
                            class_name="my-3 border-t border-[#dce4dc]",
                        ),
                        nav_link("book-open", "Guía clínica", "/guide"),
                        nav_link(
                            "flask-conical", "Estrés y validación", "/stress"
                        ),
                        class_name="flex flex-col gap-1",
                    ),
                    class_name="flex flex-1 flex-col gap-3 overflow-auto px-3 py-6",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.icon(
                            "shield-check", class_name="h-4 w-4 text-[#2d7a68]"
                        ),
                        rx.el.div(
                            rx.el.p(
                                "Entorno protegido",
                                class_name="text-xs font-semibold text-[#174e50]",
                            ),
                            rx.el.p(
                                "Sin credenciales externas",
                                class_name="mt-0.5 text-[11px] text-[#77837d]",
                            ),
                        ),
                        class_name="flex items-start gap-2.5",
                    ),
                    class_name="border-t border-[#dce4dc] px-5 py-4",
                ),
                class_name="flex h-full flex-col",
            ),
            class_name="hidden h-screen w-64 shrink-0 border-r border-[#dce4dc] bg-[#fbfaf6] lg:flex",
        ),
        rx.el.main(
            rx.el.header(
                rx.el.div(
                    rx.el.div(
                        rx.el.p(
                            eyebrow,
                            class_name="text-[11px] font-semibold uppercase tracking-[0.18em] text-[#ad7619]",
                        ),
                        rx.el.h1(
                            title,
                            class_name="mt-1 text-2xl font-semibold tracking-tight text-[#173f46] sm:text-3xl",
                        ),
                        class_name="min-w-0",
                    ),
                    rx.el.div(
                        rx.el.div(
                            class_name="h-2 w-2 rounded-full bg-[#3d9678]",
                        ),
                        rx.el.span(
                            "Sistema operativo",
                            class_name="text-xs font-medium text-[#526761]",
                        ),
                        class_name="hidden items-center gap-2 rounded-full border border-[#d8e4d9] bg-[#f3f8f2] px-3 py-2 sm:flex",
                    ),
                    class_name="flex items-start justify-between gap-4",
                ),
                rx.el.nav(
                    nav_link("layout-dashboard", "Inicio", "/"),
                    nav_link("user-round", "Individual", "/individual"),
                    nav_link("scan-search", "Diagnóstico", "/diagnosis"),
                    nav_link("layers-3", "Lotes", "/batches"),
                    nav_link("database", "Datos", "/database"),
                    nav_link("book-open", "Guía", "/guide"),
                    nav_link("flask-conical", "Estrés", "/stress"),
                    class_name="mt-5 flex flex-wrap gap-1 border-t border-[#e5e9e3] pt-3 lg:hidden",
                ),
                class_name="border-b border-[#dce4dc] bg-[#fbfaf6] px-5 py-5 sm:px-8 lg:px-10",
            ),
            rx.el.div(
                content,
                class_name="w-full flex-1 px-5 py-6 sm:px-8 sm:py-8 lg:px-10",
            ),
            class_name="flex min-h-screen min-w-0 flex-1 flex-col bg-[#f5f2ea]",
        ),
        class_name="flex min-h-screen w-full bg-[#f5f2ea] font-['Inter']",
    )
