import flet as ft
from typing import Callable, Optional
from datetime import datetime
from components.landing.palette import PAGE, BORDER, TEXT, MUTED, ACCENT, MAX_CONTENT_WIDTH

def criar_rodape(
    ir_para_inicio: Optional[Callable] = None,
    ir_para_recursos: Optional[Callable] = None,
    ir_para_sobre: Optional[Callable] = None,
    mudar_tela: Optional[Callable[[str], None]] = None,
) -> ft.Container:
    """Cria uma faixa de rodapé compacta com marca e navegação útil."""

    marca = ft.Container(
        content=ft.Row(
            spacing=0,
            tight=True,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    "evalytics",
                    size=14,
                    weight=ft.FontWeight.W_700,
                    color=TEXT,
                ),
                ft.Text(
                    "_",
                    size=14,
                    weight=ft.FontWeight.W_700,
                    color=ACCENT,
                ),
            ],
        ),
        on_click=ir_para_inicio,
        ink=False,
    )

    assinatura = ft.Row(
        spacing=8,
        wrap=True,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            marca,
            ft.Text("©", size=10, color=MUTED),
            ft.Text(str(datetime.now().year), size=10, color=MUTED),
            ft.Text("Avaliação institucional orientada por dados", size=10, color=MUTED),
        ],
    )

    def link(texto: str, callback: Optional[Callable]) -> ft.TextButton:
        return ft.TextButton(
            texto,
            on_click=callback,
            style=ft.ButtonStyle(
                color={
                    ft.ControlState.DEFAULT: MUTED,
                    ft.ControlState.HOVERED: TEXT,
                },
                padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                overlay_color=ft.Colors.TRANSPARENT,
                text_style=ft.TextStyle(size=10),
            ),
        )

    navegacao = ft.Row(
        spacing=2,
        wrap=True,
        alignment=ft.MainAxisAlignment.END,
        controls=[
            link("Início", ir_para_inicio),
            link("Recursos", ir_para_recursos),
            link("Indicadores", lambda e: mudar_tela("/indicadores") if mudar_tela else None),
            link("Sobre", ir_para_sobre),
            link("Desenvolvedores", lambda e: mudar_tela("/desenvolvedores") if mudar_tela else None),
            link("Login", lambda e: mudar_tela("/login") if mudar_tela else None),
        ],
    )

    return ft.Container(
        bgcolor=PAGE,
        border=ft.Border(
            top=ft.BorderSide(1, BORDER),
        ),
        padding=ft.Padding.only(top=9, bottom=10, left=20, right=20),
        alignment=ft.Alignment.CENTER,
        content=ft.Container(
            width=MAX_CONTENT_WIDTH,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                wrap=True,
                spacing=8,
                controls=[
                    assinatura,
                    navegacao,
                ],
            ),
        ),
    )
