import reflex as rx

from app.components.clinical_shell import clinical_shell
from app.components.clinical_ui import (
    panel,
    panel_heading,
    risk_pill,
    select_field,
    stat_tile,
)
from app.services.validation_lab import CalibrationPoint, Scenario
from app.states.stress_state import StressState


def controls_panel() -> rx.Component:
    return panel(
        panel_heading(
            "sliders-horizontal",
            "Diseño del experimento",
            "Cohorte sintética generada localmente con semilla reproducible.",
            rx.cond(StressState.is_running, "Ejecutando...", "Listo"),
        ),
        rx.el.div(
            select_field(
                "Tamaño de cohorte",
                StressState.scenario_count,
                StressState.count_options,
                StressState.set_scenario_count,
            ),
            select_field(
                "Prevalencia simulada",
                StressState.positive_ratio,
                StressState.ratio_options,
                StressState.set_positive_ratio,
            ),
            rx.el.label(
                rx.el.span(
                    "Semilla",
                    class_name="mb-2 block text-xs font-semibold text-[#526761]",
                ),
                rx.el.input(
                    type="number",
                    default_value=StressState.seed,
                    on_change=StressState.set_seed.debounce(400),
                    class_name="w-full rounded-xl border border-[#cedbd0] bg-[#fbfaf6] px-3.5 py-2.5 text-sm text-[#173f46] outline-hidden focus:border-[#3d9678] focus:ring-2 focus:ring-[#dcefe0]",
                ),
                class_name="block",
            ),
            rx.el.label(
                rx.el.span(
                    f"Umbral de positividad · {StressState.threshold_value:.0f}/100",
                    class_name="mb-2 block text-xs font-semibold text-[#526761]",
                ),
                rx.el.input(
                    type="range",
                    min="5",
                    max="95",
                    step="5",
                    default_value=StressState.threshold,
                    key=StressState.threshold,
                    on_change=StressState.set_threshold.throttle(300),
                    class_name="mt-3 w-full accent-[#174e50]",
                ),
                class_name="block",
            ),
            class_name="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4",
        ),
        rx.cond(
            StressState.is_running,
            rx.el.div(
                rx.spinner(size="2"),
                rx.el.span(
                    StressState.stage,
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
                    StressState.is_running,
                    "Ejecutando...",
                    "Ejecutar validación",
                ),
                type="button",
                disabled=StressState.is_running,
                on_click=StressState.run_suite,
                class_name="flex items-center gap-2 rounded-xl bg-[#174e50] px-4 py-2.5 text-sm font-semibold text-[#fbfaf6] hover:bg-[#123f41] disabled:opacity-60",
            ),
            rx.el.button(
                rx.icon("dices", class_name="h-4 w-4"),
                "Nueva semilla",
                type="button",
                on_click=StressState.shuffle_seed,
                class_name="flex items-center gap-2 rounded-xl border border-[#c8d7cb] bg-[#fbfaf6] px-4 py-2.5 text-sm font-semibold text-[#174e50] hover:bg-[#eef4ed]",
            ),
            rx.el.button(
                rx.icon("rotate-ccw", class_name="h-4 w-4"),
                "Restablecer",
                type="button",
                on_click=StressState.reset_suite,
                class_name="flex items-center gap-2 rounded-xl border border-[#c8d7cb] bg-[#fbfaf6] px-4 py-2.5 text-sm font-semibold text-[#174e50] hover:bg-[#eef4ed]",
            ),
            class_name="mt-5 flex flex-wrap gap-3",
        ),
    )


def metrics_row() -> rx.Component:
    return rx.el.div(
        stat_tile(
            "Sensibilidad",
            f"{StressState.metrics['sensitivity']:.1f}%",
            "mt-2 text-3xl font-semibold text-[#2d7a68]",
        ),
        stat_tile(
            "Especificidad",
            f"{StressState.metrics['specificity']:.1f}%",
            "mt-2 text-3xl font-semibold text-[#174e50]",
        ),
        stat_tile(
            "Precisión (VPP)",
            f"{StressState.metrics['precision']:.1f}%",
            "mt-2 text-3xl font-semibold text-[#936518]",
        ),
        stat_tile(
            "Exactitud",
            f"{StressState.metrics['accuracy']:.1f}%",
            "mt-2 text-3xl font-semibold text-[#41616a]",
        ),
        class_name="grid grid-cols-2 gap-4 md:grid-cols-4",
    )


