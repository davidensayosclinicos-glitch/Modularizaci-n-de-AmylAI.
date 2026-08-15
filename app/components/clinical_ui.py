import reflex as rx


def panel(*children, class_name: str = "") -> rx.Component:
    return rx.el.div(
        *children,
        class_name=f"rounded-2xl border border-[#dce4dc] bg-[#fbfaf6] p-5 sm:p-6 {class_name}",
    )


def panel_heading(
    icon: str, title: str, description: str, badge: rx.Var | str = ""
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon(icon, class_name="h-4 w-4 text-[#174e50]"),
                rx.el.p(
                    title, class_name="text-base font-semibold text-[#173f46]"
                ),
                class_name="flex items-center gap-2",
            ),
            rx.el.p(
                description,
                class_name="mt-1 text-sm leading-6 text-[#71807a]",
            ),
            class_name="min-w-0",
        ),
        rx.el.span(
            badge,
            class_name="shrink-0 rounded-full bg-[#f0f2ed] px-2.5 py-1 text-[11px] font-medium text-[#738079]",
        ),
        class_name="mb-5 flex items-start justify-between gap-4",
    )


def stat_tile(
    label: str, value: rx.Var | str, value_class: str
) -> rx.Component:
    return rx.el.div(
        rx.el.p(
            label,
            class_name="text-[11px] font-semibold uppercase tracking-[0.13em] text-[#8a9791]",
        ),
        rx.el.p(value, class_name=value_class),
        class_name="w-full rounded-xl border border-[#dce4dc] bg-[#fbfaf6] p-4",
    )


def risk_pill(level: rx.Var, label: rx.Var) -> rx.Component:
    return rx.el.span(
        label,
        class_name=rx.match(
            level,
            (
                "low",
                "w-fit rounded-full bg-[#e6f0e7] px-2.5 py-1 text-[11px] font-semibold text-[#2d7a68]",
            ),
            (
                "moderate",
                "w-fit rounded-full bg-[#f4ead1] px-2.5 py-1 text-[11px] font-semibold text-[#936518]",
            ),
            (
                "high",
                "w-fit rounded-full bg-[#f8e3dc] px-2.5 py-1 text-[11px] font-semibold text-[#9b5545]",
            ),
            "w-fit rounded-full bg-[#f0f2ed] px-2.5 py-1 text-[11px] font-semibold text-[#738079]",
        ),
    )


def status_pill(status: rx.Var) -> rx.Component:
    return rx.el.span(
        status,
        class_name=rx.match(
            status,
            (
                "processed",
                "w-fit rounded-full bg-[#e6f0e7] px-2.5 py-1 text-[11px] font-semibold text-[#2d7a68]",
            ),
            (
                "completed",
                "w-fit rounded-full bg-[#e6f0e7] px-2.5 py-1 text-[11px] font-semibold text-[#2d7a68]",
            ),
            (
                "analyzed",
                "w-fit rounded-full bg-[#e6f0e7] px-2.5 py-1 text-[11px] font-semibold text-[#2d7a68]",
            ),
            (
                "error",
                "w-fit rounded-full bg-[#f8e3dc] px-2.5 py-1 text-[11px] font-semibold text-[#9b5545]",
            ),
            (
                "failed",
                "w-fit rounded-full bg-[#f8e3dc] px-2.5 py-1 text-[11px] font-semibold text-[#9b5545]",
            ),
            (
                "completed_with_errors",
                "w-fit rounded-full bg-[#f4ead1] px-2.5 py-1 text-[11px] font-semibold text-[#936518]",
            ),
            (
                "processing",
                "w-fit rounded-full bg-[#f4ead1] px-2.5 py-1 text-[11px] font-semibold text-[#936518]",
            ),
            "w-fit rounded-full bg-[#f0f2ed] px-2.5 py-1 text-[11px] font-semibold text-[#738079]",
        ),
    )


def select_field(
    label: str,
    value: rx.Var,
    options: rx.Var,
    on_change: rx.event.EventType,
) -> rx.Component:
    return rx.el.label(
        rx.el.span(
            label,
            class_name="mb-2 block text-xs font-semibold text-[#526761]",
        ),
        rx.el.div(
            rx.el.select(
                rx.foreach(
                    options,
                    lambda option: rx.el.option(option[0], value=option[1]),
                ),
                value=value,
                on_change=on_change,
                class_name="w-full appearance-none rounded-xl border border-[#cedbd0] bg-[#fbfaf6] px-3.5 py-2.5 text-sm text-[#173f46] outline-hidden focus:border-[#3d9678] focus:ring-2 focus:ring-[#dcefe0]",
            ),
            rx.icon(
                "chevron-down",
                class_name="pointer-events-none absolute right-3 top-3 h-4 w-4 text-[#8a9791]",
            ),
            class_name="relative",
        ),
        class_name="block",
    )
