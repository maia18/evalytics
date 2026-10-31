import flet as ft
from typing import Callable, Optional
from components.landing.palette import PAGE, BORDER, TEXT, MUTED, ACCENT, MAX_CONTENT_WIDTH

def criar_rodape(ir_para_inicio: Optional[Callable] = None) -> ft.Container:
    """Cria o rodapé minimalista com a marca e a descrição."""

    marca = ft.Container(
        content=ft.Row(
            spacing=0,
            tight=True,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    "evalytics",
                    size=16,
                    weight=ft.FontWeight.W_700,
                    color=TEXT,
                ),
                ft.Text(
                    "_",
                    size=16,
                    weight=ft.FontWeight.W_700,
                    color=ACCENT,
                ),
            ],
        ),
        on_click=ir_para_inicio,
        ink=False,
    )

    descricao = ft.Text(
        "Avaliações organizadas por curso e eixo.",
        size=12,
        color=MUTED,
    )

    return ft.Container(
        bgcolor=PAGE,
        border=ft.Border(
            top=ft.BorderSide(1, BORDER),
        ),
        padding=ft.Padding.only(top=18, bottom=26, left=24, right=24),
        alignment=ft.Alignment.CENTER,
        content=ft.Container(
            width=MAX_CONTENT_WIDTH,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                wrap=True,
                controls=[
                    marca,
                    descricao,
                ],
            ),
        ),
    )
