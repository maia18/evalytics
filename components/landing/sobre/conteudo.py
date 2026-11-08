import flet as ft
from components.core.constants.constants import (
    COR_TEXTO_TITULO,
    COR_TEXTO_SECUNDARIO,
    COR_PRIMARIA,
)

def criar_sobre_conteudo() -> ft.Column:
    """Gera o conteúdo institucional da seção Sobre o Evalytics."""

    return ft.Column(
        spacing=18,
        controls=[
            
            # =========================================================
            # TÍTULO
            # =========================================================

            ft.Text(
                "Sobre",
                size=30,
                weight=ft.FontWeight.BOLD,
                color=COR_TEXTO_TITULO,
            ),

            # =========================================================
            # DESCRIÇÃO
            # =========================================================

            ft.Text(
                "O Evalytics foi pensado para centralizar o processo "
                "de avaliação institucional em uma única plataforma.",
                size=16,
                color=COR_TEXTO_SECUNDARIO,
            ),

            ft.Text(
                "A proposta é facilitar a coleta, organização e análise "
                "das informações produzidas pelas avaliações, permitindo "
                "que esses dados sejam acompanhados de forma mais estruturada.",
                size=15,
                color=COR_TEXTO_SECUNDARIO,
            ),

            # =========================================================
            # DESTAQUE
            # =========================================================

            ft.Container(
                margin=ft.Margin.only(top=6),
                padding=ft.Padding.only(left=16),
                border=ft.Border(
                    left=ft.BorderSide(
                        3,
                        COR_PRIMARIA,
                    ),
                ),
                content=ft.Text(
                    "Da avaliação à melhoria contínua.",
                    size=17,
                    weight=ft.FontWeight.BOLD,
                    color=COR_PRIMARIA,
                ),
            ),
        ],
    )