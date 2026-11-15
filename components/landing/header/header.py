import flet as ft
from typing import Callable, Optional
from components.landing.header.logo import criar_logo
from components.landing.header.desktop import criar_menu_desktop
from components.landing.header.mobile import criar_menu_mobile
from components.landing.palette import (
    PAGE,
    BORDER,
    MAX_CONTENT_WIDTH,
    ROXO,
    ROXO_CLARO,
    SURFACE_ALT,
    TEXT,
    MUTED,
)

def criar_header(
    page: ft.Page,
    mudar_tela: Callable[[str], None],
    ir_para_recursos: Callable,
    ir_para_sobre: Callable,
    ir_para_inicio: Optional[Callable] = None,
) -> ft.Container:
    """Cria o cabeçalho superior minimalista alinhado com a paleta Evalytics."""

    logo = criar_logo(ir_para_inicio=ir_para_inicio)

    menu_desktop = criar_menu_desktop(
        mudar_tela=mudar_tela,
        ir_para_recursos=ir_para_recursos,
        ir_para_sobre=ir_para_sobre,
    )

    menu_mobile = criar_menu_mobile(
        page=page,
        mudar_tela=mudar_tela,
        ir_para_recursos=ir_para_recursos,
        ir_para_sobre=ir_para_sobre,
    )

    # Layout desktop (telas a partir de md). O Stack ancora as extremidades e
    # centraliza a navegação na largura total, independentemente dos botões.
    acoes_conta = ft.Row(
        spacing=8,
        controls=[
            ft.OutlinedButton(
                "Login",
                on_click=lambda e: mudar_tela("/login"),
                height=32,
                style=ft.ButtonStyle(
                    color={
                        ft.ControlState.DEFAULT: MUTED,
                        ft.ControlState.HOVERED: ROXO_CLARO,
                    },
                    side=ft.BorderSide(1, BORDER),
                    bgcolor={
                        ft.ControlState.DEFAULT: PAGE,
                        ft.ControlState.HOVERED: SURFACE_ALT,
                    },
                    shape=ft.RoundedRectangleBorder(radius=16),
                    padding=ft.Padding.symmetric(horizontal=12, vertical=6),
                    overlay_color=ft.Colors.TRANSPARENT,
                    text_style=ft.TextStyle(size=11, weight=ft.FontWeight.W_500),
                ),
            ),
            ft.ElevatedButton(
                "Cadastrar-se",
                on_click=lambda e: mudar_tela("/cadastro"),
                height=32,
                style=ft.ButtonStyle(
                    color=TEXT,
                    bgcolor={
                        ft.ControlState.DEFAULT: ROXO,
                        ft.ControlState.HOVERED: ROXO_CLARO,
                    },
                    elevation=0,
                    animation_duration=180,
                    shape=ft.RoundedRectangleBorder(radius=16),
                    padding=ft.Padding.symmetric(horizontal=12, vertical=6),
                    text_style=ft.TextStyle(size=11, weight=ft.FontWeight.W_600),
                ),
            ),
        ],
    )
    header_desktop = ft.Stack(
        expand=True,
        height=40,
        controls=[
            ft.Container(
                left=0,
                top=0,
                bottom=0,
                alignment=ft.Alignment.CENTER_LEFT,
                content=logo,
            ),
            ft.Container(
                left=0,
                right=0,
                top=0,
                bottom=0,
                alignment=ft.Alignment.CENTER,
                content=menu_desktop,
            ),
            ft.Container(
                right=0,
                top=0,
                bottom=0,
                alignment=ft.Alignment.CENTER_RIGHT,
                content=acoes_conta,
            ),
        ],
    )

    # Layout mobile (telas pequenas)
    header_mobile = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            criar_logo(ir_para_inicio=ir_para_inicio),
            menu_mobile,
        ],
    )

    # Responsividade
    conteudo_responsivo = ft.ResponsiveRow(
        columns=12,
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Container(
                col={"xs": 12, "sm": 12, "md": 0, "lg": 0, "xl": 0},
                content=header_mobile,
            ),
            ft.Container(
                col={"xs": 0, "sm": 0, "md": 12, "lg": 12, "xl": 12},
                content=header_desktop,
            ),
        ],
    )

    return ft.Container(
        bgcolor=PAGE,
        border=ft.Border(
            bottom=ft.BorderSide(1, BORDER),
        ),
        padding=ft.Padding.symmetric(horizontal=24, vertical=10),
        alignment=ft.Alignment.CENTER,
        content=ft.Container(
            width=MAX_CONTENT_WIDTH,
            content=conteudo_responsivo,
        ),
    )
