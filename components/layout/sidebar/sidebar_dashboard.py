import flet as ft
from typing import Callable

from components.core.router.rotas_cts import (
    ROTA_DASHBOARD,
    ROTA_DASHBOARD_VISAO_GERAL,
    ROTA_DASHBOARD_AVALIACOES,
    ROTA_DASHBOARD_RESULTADOS,
)
from components.widgets.menu.menu_button_base import criar_botao_menu_base
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
    estado_hover = {"ativo": False}
    destacado_inicial = expandido
    icone_dashboard = ft.Icon(
        ft.Icons.GRID_VIEW_OUTLINED,
        size=18,
        color=("#B69CFF" if dark_mode else COR_PRIMARIA)
        if destacado_inicial
        else cor_icone,
    )
    texto_dashboard = ft.Text(
        "Dashboard",
        size=13,
        weight="w600" if destacado_inicial else "w500",
        color=("#B69CFF" if dark_mode else COR_PRIMARIA)
        if destacado_inicial
        else cor_texto,
    )

    def atualizar_destaque_dashboard() -> None:
        destacado = (
            estado_hover["ativo"]
            or subtelas.visible
            or rota_atual.startswith(ROTA_DASHBOARD)
        )
        # Mantém o contorno no item principal; os subtópicos usam marcador próprio.
        botao_dashboard.bgcolor = (
            ("#302747" if dark_mode else "#EEE9FB") if destacado else None
        )
        botao_dashboard.border = ft.Border(
            left=ft.BorderSide(3, COR_PRIMARIA if destacado else "#00000000")
        )
        icone_dashboard.color = (
            ("#B69CFF" if dark_mode else COR_PRIMARIA) if destacado else cor_icone
        )
        texto_dashboard.color = (
            ("#B69CFF" if dark_mode else COR_PRIMARIA) if destacado else cor_texto
        )
        texto_dashboard.weight = "w600" if destacado else "w500"

    def alternar_subtelas(e=None) -> None:
        subtelas.visible = not subtelas.visible
        atualizar_destaque_dashboard()
        page.update()

    def ao_passar_mouse(e: ft.ControlEvent) -> None:
        estado_hover["ativo"] = e.data == "true"
        atualizar_destaque_dashboard()
        page.update()

    botao_dashboard = criar_botao_menu_base(
        content=ft.Row(
            spacing=10,
            controls=[icone_dashboard, texto_dashboard],
        ),
        rota=ROTA_DASHBOARD,
        dark_mode=dark_mode,
        mudar_tela=None,
        expand=True,
        on_click=alternar_subtelas,
        # O contorno pertence ao invólucro externo, sem duplicar a borda do botão.
        ativo=False,
    )
    botao_dashboard.on_hover = ao_passar_mouse

    def criar_subtela(texto: str, rota: str, icone: str) -> ft.Control:
        ativo = rota_atual == rota
        botao = criar_botao_menu_base(
            content=ft.Row(
                spacing=8,
                controls=[
                    ft.Container(
                        width=3,
                        height=16,
                        bgcolor="#A78BFA" if ativo else "#00000000",
                    ),
                    ft.Icon(icone, size=14, color=cor_icone),
                    ft.Text(
                        texto,
                        size=11,
                        weight="w600" if ativo else "w500",
                        color=cor_texto,
                    ),
                ],
            ),
            rota=rota,
            dark_mode=dark_mode,
            mudar_tela=mudar_tela,
            alignment=ft.Alignment(-1, 0),
            expand=True,
            ativo=ativo,
        )
        if ativo:
            # A seleção usa um marcador vertical, sem contorno nem caixa.
            botao.bgcolor = None
            botao.border = ft.Border(
                left=ft.BorderSide(3, "#00000000")
            )
        return ft.Container(
            expand=True,
            padding=ft.Padding.only(left=16, right=2),
            content=botao,
        )

    subtelas = ft.Column(
        spacing=2,
        visible=expandido,
        controls=[
            criar_subtela(
                "Indicadores",
                ROTA_DASHBOARD_VISAO_GERAL,
                ft.Icons.GRID_VIEW_ROUNDED,
            ),
            criar_subtela(
                "Acompanhamento",
                ROTA_DASHBOARD_AVALIACOES,
                ft.Icons.TABLE_ROWS_ROUNDED,
            ),
            criar_subtela(
                "Resultados por eixo",
                ROTA_DASHBOARD_RESULTADOS,
                ft.Icons.INSERT_CHART_OUTLINED,
            ),
        ],
    )
    atualizar_destaque_dashboard()
    return [botao_dashboard, subtelas]
