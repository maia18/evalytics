import asyncio
import requests
import flet as ft
from typing import Callable
from database.services.firebase_keys import FIREBASE_API_KEY
from components.core.auth.auth_state import auth_state
from models.login.core.cabecalho_login import criar_cabecalho
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
from components.landing.palette import (
    PAGE as LOGIN_FUNDO,
    SURFACE as LOGIN_CARD,
    BORDER as LOGIN_BORDA,
    TEXT as LOGIN_TEXTO,
    MUTED as LOGIN_TEXTO_SECUNDARIO,
    ROXO_CLARO as LOGIN_DESTAQUE,
    CIANO as LOGIN_CIANO,
    ROSA as LOGIN_ROSA,
)

from utils.services.avaliacoes.avaliacoes_service import listar_avaliacoes

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
        campo.controls[1].bgcolor = LOGIN_FUNDO
        campo.controls[1].focused_border_color = COR_PRIMARIA
    
    # Desempacota as opções extras (Checkbox de Lembrar-me e Link de Esqueceu a Senha)
    opcoes_extras, checkbox_lembrar = criar_opcoes_extras(
        LOGIN_TEXTO_SECUNDARIO,
        COR_PRIMARIA,
    )

    modo_cadastro = {"ativo": False}
    btn_cadastro = ft.TextButton(
        "Cadastre-se",
        data="signup",
        style=ft.ButtonStyle(
            color=COR_PRIMARIA,
            padding=ft.Padding.symmetric(horizontal=4, vertical=2),
            text_style=ft.TextStyle(size=12, weight=ft.FontWeight.W_600),
        ),
    )
    texto_cadastro = ft.Text("Não possui uma conta?", size=12, color=LOGIN_TEXTO_SECUNDARIO)
    rodape_cadastro = ft.Row(
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=4,
        controls=[texto_cadastro, btn_cadastro],
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

        is_signup = modo_cadastro["ativo"]
        
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
    secao_social = criar_login_social(LOGIN_TEXTO_SECUNDARIO, LOGIN_BORDA, LOGIN_TEXTO)
    secao_social.visible = True

    # O botão principal da ação (Sign In / Create Account)
    btn_login = ft.ElevatedButton(
        "Entrar", bgcolor=COR_PRIMARIA, color=ft.Colors.WHITE,
        width=float("inf"), # float("inf") faz o botão ocupar 100% da largura disponível
        height=45, style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
        on_click=fazer_login,
    )

    def alternar_modo_cadastro(e: ft.ControlEvent) -> None:
        modo_cadastro["ativo"] = not modo_cadastro["ativo"]
        em_cadastro = modo_cadastro["ativo"]
        campo_nome.visible = em_cadastro
        opcoes_extras.visible = not em_cadastro
        secao_social.visible = not em_cadastro
        btn_login.content = "Criar conta" if em_cadastro else "Entrar"
        cabecalho.controls[0].value = "Criar sua conta no Evalytics" if em_cadastro else "Fazer login em sua conta"
        cabecalho.controls[1].value = (
            "Preencha seus dados para criar uma conta."
            if em_cadastro
            else "Acesse o Evalytics para gerenciar as avaliações institucionais."
        )
        texto_cadastro.value = "Já possui uma conta?" if em_cadastro else "Não possui uma conta?"
        btn_cadastro.content = "Fazer login" if em_cadastro else "Cadastre-se"
        page.update()

    btn_cadastro.on_click = alternar_modo_cadastro

    # Agrupa os campos e as ações na ordem da referência visual.
    card_login = criar_card_login(
        campo_nome,
        campo_email,
        campo_senha,
        opcoes_extras,
        btn_login,
        secao_social,
        rodape_cadastro,
    )

    formulario_responsivo = ft.ResponsiveRow(
        columns=12,
        alignment=ft.MainAxisAlignment.CENTER,
        controls=[
            ft.Container(
                col={"xs": 12, "sm": 10, "md": 9, "lg": 8},
                content=card_login,
            ),
        ],
    )

    coluna_login = ft.Container(
        col={"xs": 12, "sm": 12, "md": 12, "lg": 6},
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16,
            controls=[cabecalho, formulario_responsivo],
        ),
    )

    curso_preview = ft.Text("", size=12, color=LOGIN_TEXTO_SECUNDARIO, font_family="monospace")
    semestre_preview = ft.Text("", size=12, color=LOGIN_TEXTO_SECUNDARIO, font_family="monospace")
    painel_animado = ft.Container(
        col={"xs": 12, "sm": 12, "md": 12, "lg": 6},
        padding=30,
        bgcolor=LOGIN_CARD,
        border=ft.Border.all(1, LOGIN_BORDA),
        border_radius=18,
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.START,
            spacing=20,
            controls=[
                ft.Text("Do feedback às decisões acadêmicas", size=26, weight=ft.FontWeight.W_700, color=LOGIN_TEXTO),
                ft.Text(
                    "Acompanhe avaliações, resultados por eixo e relatórios em um só lugar.",
                    size=14,
                    color=LOGIN_TEXTO_SECUNDARIO,
                ),
                ft.Container(
                    padding=22,
                    bgcolor=LOGIN_FUNDO,
                    border=ft.Border.all(1, LOGIN_BORDA),
                    border_radius=12,
                    content=ft.Column(
                        spacing=16,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.Text("Avaliação semestral", size=12, weight=ft.FontWeight.W_600, color=LOGIN_TEXTO),
                                    ft.Text("1 de 3 eixos", size=10, color=LOGIN_TEXTO_SECUNDARIO),
                                ],
                            ),
                            ft.Text("Curso", size=10, color=LOGIN_TEXTO_SECUNDARIO),
                            curso_preview,
                            ft.Container(height=1, bgcolor=LOGIN_BORDA),
                            ft.Text("Semestre", size=10, color=LOGIN_TEXTO_SECUNDARIO),
                            semestre_preview,
                        ],
                    ),
                ),
                ft.Row(
                    spacing=10,
                    controls=[
                        ft.Container(width=5, height=24, border_radius=3, bgcolor=LOGIN_CIANO),
                        ft.Text("Respostas organizadas por eixo", size=12, color=LOGIN_TEXTO),
                    ],
                ),
                ft.Row(
                    spacing=10,
                    controls=[
                        ft.Container(width=5, height=24, border_radius=3, bgcolor=LOGIN_ROSA),
                        ft.Text("Exportação em PDF ou CSV", size=12, color=LOGIN_TEXTO),
                    ],
                ),
            ],
        ),
    )

    layout_login = ft.ResponsiveRow(
        columns=12,
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=24,
        run_spacing=24,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            coluna_login,
            painel_animado,
        ],
    )

    conteudo = ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        alignment=ft.MainAxisAlignment.CENTER,
        controls=[
            ft.Container(
                expand=True,
                padding=ft.Padding.symmetric(horizontal=24, vertical=20),
                alignment=ft.Alignment.CENTER,
                content=layout_login,
            ),
        ],
    )

    token_animacao = object()
    page._login_preview_token = token_animacao

    def previa_ativa() -> bool:
        return (
            getattr(page, "_login_preview_token", None) is token_animacao
            and getattr(page, "rota_navegacao_atual", "/login") == "/login"
        )

    async def animar_previa() -> None:
        valores = (
            (curso_preview, "Engenharia de Telecomunicações"),
            (semestre_preview, "2026.1"),
        )
        await asyncio.sleep(0.5)
        while previa_ativa():
            for controle, valor in valores:
                for indice in range(len(valor) + 1):
                    if not previa_ativa():
                        return
                    controle.value = valor[:indice]
                    try:
                        controle.update()
                    except (RuntimeError, AssertionError):
                        return
                    await asyncio.sleep(0.045)
            await asyncio.sleep(1.5)
            for controle, _ in reversed(valores):
                valor_atual = controle.value or ""
                for indice in range(len(valor_atual) - 1, -1, -1):
                    if not previa_ativa():
                        return
                    controle.value = valor_atual[:indice]
                    try:
                        controle.update()
                    except (RuntimeError, AssertionError):
                        return
                    await asyncio.sleep(0.02)
            await asyncio.sleep(0.4)

    view = ft.View(
        route="/login", 
        bgcolor=LOGIN_FUNDO,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        vertical_alignment=ft.MainAxisAlignment.START,
        padding=ft.Padding.symmetric(horizontal=16, vertical=6),
        controls=[conteudo],
    )
    page.run_task(animar_previa)
    return view
