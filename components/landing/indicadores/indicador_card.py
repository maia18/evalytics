import flet as ft

from components.landing.palette import (
    SURFACE,
    BORDER,
    TEXT,
    MUTED,
    ROXO_CLARO,
)
from components.landing.indicadores.indicadores_config import (
    NOMES_EIXOS,
    CORES_EIXOS,
    CORES_CONCEITOS,
    ROTULOS_CONCEITOS,
)
def _badge_eixo(eixo_num: int) -> ft.Container:
    cor = CORES_EIXOS.get(eixo_num, ROXO_CLARO)
    nome = NOMES_EIXOS.get(eixo_num, f"Eixo {eixo_num}")
    return ft.Container(
        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
        bgcolor=ft.Colors.with_opacity(0.12, cor),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.35, cor)),
        border_radius=14,
        content=ft.Text(
            nome,
            size=11,
            weight=ft.FontWeight.W_600,
            color=cor,
        ),
    )

def _criar_card_indicador(item: dict, indice: int) -> ft.Container:
    eixo_num = item.get("eixo", 1)
    cor_eixo = CORES_EIXOS.get(eixo_num, ROXO_CLARO)
    titulo = item.get("titulo", "")
    descricao = item.get("descricao", "")
    criterios = item.get("criterios", {})

    detalhes_abertos = False

    criterios_coluna = ft.Column(
        spacing=8,
        visible=False,
        controls=[
            ft.Divider(height=1, color=BORDER),
            ft.Text(
                "Critérios de Avaliação (Conceitos 1 a 5):",
                size=12,
                weight=ft.FontWeight.W_600,
                color=TEXT,
            ),
        ],
    )

    for nivel in ["1", "2", "3", "4", "5"]:
        texto_criterio = criterios.get(nivel)
        if texto_criterio:
            cor_nivel = CORES_CONCEITOS.get(nivel, ROXO_CLARO)
            rotulo = ROTULOS_CONCEITOS.get(nivel, f"Critério {nivel}")
            criterios_coluna.controls.append(
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=12, vertical=8),
                    bgcolor=ft.Colors.with_opacity(0.05, cor_nivel),
                    border=ft.Border(
                        left=ft.BorderSide(3, cor_nivel),
                    ),
                    border_radius=ft.BorderRadius.only(
                        top_right=6,
                        bottom_right=6,
                    ),
                    content=ft.Column(
                        spacing=3,
                        controls=[
                            ft.Text(
                                rotulo,
                                size=11,
                                weight=ft.FontWeight.W_700,
                                color=cor_nivel,
                            ),
                            ft.Text(
                                texto_criterio,
                                size=12,
                                color=MUTED,
                                selectable=True,
                            ),
                        ],
                    ),
                )
            )

    btn_toggle = ft.TextButton(
        content=ft.Row(
            spacing=6,
            tight=True,
            controls=[
                ft.Text(
                    "Ver os 5 critérios de pontuação",
                    size=12,
                    weight=ft.FontWeight.W_600,
                    color=cor_eixo,
                ),
                ft.Icon(
                    ft.Icons.KEYBOARD_ARROW_DOWN_ROUNDED,
                    size=18,
                    color=cor_eixo,
                ),
            ],
        ),
        style=ft.ButtonStyle(
            overlay_color=ft.Colors.TRANSPARENT,
            padding=ft.Padding.symmetric(horizontal=0, vertical=4),
        ),
    )

    def alternar_detalhes(e):
        nonlocal detalhes_abertos
        detalhes_abertos = not detalhes_abertos
        criterios_coluna.visible = detalhes_abertos
        btn_toggle.content.controls[0].value = (
            "Ocultar critérios de pontuação" if detalhes_abertos else "Ver os 5 critérios de pontuação"
        )
        btn_toggle.content.controls[1].name = (
            ft.Icons.KEYBOARD_ARROW_UP_ROUNDED if detalhes_abertos else ft.Icons.KEYBOARD_ARROW_DOWN_ROUNDED
        )
        card_container.update()

    btn_toggle.on_click = alternar_detalhes

    card_container = ft.Container(
        bgcolor=SURFACE,
        border=ft.Border.all(1, BORDER),
        border_radius=12,
        padding=20,
        content=ft.Column(
            spacing=10,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    wrap=True,
                    controls=[
                        _badge_eixo(eixo_num),
                        ft.Text(
                            f"Indicador #{indice}",
                            size=11,
                            color=MUTED,
                            font_family="monospace",
                        ),
                    ],
                ),
                ft.Text(
                    titulo,
                    size=16,
                    weight=ft.FontWeight.W_700,
                    color=TEXT,
                ),
                *(
                    [
                        ft.Text(
                            descricao,
                            size=12,
                            color=MUTED,
                        )
                    ]
                    if descricao
                    else []
                ),
                btn_toggle,
                criterios_coluna,
            ],
        ),
    )

    return card_container

