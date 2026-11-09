import flet as ft
from components.core.constants.constants import (
    BORDA,
    CARD,
    TEXTO_PRINCIPAL,
    TEXTO_SECUNDARIO,
)
from components.core.theme.border_utils import criar_borda_uniforme

def criar_kpi_card(
    layout,
    titulo: str,
    valor: str,
    icone: str,
    cor_icone: str,
    col: dict[str, int] | None = None,
) -> ft.Container:
    """Constrói um cartão numérico de KPI."""

    return ft.Container(
        col=col,
        height=96,
        bgcolor=layout.cores[CARD],
        padding=12,
        border_radius=8,
        border=criar_borda_uniforme(
            layout.cores[BORDA]
        ),
        content=ft.Column(
            spacing=8,
            controls=[
                ft.Row(
                    alignment=(
                        ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    controls=[
                        ft.Text(
                            titulo,
                            size=10,
                            max_lines=2,
                            expand=1,
                            color=layout.cores[
                                TEXTO_SECUNDARIO
                            ],
                            weight="w500",
                        ),
                        ft.Icon(
                            icone,
                            color=cor_icone,
                            size=16,
                        ),
                    ],
                ),
                ft.Text(
                    valor,
                    size=24,
                    weight="bold",
                    color=layout.cores[
                        TEXTO_PRINCIPAL
                    ],
                ),
            ],
        ),
    )
