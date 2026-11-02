import flet as ft
from typing import Callable

from components.core.router.rotas_cts import (
    ROTA_DASHBOARD,
    ROTA_DASHBOARD_VISAO_GERAL,
    ROTA_DASHBOARD_AVALIACOES,
)
from components.widgets.menu.menu_button_base import criar_botao_menu_base
from components.widgets.menu.menu_item import criar_item_menu
from components.core.constants.constants import COR_PRIMARIA


def criar_menu_dashboard(
    page: ft.Page,
    dark_mode: bool,
    cor_texto: str,
    mudar_tela: Callable[[str], None],
) -> list[ft.Control]:
    """Cria Dashboard na sidebar com links para suas duas subtelas."""
    rota_atual = getattr(page, "route", "") or ""
    expandido = rota_atual.startswith(ROTA_DASHBOARD)
    cor_icone = ft.Colors.GREY_700 if not dark_mode else ft.Colors.GREY_300

    def alternar_subtelas(e=None) -> None:
        subtelas.visible = not subtelas.visible
        seta.icon = (
            ft.Icons.KEYBOARD_ARROW_DOWN
            if subtelas.visible
            else ft.Icons.KEYBOARD_ARROW_RIGHT
        )
        seta.tooltip = (
            "Recolher subtelas do dashboard"
            if subtelas.visible
            else "Mostrar subtelas do dashboard"
        )
        page.update()

    botao_dashboard = criar_item_menu(
        ft.Icons.GRID_VIEW_OUTLINED,
        "Dashboard",
        ROTA_DASHBOARD,
        dark_mode,
        cor_texto,
        mudar_tela,
        ativo=rota_atual == ROTA_DASHBOARD,
    )
    botao_dashboard.expand = True

    seta = ft.IconButton(
        icon=(
            ft.Icons.KEYBOARD_ARROW_DOWN
            if expandido
            else ft.Icons.KEYBOARD_ARROW_RIGHT
        ),
        icon_size=18,
        tooltip=(
            "Recolher subtelas do dashboard"
            if expandido
            else "Mostrar subtelas do dashboard"
        ),
        on_click=alternar_subtelas,
    )
    linha_dashboard = ft.Row(
        spacing=0,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[botao_dashboard, ft.Container(height=45, content=seta)],
    )

    def criar_subtela(texto: str, rota: str, icone: str) -> ft.Control:
        ativo = rota_atual == rota
        botao = criar_botao_menu_base(
            content=ft.Row(
                spacing=10,
                controls=[
                    ft.Icon(icone, size=14, color=("#B69CFF" if dark_mode else COR_PRIMARIA) if ativo else cor_icone),
                    ft.Text(texto, size=11, color=("#B69CFF" if dark_mode else COR_PRIMARIA) if ativo else cor_texto),
                ],
            ),
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
                "Visão Geral",
                ROTA_DASHBOARD_VISAO_GERAL,
                ft.Icons.GRID_VIEW_ROUNDED,
            ),
            criar_subtela(
                "Acompanhamento",
                ROTA_DASHBOARD_AVALIACOES,
                ft.Icons.TABLE_ROWS_ROUNDED,
            ),
        ],
    )
    return [linha_dashboard, subtelas]