def secondary_metrics() -> rx.Component:
    return panel(
        panel_heading(
            "chart-column",
            "Análisis estadístico",
            "Discriminación, calibración y balance de errores sobre la cohorte evaluada.",
            f"{StressState.metrics['total']} casos",
        ),
        rx.el.div(
            stat_tile(
                "AUC (ROC)",
                f"{StressState.metrics['auc']:.1f}%",
                "mt-2 text-2xl font-semibold text-[#2d7a68]",
            ),
            stat_tile(
                "F1",
                f"{StressState.metrics['f1']:.1f}%",
                "mt-2 text-2xl font-semibold text-[#174e50]",
            ),
            stat_tile(
                "VPN",
                f"{StressState.metrics['npv']:.1f}%",
                "mt-2 text-2xl font-semibold text-[#41616a]",
            ),
            stat_tile(
                "Brier score",
                f"{StressState.metrics['brier']:.3f}",
                "mt-2 text-2xl font-semibold text-[#936518]",
            ),
            stat_tile(
                "Error de calibración",
                f"{StressState.metrics['calibration_error']:.1f} pts",
                "mt-2 text-2xl font-semibold text-[#9b5545]",
            ),
            stat_tile(
                "Tasa de error",
                f"{StressState.error_rate:.1f}%",
                "mt-2 text-2xl font-semibold text-[#9b5545]",
            ),
            class_name="grid grid-cols-2 gap-3 md:grid-cols-3",
        ),
        rx.el.div(
            rx.el.p(
                "Matriz de confusión",
                class_name="text-[11px] font-semibold uppercase tracking-[0.12em] text-[#8a9791]",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.p("VP", class_name="text-xs text-[#71807a]"),
                    rx.el.p(
                        StressState.metrics["tp"].to_string(),
                        class_name="text-xl font-semibold text-[#2d7a68]",
                    ),
                    class_name="rounded-xl border border-[#d8e4d9] bg-[#edf5ed] p-3",
                ),
                rx.el.div(
                    rx.el.p("FP", class_name="text-xs text-[#71807a]"),
                    rx.el.p(
                        StressState.metrics["fp"].to_string(),
                        class_name="text-xl font-semibold text-[#9b5545]",
                    ),
                    class_name="rounded-xl border border-[#ecd5cd] bg-[#fdf3ef] p-3",
                ),
                rx.el.div(
                    rx.el.p("FN", class_name="text-xs text-[#71807a]"),
                    rx.el.p(
                        StressState.metrics["fn"].to_string(),
                        class_name="text-xl font-semibold text-[#9b5545]",
                    ),
                    class_name="rounded-xl border border-[#ecd5cd] bg-[#fdf3ef] p-3",
                ),
                rx.el.div(
                    rx.el.p("VN", class_name="text-xs text-[#71807a]"),
                    rx.el.p(
                        StressState.metrics["tn"].to_string(),
                        class_name="text-xl font-semibold text-[#174e50]",
                    ),
                    class_name="rounded-xl border border-[#d8e4d9] bg-[#edf5ed] p-3",
                ),
                class_name="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-4",
            ),
            class_name="mt-5 rounded-xl border border-[#dce4dc] bg-[#fbfaf6] p-4",
        ),
        rx.el.p(
            f"Puntuación media: {StressState.metrics['mean_score_positive']:.1f}/100 en la cohorte con enfermedad y {StressState.metrics['mean_score_control']:.1f}/100 en controles; confianza media {StressState.metrics['mean_confidence']:.1f}%.",
            class_name="mt-4 border-l-2 border-[#dfe9df] pl-3 text-sm leading-6 text-[#66756f]",
        ),
    )


def _legend_item(color_class: str, label: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(class_name=f"h-2.5 w-2.5 rounded-full {color_class}"),
        rx.el.span(label, class_name="text-xs font-medium text-[#587069]"),
        class_name="flex items-center gap-2",
    )


def distribution_chart() -> rx.Component:
    return panel(
        panel_heading(
            "chart-bar",
            "Distribución por nivel de riesgo",
            "Cómo se reparten casos con enfermedad y controles en cada nivel.",
            "Recuento",
        ),
        rx.el.div(
            rx.recharts.bar_chart(
                rx.recharts.cartesian_grid(
                    horizontal=True, vertical=False, class_name="opacity-25"
                ),
                rx.recharts.graphing_tooltip(),
                rx.recharts.bar(
                    data_key="positivos",
                    fill="#174e50",
                    radius=[6, 6, 0, 0],
                ),
                rx.recharts.bar(
                    data_key="controles",
                    fill="#e0a53a",
                    radius=[6, 6, 0, 0],
                ),
                rx.recharts.x_axis(
                    data_key="level",
                    axis_line=False,
                    tick_line=False,
                    custom_attrs={"fontSize": "12px"},
                ),
                rx.recharts.y_axis(
                    axis_line=False,
                    tick_line=False,
                    allow_decimals=False,
                    custom_attrs={"fontSize": "12px"},
                ),
                data=StressState.distribution,
                width="100%",
                height=300,
                min_width=300,
                margin={"left": 10, "right": 20, "top": 15},
            ),
            class_name="h-[19rem] w-full min-w-[300px]",
        ),
        rx.el.div(
            _legend_item("bg-[#174e50]", "Con enfermedad"),
            _legend_item("bg-[#e0a53a]", "Controles"),
            class_name="mt-3 flex flex-wrap items-center justify-center gap-5 border-t border-[#e5e9e3] pt-4",
        ),
    )


