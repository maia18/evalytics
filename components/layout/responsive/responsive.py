import flet as ft
from components.layout.sidebar.sidebar_factory import (
    criar_sidebar_desktop, 
    criar_sidebar_mobile,
)
from components.layout.topbar.topbar_factory import criar_topbar
from components.layout.responsive.overlay import criar_overlay
from components.layout.responsive.view_builder import montar_view
from components.core.theme.theme_config import configurar_tema
from .layout.layout_controller import LayoutController

class ResponsiveLayout:
    """
    Orquestrador central do layout da aplicação.
        Responsável por instanciar os componentes base da tela (Topbar, Sidebar) e encapsulá-los em um `ft.View` que será roteado pelo sistema.
    """

    def __init__(
        self,
        page: ft.Page,
        titulo_pagina: str,
        subtitulo: str = "",
        mudar_tela=None,
    ):
        self.page = page
        self.titulo_pagina = titulo_pagina
        self.subtitulo = subtitulo
        self.mudar_tela = mudar_tela
        
        self.conteudo_principal = ft.Column() # Inicia vazio. O desenvolvedor deve chamar `add_content()` antes de renderizar a view.

        '''
        DELEGAÇÃO DE ESTADO (MVC):
            Passamos a responsabilidade de gerenciar cliques, aberturas de menu e redimensionamento para o Controller, mantendo esta classe focada apenas em "montar peças".
        '''
        self.controller = LayoutController(page, mudar_tela)
        
        self.cores = configurar_tema(self.page, self.controller.dark_mode) # Carrega a paleta de cores correta baseada no estado de tema do controller

        # Constrói as peças do layout imediatamente na inicialização
        self._criar_componentes()

    def _criar_componentes(self):
        """Instancia os fragmentos de interface e os injeta no Controller."""

        overlay = criar_overlay(self.controller.fechar_sidebar) # O Overlay é o fundo escurecido usado quando a Sidebar mobile é aberta
        sidebar_desktop = criar_sidebar_desktop(
            page=self.page,
            dark_mode=self.controller.dark_mode,
            mudar_tela=self.mudar_tela,
            collapsed=False,
        )
        sidebar_mobile = criar_sidebar_mobile(
            page=self.page,
            dark_mode=self.controller.dark_mode,
            mudar_tela=self.mudar_tela,
        )

        # A Topbar recebe os callbacks do Controller para acionar ações globais
        topbar = criar_topbar(
            page=self.page,
            titulo=self.titulo_pagina,
            subtitulo=self.subtitulo,
            dark_mode=self.controller.dark_mode,
            toggle_sidebar=self.controller.toggle_sidebar,
            atualizar_tema=self.controller.toggle_dark_mode,
            mudar_tela=self.mudar_tela,
        )

        '''
        INJEÇÃO DE DEPENDÊNCIA:
            O Controller precisa saber quem são os componentes para poder alterá-los depois.
        '''
        self.controller.registrar_componentes(sidebar_mobile, sidebar_desktop, topbar, overlay)

        '''
        TRATAMENTO DE OVERLAY (Notificações):
            Elementos flutuantes (como painéis e modais) precisam ser injetados na lista global `page.overlay` do Flet para renderizarem por cima de toda a aplicação.
        '''
        if hasattr(topbar, "painel_notificacoes"):
            painel = topbar.painel_notificacoes
            # Evita duplicação do painel na lista global ao trocar de tela
            if painel not in self.page.overlay:
                self.page.overlay.append(painel)

    def add_content(self, content: ft.Control):
        """Injeta o miolo da página (formulários, tabelas, dashboards) no layout."""
        self.conteudo_principal = content

    def criar_view(self, route: str) -> ft.View:
        """
        Gera o `ft.View` final contendo a página pronta para o roteador do Flet.
            DEVE ser chamado após `add_content()`.
        """
        self.controller.rota_atual = route
        
        '''
        EVENTO DE JANELA:
            Toda vez que o usuário redimensionar o navegador, o Flet avisa o Controller.
        '''
        self.page.on_resize = self.controller.ajustar_responsividade
        
        self.controller.ajustar_responsividade() # Força um ajuste imediato para a tela abrir já no formato correto (Mobile ou PC)

        # O 'montar_view' junta fisicamente as instâncias em uma estrutura de Row/Column/Stack
        return montar_view(
            route,
            self.cores,
            self.controller.sidebar_desktop,
            self.controller.topbar,
            self.conteudo_principal,
            self.controller.overlay,
            self.controller.sidebar_mobile,
            self.controller.ajustar_responsividade,
            self.page,
        )
