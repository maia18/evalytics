import flet as ft
from typing import Callable
from components.core.theme.app_colors import AppColors
from components.core.constants.constants import (
    CARD,
    BORDA,
    LARGURA_SIDEBAR_EXPANDIDA,
    LARGURA_SIDEBAR_COLAPSADA,
)
from components.layout.sidebar.sidebar_content import criar_sidebar_content
from components.layout.sidebar.sidebar_collapsed import criar_sidebar_colapsada

class Sidebar(ft.Container):
    """
    Componente customizado que atua como o esqueleto principal do menu lateral.
        Adapta automaticamente sua largura e seu conteúdo conforme o estado expandido ou colapsado.
    """

    def __init__(
        self,
        page: ft.Page,
        dark_mode: bool,
        mudar_tela: Callable[[str], None],
        collapsed: bool = False,
        allow_collapse: bool = True,
    ) -> None:

        super().__init__()

        # Estado da Sidebar
        self.page_ref = page
        self.dark_mode = dark_mode
        self.mudar_tela = mudar_tela
        self.allow_collapse = allow_collapse
        preferencia_recolhida = getattr(page, "sidebar_recolhida", None)
        self.collapsed = (
            bool(preferencia_recolhida)
            if allow_collapse and preferencia_recolhida is not None
            else collapsed
        )

        # Paleta de cores atual
        self.cores = AppColors.get(self.dark_mode)

        # Aparência
        self.bgcolor = "#171827" if self.dark_mode else "#F8F8FC"
        self.padding = 8 if self.collapsed else 14
        self.animate = ft.Animation(180, ft.AnimationCurve.EASE_OUT)

        # Borda direita
        self.border = ft.Border(
            right=ft.BorderSide(
                1,
                self.cores[BORDA],
            )
        )

        # Largura de acordo com o estado
        self.width = (
            LARGURA_SIDEBAR_COLAPSADA
            if self.collapsed
            else LARGURA_SIDEBAR_EXPANDIDA
        )

        # Conteúdo de acordo com o estado
        self.content = self._criar_conteudo()

    def _criar_conteudo(self) -> ft.Control:
        alternar = self.alternar_recolhimento if self.allow_collapse else None
        if self.collapsed:
            return criar_sidebar_colapsada(
                page=self.page_ref,
                dark_mode=self.dark_mode,
                mudar_tela=self.mudar_tela,
                cores=self.cores,
                alternar_recolhimento=alternar,
            )
        return criar_sidebar_content(
            page=self.page_ref,
            dark_mode=self.dark_mode,
            mudar_tela=self.mudar_tela,
            cores=self.cores,
            alternar_recolhimento=alternar,
        )

    def alternar_recolhimento(self, e=None) -> None:
        if not self.allow_collapse:
            return
        recolhida = not self.collapsed
        self.page_ref.sidebar_recolhida = recolhida
        self.definir_recolhida(recolhida)

    def definir_recolhida(self, recolhida: bool, atualizar: bool = True) -> None:
        self.collapsed = recolhida
        self.width = (
            LARGURA_SIDEBAR_COLAPSADA
            if self.collapsed
            else LARGURA_SIDEBAR_EXPANDIDA
        )
        self.padding = 8 if self.collapsed else 14
        self.content = self._criar_conteudo()
        if atualizar:
            self.page_ref.update()