def roc_chart() -> rx.Component:
    return panel(
        panel_heading(
            "trending-up",
            "Curva ROC del motor local",
            "Barrido de umbrales sobre la puntuación combinada (0 a 100).",
            f"AUC {StressState.metrics['auc']:.1f}%",
        ),
        rx.el.div(
            rx.recharts.line_chart(
                rx.recharts.cartesian_grid(
                    horizontal=True, vertical=False, class_name="opacity-25"
                ),
                rx.recharts.graphing_tooltip(),
                rx.recharts.line(
                    data_key="tpr",
                    stroke="#174e50",
                    type_="monotone",
                    dot=False,
                    stroke_width=2,
                ),
                rx.recharts.x_axis(
                    data_key="fpr",
                    type_="number",
                    domain=[0, 100],
                    axis_line=False,
                    tick_line=False,
                    custom_attrs={"fontSize": "12px"},
                ),
                rx.recharts.y_axis(
                    domain=[0, 100],
                    axis_line=False,
                    tick_line=False,
                    custom_attrs={"fontSize": "12px"},
                ),
                data=StressState.roc,
                width="100%",
                height=300,
                min_width=300,
                margin={"left": 10, "right": 20, "top": 15},
            ),
            class_name="h-[19rem] w-full min-w-[300px]",
        ),
        rx.el.p(
            "Eje X: falsos positivos (%). Eje Y: verdaderos positivos (%).",
            class_name="mt-3 border-t border-[#e5e9e3] pt-4 text-xs text-[#8a9791]",
        ),
    )


def calibration_row(item: CalibrationPoint) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.p(
                f"Puntuación {item['bucket']}",
                class_name="text-sm font-semibold text-[#36544e]",
            ),
            rx.el.span(
                f"{item['count']} casos",
                class_name="ml-auto rounded-full bg-[#f0f2ed] px-2 py-0.5 text-[11px] font-medium text-[#738079]",
            ),
            class_name="flex items-center gap-3",
        ),
        rx.el.div(
            rx.el.div(
                class_name="h-full rounded-full bg-[#174e50]",
                style={"width": f"{item['expected']}%"},
            ),
            class_name="mt-3 h-2 w-full overflow-hidden rounded-full bg-[#e6ebe4]",
        ),
        rx.el.div(
            rx.el.div(
                class_name="h-full rounded-full bg-[#e0a53a]",
                style={"width": f"{item['observed']}%"},
            ),
            class_name="mt-2 h-2 w-full overflow-hidden rounded-full bg-[#e6ebe4]",
        ),
        rx.el.p(
            f"Esperado {item['expected']:.1f}% · observado {item['observed']:.1f}%",
            class_name="mt-2 text-xs text-[#8a9791]",
        ),
        class_name="rounded-xl border border-[#dce4dc] bg-[#fbfaf6] p-4",
    )


def calibration_panel() -> rx.Component:
    return panel(
        panel_heading(
            "gauge",
            "Calibración por tramo de puntuación",
            "Compara la puntuación media declarada con la prevalencia observada.",
            f"±{StressState.metrics['calibration_error']:.1f} pts",
        ),
        rx.el.div(
            rx.foreach(StressState.calibration, calibration_row),
            class_name="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3",
        ),
        rx.el.div(
            _legend_item("bg-[#174e50]", "Puntuación esperada"),
            _legend_item("bg-[#e0a53a]", "Prevalencia observada"),
            class_name="mt-4 flex flex-wrap items-center gap-5 border-t border-[#e5e9e3] pt-4",
        ),
    )


def _th(label: str) -> rx.Component:
    return rx.el.th(
        label,
        class_name="px-4 py-3 text-left text-[11px] font-semibold uppercase tracking-[0.12em] text-[#8a9791]",
    )


def outcome_pill(outcome: rx.Var, label: rx.Var) -> rx.Component:
    return rx.el.span(
        label,
        class_name=rx.match(
            outcome,
            (
                "tp",
                "w-fit rounded-full bg-[#e6f0e7] px-2.5 py-1 text-[11px] font-semibold text-[#2d7a68]",
            ),
            (
                "tn",
                "w-fit rounded-full bg-[#f0f2ed] px-2.5 py-1 text-[11px] font-semibold text-[#738079]",
            ),
            (
                "fp",
                "w-fit rounded-full bg-[#f4ead1] px-2.5 py-1 text-[11px] font-semibold text-[#936518]",
            ),
            (
                "fn",
                "w-fit rounded-full bg-[#f8e3dc] px-2.5 py-1 text-[11px] font-semibold text-[#9b5545]",
            ),
            "w-fit rounded-full bg-[#f0f2ed] px-2.5 py-1 text-[11px] font-semibold text-[#738079]",
        ),
    )


