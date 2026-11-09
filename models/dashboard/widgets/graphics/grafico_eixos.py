import flet as ft

from components.core.constants.constants import CARD, BORDA, TEXTO_PRINCIPAL, TEXTO_SECUNDARIO
from components.core.theme.border_utils import criar_borda_uniforme


def criar_grafico_eixos(
    layout,
    medias_eixos: dict[int, float],
    nomes_eixos: dict[int, str],
    cores_barras: list[str],
    respostas_por_eixo: dict[int, int] | None = None,
    media_geral: float | None = None,
    altura: int | None = None,
) -> ft.Container:
    """Exibe médias por eixo na escala de 0 a 5, com volume e comparação."""
    respostas_por_eixo = respostas_por_eixo or {}
    eixos_ordenados = sorted(
        medias_eixos.items(), key=lambda item: item[1], reverse=True
    )

    linhas = []
    for indice, (eixo_id, media) in enumerate(eixos_ordenados):
        diferenca = (
            media - media_geral if media_geral is not None else None
        )
        comparacao = (
            f"{diferenca:+.1f} vs. média geral"
            if diferenca is not None
            else "Sem base para comparação"
        )
        cor = cores_barras[indice % len(cores_barras)] if cores_barras else None
        linhas.append(
            ft.Column(
                spacing=5,
                controls=[
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(
                                nomes_eixos.get(eixo_id, f"Eixo {eixo_id}"),
                                size=12,
                                max_lines=3,
                                weight="w500",
                                color=layout.cores[TEXTO_PRINCIPAL],
                            ),
                            ft.Text(
                                f"{media:.1f} / 5,0",
                                size=12,
                                weight="bold",
                                color=layout.cores[TEXTO_PRINCIPAL],
                            ),
                        ],
                    ),
                    ft.ProgressBar(
                        value=max(0.0, min((media - 1.0) / 4.0, 1.0)),
                        color=cor,
                        bgcolor=ft.Colors.with_opacity(0.16, cor),
                        bar_height=10,
                        border_radius=8,
                    ),
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(
                                f"{respostas_por_eixo.get(eixo_id, 0)} respostas",
                                size=10,
                                color=layout.cores[TEXTO_SECUNDARIO],
                            ),
                            ft.Text(
                                comparacao,
                                size=10,
                                max_lines=3,
                                color=layout.cores[TEXTO_SECUNDARIO],
                            ),
                        ],
                    ),
                ],
            )
        )

    if not linhas:
        linhas = [
            ft.Text(
                "Não há respostas válidas para os filtros selecionados.",
                color=layout.cores[TEXTO_SECUNDARIO],
            )
        ]

    return ft.Container(
        height=altura,
        bgcolor=layout.cores[CARD],
        padding=8,
        border_radius=8,
        border=criar_borda_uniforme(layout.cores[BORDA]),
        content=ft.Column(
            expand=True,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            spacing=10,
            controls=[
                ft.Column(
                    spacing=4,
                    controls=[
                        ft.Text(
                            "Desempenho médio por eixo",
                            size=15,
                            weight="bold",
                            color=layout.cores[TEXTO_PRINCIPAL],
                        ),
                        ft.Text(
                            "Média das respostas válidas em cada eixo.",
                            size=11,
                            color=layout.cores[TEXTO_SECUNDARIO],
                        ),
                    ],
                ),
                *linhas,
                ft.Text(
                    "Escala de avaliação: 1,0 a 5,0",
                    size=9,
                    color=layout.cores[TEXTO_SECUNDARIO],
                ),
            ],
        ),
    )
