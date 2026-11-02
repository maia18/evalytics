import flet as ft
from typing import Callable

from components.widgets.menu.menu_button_base import criar_botao_menu_base
from components.widgets.menu.menu_item import criar_item_menu
from components.core.router.rotas_cts import (
    ROTA_RELATORIOS,
    ROTA_RELATORIOS_DASHBOARD,
    ROTA_RELATORIOS_DADOS,
)
from components.core.constants.constants import COR_PRIMARIA


def criar_menu_relatorios(
    page: ft.Page,
    dark_mode: bool,
    cor_texto: str,
    mudar_tela: Callable[[str], None],
) -> list[ft.Control]:
    """Cria o item Relatórios com seta e links para suas subtelas."""
    rota_atual = getattr(page, "route", "") or ""
    expandido = rota_atual.startswith("/relatorios")
    cor_icone = ft.Colors.GREY_700 if not dark_mode else ft.Colors.GREY_300

    def alternar_subtelas(e=None) -> None:
        subtelas.visible = not subtelas.visible
        seta.icon = (
            ft.Icons.KEYBOARD_ARROW_DOWN
            if subtelas.visible
            else ft.Icons.KEYBOARD_ARROW_RIGHT
        )
        seta.tooltip = (
            "Recolher subtelas de relatórios"
            if subtelas.visible
            else "Mostrar subtelas de relatórios"
        )
        page.update()

    botao_relatorios = criar_item_menu(
        ft.Icons.PIE_CHART_OUTLINE,
        "Relatórios",
        ROTA_RELATORIOS,
        dark_mode,
        cor_texto,
        mudar_tela,
        ativo=rota_atual == ROTA_RELATORIOS,
    )
    botao_relatorios.expand = True

    seta = ft.IconButton(
        icon=(
            ft.Icons.KEYBOARD_ARROW_DOWN
            if expandido
            else ft.Icons.KEYBOARD_ARROW_RIGHT
        ),
        icon_size=18,
        tooltip="Recolher subtelas de relatórios" if expandido else "Mostrar subtelas de relatórios",
        on_click=alternar_subtelas,
    )

    linha_relatorios = ft.Row(
        spacing=0,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            botao_relatorios,
            ft.Container(height=45, content=seta),
        ],
    )

    def criar_subtela(texto: str, rota: str, icone: str) -> ft.Control:
        ativo = rota_atual == rota
        conteudo = ft.Row(
            spacing=10,
            controls=[
                ft.Icon(icone, size=14, color=("#B69CFF" if dark_mode else COR_PRIMARIA) if ativo else cor_icone),
                ft.Text(texto, size=11, color=("#B69CFF" if dark_mode else COR_PRIMARIA) if ativo else cor_texto),
            ],
        )
        botao = criar_botao_menu_base(
            content=conteudo,
            rota=rota,
            dark_mode=dark_mode,
            mudar_tela=mudar_tela,
            alignment=ft.Alignment(-1, 0),
            expand=True,
            ativo=ativo,
        )
        return ft.Container(
            expand=True,
            padding=ft.Padding.only(left=16),
            content=botao,
        )

    subtelas = ft.Column(
        spacing=0,
        visible=expandido,
        controls=[
            criar_subtela(
                "Dashboard Executivo",
                ROTA_RELATORIOS_DASHBOARD,
                ft.Icons.DASHBOARD_OUTLINED,
            ),
            criar_subtela(
                "Dados e exportação",
                ROTA_RELATORIOS_DADOS,
                ft.Icons.TABLE_CHART_OUTLINED,
            ),
        ],
    )

    return [linha_relatorios, subtelas]
