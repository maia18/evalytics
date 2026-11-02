import flet as ft
from typing import Callable

from components.core.constants.constants import COR_PRIMARIA, TEXTO_PRINCIPAL
from components.core.router.rotas_cts import ROTA_CONFIGURACOES
from components.layout.topbar.core.account_menu import abrir_ajuda, abrir_sobre
from components.widgets.menu.botao_icon import criar_botao_icon
from components.widgets.menu.menu_button_base import criar_botao_menu_base
from components.widgets.menu.menu_item import criar_item_menu


def criar_rodape_sidebar(
    page: ft.Page,
    dark_mode: bool,
    cores: dict[str, str],
    mudar_tela: Callable[[str], None],
    compacta: bool = False,
) -> ft.Column:
    """Ações pessoais fixas no rodapé da sidebar."""
    rota_atual = getattr(page, "route", "") or ""

    def abrir_ajuda_click(e) -> None:
        abrir_ajuda(page, cores, mudar_tela)

    def abrir_sobre_click(e) -> None:
        abrir_sobre(page, cores)

    if compacta:
        configuracoes = criar_botao_icon(
            ft.Icons.SETTINGS_OUTLINED,
            "Configurações",
            ROTA_CONFIGURACOES,
            dark_mode,
            cores[TEXTO_PRINCIPAL],
            mudar_tela,
            ativo=rota_atual == ROTA_CONFIGURACOES,
        )
        ajuda = criar_botao_menu_base(
            content=ft.Icon(
                ft.Icons.HELP_OUTLINE,
                size=20,
                color=cores[TEXTO_PRINCIPAL],
                tooltip="Ajuda e suporte",
            ),
            rota="",
            dark_mode=dark_mode,
            mudar_tela=None,
            alignment=ft.Alignment.CENTER,
            expand=True,
            on_click=abrir_ajuda_click,
        )
        sobre = criar_botao_menu_base(
            content=ft.Icon(
                ft.Icons.INFO_OUTLINE,
                size=20,
                color="#B69CFF" if dark_mode else COR_PRIMARIA,
                tooltip="Sobre o Evalytics",
            ),
            rota="",
            dark_mode=dark_mode,
            mudar_tela=None,
            alignment=ft.Alignment.CENTER,
            expand=True,
            on_click=abrir_sobre_click,
        )
    else:
        configuracoes = criar_item_menu(
            ft.Icons.SETTINGS_OUTLINED,
            "Configurações",
            ROTA_CONFIGURACOES,
            dark_mode,
            cores[TEXTO_PRINCIPAL],
            mudar_tela,
            ativo=rota_atual == ROTA_CONFIGURACOES,
        )
        ajuda = criar_botao_menu_base(
            content=ft.Row(
                spacing=10,
                controls=[
                    ft.Icon(ft.Icons.HELP_OUTLINE, size=18, color=cores[TEXTO_PRINCIPAL]),
                    ft.Text("Ajuda e suporte", size=12, weight=ft.FontWeight.W_500, color=cores[TEXTO_PRINCIPAL]),
                ],
            ),
            rota="",
            dark_mode=dark_mode,
            mudar_tela=None,
            expand=True,
            on_click=abrir_ajuda_click,
        )
        sobre = criar_botao_menu_base(
            content=ft.Row(
                spacing=10,
                controls=[
                    ft.Icon(
                        ft.Icons.INFO_OUTLINE,
                        size=18,
                        color="#B69CFF" if dark_mode else COR_PRIMARIA,
                    ),
                    ft.Text(
                        "Sobre o Evalytics",
                        size=12,
                        weight=ft.FontWeight.W_600,
                        color="#B69CFF" if dark_mode else COR_PRIMARIA,
                    ),
                ],
            ),
            rota="",
            dark_mode=dark_mode,
            mudar_tela=None,
            expand=True,
            on_click=abrir_sobre_click,
        )

    return ft.Column(
        spacing=0,
        controls=[
            ft.Divider(height=12),
            configuracoes,
            ajuda,
            sobre,
        ],
    )
