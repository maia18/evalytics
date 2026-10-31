import flet as ft
from .auth_service import renovar_token_firebase
from .auth_constants import (
    CHAVE_REFRESH_TOKEN, 
    CHAVE_LEMBRAR_ME,
)

class AuthState:
    """
    Gerenciador global de estado de autenticação.
        Centraliza as informações do usuário logado e gerencia a persistência da sessão (armazenamento local) para evitar re-logins desnecessários.
    """
    
    def __init__(self):
        self._autenticado = False
        self._usuario = None
        self._id_token = None
        self._refresh_token = None
        self._prefs = None # Instância do ft.SharedPreferences (armazenamento local do Flet)

    async def inicializar_storage(self, page: ft.Page):
        """
        Inicializa o SharedPreferences sob demanda (Lazy Initialization).
            O Flet exige que o SharedPreferences seja adicionado à lista de `services` da página antes de podermos ler ou gravar dados nele.
        """
        if self._prefs is None:
            self._prefs = ft.SharedPreferences()
            page.services.append(self._prefs)

    """
    # =========================================================================
    # GETTERS (Propriedades públicas somente leitura)
    #   Protegem as variáveis originais contra alterações acidentais pela UI.
    # =========================================================================
    """ 
    
    @property
    def autenticado(self):
        return self._autenticado

    @property
    def usuario(self):
        return self._usuario

    @property
    def id_token(self):
        return self._id_token

    @property
    def refresh_token(self):
        return self._refresh_token

    """
    # =========================================================================
    # MÉTODOS DE CONTROLE DE SESSÃO
    # =========================================================================
    """
    
    async def iniciar_sessao(self, dados: dict, page: ft.Page, lembrar_me: bool = False):
        """Atualiza a classe com os dados do Firebase após um login bem-sucedido."""
        
        await self.inicializar_storage(page)

        # Preenche o estado em memória
        self._autenticado = True
        self._usuario = dados
        self._id_token = dados.get("idToken")
        self._refresh_token = dados.get("refreshToken")

        # Se o usuário marcou "Lembrar de mim", salva-se o token de renovação no cache local.
        if lembrar_me and self._refresh_token:
            await self._prefs.set(CHAVE_REFRESH_TOKEN, self._refresh_token)
            await self._prefs.set(CHAVE_LEMBRAR_ME, True)
        else:
            await self._remover_sessao_persistida() # Caso contrário, limpamos qualquer cache antigo por segurança.

    async def encerrar_sessao(self, page: ft.Page):
        """Invalida a sessão atual e apaga o cache local (Logout)."""
        
        await self.inicializar_storage(page)

        # Reseta as variáveis em memória
        self._autenticado = False
        self._usuario = None
        self._id_token = None
        self._refresh_token = None

        # Remove fisicamente o acesso persistido do dispositivo do usuário
        await self._remover_sessao_persistida()

    async def atualizar_dados_usuario(self, dados: dict):
        """Atualiza os dados e tokens em memória após uma alteração do perfil."""
        if self._usuario is None:
            self._usuario = {}
        self._usuario.update(dados)
        self._id_token = dados.get("idToken", self._id_token)
        self._refresh_token = dados.get("refreshToken", self._refresh_token)

        if self._prefs is not None and self._refresh_token:
            lembrar_me = await self._prefs.get(CHAVE_LEMBRAR_ME)
            if lembrar_me:
                await self._prefs.set(CHAVE_REFRESH_TOKEN, self._refresh_token)

    async def _remover_sessao_persistida(self):
        """Método interno de utilidade para limpar o SharedPreferences."""
        if self._prefs is None:
            return

        await self._prefs.remove(CHAVE_REFRESH_TOKEN)
        await self._prefs.remove(CHAVE_LEMBRAR_ME)

    async def possui_sessao_persistida(self, page: ft.Page) -> bool:
        """Verifica se existe um token salvo (útil para decidir se mostra a tela de login ou carrega o app direto)."""
        await self.inicializar_storage(page)
        refresh_token = await self._prefs.get(CHAVE_REFRESH_TOKEN)
        
        # Converte a string do token (ou None) para um valor Booleano (True/False)
        return bool(refresh_token)

    async def obter_refresh_token(self, page: ft.Page):
        """Retorna o token de renovação salvo no dispositivo."""
        await self.inicializar_storage(page)
        return await self._prefs.get(CHAVE_REFRESH_TOKEN)

    async def restaurar_sessao(self, page: ft.Page, api_key: str) -> bool:
        """
        Tenta restaurar uma sessão que expirou usando o "refresh_token".
            Isso acontece em segundo plano, evitando que o usuário precise digitar a senha de novo.
        """
        refresh_token = await self.obter_refresh_token(page)

        if not refresh_token:
            return False

        data = renovar_token_firebase(api_key, refresh_token) # Delega a requisição HTTP (REST API do Firebase) para a camada de serviços

        # Se a renovação falhou (ex: token revogado ou expirado no backend), limpamos tudo.
        if not data:
            await self._remover_sessao_persistida()
            return False

        # Restaura o estado em memória com os NOVOS tokens recebidos
        self._autenticado = True
        self._usuario = data
        self._id_token = data.get("id_token")
        
        self._refresh_token = data.get("refresh_token", refresh_token) # O Firebase pode retornar um novo refresh_token; se não retornar, usamos o antigo.

        # Salva o novo token persistente
        await self._prefs.set(CHAVE_REFRESH_TOKEN, self._refresh_token)
        return True

auth_state = AuthState() # Exporta uma instância única (Singleton) que será importada e compartilhada por todo o app
