import reflex as rx

from app.components.clinical_shell import clinical_shell
from app.components.dashboard import dashboard_overview
from app.pages.batches import batches_page
from app.pages.database import database_page
from app.pages.diagnosis import diagnosis_page
from app.pages.individual import individual_page
from app.pages.guide import guide_page
from app.pages.stress import stress_page
from app.states.database_state import DatabaseState
from app.states.stress_state import StressState


def index() -> rx.Component:
    return clinical_shell(
        "Tablero clínico",
        "AmylAI · Centro de operaciones",
        dashboard_overview(),
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(
            rel="preconnect",
            href="https://fonts.gstatic.com",
            cross_origin="",
        ),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(index, route="/")
app.add_page(individual_page, route="/individual")
app.add_page(diagnosis_page, route="/diagnosis")
app.add_page(batches_page, route="/batches")
app.add_page(database_page, route="/database", on_load=DatabaseState.load_data)
app.add_page(guide_page, route="/guide")
app.add_page(stress_page, route="/stress", on_load=StressState.run_suite)
