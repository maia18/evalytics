import flet as ft
from typing import Callable
from components.landing.palette import PAGE

# Componentes da Landing Page
from components.landing.hero import criar_hero
from components.landing.header import criar_header
from components.landing.widgets.cta import criar_cta
from components.landing.widgets.footer import criar_rodape
from components.landing.recursos import criar_secao_recursos

def ViewLanding(
    page: ft.Page,
    mudar_tela: Callable[[str], None],
) -> ft.View:
    """Cria e retorna a View principal da Landing Page fiel ao design minimalista dark/terminal."""

    # =========================================================
    # NAVEGAÇÃO INTERNA COM SCROLL SUAVE
    # =========================================================

    async def ir_para_inicio(e=None):
        """Navega até o topo (Hero)."""
        await view.scroll_to(
            scroll_key="inicio",
            duration=400,
            curve=ft.AnimationCurve.EASE_IN_OUT,
        )

    async def ir_para_recursos(e=None):
        """Navega até a prévia de demonstração / terminal."""
        await view.scroll_to(
            scroll_key="recursos",
            duration=400,
            curve=ft.AnimationCurve.EASE_IN_OUT,
        )

    async def ir_para_indicadores(e=None):
        """Navega até o módulo de indicadores nos benefícios."""
        await view.scroll_to(
            scroll_key="indicadores",
            duration=400,
            curve=ft.AnimationCurve.EASE_IN_OUT,
        )

    async def ir_para_relatorios(e=None):
        """Navega até o módulo de relatórios nos benefícios."""
        await view.scroll_to(
            scroll_key="relatorios",
            duration=400,
            curve=ft.AnimationCurve.EASE_IN_OUT,
        )

    # =========================================================
    # COMPONENTES
    # =========================================================

    header = criar_header(
        page=page,
        mudar_tela=mudar_tela,
        ir_para_recursos=ir_para_recursos,
        ir_para_indicadores=ir_para_indicadores,
        ir_para_relatorios=ir_para_relatorios,
        ir_para_inicio=ir_para_inicio,
    )

    hero = criar_hero(
        page=page,
        mudar_tela=mudar_tela,
        ir_para_recursos=ir_para_recursos,
    )

    recursos = criar_secao_recursos(page=page)

    cta = criar_cta(
        page=page,
        mudar_tela=mudar_tela,
    )

    rodape = criar_rodape(ir_para_inicio=ir_para_inicio)

    # =========================================================
    # VIEW
    # =========================================================

    view = ft.View(
        route="/",
        bgcolor=PAGE,
        padding=0,
        spacing=0,
        scroll=ft.ScrollMode.AUTO,
        appbar=ft.AppBar(
            title=header,
            toolbar_height=64,
            bgcolor=PAGE,
            elevation=0,
            automatically_imply_leading=False,
            title_spacing=0,
        ),
        controls=[
            hero,
            recursos,
            cta,
            rodape,
        ],
    )

    return view
