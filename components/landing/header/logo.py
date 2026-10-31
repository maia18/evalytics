import flet as ft
from typing import Callable, Optional
from components.landing.palette import TEXT, ACCENT

def criar_logo(ir_para_inicio: Optional[Callable] = None) -> ft.Container:
    """Cria a marca textual 'evalytics_' com o sublinhado na cor de destaque."""

    return ft.Container(
        content=ft.Row(
            spacing=0,
            tight=True,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    "evalytics",
                    size=19,
                    weight=ft.FontWeight.W_700,
                    color=TEXT,
                ),
                ft.Text(
                    "_",
                    size=19,
                    weight=ft.FontWeight.W_700,
                    color=ACCENT,
                ),
            ],
        ),
        on_click=ir_para_inicio,
        ink=False,
    )
