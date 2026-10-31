import flet as ft
from typing import Callable, Optional
from components.landing.palette import (
    SURFACE,
    BORDER,
    TEXT,
    MUTED,
    ROXO_CLARO,
)

def criar_card_beneficio(
    titulo: str,
    descricao: str,
    cor_destaque: str = ROXO_CLARO,
    tag: str = "",
    acao_texto: str = "",
    on_acao: Optional[Callable] = None,
    scroll_key: str = None,
) -> ft.Container:
    """Cria um card minimalista da grade de benefícios com cor de destaque personalizada."""

    controles = [
        # Linha de cabeçalho com tag/bullet colorido
        ft.Row(
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=8,
                    height=8,
                    border_radius=4,
                    bgcolor=cor_destaque,
                ),
                *(
                    [
                        ft.Text(
                            tag,
                            size=11,
                            weight=ft.FontWeight.W_600,
                            color=cor_destaque,
                            font_family="monospace",
                        )
                    ]
                    if tag
                    else []
                ),
            ],
        ),

        # Título
        ft.Text(
            titulo,
            size=15,
            weight=ft.FontWeight.W_700,
            color=TEXT,
        ),

        # Descrição
        ft.Text(
            descricao,
            size=12,
            color=MUTED,
        ),
    ]

    # Botão de ação opcional (ex: ir para Indicadores ou Sobre)
    if acao_texto and on_acao:
        controles.append(
            ft.TextButton(
                content=ft.Row(
                    spacing=4,
                    tight=True,
                    controls=[
                        ft.Text(
                            acao_texto,
                            size=12,
                            weight=ft.FontWeight.W_600,
                            color=cor_destaque,
                        ),
                    ],
                ),
                style=ft.ButtonStyle(
                    overlay_color=ft.Colors.TRANSPARENT,
                    padding=ft.Padding.symmetric(horizontal=0, vertical=4),
                ),
                on_click=on_acao,
            )
        )

    return ft.Container(
        key=ft.ScrollKey(scroll_key) if scroll_key else None,
        bgcolor=SURFACE,
        border=ft.Border.all(1, BORDER),
        border_radius=12,
        padding=ft.Padding.only(left=20, right=20, top=18, bottom=20),
        content=ft.Column(
            spacing=8,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            controls=controles,
        ),
    )

def criar_card_responsivo(
    titulo: str,
    descricao: str,
    cor_destaque: str = ROXO_CLARO,
    tag: str = "",
    acao_texto: str = "",
    on_acao: Optional[Callable] = None,
    scroll_key: str = None,
) -> ft.Container:
    """Encapsula o card em uma coluna responsiva (4/12 no desktop, 12/12 no mobile)."""

    return ft.Container(
        col={
            "xs": 12,
            "sm": 12,
            "md": 4,
            "lg": 4,
            "xl": 4,
        },
        content=criar_card_beneficio(
            titulo=titulo,
            descricao=descricao,
            cor_destaque=cor_destaque,
            tag=tag,
            acao_texto=acao_texto,
            on_acao=on_acao,
            scroll_key=scroll_key,
        ),
    )
