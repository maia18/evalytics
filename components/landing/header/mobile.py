import flet as ft
from typing import Callable, Optional
from components.landing.palette import (
    TEXT,
    MUTED,
    ROXO,
    ROXO_CLARO,
    SURFACE,
    SURFACE_ALT,
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

    async def ir_para_rota(rota: str, e=None):
        mudar_tela(rota)

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
                    on_click=_item_click(lambda e: ir_para_rota("/indicadores", e)),
                ),
                ft.TextButton(
                    "Sobre",
                    style=ft.ButtonStyle(
                        color=MUTED,
                        alignment=ft.Alignment.CENTER_LEFT,
                    ),
                    on_click=_item_click(ir_para_sobre),
                ),
                ft.TextButton(
                    "Desenvolvedores",
                    style=ft.ButtonStyle(
                        color=MUTED,
                        alignment=ft.Alignment.CENTER_LEFT,
                    ),
                    on_click=_item_click(
                        lambda e: ir_para_rota("/desenvolvedores", e)
                    ),
                ),
                ft.Divider(height=1, color=BORDER),
                ft.ElevatedButton(
                    "Login",
                    color=TEXT,
                    height=34,
                    style=ft.ButtonStyle(
                        color=TEXT,
                        bgcolor={
                            ft.ControlState.DEFAULT: SURFACE_ALT,
                            ft.ControlState.HOVERED: BORDER,
                        },
                        side=ft.BorderSide(1, BORDER),
                        shape=ft.RoundedRectangleBorder(radius=16),
                        padding=ft.Padding.symmetric(horizontal=13, vertical=7),
                        text_style=ft.TextStyle(size=11, weight=ft.FontWeight.W_500),
                    ),
                    on_click=lambda e: mudar_tela("/login"),
                ),
                ft.OutlinedButton(
                    "Cadastrar-se",
                    height=34,
                    style=ft.ButtonStyle(
                        color=ft.Colors.WHITE,
                        bgcolor={
                            ft.ControlState.DEFAULT: ROXO,
                            ft.ControlState.HOVERED: ROXO_CLARO,
                        },
                        side=ft.BorderSide(1, ROXO_CLARO),
                        shape=ft.RoundedRectangleBorder(radius=16),
                        padding=ft.Padding.symmetric(horizontal=13, vertical=7),
                        text_style=ft.TextStyle(size=11, weight=ft.FontWeight.W_600),
                    ),
                    on_click=lambda e: mudar_tela("/cadastro"),
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
