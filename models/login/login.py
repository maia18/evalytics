import requests
import flet as ft
from typing import Callable
from database.services.firebase_keys import FIREBASE_API_KEY
from components.core.auth.auth_state import auth_state
from models.login.core.logica_abas import obter_funcao_alternar
from models.login.core.cabecalho_login import criar_cabecalho
from models.login.core.tab_style import criar_estilo_aba
from models.login.core.rodape import criar_rodape_termos
from models.login.widgets.card_login import criar_card_login
from models.login.widgets.social_login import criar_login_social
from models.login.widgets.extras_login import criar_opcoes_extras
from models.login.widgets.campos_login import (
    criar_campo_nome, 
    criar_campo_email, 
    criar_campo_senha,
)
from components.core.constants.constants import (
    COR_PRIMARIA,
)

from utils.services.avaliacoes.avaliacoes_service import listar_avaliacoes

# Paleta escura alinhada ao restante da interface do Evalytics.
LOGIN_FUNDO = "#1E1E1E"
LOGIN_CARD = "#2A2A2A"
LOGIN_CAMPO = "#252525"
LOGIN_TEXTO = "#FFFFFF"
LOGIN_TEXTO_SECUNDARIO = "#C2C2C8"
LOGIN_BORDA = "#45454B"

def ViewLogin(page: ft.Page, mudar_tela: Callable[[str], None]) -> ft.View:
    """
    Constrói a View (página inteira) de Login e Cadastro.
        Gerencia o estado da requisição HTTP para o Firebase e o redirecionamento.
    """

    """
    # =========================================================================
    # 1. INSTANCIAÇÃO DOS COMPONENTES BASE
    # =========================================================================
    """
    
    campo_nome = criar_campo_nome(LOGIN_TEXTO, LOGIN_TEXTO_SECUNDARIO, LOGIN_BORDA)
    campo_email = criar_campo_email(LOGIN_TEXTO, LOGIN_TEXTO_SECUNDARIO, LOGIN_BORDA)
    campo_senha = criar_campo_senha(LOGIN_TEXTO, LOGIN_TEXTO_SECUNDARIO, LOGIN_BORDA)
    for campo in (campo_nome, campo_email, campo_senha):
        campo.controls[1].bgcolor = LOGIN_CAMPO
        campo.controls[1].focused_border_color = COR_PRIMARIA
    
    # Desempacota as opções extras (Checkbox de Lembrar-me e Link de Esqueceu a Senha)
    opcoes_extras, checkbox_lembrar = criar_opcoes_extras(
        LOGIN_TEXTO_SECUNDARIO,
        COR_PRIMARIA,
    )

    """
    # =========================================================================
    # 2. SISTEMA DE ABAS (ENTRAR / CADASTRAR)
    # =========================================================================
    """
    
    btn_aba_signin = ft.TextButton(
        "Entrar", 
        data="signin", # O 'data' é usado para identificar qual botão foi clicado
        expand=True,   # Faz os dois botões dividirem o espaço 50/50
        style=criar_estilo_aba(ativo=True, cor_primaria=COR_PRIMARIA, cor_texto_inativo=LOGIN_TEXTO),
    )
    btn_aba_signup = ft.TextButton(
        "Cadastrar-se", 
        data="signup", 
        expand=True,
        style=criar_estilo_aba(ativo=False, cor_primaria=COR_PRIMARIA, cor_texto_inativo=LOGIN_TEXTO_SECUNDARIO),
    )

    """
    # =========================================================================
    # 3. LÓGICA DE NEGÓCIO (HTTP POST PARA O FIREBASE)
    # =========================================================================
    """
    
    async def fazer_login(e: ft.ControlEvent) -> None:
        """Coleta os dados, decide qual endpoint chamar (Login ou Cadastro) e persiste a sessão do usuário."""
        
        # Como campo_email é uma ft.Column (Rótulo + TextField), acessamos o TextField no índice 1 e pegamos seu `.value`.
        email = campo_email.controls[1].value.strip()
        senha = campo_senha.controls[1].value.strip()
        
        # Validação básica de Front-end
        if not email or not senha:
            snack = ft.SnackBar(ft.Text("Preencha e-mail e senha!"), bgcolor=ft.Colors.RED_400)
            page.overlay.append(snack) # No Flet moderno, SnackBars devem ir para o Overlay
            snack.open = True
            page.update()
            return

        # Verifica pela cor do botão se o usuário está na aba de Cadastro (Sign Up)
        is_signup = btn_aba_signup.style.color == COR_PRIMARIA if hasattr(btn_aba_signup.style, 'color') else False
        
        # Define o endpoint dinamicamente
        if is_signup:
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
        else:
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"

        payload = {
            "email": email,
            "password": senha,
            "returnSecureToken": True # Exige que o Firebase devolva os tokens de acesso
        }

        try:
            # Faz a requisição síncrona (A thread pausa aqui aguardando a API)
            response = requests.post(url, json=payload)
            data = response.json()

            if response.status_code == 200:
                lembrar_me = checkbox_lembrar.value is True # SUCESSO!

                # Aciona o State Manager Global para salvar os tokens localmente
                await auth_state.iniciar_sessao(
                    dados=data,
                    page=page,
                    lembrar_me=lembrar_me,
                )
                mudar_tela("/inicio") # Redireciona para a tela inicial

                # Diagnóstico temporário da autenticação
                print("Usuário autenticado:", auth_state.autenticado)
                print("ID token disponível:", bool(auth_state.id_token))
                print("Refresh token disponível:", bool(auth_state.refresh_token))
                
                resultado = listar_avaliacoes()
                print("Avaliações retornadas pela API:", len(resultado))
                
                # Exibe a confirmação de login.
                sucesso = ft.SnackBar(
                    content=ft.Text(
                        "Login realizado com sucesso!",
                        color=ft.Colors.WHITE,
                    ),
                    bgcolor=ft.Colors.GREEN_700,
                    duration=2500,
                )

                page.overlay.append(sucesso)
                sucesso.open = True
                page.update()
                
            else:
                erro_msg = data.get("error", {}).get("message", "Erro desconhecido") # TRATAMENTO DE ERROS DO FIREBASE
                
                # Mapeamento para PT-BR amigável
                if "INVALID_LOGIN_CREDENTIALS" in erro_msg or "INVALID_PASSWORD" in erro_msg:
                    erro_msg = "E-mail ou senha incorretos."
                elif "EMAIL_EXISTS" in erro_msg:
                    erro_msg = "Este e-mail já está cadastrado."
                elif "WEAK_PASSWORD" in erro_msg:
                    erro_msg = "A senha deve ter pelo menos 6 caracteres."

                snack = ft.SnackBar(ft.Text(f"Erro: {erro_msg}"), bgcolor=ft.Colors.RED_400)
                page.overlay.append(snack)
                snack.open = True
                page.update()

        except Exception as ex:
            
            erro_conexao = ft.SnackBar(ft.Text(f"Erro de conexão: {ex}"), bgcolor=ft.Colors.RED_400) # Captura erros de rede (Sem internet, timeout)
            page.overlay.append(erro_conexao)
            erro_conexao.open = True
            page.update()
            
    """
    # =========================================================================
    # 4. MONTAGEM FINAL DA INTERFACE
    # =========================================================================
    """
    
    cabecalho = criar_cabecalho(LOGIN_TEXTO, LOGIN_TEXTO_SECUNDARIO)

    # O botão principal da ação (Sign In / Create Account)
    btn_login = ft.ElevatedButton(
        "Entrar", bgcolor=COR_PRIMARIA, color=ft.Colors.WHITE,
        width=float("inf"), # float("inf") faz o botão ocupar 100% da largura disponível
        height=45, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        on_click=fazer_login,
    )

    secao_social = criar_login_social(LOGIN_TEXTO_SECUNDARIO, LOGIN_BORDA, LOGIN_TEXTO)
    rodape_termos = criar_rodape_termos(LOGIN_TEXTO_SECUNDARIO, COR_PRIMARIA)

    # Injeta os componentes na fábrica de closure para gerenciar a troca de visualização
    funcao_alternar = obter_funcao_alternar(
        btn_aba_signin, btn_aba_signup, campo_nome, opcoes_extras, btn_login, LOGIN_TEXTO, COR_PRIMARIA
    )
    
    # Ambas as abas chamam a mesma função; a lógica interna descobre quem chamou
    btn_aba_signin.on_click = funcao_alternar
    btn_aba_signup.on_click = funcao_alternar

    cabecalho_abas = ft.Row(controls=[btn_aba_signin, btn_aba_signup], alignment=ft.MainAxisAlignment.CENTER, spacing=10)

    # Agrupa todos os campos dentro da estrutura do Card branco
    card_login = criar_card_login(
        cabecalho_abas, campo_nome, campo_email, campo_senha, opcoes_extras, btn_login, secao_social, LOGIN_CARD
    )

    # O card ocupa uma fração responsiva da tela: em celulares usa toda a
    # largura disponível e, em telas maiores, mantém uma largura confortável.
    card_responsivo = ft.ResponsiveRow(
        columns=12,
        alignment=ft.MainAxisAlignment.CENTER,
        controls=[
            ft.Container(
                col={
                    "xs": 12,
                    "sm": 8,
                    "md": 6,
                    "lg": 5,
                    "xl": 4,
                    "xxl": 4,
                },
                content=card_login,
            ),
        ],
    )

    conteudo = ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        controls=[
            ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
                controls=[cabecalho, card_responsivo, rodape_termos],
            ),
        ],
    )

    # Retorna a página com rolagem vertical para telas baixas ou cadastro longo.
    return ft.View(
        route="/login", 
        bgcolor=LOGIN_FUNDO,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        vertical_alignment=ft.MainAxisAlignment.START,
        padding=ft.Padding.symmetric(horizontal=16, vertical=6),
        controls=[conteudo],
    )