def scenario_row(item: Scenario) -> rx.Component:
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
        rx.el.td(item["cohort"], class_name="px-4 py-3 text-sm text-[#66756f]"),
        rx.el.td(
            f"{item['age']} · {item['sex_display']}",
            class_name="px-4 py-3 text-sm text-[#66756f]",
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
            f"{item['confidence']:.0f}%",
            class_name="px-4 py-3 text-sm text-[#66756f]",
        ),
        rx.el.td(
            f"{item['symptoms'].length()} / {item['red_flags'].length()}",
            class_name="px-4 py-3 text-sm text-[#66756f]",
        ),
        rx.el.td(
            outcome_pill(item["outcome"], item["outcome_label"]),
            class_name="px-4 py-3",
        ),
        class_name="border-b border-[#eef1ec] hover:bg-[#f6faf5]",
    )


def scenarios_panel() -> rx.Component:
    return panel(
        panel_heading(
            "table",
            "Escenarios sintéticos evaluados",
            "Cada fila es un caso generado localmente y puntuado por el motor clínico.",
            f"{StressState.visible_count} en vista",
        ),
        rx.el.div(
            select_field(
                "Filtrar por resultado",
                StressState.outcome_filter,
                StressState.outcome_options,
                StressState.set_outcome_filter,
            ),
            class_name="mb-4 max-w-xs",
        ),
        rx.cond(
            StressState.visible_count > 0,
            rx.el.div(
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            _th("Escenario"),
                            _th("Cohorte"),
                            _th("Paciente"),
                            _th("Riesgo"),
                            _th("Score"),
                            _th("Confianza"),
                            _th("Sínt./Flags"),
                            _th("Resultado"),
                            class_name="border-b border-[#dce4dc] bg-[#f3f6f1]",
                        )
                    ),
                    rx.el.tbody(
                        rx.foreach(StressState.filtered_scenarios, scenario_row)
                    ),
                    class_name="table-auto w-full",
                ),
                class_name="overflow-x-auto rounded-xl border border-[#dce4dc]",
            ),
            rx.el.div(
                rx.icon("inbox", class_name="h-6 w-6 text-[#8a9791]"),
                rx.el.p(
                    "Sin escenarios para este filtro",
                    class_name="mt-3 text-sm font-semibold text-[#36544e]",
                ),
                rx.el.p(
                    "Cambia el filtro o ejecuta la validación con otra semilla.",
                    class_name="mt-1 text-sm leading-6 text-[#71807a]",
                ),
                class_name="flex min-h-40 flex-col items-center justify-center rounded-xl border border-dashed border-[#cddbcf] bg-[#f6faf5] p-6 text-center",
            ),
        ),
        rx.el.p(
            "Se muestran hasta 40 escenarios; las métricas se calculan sobre la cohorte completa.",
            class_name="mt-4 text-xs text-[#8a9791]",
        ),
    )


def stress_page() -> rx.Component:
    return clinical_shell(
        "Estrés y validación",
        "06 · Calidad clínica",
        rx.el.div(
            rx.el.div(
                rx.el.span(
                    "Módulo de validación",
                    class_name="text-[11px] font-semibold uppercase tracking-[0.16em] text-[#ad7619]",
                ),
                rx.el.h2(
                    "Conoce cómo responde el sistema antes de confiar en él.",
                    class_name="mt-3 max-w-2xl text-2xl font-semibold leading-tight text-[#173f46] sm:text-3xl",
                ),
                rx.el.p(
                    "Cohortes sintéticas deterministas evaluadas por el mismo motor local, con métricas de discriminación y calibración calculadas sobre los resultados reales.",
                    class_name="mt-3 max-w-2xl text-sm leading-6 text-[#66756f] sm:text-base",
                ),
                class_name="rounded-2xl border border-[#dce4dc] bg-[#e7efe7] p-6 sm:p-8",
            ),
            controls_panel(),
            metrics_row(),
            rx.el.div(
                rx.el.div(distribution_chart(), class_name="min-w-0 flex-1"),
                rx.el.div(roc_chart(), class_name="min-w-0 flex-1"),
                class_name="flex flex-col gap-5 xl:flex-row",
            ),
            secondary_metrics(),
            calibration_panel(),
            scenarios_panel(),
            class_name="flex w-full flex-col gap-5",
        ),
    )
