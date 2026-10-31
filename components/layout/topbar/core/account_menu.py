import requests
import flet as ft
from typing import Callable

from components.core.auth.auth_state import auth_state
from components.core.constants.constants import TEXTO_PRINCIPAL, SURFACE, COR_PRIMARIA
from components.core.router.rotas_cts import (
    ROTA_AVALIACOES,
    ROTA_CONFIGURACOES,
    ROTA_DASHBOARD_VISAO_GERAL,
    ROTA_INICIAL,
    ROTA_RELATORIOS,
)
from database.services.firebase_keys import FIREBASE_API_KEY


def _exibir_dialogo(page: ft.Page, titulo: str, conteudo: ft.Control, cores: dict[str, str]):
    dialogo = ft.AlertDialog(
        modal=True,
        bgcolor=cores[SURFACE],
        shape=ft.RoundedRectangleBorder(radius=14),
        title=ft.Text(titulo, color=cores[TEXTO_PRINCIPAL], weight=ft.FontWeight.W_700),
        content=ft.Container(width=420, content=conteudo),
        actions=[
            ft.TextButton(
                "Fechar",
                on_click=lambda e: _fechar_dialogo(page, dialogo),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(dialogo)
    dialogo.open = True
    page.update()
    return dialogo


def _fechar_dialogo(page: ft.Page, dialogo: ft.AlertDialog):
    dialogo.open = False
    page.update()


def _notificar(page: ft.Page, mensagem: str, sucesso: bool):
    snackbar = ft.SnackBar(
        content=ft.Text(mensagem, color=ft.Colors.WHITE),
        bgcolor=ft.Colors.GREEN_700 if sucesso else ft.Colors.RED_700,
    )
    page.overlay.append(snackbar)
    snackbar.open = True
    page.update()


def abrir_perfil(
    page: ft.Page,
    cores: dict[str, str],
    ao_salvar: Callable[[str, str], None],
):
    usuario = auth_state.usuario or {}
    email_atual = usuario.get("email", "")
    nome_atual = usuario.get("displayName") or usuario.get("name") or ""
    campo_nome = ft.TextField(
        label="Nome de exibição",
        value=nome_atual,
        hint_text="Como seu nome deve aparecer no Evalytics",
        text_style=ft.TextStyle(color=cores[TEXTO_PRINCIPAL]),
        label_style=ft.TextStyle(color=ft.Colors.GREY_500),
        border_color=ft.Colors.GREY_600,
        focused_border_color=COR_PRIMARIA,
        border_radius=8,
    )
    campo_email = ft.TextField(
        label="E-mail da conta",
        value=email_atual or "Carregando dados da conta...",
        read_only=True,
        text_style=ft.TextStyle(color=ft.Colors.GREY_400),
        label_style=ft.TextStyle(color=ft.Colors.GREY_500),
        border_color=ft.Colors.GREY_700,
        border_radius=8,
    )
    dialogo = None

    def salvar(e):
        nome = (campo_nome.value or "").strip()
        token = auth_state.id_token
        if not nome:
            _notificar(page, "Informe um nome para exibição.", False)
            return
        if not token or not FIREBASE_API_KEY:
            _notificar(page, "Não foi possível validar sua sessão para atualizar o perfil.", False)
            return

        try:
            resposta = requests.post(
                f"https://identitytoolkit.googleapis.com/v1/accounts:update?key={FIREBASE_API_KEY}",
                json={"idToken": token, "displayName": nome, "returnSecureToken": True},
                timeout=15,
            )
            dados = resposta.json()
        except requests.RequestException:
            _notificar(page, "Falha de conexão ao atualizar o perfil. Tente novamente.", False)
            return

        if resposta.status_code != 200:
            mensagem = dados.get("error", {}).get("message", "Não foi possível salvar o perfil.")
            if mensagem == "TOKEN_EXPIRED":
                mensagem = "Sua sessão expirou. Entre novamente para atualizar o perfil."
            _notificar(page, mensagem, False)
            return

        dados_usuario = auth_state.usuario
        if isinstance(dados_usuario, dict):
            dados_usuario.update(dados)
        email = dados.get("email") or email_atual
        nome_salvo = dados.get("displayName") or nome
        ao_salvar(nome_salvo, email)
        dialogo.open = False
        _notificar(page, "Perfil atualizado.", True)

    dialogo = ft.AlertDialog(
        modal=True,
        bgcolor=cores[SURFACE],
        shape=ft.RoundedRectangleBorder(radius=14),
        title=ft.Text("Meu perfil", color=cores[TEXTO_PRINCIPAL], weight=ft.FontWeight.W_700),
        content=ft.Container(
            width=420,
            content=ft.Column(
                tight=True,
                spacing=14,
                controls=[
                    ft.Text("Atualize o nome associado à sua conta.", size=12, color=ft.Colors.GREY_400),
                    campo_nome,
                    campo_email,
                ],
            ),
        ),
        actions=[
            ft.TextButton("Cancelar", on_click=lambda e: _fechar_dialogo(page, dialogo)),
            ft.ElevatedButton(
                "Salvar alterações",
                bgcolor=COR_PRIMARIA,
                color=ft.Colors.WHITE,
                on_click=salvar,
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.overlay.append(dialogo)
    dialogo.open = True
    page.update()


def abrir_ajuda(page: ft.Page, cores: dict[str, str], mudar_tela: Callable[[str], None]):
    conteudo = ft.Column(
        tight=True,
        spacing=12,
        controls=[
            ft.Text("Comece por uma avaliação, acompanhe os indicadores no dashboard e consulte os relatórios para analisar os resultados.", color=ft.Colors.GREY_400, size=13),
            ft.Text("Atalhos", color=cores[TEXTO_PRINCIPAL], weight=ft.FontWeight.W_600),
            ft.Row(
                wrap=True,
                controls=[
                    ft.TextButton("Avaliações", on_click=lambda e: mudar_tela(ROTA_AVALIACOES)),
                    ft.TextButton("Dashboard", on_click=lambda e: mudar_tela(ROTA_DASHBOARD_VISAO_GERAL)),
                    ft.TextButton("Relatórios", on_click=lambda e: mudar_tela(ROTA_RELATORIOS)),
                ],
            ),
            ft.Divider(),
            ft.Text("O contato de suporte da instituição não está configurado no aplicativo.", size=11, color=ft.Colors.GREY_500),
        ],
    )
    _exibir_dialogo(page, "Ajuda e suporte", conteudo, cores)


def abrir_sobre(page: ft.Page, cores: dict[str, str]):
    conteudo = ft.Column(
        tight=True,
        spacing=10,
        controls=[
            ft.Text("Evalytics", size=18, weight=ft.FontWeight.W_700, color=cores[TEXTO_PRINCIPAL]),
            ft.Text(
                "Sistema de avaliação institucional para organizar cursos e indicadores, acompanhar resultados e gerar relatórios em PDF e CSV.",
                size=13,
                color=ft.Colors.GREY_400,
            ),
        ],
    )
    _exibir_dialogo(page, "Sobre o Evalytics", conteudo, cores)


def criar_menu_conta(
    page: ft.Page,
    cores: dict[str, str],
    mudar_tela: Callable[[str], None],
) -> ft.PopupMenuButton:
    usuario = auth_state.usuario or {}
    estado = {
        "nome": usuario.get("displayName") or usuario.get("name") or "Conta",
        "email": usuario.get("email", ""),
    }
    avatar_texto = ft.Text(size=10, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)
    nome_texto = ft.Text(size=12, weight=ft.FontWeight.W_600, color=cores[TEXTO_PRINCIPAL])
    email_texto = ft.Text(size=10, color=ft.Colors.GREY_500)

    def atualizar_identificacao(nome: str, email: str):
        estado["nome"] = nome or "Conta"
        estado["email"] = email or ""
        partes = [parte for parte in estado["nome"].replace(".", " ").replace("_", " ").split() if parte]
        avatar_texto.value = "".join(parte[0] for parte in partes[:2]).upper() or "U"
        nome_texto.value = estado["nome"]
        email_texto.value = estado["email"] or "Usuário autenticado"
        page.update()

    atualizar_identificacao(estado["nome"], estado["email"])

    async def fazer_logout(e):
        await auth_state.encerrar_sessao(page)
        mudar_tela(ROTA_INICIAL)

    return ft.PopupMenuButton(
        content=ft.CircleAvatar(
            radius=14,
            bgcolor=COR_PRIMARIA,
            color=ft.Colors.WHITE,
            content=avatar_texto,
        ),
        items=[
            ft.PopupMenuItem(
                content=ft.Column(spacing=2, controls=[nome_texto, email_texto]),
                height=56,
            ),
            ft.PopupMenuItem(
                content="Meu perfil",
                icon=ft.Icons.PERSON_OUTLINE,
                on_click=lambda e: abrir_perfil(page, cores, atualizar_identificacao),
            ),
            ft.PopupMenuItem(
                content="Ajuda e suporte",
                icon=ft.Icons.HELP_OUTLINE,
                on_click=lambda e: abrir_ajuda(page, cores, mudar_tela),
            ),
            ft.PopupMenuItem(
                content="Sobre o Evalytics",
                icon=ft.Icons.INFO_OUTLINE,
                on_click=lambda e: abrir_sobre(page, cores),
            ),
            ft.PopupMenuItem(
                content="Configurações",
                icon=ft.Icons.SETTINGS_OUTLINED,
                on_click=lambda e: mudar_tela(ROTA_CONFIGURACOES),
            ),
            ft.PopupMenuItem(content="Sair", icon=ft.Icons.LOGOUT, on_click=fazer_logout),
        ],
        bgcolor=cores[SURFACE],
        menu_position=ft.PopupMenuPosition.UNDER,
        shape=ft.RoundedRectangleBorder(radius=10),
        tooltip="Menu da conta",
    )
