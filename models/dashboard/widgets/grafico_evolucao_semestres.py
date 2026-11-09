import flet as ft

from components.core.constants.constants import (
    CARD,
    BORDA,
    TEXTO_PRINCIPAL,
    TEXTO_SECUNDARIO,
)
from components.core.theme.border_utils import criar_borda_uniforme


def criar_grafico_evolucao_semestres(
    layout, evolucao: list[dict], altura: int | None = None
) -> ft.Container:
    """Compara a média das respostas válidas entre semestres."""
    if evolucao:
        controles = [
            ft.Container(
                padding=ft.Padding.symmetric(vertical=5),
                content=ft.Column(
                    spacing=5,
                    controls=[
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text(item["semestre"], size=11),
                                ft.Text(
                                    f"{item['media_geral']:.1f}/5,0 · {item['respostas_validas']} resp.",
                                    size=10,
                                    color=layout.cores[TEXTO_SECUNDARIO],
                                ),
                            ],
                        ),
                        ft.ProgressBar(
                            value=max(
                                0.0,
                                min((item["media_geral"] - 1.0) / 4.0, 1.0),
                            ),
                            color=ft.Colors.BLUE_400,
                            bgcolor=ft.Colors.with_opacity(
                                0.14, ft.Colors.BLUE_400
                            ),
                            height=8,
                            border_radius=6,
                        ),
                    ],
                ),
            )
            for item in evolucao
        ]
    else:
        controles = [
            ft.Text(
                "Ainda não há avaliações com data e respostas válidas para comparar.",
                color=layout.cores[TEXTO_SECUNDARIO],
            )
        ]

    return ft.Container(
        height=altura,
        bgcolor=layout.cores[CARD],
        padding=14,
        border_radius=8,
        border=criar_borda_uniforme(layout.cores[BORDA]),
        content=ft.Column(
            alignment=ft.MainAxisAlignment.START,
            spacing=6,
            controls=[
                ft.Column(
                    spacing=4,
                    controls=[
                        ft.Text(
                            "Evolução por semestre",
                            size=14,
                            weight="bold",
                            color=layout.cores[TEXTO_PRINCIPAL],
                        ),
                        ft.Text(
                            "Média das respostas por semestre; respeita o curso selecionado e considera todos os semestres.",
                            size=10,
                            color=layout.cores[TEXTO_SECUNDARIO],
                        ),
                    ],
                ),
                *controles,
                ft.Text(
                    "Escala: 1,0 a 5,0",
                    size=9,
                    color=layout.cores[TEXTO_SECUNDARIO],
                ),
            ],
        ),
    )
