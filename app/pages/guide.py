import reflex as rx

from app.components.clinical_shell import clinical_shell
from app.components.clinical_ui import panel, panel_heading
from app.states.guide_state import GuideItem, GuideSection, GuideState


def section_button(item: GuideSection) -> rx.Component:
    return rx.el.button(
        rx.icon(item["icon"], class_name="h-4 w-4 shrink-0"),
        rx.el.div(
            rx.el.p(item["label"], class_name="text-sm font-semibold"),
            rx.el.p(
                item["caption"],
                class_name="mt-0.5 text-[11px] leading-4 text-[#8a9791]",
            ),
            class_name="min-w-0 text-left",
        ),
        type="button",
        on_click=lambda: GuideState.select_section(item["id"]),
        class_name=rx.cond(
            GuideState.section == item["id"],
            "flex w-full items-start gap-3 rounded-xl border border-[#a9c4b1] bg-[#e7efe7] px-3.5 py-3 text-[#174e50] transition-colors",
            "flex w-full items-start gap-3 rounded-xl border border-[#dce4dc] bg-[#fbfaf6] px-3.5 py-3 text-[#66756f] transition-colors hover:border-[#a9c4b1] hover:bg-[#f2f7f1]",
        ),
    )


def guide_card(item: GuideItem) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon(item["icon"], class_name="h-4 w-4 text-[#174e50]"),
                class_name="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-[#e8eee9]",
            ),
            rx.el.p(
                item["title"],
                class_name="text-sm font-semibold text-[#173f46]",
            ),
            class_name="flex items-center gap-3",
        ),
        rx.el.p(
            item["body"],
            class_name="mt-3 text-sm leading-6 text-[#66756f]",
        ),
        class_name="rounded-xl border border-[#dce4dc] bg-[#fbfaf6] p-4",
    )


def index_panel() -> rx.Component:
    return panel(
        panel_heading(
            "book-open",
            "Índice de la guía",
            "Cinco secciones navegables para el uso responsable del sistema.",
            GuideState.sections.length().to_string(),
        ),
        rx.el.nav(
            rx.foreach(GuideState.sections, section_button),
            class_name="flex w-full min-w-0 flex-col gap-2",
        ),
        rx.el.div(
            rx.icon("shield-check", class_name="h-4 w-4 text-[#2d7a68]"),
            rx.el.p(
                "Lectura orientativa: la decisión clínica siempre es humana.",
                class_name="text-xs leading-5 text-[#526761]",
            ),
            class_name="mt-5 flex items-start gap-2.5 rounded-xl border border-[#d8e4d9] bg-[#edf5ed] p-4",
        ),
    )


def content_panel() -> rx.Component:
    return panel(
        rx.el.div(
            rx.el.div(
                rx.el.span(
                    GuideState.section_caption,
                    class_name="text-[11px] font-semibold uppercase tracking-[0.16em] text-[#ad7619]",
                ),
                rx.el.h2(
                    GuideState.section_label,
                    class_name="mt-2 text-2xl font-semibold tracking-tight text-[#173f46]",
                ),
                class_name="min-w-0",
            ),
            rx.el.span(
                f"{GuideState.items.length()} apuntes",
                class_name="shrink-0 rounded-full bg-[#f0f2ed] px-2.5 py-1 text-[11px] font-medium text-[#738079]",
            ),
            class_name="mb-5 flex items-start justify-between gap-4",
        ),
        rx.el.div(
            rx.foreach(GuideState.items, guide_card),
            class_name="grid grid-cols-1 gap-4 md:grid-cols-2",
        ),
        rx.el.div(
            rx.el.a(
                rx.icon("user-round-plus", class_name="h-4 w-4"),
                "Abrir evaluación individual",
                href="/individual",
                class_name="flex items-center gap-2 rounded-xl bg-[#174e50] px-4 py-2.5 text-sm font-semibold text-[#fbfaf6] hover:bg-[#123f41]",
            ),
            rx.el.a(
                rx.icon("flask-conical", class_name="h-4 w-4"),
                "Validar el comportamiento",
                href="/stress",
                class_name="flex items-center gap-2 rounded-xl border border-[#c8d7cb] bg-[#fbfaf6] px-4 py-2.5 text-sm font-semibold text-[#174e50] hover:bg-[#eef4ed]",
            ),
            class_name="mt-5 flex flex-wrap gap-3 border-t border-[#e5e9e3] pt-5",
        ),
    )


def guide_page() -> rx.Component:
    return clinical_shell(
        "Guía clínica",
        "05 · Referencia de trabajo",
        rx.el.div(
            rx.el.div(
                rx.el.span(
                    "Marco de uso",
                    class_name="text-[11px] font-semibold uppercase tracking-[0.16em] text-[#ad7619]",
                ),
                rx.el.h2(
                    "Una lectura estructurada, no una caja negra.",
                    class_name="mt-3 max-w-2xl text-2xl font-semibold leading-tight text-[#173f46] sm:text-3xl",
                ),
                rx.el.p(
                    "Cada sección explica cómo capturar, interpretar y auditar un caso sin perder de vista los límites del sistema.",
                    class_name="mt-3 max-w-2xl text-sm leading-6 text-[#66756f] sm:text-base",
                ),
                class_name="rounded-2xl border border-[#dce4dc] bg-[#e7efe7] p-6 sm:p-8",
            ),
            rx.el.div(
                rx.el.div(index_panel(), class_name="min-w-0"),
                rx.el.div(content_panel(), class_name="min-w-0"),
                class_name="grid grid-cols-1 gap-5 xl:grid-cols-[minmax(18rem,0.35fr)_minmax(0,1fr)]",
            ),
            class_name="flex w-full flex-col gap-5",
        ),
    )
