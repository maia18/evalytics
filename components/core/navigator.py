import logging # módulo nativo de logs para rastreamento do sistema.
import flet as ft
from typing import Callable
from components.core.auth.auth_state import auth_state
from components.core.router.router import (
    ViewBuilder, 
    obter_view
)

# Cria um logger específico para este módulo.
logger = logging.getLogger(__name__)

'''
Criação de um "Type Alias" (Apelido de Tipo).
    Isso diz que 'NavigateCallback' representa qualquer função que receba uma string (str) e não retorne nada (None).
'''
NavigateCallback = Callable[[str], None]

class Navigator:
    """
    Gerencia a navegação entre diferentes rotas/views da aplicação Flet.
        Centralizar a navegação em uma classe evita que você precise reescrever a lógica de troca de telas em cada botão do seu aplicativo.
    """
    def __init__(self, page: ft.Page) -> None:
        '''
        Salva a referência da página principal (a janela do app) dentro da classe.
            Assim, os métodos da classe podem manipular a interface.
        '''
        self.page = page

    # Navega para a rota informada, substituindo a view (tela) atual
    def go(self, rota: str) -> None:

        rotas_publicas = {
            "/",
            "/login",
            "/indicadores",
        }

        if rota not in rotas_publicas and not auth_state.autenticado:
            logger.warning(
                "Acesso bloqueado à rota '%s'. Usuário não autenticado.",
                rota,
            )
            rota = "/login"

        self.page.views.clear()
        self.page.overlay.clear()

        # Mantém a rota atual disponível para componentes como a sidebar,
        # já que esta navegação monta views diretamente sem chamar page.go().
        self.page.rota_navegacao_atual = rota
        self.page.route = rota

        view_builder: ViewBuilder = obter_view(rota)

        self.page.views.append(
            view_builder(self.page, self.go)
        )

        self.page.update()
