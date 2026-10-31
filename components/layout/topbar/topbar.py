import flet as ft
from typing import Callable
from components.core.theme.app_colors import AppColors
from components.core.constants.constants import CARD, BORDA
from components.layout.topbar.topbar_content import criar_topbar_content
from .topbar_monitor import iniciar_monitor_notificacoes

class TopBar(ft.Container):
    """Componente principal da barra superior (TopBar)."""

    def __init__(
        self,
        page: ft.Page,
        titulo_pagina: str,
        subtitulo: str,
        dark_mode: bool,
        toggle_sidebar: Callable[[], None],
        atualizar_tema: Callable[[], None],
        mudar_tela: Callable[[str], None] | None = None,
    ) -> None:

        super().__init__()
        
        self._page = page
        self.titulo_pagina = titulo_pagina
        self.subtitulo = subtitulo
        self.dark_mode = dark_mode
        self._toggle_sidebar = toggle_sidebar
        self._atualizar_tema = atualizar_tema

        # Estado inicial
        self.notificacoes_pendentes = 0
        self.cores = AppColors.get(self.dark_mode)

        # Botão Menu
        self.menu_button = ft.IconButton(
            icon=ft.Icons.MENU,
            on_click=lambda e: self._toggle_sidebar(),
        )

        # Estilização
        self.bgcolor = self.cores[CARD]
        self.padding = 20
        self.border = ft.Border(bottom=ft.BorderSide(1, self.cores[BORDA]))

        # Conteúdo
        self.content = criar_topbar_content(
            page=page,
            titulo=titulo_pagina,
            subtitulo=subtitulo,
            dark_mode=dark_mode,
            cores=self.cores,
            menu_button=self.menu_button,
            atualizar_tema=atualizar_tema,
            mudar_tela=mudar_tela,
            notificacoes_pendentes=self.notificacoes_pendentes,
        )

        # Referências do sistema de notificações (injetadas por topbar_content)
        self.badge_notificacoes = getattr(self.content, "badge_notificacoes", None)
        self.painel_notificacoes = getattr(self.content, "painel_notificacoes", None)
        self.atualizar_lista_notificacoes = getattr(self.content, "atualizar_lista_notificacoes", None)
        
        # Delega a tarefa de inicialização do monitoramento para o serviço externo
        iniciar_monitor_notificacoes(self._page, self)

    def atualizar_notificacoes(self, quantidade: int) -> None:
        """Atualiza visualmente a quantidade de notificações não lidas no badge."""
        
        self.notificacoes_pendentes = max(0, quantidade)
        if self.badge_notificacoes is None:
            return

        self.badge_notificacoes.visible = self.notificacoes_pendentes > 0
        self.badge_notificacoes.content = ft.Text(
            str(self.notificacoes_pendentes),
            size=9,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.WHITE,
        )
