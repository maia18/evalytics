import flet as ft
from typing import Callable, Optional
from components.landing.palette import (
    TEXT,
    MUTED,
    ROXO,
    ROXO_CLARO,
    SURFACE,
    BORDER,
)

def criar_menu_mobile(
    page: ft.Page, 
    mudar_tela: Callable[[str], None], 
    ir_para_recursos: Callable, 
    ir_para_sobre: Callable,
) -> ft.Column:
    """Cria o menu de navegação mobile com Recursos, Indicadores, Sobre e Entrar."""

    menu_mobile_aberto = False

    btn_menu = ft.IconButton(
        icon=ft.Icons.MENU_ROUNDED,
        icon_size=24,
        icon_color=TEXT,
    )

    btn_fechar = ft.IconButton(
        icon=ft.Icons.CLOSE_ROUNDED,
        icon_size=24,
        icon_color=TEXT,
        visible=False,
    )

    def _item_click(action):
        async def _wrapper(e):
            nonlocal menu_mobile_aberto
            menu_mobile_aberto = False
            menu_mobile_conteudo.visible = False
            btn_menu.visible = True
            btn_fechar.visible = False
            page.update()
            if action:
                await action(e)
        return _wrapper

    menu_mobile_conteudo = ft.Container(
        visible=False,
        bgcolor=SURFACE,
        border=ft.Border.all(1, BORDER),
        border_radius=10,
        padding=16,
        margin=ft.Margin.only(top=8, bottom=12),
        content=ft.Column(
            spacing=8,
            controls=[
                ft.TextButton(
                    "Recursos",
                    style=ft.ButtonStyle(
                        color=MUTED,
                        alignment=ft.Alignment.CENTER_LEFT,
                    ),
                    on_click=_item_click(ir_para_recursos),
                ),
                ft.TextButton(
                    "Indicadores",
                    style=ft.ButtonStyle(
                        color=ROXO_CLARO,
                        alignment=ft.Alignment.CENTER_LEFT,
                    ),
                    on_click=_item_click(lambda e: mudar_tela("/indicadores")),
                ),
                ft.TextButton(
                    "Sobre",
                    style=ft.ButtonStyle(
                        color=MUTED,
                        alignment=ft.Alignment.CENTER_LEFT,
                    ),
                    on_click=_item_click(ir_para_sobre),
                ),
                ft.Divider(height=1, color=BORDER),
                ft.ElevatedButton(
                    "Entrar",
                    bgcolor=ROXO,
                    color="#ffffff",
                    height=38,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    on_click=lambda e: mudar_tela("/login"),
                ),
            ],
        ),
    )

    async def alternar_menu_mobile(e):
        nonlocal menu_mobile_aberto
        menu_mobile_aberto = not menu_mobile_aberto
        menu_mobile_conteudo.visible = menu_mobile_aberto
        btn_menu.visible = not menu_mobile_aberto
        btn_fechar.visible = menu_mobile_aberto
        page.update()

    btn_menu.on_click = alternar_menu_mobile
    btn_fechar.on_click = alternar_menu_mobile

    return ft.Column(
        spacing=0,
        horizontal_alignment=ft.CrossAxisAlignment.END,
        controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.END,
                controls=[btn_menu, btn_fechar],
            ),
            menu_mobile_conteudo,
        ],
    )
