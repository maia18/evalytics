import flet as ft
from typing import Callable
from components.landing.palette import PAGE, MAX_CONTENT_WIDTH
from components.landing.hero.texto import criar_hero_texto
from components.landing.hero.painel import criar_painel_hero

def criar_hero(
    page: ft.Page,
    mudar_tela: Callable[[str], None],
    ir_para_recursos: Callable,
) -> ft.Container:
    """
    Cria a seção inicial (Hero + Terminal Demo) da Landing Page.
    """

    hero_texto = criar_hero_texto(
        mudar_tela=mudar_tela,
        ir_para_recursos=ir_para_recursos,
    )

    terminal_demo = criar_painel_hero(page=page)

    return ft.Container(
        key=ft.ScrollKey("inicio"),
        bgcolor=PAGE,
        padding=ft.Padding.only(top=56, bottom=36, left=24, right=24),
        alignment=ft.Alignment.CENTER,
        content=ft.Container(
            width=MAX_CONTENT_WIDTH,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=36,
                controls=[
                    hero_texto,
                    ft.Container(
                        key=ft.ScrollKey("recursos"),
                        alignment=ft.Alignment.CENTER,
                        content=terminal_demo,
                    ),
                ],
            ),
        ),
    )
